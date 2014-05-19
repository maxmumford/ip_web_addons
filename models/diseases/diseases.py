from openerp.osv import osv, fields

class diseases(osv.osv):

	_name = "ip_web_addons.disease"

	_columns = {
		"name": fields.char("Name", required=True),
	}
