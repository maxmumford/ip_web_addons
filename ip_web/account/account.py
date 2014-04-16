# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.models import website
from openerp.tools.translate import _
 
class IpMyAccount(http.Controller):

    @http.route(['/account/'], type='http', auth="public", multilang=True, website=True)
    def account(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        user_obj = pool['res.users']
        invoices_obj = pool['account.invoice']
        sale_obj = pool['sale.order']
        delivery_obj = pool['stock.picking.out']
        incoming_obj = pool['stock.picking.in']
        payment_obj = pool['payment.transaction']
        
        # get customer from logged in user
        user = user_obj.browse(cr, 1, uid)
        partner_id = user.partner_id.id
        
        # if user is public user, redirect to login page
        public_user_id = pool['website'].get_public_user(cr, 1)
        if user.id == public_user_id:
            return request.redirect("/web/login?redirect=/account/") 
        
        # get sales orders
        sale_order_ids = sale_obj.search(cr, uid, [
                ('partner_id.commercial_partner_id', '=', partner_id),
                ('state', 'not in', ['draft', 'cancelled', 'invoice_except', 'shipping_except'])
            ], context=context)
        sale_orders = sale_obj.browse(cr, uid, sale_order_ids, context=context)

        # get invoices
        invoice_ids = invoices_obj.search(cr, uid, [
                ('partner_id.commercial_partner_id', '=', partner_id), 
                ('type', '=', 'out_invoice'), 
                ('state', 'in', ['open', 'paid'])
            ], context=context)
        invoices = invoices_obj.browse(cr, uid, invoice_ids, context=context)

        # get delivery orders
        delivery_ids = delivery_obj.search(cr, uid, [
                ('type', '=', 'out'), 
                ('sale_id', 'in', sale_order_ids), 
                ('state', 'in', ['confirmed', 'assigned', 'done'])
            ], context=context)
        deliveries = delivery_obj.browse(cr, uid, delivery_ids, context=context)

        # get auto ships
        auto_ship_ids = sale_obj.search(cr, uid, [
                ('partner_id.commercial_partner_id', '=', partner_id),
                #('recurring', '=', True)
            ], context=context)
        auto_ships = sale_obj.browse(cr, uid, auto_ship_ids)
        
        # get transactions
        transaction_ids = payment_obj.search(cr, uid, [('partner_id', '=', partner_id)])
        transactions = payment_obj.browse(cr, uid, transaction_ids, context=context)
        
        # get returns
        return_ids = incoming_obj.search(cr, uid, [
                ('partner_id', '=', partner_id), 
                ('type', '=', 'in'),
                ('state', '!=', 'draft'),
            ], context=context) 
        returns = incoming_obj.browse(cr, uid, return_ids, context=context)
        
        vals = {
            'invoices': invoices,
            'sale_orders': sale_orders,
            'deliveries': deliveries,
            'auto_ships': auto_ships,
            'transactions': transactions,
            'returns': returns,
         }

        return request.website.render("ip_web.account", vals)
