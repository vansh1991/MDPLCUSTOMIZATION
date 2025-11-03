__version__ = '0.0.1'

import frappe

try:
    # Import ERPNext controller (only works if ERPNext is already installed)
    from erpnext.controllers import sales_and_purchase_return as sra
    from mdpl_customization.utils import validate_return_against as cra

    # Override ERPNext's function
    sra.validate_return_against = cra

except ImportError:
    frappe.logger().warning("ERPNext not found — skipping return validation override during build.")
