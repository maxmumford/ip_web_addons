# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.models import website

class WebsiteSaleMyAccount(http.Controller):

    @http.route(['/account/'], type='http', auth="user", multilang=True, website=True)
    def account(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        invoices_obj = request.registry.get('account.invoice')
        sale_obj = request.registry.get('sale.order')
        delivery_obj = request.registry.get('stock.picking.out')

        # TODO: handle user company too?
        customer_invoice_ids = invoices_obj.search(cr, uid, [
                ('user_id', '=', uid), 
                ('type', '=', 'out_invoice'), 
                ('state', 'in', ['open', 'paid'])
            ], context=context)
        customer_invoices = invoices_obj.browse(cr, uid, customer_invoice_ids, context=context)
        
        customer_sale_order_ids = sale_obj.search(cr, uid, [
                ('user_id', '=', uid), 
                ('state', 'not in', ['done', 'draft'])
            ], context=context)
        customer_sale_orders = sale_obj.browse(cr, uid, customer_sale_order_ids, context=context)

        customer_delivery_ids = delivery_obj.search(cr, uid, [
                ('type', '=', 'out'), 
                ('sale_id', 'in', customer_sale_order_ids), 
            ], context=context)
        customer_deliveries = delivery_obj.browse(cr, uid, customer_delivery_ids, context=context)
        
        vals = {
            'invoices': customer_invoices,
            'sale_orders': customer_sale_orders,
            'deliveries': customer_deliveries,
         }

        return request.website.render("website_sale_my_account.account", vals)

    @http.route(['/account/sale-order/<model("sale.order"):sale_order>/'], type='http', auth="user", multilang=True, website=True)
    def sale_order(self, sale_order, **post):
        if sale_order.user_id != request.uid:
            request.redirect("/account/")
        return request.website.render("website_sale_my_account.sale_order", {'sale_order': sale_order})

    @http.route(['/account/invoice/<model("account.invoice"):invoice>/'], type='http', auth="user", multilang=True, website=True)
    def invoice(self, invoice, **post):
        if invoice.user_id != request.uid:
            request.redirect("/account/")
        return request.website.render("website_sale_my_account.invoice", {'invoice': invoice})
