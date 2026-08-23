import frappe
import json
@frappe.whitelist()
def update_receipt(self,method=None):
    if self.purchase_invoice:
        if self.items:
            for item in self.items:
                if not item.serial_no:
                    # frappe.msgprint("Hello")
                    item.serial_no=frappe.db.get_value("Purchase Invoice Item",{"item_code":item.item_code,"parent":self.purchase_invoice},"serial_no")
def issue_query(user=None):
    user=frappe.session.user
    if user != "Administrator":
        return f"""`tabIssue`.name in (select name from `tabIssue` where owner = '{user}' or _assign like '%{user}%')"""
import frappe
from frappe import _
from frappe.model.meta import get_field_precision
from frappe.utils import flt, format_datetime, get_datetime
@frappe.whitelist()
def validate_return_against(doc):
	if not frappe.db.exists(doc.doctype, doc.return_against):
		frappe.throw(
			_("Invalid {0}: {1}").format(doc.meta.get_label("return_against"), doc.return_against)
		)
	else:
		ref_doc = frappe.get_doc(doc.doctype, doc.return_against)
		party_type = "customer" if doc.doctype in ("Sales Invoice", "Delivery Note") else "supplier"
		if (
			ref_doc.company == doc.company
			and ref_doc.get(party_type) == doc.get(party_type)
			and ref_doc.docstatus.is_submitted()
		):
			# validate posting date time
			return_posting_datetime = "%s %s" % (doc.posting_date, doc.get("posting_time") or "00:00:00")
			ref_posting_datetime = "%s %s" % (
				ref_doc.posting_date,
				ref_doc.get("posting_time") or "00:00:00",
			)
               
			account_settings= frappe.db.get_single_value("Accounts Settings", "custom_allowed_role_for_pi", cache=True)
			frappe.log_error("account_settings",frappe.session.user)
			# if account_settings in frappe.get_roles(frappe.session.user):
			# 	return
			if get_datetime(return_posting_datetime) < get_datetime(ref_posting_datetime):
				# account_settings= frappe.db.get_single_value("Accounts Settings", "custom_allowed_role_for_pi", cache=True)
				user_role=frappe.get_roles(frappe.session.user)
				frappe.log_error("user_role",user_role)
				if str(account_settings) in user_role:
					frappe.log_error("account_settings",account_settings)
					return
				else:
					frappe.throw(
						_("Posting timestamp must be after {0}").format(format_datetime(ref_posting_datetime))
					)
			# validate same exchange rate
			if doc.conversion_rate != ref_doc.conversion_rate:
				frappe.throw(
					_("Exchange Rate must be same as {0} {1} ({2})").format(
						doc.doctype, doc.return_against, ref_doc.conversion_rate
					)
				)
			# validate update stock
			if doc.doctype == "Sales Invoice" and doc.update_stock and not ref_doc.update_stock:
				frappe.throw(
					_("'Update Stock' can not be checked because items are not delivered via {0}").format(
						doc.return_against
					)
				)
from erpnext.accounts.utils import (
	cancel_exchange_gain_loss_journal,
	get_account_currency,
	get_balance_on,
	get_stock_accounts,
	get_stock_and_account_balance,
)


def _resolve_outstanding_updater():
	"""
	The function that recalculates a voucher's outstanding_amount was
	renamed between ERPNext versions: older releases call it
	update_outstanding_amt, newer v15 releases (matching what core
	sales_invoice.py / purchase_invoice.py import) call it
	update_voucher_outstanding. Resolve whichever exists on this install
	instead of hardcoding one name, so this keeps working across patch
	upgrades.
	"""
	from erpnext.accounts import utils as accounts_utils

	fn = getattr(accounts_utils, "update_voucher_outstanding", None)
	if fn is None:
		fn = getattr(accounts_utils, "update_outstanding_amt", None)
	return fn


@frappe.whitelist()
def make_gl_entries(self, method=None):
	"""
	BUG THIS FIXES:
	This hook fires on Journal Entry's on_update_after_submit event --
	i.e. every time a submitted JV is edited and saved again (for example,
	splitting one lump settlement into several invoice-specific rows
	across multiple saves, which is a normal accounting workflow).

	The original version below rebuilt GL Entries from ALL of the JV's
	CURRENT account rows on every single resave, always with
	update_outstanding="Yes". That re-decremented the outstanding_amount
	of every referenced Sales/Purchase Invoice on every resave --
	including rows that hadn't changed and were already correctly
	decremented by an earlier save. The GL Entry table itself stayed
	correct (it's fully deleted and rebuilt each time), but the invoice's
	own cached outstanding_amount field kept compounding downward with
	each edit, producing invoices whose outstanding_amount was 2x, 3x,
	etc. more negative than it should have been.

	FIX: before rebuilding, reverse the outstanding-amount effect of the
	PREVIOUSLY saved state (using the resolved updater function, which
	recalculates from GL + Payment Ledger rather than blindly
	incrementing/decrementing), then rebuild forward from the current
	state. This makes each resave idempotent -- it reflects only the
	actual current allocation, not an accumulating stack of every past
	save.
	"""
	from erpnext.accounts.general_ledger import make_gl_entries as core_make_gl_entries

	update_voucher_outstanding = _resolve_outstanding_updater()

	# 1. Reverse the outstanding effect of the PREVIOUSLY saved state
	#    before we delete/rebuild GL Entries for this JV.
	old_doc = self.get_doc_before_save()
	if old_doc and update_voucher_outstanding:
		for row in old_doc.accounts:
			if row.reference_type and row.reference_name and row.party_type and row.party:
				try:
					update_voucher_outstanding(
						row.account,
						row.party_type,
						row.party,
						row.reference_type,
						row.reference_name,
					)
				except Exception:
					frappe.log_error(
						title="make_gl_entries: failed to reverse prior outstanding",
						message=frappe.get_traceback(),
					)

	# 2. Delete and rebuild this JV's GL Entries from its CURRENT state, as before.
	frappe.db.delete("GL Entry", {
		"voucher_type": "Journal Entry", "voucher_no": self.name
	})

	cancel = 0
	adv_adj = 0
	merge_entries = frappe.db.get_single_value("Accounts Settings", "merge_similar_account_heads")
	gl_map = self.build_gl_map()

	if self.voucher_type in ("Deferred Revenue", "Deferred Expense"):
		update_outstanding = "No"
	else:
		update_outstanding = "Yes"

	if gl_map:
		core_make_gl_entries(
			gl_map,
			cancel=cancel,
			adv_adj=adv_adj,
			merge_entries=merge_entries,
			update_outstanding=update_outstanding,
		)
		if cancel:
			cancel_exchange_gain_loss_journal(frappe._dict(doctype=self.doctype, name=self.name))
