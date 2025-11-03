__version__ = '0.0.1'

from erpnext.controllers import sales_and_purchase_return as sra 
from mdpl_customization.utils import validate_return_against as cra


sra.validate_return_against=cra
