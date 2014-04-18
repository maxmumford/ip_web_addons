from openerp.osv import osv, fields
from openerp.tools.translate import _

class sale_order(osv.osv):

	_inherit = "sale.order"

	_columns = {
		"auto_ship_id": fields.many2one("ip.auto_ship", "Auto Ship"),
	}
	
	def create_auto_ship(self, cr, uid, so_id, interval, end_date, context=None):
		""" Create an auto ship for a sale order """
		assert isinstance(so_id, (int, long)), _("so_id variable should be int or long")
		assert interval and end_date, _("interval and end_date variables are both required and must be truthy")
		
		auto_ship_obj = self.pool['ip.auto_ship']
		so = self.browse(cr, uid, so_id)
		
		auto_ship_vals = {
			'interval': interval,
			'end_date': end_date,
			'partner_id': so.partner_id.id,
		}
		
		# create auto ship and set auto_ship_id on SO
		auto_ship_id = auto_ship_obj.create(cr, uid, auto_ship_vals, context=context)
		self.write(cr, uid, so_id, {'auto_ship_id': auto_ship_id}, context=context)
		return auto_ship_id
