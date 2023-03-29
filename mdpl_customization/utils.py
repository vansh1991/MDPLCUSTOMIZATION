import frappe


@frappe.whitelist()
def update_receipt(self,method=None):
    if self.purchase_invoice:
        if self.items:
            for item in self.items:
                if not item.serial_no:
                    # frappe.msgprint("Hello")
                    item.serial_no=frappe.db.get_value("Purchase Invoice Item",{"item_code":item.item_code,"parent":self.purchase_invoice},"serial_no")