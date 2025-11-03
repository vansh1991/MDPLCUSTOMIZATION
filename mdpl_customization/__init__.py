__version__ = '0.0.1'

def patch_sales_and_purchase_return():
    try:
        from erpnext.controllers import sales_and_purchase_return as sra
        from mdpl_customization.utils import validate_return_against as cra
        sra.validate_return_against = cra
    except ModuleNotFoundError:
        # frappe/erpnext not available during build
        pass

# run patch after frappe loads
try:
    import frappe
    frappe.ready += patch_sales_and_purchase_return
except Exception:
    # ignore build-time errors
    pass
