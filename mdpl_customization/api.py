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

##HDFC Integrattion Part

@frappe.whitelist(allow_guest=True)
def get_hdfc_log(**kwargs):
	if kwargs:
		frappe.log_error("Kwargs",kwargs)
		# custom_decrypt(kwargs)
		get_redirect_date(kwargs)
		frappe.log_error("Kwargsd",kwargs.get('encResp'))
		# return kwargs


from string import Template
from Crypto.Cipher import AES
import hashlib
import json
import urllib.parse

'''
Please put in the 32 bit alphanumeric key and Access Code in quotes provided by CCAvenues.
'''
accessCode = 'AVSX39KL56AW20XSWA' 	
workingKey = 'EB1A0F6223A2933E9215F793C8DE6A7C'



#Encrypt Decrypt

# @frappe.whitelist(allow_guest=True)
# def pad(data):
# 	length = 16 - (len(data) % 16)
# 	data += chr(length)*length
# 	return data

# @frappe.whitelist(allow_guest=True)
# def encrypt(plainText,workingKey):
#     iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
#     plainText = pad(plainText)
#     encDigest = hashlib.md5()
#     encDigest.update(workingKey.encode())
#     enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
#     encryptedText = enc_cipher.encrypt(plainText.encode()).hex()
#     return encryptedText


# @frappe.whitelist(allow_guest=True)
# def decrypt(cipherText,workingKey):
#     iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
#     decDigest = hashlib.md5()
#     decDigest.update(workingKey.encode())
#     encryptedText = bytes.fromhex(cipherText)
#     dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
#     decryptedText = dec_cipher.decrypt(encryptedText)
#     decoded_string = decryptedText.decode('utf-8')
#     parsed_data = urllib.parse.parse_qs(decoded_string)
#     parsed_dict = {k: v[0] for k, v in parsed_data.items()}
#     json_data = json.dumps(parsed_dict, indent=4)
#     print(json_data)
#     return str(json_data)

# @frappe.whitelist(allow_guest=True)
# def custom_decrypt(kwargs):
# 	cipherText=kwargs.get('encResp')
# 	workingKey= 'EB1A0F6223A2933E9215F793C8DE6A7C'
# 	decrypt_json=decrypt(cipherText,workingKey)
# 	frappe.log_error("decrypt_json",decrypt_json)




@frappe.whitelist()
def get_redirect_date(kwargs):
	# frappe.set_user("Administrator")
	# if kwargs:
	# 	import requests
	# 	import json

	# 	url = "https://testing.mdpl.org.in/api/method/mdpl_customization.api.get_sales_pr"

	# 	payload ={
	# 		"kwargs":kwargs,
	# 		"sales_order":kwargs.get('orderNo')
	# 	}
	# 	headers = {
	# 	'Authorization': 'token e9ffc25922df3cd:551fea26a3edabd',
	# 	'Content-Type': 'application/json'
	# 	}

	# 	response = requests.request("POST", url, headers=headers, data=payload)

	# 	if response.json():
	# 		frappe.log_error("kwargs pr",response.json())

	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = "https://testing.mdpl.org.in/all-products"




# @frappe.whitelist()
# def create_log(kwarg):
# 	if kwarg:
# 		frappe.get_doc({
# 			"doctype":"HDFC Log",
# 			"params":str(kwarg),
# 			"status":"Success"
# 		}).insert(ignore_permissions=True)

# @frappe.whitelist()
# def create_payment(kwarg,orderNo):
# 	frappe.log_error("Payment Entry",kwarg)
# 	if kwarg:
# 		split_kwarg=kwarg.split("&")
# 		frappe.get_doc({
# 			"doctype":"HDFC Payment",
# 			"data":str(kwarg),
# 			"status":"Success",
# 			"reference_doctype":"Sales Order",
# 			"reference_docname":orderNo
# 			# "bank_reference_no":split_kwarg[],
# 			# "tracking_id":split_kwarg[1].split("=")[1]
# 		}).insert()



@frappe.whitelist()
def get_sales_pr(sales_order):
	if sales_order:
		# amount=frappe.db.get_value("Sales Order",sales_order,"grand_total")
		# pr=frappe.db.get_value("Payment Request",{"reference_name":sales_order,"reference_doctype":"Sales Order"},"name")
		# kwarg=decrypt(kwargs.get("encResp"),workingKey)
		# frappe.log_error("kwargs pr",get_payment_requests)
		# if pr:
		# 	# make_payment_entry(pr)
			# create_log(kwarg)
			# create_payment(kwarg,sales_order)
		return "Hello"


from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_url, nowdate
from frappe.utils.background_jobs import enqueue
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpnext.accounts.doctype.payment_entry.payment_entry import (
	get_company_defaults,
	get_payment_entry,
)
from erpnext.accounts.doctype.subscription_plan.subscription_plan import get_plan_rate
from erpnext.accounts.party import get_party_account, get_party_bank_account
from erpnext.accounts.utils import get_account_currency
#from erpnext.erpnext_integrations.stripe_integration import create_stripe_subscription
from erpnext.utilities import payment_app_import_guard


# @frappe.whitelist()
# def get_payment_request(self,method=None):
# 	if name:
# 		pr=frappe.db.get_value("Payment Request",{"reference_name":self.reference_docname,"reference_doctype":"Sales Order"},"name")
# 		make_payment_entry(pr)


# @frappe.whitelist()
# def make_payment_entry(docname):
# 	doc = frappe.get_doc("Payment Request", docname)
	
# 	create_payment_entry(doc,submit=False)


# @frappe.whitelist()
# def create_payment_entry(self, submit=True):
# 		"""create entry"""
# 		frappe.flags.ignore_account_permission = True
# 		frappe.flags.ignore_permissions = True

# 		ref_doc = frappe.get_doc(self.reference_doctype, self.reference_name)
		

# 		if self.reference_doctype in ["Sales Invoice", "POS Invoice"]:
# 			party_account = ref_doc.debit_to
# 		elif self.reference_doctype == "Purchase Invoice":
# 			party_account = ref_doc.credit_to
# 		else:
# 			party_account = get_party_account("Customer", ref_doc.get("customer"), ref_doc.company)

# 		party_account_currency = ref_doc.get("party_account_currency") or get_account_currency(
# 			party_account
# 		)

# 		bank_amount = self.grand_total
# 		if (
# 			party_account_currency == ref_doc.company_currency and party_account_currency != self.currency
# 		):
# 			party_amount = ref_doc.get("base_rounded_total") or ref_doc.get("base_grand_total")
# 		else:
# 			party_amount = self.grand_total

# 		payment_entry = get_payment_entry(
# 			self.reference_doctype,
# 			self.reference_name,
# 			party_amount=party_amount,
# 			bank_account=self.payment_account,
# 			bank_amount=bank_amount,
# 		)

		

# 		payment_entry.update(
# 			{
# 				"mode_of_payment":"HDFC UPI Transfer",
# 				"reference_no": self.name,
# 				"reference_date": nowdate(),
# 				"remarks": "Payment Entry against {0} {1} via Payment Request {2}".format(
# 					self.reference_doctype, self.reference_name, self.name
# 				),
# 			}
# 		)

# 		# Update dimensions
# 		payment_entry.update(
# 			{
# 				"cost_center": self.get("cost_center"),
# 				"project": self.get("project"),
# 			}
# 		)
		

# 		for dimension in get_accounting_dimensions():
# 			payment_entry.update({dimension: self.get(dimension)})

# 		if payment_entry.difference_amount:
# 			company_details = get_company_defaults(ref_doc.company)

# 			payment_entry.append(
# 				"deductions",
# 				{
# 					"account": company_details.exchange_gain_loss_account,
# 					"cost_center": company_details.cost_center,
# 					"amount": payment_entry.difference_amount,
# 				},
# 			)

# 		frappe.log_error("payment_entry",payment_entry.as_dict())
# 		if payment_entry:
# 			# fraappe.log_error("payment_entry",payment_entry)
# 			payment_entry.insert(ignore_permissions=True)
# 			payment_entry.submit()

# 		return payment_entry
