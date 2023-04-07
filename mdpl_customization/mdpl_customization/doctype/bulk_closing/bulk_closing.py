# Copyright (c) 2023, vansh and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class BulkClosing(Document):
	pass


@frappe.whitelist()
def get_record(doc):
    if doc == "Purchase Order":
        return frappe.db.sql(f"""select name,grand_total,supplier,status from `tabPurchase Order` where status not in ('Closed','On Hold','Completed') and docstatus = 1""",as_dict=1)
    else:
        if doc=="Sales Order":
            return frappe.db.sql(f"""select name,grand_total,customer,status from `tabSales Order` where status not in ('Closed','On Hold','Completed') and docstatus = 1""",as_dict=1)
        elif doc == "Delivery Note":
            return frappe.db.sql(f"""select name,grand_total,customer,status from `tabDelivery Note` where status not in ('Closed','Completed') and docstatus = 1""",as_dict=1)