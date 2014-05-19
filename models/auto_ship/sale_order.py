from openerp.osv import osv, fields
from openerp.tools.translate import _

EXISTING_AUTO_SHIP = 'Existing Auto Ship'
INVALID_PRODUCTS = 'Invalid Products'

class sale_order(osv.osv):

	_inherit = "sale.order"

	_columns = {
		"auto_ship_id": fields.many2one("ip_web_addons.auto_ship", "Auto Ship"),
		
		'draft_auto_ship': fields.boolean('To Create Auto Ship?', help="Indicates whether or not an Auto Ship should be created when this sale order is confirmed"),
		'draft_auto_ship_interval': fields.integer('Auto Ship Interval', help="The interval of the auto ship to be created"),
		'draft_auto_ship_end_date': fields.date('Auto Ship Date', help="The end date of the Auto to be created")
	}
	
	def action_button_confirm(self, cr, uid, ids, context=None):
		""" Override action_button_confirm to create auto_ship if necessary on SO confirmation """
		res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
		order = self.browse(cr, uid, ids[0], context=context)
		if order.draft_auto_ship and not order.auto_ship_id:
			self.create_auto_ship(cr, uid, order.id, order.draft_auto_ship_interval, order.draft_auto_ship_end_date, context=context)
			order.write({'draft_auto_ship': False, 'draft_auto_ship_interval': 0, 'draft_auto_ship_end_date': None})
		return res
	
	def button_create_auto_ship(self, cr, uid, ids, context=None):
		""" Form view button for creating an auto ship from a sales order """
		assert len(ids) == 1, 'Can only create an auto ship for one SO at a time'
		so = self.browse(cr, uid, ids[0], context=context)
		
		try:
			self.create_auto_ship(cr, uid, so.id, context=context)
		except ValueError as v:
			
			if v.message == EXISTING_AUTO_SHIP:
				raise osv.except_osv(_("Auto Ship Already Exists"), _("An Auto Ship already exists for this sale order. Look in the Auto Ship tab."))
			
			elif v.message == INVALID_PRODUCTS:
				raise osv.except_osv(_("Invalid Products"), _("Not all products in the sale order lines are marked as Auto Shippable"))
	
	def create_auto_ship(self, cr, uid, so_id, interval=0, end_date=None, context=None):
		""" Create an auto ship for a sale order """
		assert isinstance(so_id, (int, long)), _("so_id variable should be int or long")
		
		auto_ship_obj = self.pool['ip_web_addons.auto_ship']
		so = self.browse(cr, uid, so_id)

		# check no existing auto ship exists for this SO		
		if so.auto_ship_id:
			raise ValueError(EXISTING_AUTO_SHIP)
		
		# check all products in all sales order lines are auto shippable
		if not all([line.product_id.auto_ship for line in so.order_line]):
			raise ValueError(INVALID_PRODUCTS)
		
		auto_ship_vals = {
			'interval': interval,
			'end_date': end_date,
			'partner_id': so.partner_id.id,
		}
		
		# create auto ship and set auto_ship_id on SO
		auto_ship_id = auto_ship_obj.create(cr, uid, auto_ship_vals, context=context)
		self.write(cr, uid, so_id, {'auto_ship_id': auto_ship_id}, context=context)
		return auto_ship_id
