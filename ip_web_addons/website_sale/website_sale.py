import json

from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.translate import _
from datetime import datetime

class Ecommerce(http.Controller):
	
	NO_ORDER = 'No Order'

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
		
	@http.route(['/shop/get_cart_product_quantities/'], type='http', auth="public", methods=['POST', 'GET'], website=True, multilang=True)
	def get_cart_product_quantities(self):
		"""
		Get the IDS and quantities of products in the cart
		@return json object where keys are ids and values are quantities 
		"""
		order = request.registry['website'].ecommerce_get_current_order(request.cr, request.uid, context=request.context)
		if not order:
			return 'false: no order'
		
		product_quantites = dict([(line.product_id.id, 0) for line in order.order_line])
		for line in order.order_line:
			product_quantites[line.product_id.id] += line.product_uos_qty
		
		return json.dumps(product_quantites)

	@http.route(['/shop/set_auto_ship/'], type='http', auth="public", methods=['POST'], website=True, multilang=True)
	def set_auto_ship(self, auto_ship, interval=0, end_date=None):
		"""
		Saves onto customers quotation the auto_ship setting and if 'true', also sets associated interval and end_date.
		Returns one of the following strings: 'false: no order', 'false: cannot auto ship', 'false: error while writing', 'true'
		"""
		# must have auto shippable order
		order = request.registry['website'].ecommerce_get_current_order(request.cr, request.uid, context=request.context)
		if not order:
			return 'false: no order'
		elif not self._can_auto_ship(order):
			return 'false: cannot auto ship'
		
		# set auto ship variables on sale order
		auto_ship = True if auto_ship == 'true' else False
		interval = int(interval)
		vals = {}
		
		if auto_ship:
			vals['draft_auto_ship'] = auto_ship
			vals['draft_auto_ship_interval'] = interval
			vals['draft_auto_ship_end_date'] = datetime.strptime(end_date, '%Y-%m-%d').date()
		else:
			vals['draft_auto_ship'] = auto_ship
			vals['draft_auto_ship_interval'] = 0
			vals['draft_auto_ship_end_date'] = None
		
		return 'true' if order.write(vals) else 'false: error while writing'
	
	@http.route(['/shop/get_auto_ship/'], type='http', auth="public", methods=['POST'], website=True, multilang=True)
	def get_auto_ship(self):
		"""
		Returns a json object containing auto_ship, interval and end_date for the current order:
		 
		{
			"auto_ship": "boolean",
			"interval": "int",
			"end_date": "string: %Y-%m-%d"
		}
		
		or a string containing an error message. Usage:
		
		$.ajax({url: '/shop/get_auto_ship', type: 'post', dataType: 'json', 
				success: function(response){console.log(response);}});
		"""
		# get auto ship settings from the session
		order = request.registry['website'].ecommerce_get_current_order(request.cr, request.uid, context=request.context)
		if not order:
			return 'false: no order'
		
		auto_ship = 'true' if order.draft_auto_ship else 'false'
		interval = order.draft_auto_ship_interval
		end_date = order.draft_auto_ship_end_date or 'null'
		
		return """{
			"auto_ship": "%s",
			"interval": "%s",
			"end_date": "%s"
		}""" % (auto_ship, interval, end_date)
		
	@http.route(['/shop/can_auto_ship/'], type='http', auth="public", methods=['POST', 'GET'], website=True, multilang=True)
	def can_auto_ship(self):
		"""
		Returns 'true' if all products in the cart are auto shippable, otherwise returns 'false' 
		"""
		order = request.registry['website'].ecommerce_get_current_order(request.cr, request.uid, context=request.context)
		try:
			return 'true' if self._can_auto_ship(order) else 'false'
		except ValueError as e:
			if e.message == self.NO_ORDER:
				return 'false: No Order'
			raise
	
	def _can_auto_ship(self, order):
		""" Returns True of all products in order lines are auto shippable """
		if not order:
			raise ValueError(self.NO_ORDER)
		for line in order.order_line:
			if not line.product_id.auto_ship:
				return False
		return True
