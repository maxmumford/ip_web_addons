from openerp.osv import osv, fields

class res_partner(osv.osv):

	_inherit = "res.partner"
	
	_columns = {
		"disease_ids": fields.many2many('ip.diseases', 'partner_diseases_rel', 'partner_id', 'disease_id', 'Diseases'),
	}
