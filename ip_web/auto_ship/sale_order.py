from openerp.osv import osv, fields

class sale_order(osv.osv):

	_inherit = 'sale.order'

	_columns = {
		'recurring': fields.boolean('Recurring', help="This is sales order an auto ship? I.e. should it be re-made every INTERVAL weeks?")
	}
