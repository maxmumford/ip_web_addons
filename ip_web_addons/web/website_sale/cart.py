from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.translate import _

from openerp.addons.ip_web_addons import jsend, tools

class Ecommerce(http.Controller):
	
	NO_ORDER = 'No Order'

	@jsend.jsend_error_catcher
	@http.route(['/shop/add_cart_multi/'], type='http', auth="public", methods=['POST'], website=True, multilang=True)
	def add_cart_multi(self, **product_quantity_map):
		"""
		Add multiple products to the cart with specified quantities
		@param dict product_quantity_map: A dictionary keyed by product IDs where values represent quantities 
		"""
		if not hasattr(product_quantity_map, '__iter__'):
			raise jsend.JsendTypeError('product_quantity_map', 'product_quantity_map should be a json object mapping product IDs to quantities to add to the cart')
		
		for product_id, quantity in product_quantity_map.items():
			# data validation
			if not tools.isnumeric(product_id):
				raise jsend.JsendTypeError('product_id', 'Product IDS must be numeric')
			if not tools.isnumeric(quantity):
				raise jsend.JsendTypeError('quantity', 'Quantity must be numeric') 
			
			product_id = int(product_id)
			quantity = float(quantity)
			
			new_quantity = request.registry['website']._ecommerce_add_product_to_cart(request.cr, request.uid,
				product_id=product_id,
				number=quantity,
				context=request.context)
			# bug in _ecommerce_add_product_to_cart means that if adding a new product to the cart, 
			# the quantity is always set to 1. Handle this by checking returned qty against specified
			# quantity and adjust it accordingly
			if new_quantity < quantity:
				request.registry['website']._ecommerce_add_product_to_cart(request.cr, request.uid,
				product_id=int(product_id),
				number=quantity - new_quantity,
				context=request.context)
				
		return self.get_cart_info()
		
	@jsend.jsend_error_catcher
	@http.route(['/shop/get_cart_info/'], type='http', auth="public", website=True, multilang=True)
	def get_cart_info(self):
		"""
		Get the IDS and quantities of products in the cart
		"""
		order = request.registry['website'].ecommerce_get_current_order(request.cr, request.uid, context=request.context)
		if not order:
			return jsend.jsend_fail({'order': 'There are no current orders for this customer'})

		product_quantites = dict([(line.product_id.id, line.product_uom_qty) for line in order.order_line])
		for line in order.order_line:
			product_quantites[line.product_id.id] += line.product_uos_qty
		
		vals = {
			'product_quantities': product_quantites, 
			'total_price': order.amount_total, 
			'product_count': order.get_number_of_products()
		}
		return jsend.jsend_success(vals)
