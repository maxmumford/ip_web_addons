from openerp.osv import osv, fields
from openerp.tools.translate import _

class product_template(osv.osv):

	_inherit = "product.template"

	_columns = {
		"auto_ship": fields.boolean('Can Auto Ship?', help="Defines whether customers are allowed to auto ship this product or not"),
	}
