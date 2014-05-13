from openerp.osv import osv, fields

class website(osv.osv):
    _inherit = "website"
    
    def render(self, cr, uid, ids, template, values=None, status_code=None, context=None):
        if template == 'website_sale.product' and 'product' in values:
            values['product'] = self.pool[values['product']._name].browse(cr, 1, values['product'].id)
        return super(website, self).render(cr, uid, ids, template, values=values, status_code=status_code, context=context)
