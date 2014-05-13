from datetime import datetime

from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.translate import _

from openerp.addons.ip_web_addons import jsend, tools

class Ecommerce(http.Controller):
	
	NO_ORDER = 'No Order'

	@jsend.jsend_error_catcher
	@http.route(['/shop/set_auto_ship/'], type='http', auth="public", methods=['POST'], website=True, multilang=True)
	def set_auto_ship(self, auto_ship, interval=0, end_date=None):
		"""
		Saves onto customers quotation the auto_ship setting and if 'true', also sets associated interval and end_date.
		"""
		# must have auto shippable order
		order = request.registry['website'].ecommerce_get_current_order(request.cr, request.uid, context=request.context)
		if not order:
			return jsend.jsend_fail({'order': 'Customer has no orders in progress'})
		if not self._can_auto_ship(order):
			return jsend.jsend_fail({'auto_ship': 'Not all products in the cart are marked as Auto Ship'})
		if not tools.isnumeric(interval):
			raise jsend.JsendTypeError('interval', 'Interval must be numeric')
		
		# set auto ship variables on sale order
		auto_ship = True if auto_ship == 'true' else False
		interval = int(interval)
		vals = {}
		
		if auto_ship:
			if not end_date:
				return jsend.jsend_fail({'end_date', 'End Date must have a value'})
			try:
				end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
			except ValueError:
				raise jsend.JsendValueError('end_date', 'End Date was not a valid date - it must be in format YYYY-MM-DD')
			
			vals['draft_auto_ship'] = auto_ship
			vals['draft_auto_ship_interval'] = interval
			vals['draft_auto_ship_end_date'] = end_date
		else:
			vals['draft_auto_ship'] = auto_ship
			vals['draft_auto_ship_interval'] = 0
			vals['draft_auto_ship_end_date'] = None
			
		order.write(vals)
		
	@jsend.jsend_error_catcher
	@http.route(['/shop/get_auto_ship/'], type='http', auth="public", website=True, multilang=True)
	def get_auto_ship(self):
		"""
		Returns the auto_ship bool, interval int and end_date string
		"""
		# get auto ship settings from the session
		order = request.registry['website'].ecommerce_get_current_order(request.cr, request.uid, context=request.context)
		if not order:
			return jsend.jsend_fail({'order': 'Customer has no current orders'})
		
		auto_ship = 'true' if order.draft_auto_ship else 'false'
		interval = order.draft_auto_ship_interval
		end_date = order.draft_auto_ship_end_date or 'null'
		return jsend.jsend_success({
									'auto_ship': auto_ship,
									'interval': interval,
									'end_date': end_date,
								})
	
	@jsend.jsend_error_catcher
	@http.route(['/shop/can_auto_ship/'], type='http', auth="public", website=True, multilang=True)
	def can_auto_ship(self):
		"""
		Returns data {'can_auto_ship': 'true'/'false'} 
		"""
		order = request.registry['website'].ecommerce_get_current_order(request.cr, request.uid, context=request.context)
		res = 'true' if self._can_auto_ship(order) else 'false'
		return jsend.jsend_success({'can_auto_ship': res})
	
	def _can_auto_ship(self, order):
		""" Returns True of all products in order lines are auto shippable """
		if not order:
			return True
		for line in order.order_line:
			if not line.product_id.auto_ship:
				return False
		return True
