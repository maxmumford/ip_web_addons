from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.translate import _

class Ecommerce(http.Controller):

	@http.route(['/shop/add_cart_multi/'], type='http', auth="public", methods=['POST'], website=True, multilang=True)
	def add_cart_multi(self, **product_quantity_map):
		"""
		Add multiple products to the cart with specified quantities
		@param dict product_quantity_map: A dictionary keyed by product IDs where values represent quantities 
		"""
		for product_id, quantity in product_quantity_map.items():
			product_id = int(product_id)
			quantity = float(quantity)
			
			new_quantity = request.registry['website']._ecommerce_add_product_to_cart(request.cr, request.uid,
				product_id=product_id,
				number=quantity,
				context=request.context)
			# bug in _ecommerce_add_product_to_cart means that if adding a new product to the cart, 
			# the quantity is always set to 1. Handle this by checking returned qty against specified
			# quantity and adjust it accordingly
			if new_quantity != quantity:
				request.registry['website']._ecommerce_add_product_to_cart(request.cr, request.uid,
				product_id=int(product_id),
				number=quantity - new_quantity,
				context=request.context)
		return 'true'
