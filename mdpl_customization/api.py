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
	url = "https://mdpltest.cloud.mattermost.com/api/v4/actions/dialogs/open"
	headers = {
		'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=json.dumps(dict_data))
	frappe.local.response.update(json.loads(response.text))
