from datetime import datetime, timedelta

from openerp.osv import osv, fields
from openerp.tools.translate import _

class product_template(osv.osv):

	_inherit = "product.template"
	
	def _earliest_delivery_date(self, cr, uid, ids, field_name, arg, context):
		""" Calculates the earliest delivery based on product.sale_dely and if today is before 6:30pm or not """
		res = {}
		start = datetime.today()
		
		if start.hour > 18 or (start.hour == 18 and start.minute > 30):
			start = (start + timedelta(days=1))
		start = start.date()
		
		for product in self.browse(cr, uid, ids, context=context):
			earliest_delivery_date = start + timedelta(days=product.sale_delay)
			res[product.id] = earliest_delivery_date.strftime('%Y-%m-%d')
		return res
	
	_columns = {
		"auto_ship": fields.boolean('Can Auto Ship?', help="Defines whether customers are allowed to auto ship this product or not"),
		"box_quantity": fields.integer("Box Quantity", help="The number of products contained in each box from the supplier"),
		'earliest_delivery_date': fields.function(
            _earliest_delivery_date,
            type='date',
            method=True,
            string='Earliest Delivery Date',
            help="The earliest date of delivery if the product is bought before 18:30"),
	}
	
	_defaults = {
		"box_quantity": 1,
	}
