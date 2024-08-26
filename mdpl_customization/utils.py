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

@frappe.whitelist()
def make_gl_entries(self,method=None):

	# get_all_pre_gl=frappe.db.get_all("GL Entry",filters={"voucher_type":"Journal Entry","voucher_no":self.name},fileds=["name"])
	# if get_all_pre_gl:
	# 	for gl in get_all_pre_gl:
	# 		frappe
	frappe.db.delete("GL Entry", {
		"voucher_type":"Journal Entry","voucher_no":self.name
	})

	cancel=0 
	adv_adj=0
	from erpnext.accounts.general_ledger import make_gl_entries

	merge_entries = frappe.db.get_single_value("Accounts Settings", "merge_similar_account_heads")

	gl_map = self.build_gl_map()
	if self.voucher_type in ("Deferred Revenue", "Deferred Expense"):
		update_outstanding = "No"
	else:
		update_outstanding = "Yes"

	if gl_map:
		make_gl_entries(
			gl_map,
			cancel=cancel,
			adv_adj=adv_adj,
			merge_entries=merge_entries,
			update_outstanding=update_outstanding,
		)
		if cancel:
			cancel_exchange_gain_loss_journal(frappe._dict(doctype=self.doctype, name=self.name))