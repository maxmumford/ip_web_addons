# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.models import website
from openerp.tools.translate import _
 
class IpPortalReports(http.Controller):
    """ 
    Generate reports for ids and return the PDF for user to download
    @param string model: The model for which to create the report
    @param list ids: The ids of the records for which to create the report
    @param string report_name: The internal technical name of the report to be used
    """
    @http.route(['/account/report/<model>/<int:rec_id>/<report_name>'], type="http", auto='user', multilang=True, website=True)
    def report(self, model, rec_id, report_name, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        assert isinstance(rec_id, (long, int)), _('ID must be float or int')
        assert pool.get(model), _('Could not find model "%s"') % model
        assert pool[model].search(cr, SUPERUSER_ID, [('id', '=', rec_id)])

        report_obj = pool['ir.actions.report.xml']
        report_data = {'report_type': 'pdf', 'model': model}

        report_contents, report_extension = report_obj.render_report(cr, SUPERUSER_ID, [rec_id], report_name, report_data)
        return request.make_response(report_contents, 
            headers=[('Content-Type', 'application/pdf'), ('Content-Disposition', 'inline; filename=%s.pdf' % 'download')])
