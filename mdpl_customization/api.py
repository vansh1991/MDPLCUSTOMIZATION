import frappe, requests, json


@frappe.whitelist(allow_guest=True)
def get_all_customers():
	customers = frappe.db.sql('''select name as text, name as value from `tabCustomer` where disabled=0 ''',as_dict=1)
	items = frappe.db.sql("select name as value, item_name as text from `tabItem` where disabled=0",as_dict=1)
	dict_data = {
		"trigger_id":frappe.form_dict.trigger_id,
		"url": "https://erp.mdpl.org.in/api/method/create_sales_order",
		"dialog": {
		"callback_id": "<ID specified by the integration to identify the request>","title": "Popup",
		"introduction_text": "Popup for create Order","elements": [
		{
		"display_name": "Customer",
		"name": "customer",
		"type": "select",
		"options": customers
		},
		{
		"display_name": "Item",
		"name": "item_code",
		"type": "select",
		"options": items
                },
		{
		"display_name":"Qty",
		"name":"qty",
		"type":"text",
		"subtype":"number",
		"placeholder":"Please Enter Qty"
		}
		],
		"submit_label": "Submit",
		"notify_on_cancel": False,
		"state": "Submit"
		}
		} 
	url = "https://chat.mdpl.org.in/api/v4/actions/dialogs/open"
	headers = {
		'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=json.dumps(dict_data))
	frappe.local.response.update(json.loads(response.text))

@frappe.whitelist(allow_guest=True)
def validate_sales_order(self,method=None):
	if self.customer:
		# frappe.msgprint(str(frappe.get_roles()))
		get_role=frappe.db.get_single_value('Selling Settings', 'role_permmission')
		if not get_role in frappe.get_roles():
			from frappe.utils import today
			from frappe.utils import date_diff
			get_invoice_list=frappe.db.sql(f"select name,posting_date from `tabSales Invoice` where customer='{self.customer}' and is_return=0 and status != 'Cancelled'",as_dict=1)
			if get_invoice_list:
				for name_inv in get_invoice_list:
					# frappe.msgprint(str(name_inv))
					get_payment_entry=frappe.db.sql(f"select parent from `tabPayment Entry Reference` where reference_name='{name_inv.name}'",as_dict=1)
					if get_payment_entry:
						pass
						# for payment in get_payment_entry:
						# 	get_payment=frappe.db.get_value("Paymment Entry",)
					else:
						posting_d=name_inv.posting_date
						cur_date=today()
						total_diff=date_diff(cur_date, posting_d)
						if total_diff > frappe.db.get_value("Customer",{"name":self.customer},"payment_days"):
							frappe.throw(f"You are Not Able to Submit the Order Payment is Not Cleared against {name_inv.name}")

@frappe.whitelist()
def submit_sales_order(name):
	if name:

		get_doc_data=frappe.get_doc("Sales Order",name)
		get_doc_data.flags.ignore_permissions=True
		get_doc_data.submit()
		frappe.db.commit()

@frappe.whitelist()
def validate_payment_entry(self,method=None):
	from frappe import utils
	if self.workflow_state == "Cheque Deposited":
		if self.posting_date:
			frappe.db.set_value("Payment Entry",self.name,"posting_date",utils.today())
		# else:
		# 	frappe.db.set_value("Payment Entry",self.name,"posting_date",utils.today())
		self.reload()



@frappe.whitelist(allow_guest=True)
def get_hdfc_log(**kwargs):
	if kwargs:
		frappe.log_error("Kwargs",kwargs)
		return kwargs