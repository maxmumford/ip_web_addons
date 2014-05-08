from openerp.osv import osv, fields

class res_partner(osv.osv):

	_inherit = "res.partner"
	
	_columns = {
		"gender": fields.selection((('f','Female'), ('m','Male')), 'Gender', help="The gender of the partner"),
	}
