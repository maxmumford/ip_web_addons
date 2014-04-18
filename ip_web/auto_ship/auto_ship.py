import math

from openerp.osv import osv, fields
from datetime import datetime, date, timedelta
from openerp.tools.translate import _

class auto_ship(osv.osv):

	_name = "ip.auto_ship"

	# functional field triggers
	def next_ship_sale_order_trigger(self, cr, uid, ids, context=None):
		r = [so.auto_ship_id.id for so in self.browse(cr, uid, ids, context=context)]
		return r
	
	_next_auto_ship_date_store_triggers = {
		'ip.auto_ship': (lambda self, cr, uid, ids, context=None: ids, ['interval', 'end_date'], 5),
		'sale.order': (next_ship_sale_order_trigger, ['auto_ship_id'], 5),
	}

	_expired_store_triggers = {
		'ip.auto_ship': (lambda self, cr, uid, ids, context=None: ids,
			['interval', 'end_date', 'next_auto_ship_date'], 10)
	}

	# Functional field functions
	def _func_next_auto_ship_date(self, cr, uid, ids, field_name=None, arg=None, context=None):
		""" Calculate next_auto_ship_date based on last auto ship date, weekly interval and end_date """
		res = dict.fromkeys(ids, None)

		for auto_ship in self.browse(cr, uid, ids, context=context):
			
			if not auto_ship.expired:
				# Get latest sales order and use that as base date
				base_date = None
				if auto_ship.latest_sale_order:
					base_date = auto_ship.latest_sale_order.date_order

				# add INTERVAL weeks to base_date
				res[auto_ship.id] = self._calculate_next_auto_ship_date(base_date, auto_ship.interval)

		return res

	def _func_latest_sale_order(self, cr, uid, ids, field_name=None, arg=None, context=None):
		""" Returns the ID of the latest sales order for an auto_ship """
		res = dict.fromkeys(ids, None)
		for auto_ship in self.browse(cr, uid, ids, context=context):
			if auto_ship.sale_order_ids:
				res[auto_ship.id] = self.pool['sale.order'].search(cr, uid, [('id', 'in', [so.id for so in auto_ship.sale_order_ids])], 
																	limit=1, order='date_order DESC')[0]
		return res

	def _func_expired(self, cr, uid, ids, field_name=None, arg=None, context=None):
		""" Check if the auto ship has expired by comparing next auto ship date with end date """
		res = dict.fromkeys(ids, None)

		for so in self.browse(cr, uid, ids, context=context):
			# Check if next auto ship date is after end date 
			res[so.id] = so.next_auto_ship_date > so.end_date

		return res
	
	def _func_number_remaining(self, cr, uid, ids, field_name=None, arg=None, context=None):
		""" Calculate the number of orders remaining between now and the end_date """
		res = dict.fromkeys(ids, None)
		for auto_ship in self.browse(cr, uid, ids, context=context):
			res[auto_ship.id] = self._calculate_number_remaining(auto_ship.interval, auto_ship.end_date)
		return res

	# On change functions
	def on_change_auto_ship_fields(self, cr, uid, ids, interval, end_date, context=None):
		""" Calculate next_auto_ship_date when changing interval or end_date """
		if not interval or not end_date:
			return {
				'value': {
					'next_auto_ship_date': None,
					'number_remaining': None,
				}
			}
		elif ids:
			assert len(ids) == 1, "On change should not be called with multiple ids"
			
			auto_ship = self.browse(cr, uid, ids[0])
			next_auto_ship_date = self._calculate_next_auto_ship_date(auto_ship.latest_sale_order.date_order, interval, return_type = str)
			number_remaining = self._calculate_number_remaining(interval, end_date)

			return {
				'value': {
					'next_auto_ship_date': next_auto_ship_date,
					'number_remaining': number_remaining,
				}
			}
		else:
			return {}

	_columns = {
		"name": fields.char("Name", required=True, readonly=True),
		"partner_id": fields.many2one("res.partner", "Customer", required=True),
		"interval": fields.integer("Interval In Weeks", help="If auto_ship is true, this sales order will be resent every INTERVAL weeks"),
		"end_date": fields.date("Auto Ship End Date", help="The date that the Auto Ship expires"),
		"sale_order_ids": fields.one2many("sale.order", "auto_ship_id", "Sale Orders", help="Sale Orders created by this Auto Ship", readonly=True),
		"latest_sale_order": fields.function(
									_func_latest_sale_order,
									method = True,
									string = "Latest Sale Order",
									type = "many2one",
									obj = 'sale.order',
									help = "The most recent sales order created by this Auto Ship",
		),
		"next_auto_ship_date": fields.function(
									_func_next_auto_ship_date,
									method = True,
									string = 'Next Auto Shipment Date',
									type = 'date',
									store = _next_auto_ship_date_store_triggers,
									help = "The date of the next planned Auto Shipment"
		),
		"expired": fields.function(_func_expired,
									method = True,
									string = 'Expired?',
									type = 'boolean',
									store = _expired_store_triggers,
									help = "Has this Auto Ship expired? This field is based on whether or not the Next Auto Shipment Date is after the End Date field."
		),
		"number_remaining": fields.function(
									_func_number_remaining,
									method = True,
									string = "Number Remaining",
									type = "char",
									help = "The number of orders remaining between now and the end date",
		),
	}
	
	_defaults = {
		'name': lambda obj, cr, uid, context: obj.pool['ir.sequence'].get(cr, uid, 'ip.auto_ship'),
		'sale_order_ids': None,
		'latest_sale_order': None,
		'next_auto_ship_date': None,
		'expired': False,
	}

	# OE API
	def write(self, cr, uid, ids, vals, context=None):
		""" 
		When updating [functional?] date column to None or False, 
		the ORM leaves the old date instead, so force it manually 
		"""
		super(auto_ship, self).write(cr, uid, ids, vals, context=context)
		if 'next_auto_ship_date' in vals and (vals['next_auto_ship_date'] is None or vals['next_auto_ship_date'] is False):
			cr.execute('UPDATE ip_auto_ship SET next_auto_ship_date = null where ids in %s', ids)
			
	def copy(self, cr, uid, id, default={}, context=None):
		""" Get new 'name' value from sequence """
		default['name'] = self.pool['ir.sequence'].get(cr, uid, 'ip.auto_ship')
		default['sale_order_ids'] = None
		default['latest_sale_order'] = None
		default['next_auto_ship_date'] = None
		default['expired'] = False
		return super(auto_ship, self).copy(cr, uid, id, default=default, context=context)

	# Public methods
	def do_all_auto_ships(self, cr, uid):
		""" Called by a cron to find all auto ships that should be processed and call process_auto_ship on them """
		# get ids for auto ships whose next_auto_ship_date is in the past or today, end_date is in the future 
		today = date.today().strftime('%Y-%m-%d')
		#today = date(2015, 5, 30) # used to debug
		
		auto_ship_ids = self.search(cr, uid, [
			('next_auto_ship_date', '<=', today),
			('expired', '=', False),
		])

		# for each one call process_auto_ship
		for auto_ship_id in auto_ship_ids:
			self.process_auto_ship(cr, uid, auto_ship_id)
			
		return True

	def process_auto_ship(self, cr, uid, auto_ship_id, context=None):
		""" 
		Creates a new sales order based on the most recent one
		"""
		# Check status of auto ship
		auto_ship = self.browse(cr, uid, auto_ship_id, context=context)
		if auto_ship.expired:
			return False

		# Duplicate latest sale order and confirm it
		sale_obj = self.pool['sale.order']
		new_so_id = sale_obj.copy(cr, uid, auto_ship.latest_sale_order.id, context=context)
		sale_obj.action_button_confirm(cr, uid, [new_so_id], context=context)

		return new_so_id
	
	# Private methods
	def _calculate_next_auto_ship_date(self, base_date, interval, return_type = date):
		""" Calculates the next auto ship date based on base_date and interval """
		assert return_type in [date, str], 'Return type must be date or str'

		# skip if interval or base_date not set
		if not base_date or not interval:
			return None
		
		# parse string date
		if(isinstance(base_date, (str, unicode))):
			base_date = datetime.strptime(base_date, '%Y-%m-%d').date()
		
		# do date calculation
		next_date = base_date + timedelta(weeks=interval)
		
		# return return_type
		if return_type == date:
			return next_date
		else:
			return next_date.strftime('%Y-%m-%d')
		
	def _calculate_number_remaining(self, interval, end_date):
		""" Calculates the number of orders between now and the auto ship's end date """
		assert isinstance(interval, (int, float)), "Interval must be an int or float"
		assert isinstance(end_date, (bool, date, str, unicode)), "end_date must be str, unicode or date"
		
		if not interval or not end_date:
			return 0
		
		if isinstance(end_date, (str, unicode)):
			end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

		difference = date.today() - end_date
		return math.trunc(abs(difference.days) / (interval * 7.0))
