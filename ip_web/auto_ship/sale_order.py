from openerp.osv import osv, fields
from datetime import datetime, date, timedelta

class sale_order(osv.osv):

	_inherit = "sale.order"

	_next_auto_ship_date_store_triggers = {
		'sale.order': (lambda self, cr, uid, ids, context=None: ids,
			['interval', 'end_date'], 10)
	}

	def _next_auto_ship_date(self, cr, uid, ids, field_name=None, arg=None, context=None):
		""" Calculate next_auto_ship_date based on weekly interval and end_date """
		res = dict.fromkeys(ids, None)

		for so in self.browse(cr, uid, ids, context=context):
			
			if so.auto_ship:
				# check for previous sales order and use their next_auto_ship_date as base date 
				if so.previous_so_id:
					base_date = datetime.strptime(so.previous_so_id.next_auto_ship_date, '%Y-%m-%d').date()
				else: 
					base_date = datetime.strptime(so.date_order, '%Y-%m-%d').date()

			# add INTERVAL weeks to base_date
			res[so.id] = self._calc_next_auto_ship_date(base_date, so.interval)

		return res
	
	def _calc_next_auto_ship_date(self, base_date, interval, return_type = date):
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

	def _constrain_auto_ship_fields(self, cr, uid, ids, context=None):
		""" Constraint: If auto_ship is true, require interval and end_date to be truthy """
		res = dict.fromkeys(ids, False)
		for so in self.browse(cr, uid, ids, context=context):
			if so.auto_ship:
				return (so.interval and so.end_date)
			else:
				res[so.id] = True
		return res

	def on_change_auto_ship_fields(self, cr, uid, so_id, interval, date_order, context=None):
		""" Calculate next_auto_ship_date when changing interval or end_date """
		if not interval or not date_order:
			return {}
		else:
			return {
				'value': {
						'next_auto_ship_date': self._calc_next_auto_ship_date(date_order, interval, return_type = str)
					}
				}

	_columns = {
		"auto_ship": fields.boolean("Auto Ship", help="This is sales order an auto ship? I.e. should it be re-made every INTERVAL weeks?"),
		"interval": fields.integer("Interval In Weeks", help="If auto_ship is true, this sales order will be resent every INTERVAL weeks"),
		"end_date": fields.date("Auto Ship End Date", help="The date that the Auto Ship expires"),
		"previous_so_id": fields.many2one("sale.order", "Previous Auto Ship", help="The previous Auto Ship sale order", readonly=True),
		"processed": fields.boolean("Processed?", help="Has this Auto Ship been processed yet?", readonly=True),
		"next_auto_ship_date": fields.function(
									_next_auto_ship_date,
									method = True,
									string = 'Next Auto Shipment Date',
									type = 'date',
									store = _next_auto_ship_date_store_triggers),
	}

	_constraints = [(_constrain_auto_ship_fields, 'Interval and End Date are required fields if Auto Ship is True', ['auto_ship', 'interval', 'end_date'])]

	def do_all_auto_ships(self, cr, uid):
		""" Called by a cron to find all auto ships that should be processed and call process_auto_ship on them """
		# get ids for auto ships whose next_auto_ship_date is in the past or today, end_date is in the future and processed is false
		today = date.today().strftime('%Y-%m-%d')
		#today = date(2014, 4, 24) # used to debug
		
		auto_ship_ids = self.search(cr, uid, [
			('auto_ship', '=', True),
			('next_auto_ship_date', '<=', today),
			('processed', '=', False),
		])

		# for each one call process_auto_ship
		for auto_ship_id in auto_ship_ids:
			self.process_auto_ship(cr, uid, auto_ship_id)
			
		return True

	def process_auto_ship(self, cr, uid, old_so_id, default={}, context=None):
		""" 
		Duplicates the SO, marks the old SO as processed and sets the previous_so_id to the new SO.
		Then checks if the new SO next_auto_ship_date > end_date, and if yes, ends the auto ship.
		"""
		reset_auto_ship_fields = {
			'auto_ship': False,
			'interval': None, 
			'end_date': None, 
			'previous_so_id': None, 
			'next_auto_ship_date': None,
		}
		old_so = self.browse(cr, uid, old_so_id, context=context)
		
		# If end date is before next auto ship date, reset auto ship fields and return
		if old_so.end_date < old_so.next_auto_ship_date:
			self.write(cr, uid, old_so, reset_auto_ship_fields) 
		
		# duplicate old_
		default['next_auto_ship_date'] = None
		new_so_id = self.copy(cr, uid, old_so_id, default=default, context=context)
		new_so = self.browse(cr, uid, new_so_id, context=context)

		# update auto ship fields on old SO
		if old_so.auto_ship:
			old_so_vals = {
				'previous_so_id': new_so_id,
				'processed': True,
			}
			self.write(cr, uid, old_so_id, old_so_vals, context=context)

		# if new SO next_auto_ship_date > end_date, stop auto ship
		if new_so.auto_ship and new_so.next_auto_ship_date > new_so.end_date:
			self.write(cr, uid, new_so, reset_auto_ship_fields)
			
		# confirm new SO
		self.action_button_confirm(cr, uid, [new_so_id], context=context)

		return new_so_id
