from openerp.osv import osv, fields

class diseases(osv.osv):

	_name = "ip.diseases"

	_columns = {
		"name": fields.char("Name", required=True),
	}
