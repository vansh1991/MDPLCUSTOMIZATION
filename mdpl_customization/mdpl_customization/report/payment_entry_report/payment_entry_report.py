# Copyright (c) 2023, vansh and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters,columns)
	return columns,data


def get_columns(filters):
	columns= [
        {'label':"Sales Invoice No", 'fieldname':'sales_invoice_no','fieldtype':'Link', "options":"Sales Invoice",'width':200},
        {'label':"Customer", 'fieldname':'customer','fieldtype':'Link',"options":"Customer", 'width':200},
		{'label':"Total AMount", 'fieldname':'total_amount','fieldtype':'Float','width':100},
		{'label':"Outstanding Amount", 'fieldname':'outstanding_amount','fieldtype':'Float','width':100},
		{'label':"Posting Date", 'fieldname':'posting_date','fieldtype':'Date','width':100},
		{'label':"Cheque Date", 'fieldname':'cheque_date','fieldtype':'Date','width':100},
		{'label':"Cheque No", 'fieldname':'cheque_no','fieldtype':'Data','width':150},
		{'label':"Cheque Amount", 'fieldname':'cheque_amount','fieldtype':'Float','width':100},
		{'label':"Status", 'fieldname':'status','fieldtype':'Link',"options":"Workflow State", 'width':150},
    ]

	return columns

def get_conditions(filters):
	conditions =""
	if filters.from_date and filters.to_date:
		conditions+=f"and pe.posting_date between '{filters.get('from_date')}' and '{filters.get('to_date')}' "
	
	# if filters.status:
	# 	conditions+=f"and pe.workflow_state = '{filters.status}'"
	return conditions

def get_data(filters,columns):
	conditions=get_conditions(filters)
	frappe.log_error("Filters",conditions)
	return frappe.db.sql(f"""select per.reference_name as sales_invoice_no, si.customer as customer,si.rounded_total as total_amount,
                       si.outstanding_amount as outstanding_amount,si.posting_date as posting_date,
                        pe.reference_date as cheque_date,pe.reference_no as cheque_no,pe.paid_amount as cheque_amount,pe.workflow_state as status
                        from `tabPayment Entry` as pe left join `tabPayment Entry Reference` as per on pe.name = per.parent  
                        left join `tabSales Invoice` as si on si.name = per.reference_name 
						where per.reference_doctype= 'Sales Invoice' and si.outstanding_amount > 0 {conditions} """)