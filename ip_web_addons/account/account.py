# -*- coding: utf-8 -*-
from functools import wraps
from .. import jsend, tools

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.models import website
from openerp.tools.translate import _

class PartnerAddress(object):
    """ Object representing a partner address for use in qweb """
    def __init__(self, partner):
        super(PartnerAddress, self).__init__()

        self.id = partner.id
        self.name = partner.name
        self.street = partner.street
        self.street2 = partner.street2
        self.city = partner.city
        self.state = partner.state_id.name
        self.state_id = partner.state_id.id
        self.zip = partner.zip
        self.country = partner.country_id.name
        self.country_id = partner.country_id.id

class IpMyAccount(http.Controller):

    @tools.require_login
    @http.route(['/account/', '/account/<page>'], type='http', auth="public", multilang=True, website=True)
    def account(self, page=None, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        user_obj = pool['res.users']
        invoices_obj = pool['account.invoice']
        sale_obj = pool['sale.order']
        auto_ship_obj = pool['ip.auto_ship']
        delivery_obj = pool['stock.picking.out']
        incoming_obj = pool['stock.picking.in']
        payment_obj = pool['payment.transaction']

        # get customer from logged in user
        user = user_obj.browse(cr, SUPERUSER_ID, uid)
        partner_id = user.partner_id.id
        
        # get sales orders
        sale_order_ids = sale_obj.search(cr, SUPERUSER_ID, [
                ('partner_id.commercial_partner_id', '=', partner_id),
                ('state', 'not in', ['draft', 'cancelled', 'invoice_except', 'shipping_except'])
            ], context=context)
        sale_orders = sale_obj.browse(cr, uid, sale_order_ids, context=context)

        # get invoices
        invoice_ids = invoices_obj.search(cr, SUPERUSER_ID, [
                ('partner_id.commercial_partner_id', '=', partner_id), 
                ('type', '=', 'out_invoice'), 
                ('state', 'in', ['open', 'paid'])
            ], context=context)
        invoices = invoices_obj.browse(cr, SUPERUSER_ID, invoice_ids, context=context)

        # get delivery orders
        delivery_ids = delivery_obj.search(cr, SUPERUSER_ID, [
                ('type', '=', 'out'), 
                ('sale_id', 'in', sale_order_ids), 
                ('state', 'in', ['confirmed', 'assigned', 'done'])
            ], context=context)
        deliveries = delivery_obj.browse(cr, SUPERUSER_ID, delivery_ids, context=context)

        # get auto ships
        auto_ship_ids = auto_ship_obj.search(cr, SUPERUSER_ID, [
                ('partner_id', '=', partner_id),
            ], context=context)
        auto_ships = auto_ship_obj.browse(cr, SUPERUSER_ID, auto_ship_ids)
        
        # get transactions
        transaction_ids = payment_obj.search(cr, SUPERUSER_ID, [('partner_id', '=', partner_id)])
        transactions = payment_obj.browse(cr, SUPERUSER_ID, transaction_ids, context=context)
        
        # get returns
        return_ids = incoming_obj.search(cr, SUPERUSER_ID, [
                ('partner_id', '=', partner_id), 
                ('type', '=', 'in'),
                ('state', '!=', 'draft'),
            ], context=context) 
        returns = incoming_obj.browse(cr, SUPERUSER_ID, return_ids, context=context)
        
        vals = {
            'page': page,
            'invoices': invoices,
            'sale_orders': sale_orders,
            'deliveries': deliveries,
            'auto_ships': auto_ships,
            'transactions': transactions,
            'returns': returns,
         }

        return request.website.render("ip_web_addons.account", vals)
    
    def get_addresses(self):
        """
        Returns the below dict containing all cities, all countries, and the requestor's billing
        and shipping addresses. address_shipping can be an empty list. address_billing will always
        have at least one record. 
        
        {
            cities: [browse_record, browse_record, ... ],
            countries: [browse_record, browse_record, ... ],
            address_billing: PartnerAddress,
            address_shipping: [PartnerAddress, PartnerAddress, .. ]
        }
        """
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        user_obj = pool['res.users']
        partner_obj = pool['res.partner']
        country_obj = pool['res.country']
        state_obj = pool['res.country.state']

        # get customer from logged in user
        user = user_obj.browse(cr, SUPERUSER_ID, uid, context=context)
        partner = partner_obj.browse(cr, SUPERUSER_ID, user.partner_id.id, context=context)
        
        # get addresses
        addresses_shipping = []
        parent = partner
        children = []
        
        if partner.child_ids:
            # partner is a parent so use it as billing and children as shipping
            parent = partner
            children += parent.child_ids
        elif partner.parent_id:
            # partner is child so use it's parent as billing and siblings as children
            parent = partner.parent_id
            children_ids = partner_obj.search(cr, SUPERUSER_ID, [('parent_id', '=', partner.parent_id.id)], context=context)
            children += [child for child in partner_obj.browse(cr, SUPERUSER_ID, children_ids, context=context)]
        
        address_billing = PartnerAddress(partner)
        map(lambda child: addresses_shipping.append(PartnerAddress(child)), children)
        
        # get countries and states
        country_ids = country_obj.search(cr, SUPERUSER_ID, [], context=context)
        states_ids = state_obj.search(cr, SUPERUSER_ID, [], context=context)
        
        countries = country_obj.browse(cr, SUPERUSER_ID, country_ids, context)
        states = state_obj.browse(cr, SUPERUSER_ID, states_ids, context)

        return {
            'countries': countries,
            'states': states,
            'address_billing': address_billing,
            'addresses_shipping': addresses_shipping,
        }
    
    @tools.require_login
    @http.route(['/account/address'], type='http', auth="public", multilang=True, website=True)
    def address(self):
        """
        Allows the logged in user to view their invoice address and shipping address[es].
        The invoice address is either the user's partner itself, or their parent if it exists.
        The shipping addresses can be that of the partner, and any of the partners who share 
        the same parent_id. 
        """
        vals = self.get_addresses()
        return request.website.render("ip_web_addons.address", vals)
    
    @tools.require_login
    @http.route(['/account/address/edit'], type='http', auth="public", multilang=True, website=True)
    def address_edit(self):
        """
        Allows the logged in user to edit their invoice address and shipping address(es).
        The invoice address is either the user's partner itself, or their parent if it exists.
        The shipping addresses can be that of the partner, and any of the partners who share 
        the same parent_id. 
        """
        vals = self.get_addresses()
        return request.website.render("ip_web_addons.address_edit", vals)
    
    @tools.require_login_jsend
    @jsend.jsend_error_catcher
    @http.route(['/account/address/update'], type='http', methods=['POST'], auth="public", multilang=True, website=True)
    def update_address(self, name, street, street2, city, zip, state_id, country_id, id):
        """ JSON route to update the address fields on a partner """
        if not tools.isnumeric(id):
            return jsend.jsend_fail({'id': 'Partner ID must be a number'})
        else:
            id = int(id)
            
        if not name:
            return jsend.jsend_fail({'name': 'Name is a required field'})    
        if not street:
            return jsend.jsend_fail({'street': 'Street is a required field'})    
        if not city:
            return jsend.jsend_fail({'city': 'City is a required field'})
        if not country_id:
            return jsend.jsend_fail({'country_id': 'Country is a required field'})
        
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        partner_obj = pool['res.partner']
        partner_id = id
        # TODO: make sure user has permission to update partner object
        partner_exists = bool(partner_obj.search(cr, SUPERUSER_ID, [('id', '=', partner_id)], context=context))
        
        if not partner_exists:
            return jsend.jsend_fail({'partner_id', 'That partner does not exist'})
        
        vals = {
            'name': name,
            'street': street,
            'street2': street2,
            'city': city,
            'zip': zip,
            'state_id': state_id,
            'country_id': country_id,
        }
        partner_obj.write(cr, SUPERUSER_ID, [partner_id], vals)
    
    @tools.require_login_jsend
    @jsend.jsend_error_catcher
    @http.route(['/account/auto-ship/update/<int:auto_ship_id>'], type='http', auth="public", multilang=True, website=True)
    def update_auto_ship(self, auto_ship_id, interval, end_date, **post):
        """ Update an auto ship's interval and end date """
        if not isinstance(auto_ship_id, (int, float)):
            raise jsend.JsendTypeError("auto_ship_id", "Auto ship ID should be a number")
        if not auto_ship_id:
            raise jsend.JsendValueError("auto_ship_id", "Auto ship ID must be greater than 0")
        
        if not tools.isnumeric(interval):
            raise jsend.JsendTypeError("interval", "Interval should be a number")
        if not interval:
            raise jsend.JsendValueError("interval", "Interval should be greater than 0") 
         
        if not isinstance(end_date, (str, unicode)):
            raise jsend.JsendTypeError("end_date", "End Date was invalid")
        if not end_date:
            raise jsend.JsendValueError("end_date", "End Date is required")  
        
        cr, uid, pool = request.cr, request.uid, request.registry
        # TODO: do we need to check permission?
        pool['ip.auto_ship'].write(cr, uid, auto_ship_id, {'interval': interval, 'end_date': end_date})
    
    @tools.require_login_jsend
    @jsend.jsend_error_catcher
    @http.route(['/account/auto-ship/delete/auto_ship_id'], type='http', auth="public", multilang=True, website=True)
    def delete_auto_ship(self, auto_ship_id, **post):
        """ delete an auto ship """
        if not tools.isnumeric(auto_ship_id):
            raise jsend.JsendTypeError("auto_ship_id", "Auto ship ID should be a number")
        if not auto_ship_id:
            raise jsend.JsendValueError("auto_ship_id", "Auto ship ID should be greater than 0")
        
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        # TODO: do we need to check permission?
        pool['ip.auto_ship'].unlink(cr, uid, auto_ship_id, context=context)
        
    @tools.require_login_jsend
    @jsend.jsend_error_catcher
    @http.route(['/account/number-remaining/<interval>/<end_date>'], type='http', auth="public", multilang=True, website=True)
    def number_remaining(self, interval, end_date, **post):
        """ Return the number of auto shipments remaining based on end_date and interval """
        if not tools.isnumeric(interval):
            raise jsend.JsendTypeError("interval", "Interval should be a number")
        if not interval:
            raise jsend.JsendValueError("interval", "Interval should be greater than 0")  
        if not isinstance(end_date, (str, unicode)):
            raise jsend.JsendTypeError("end_date", "End Date was invalid")
        if not end_date:
            raise jsend.JsendValueError("end_date", "End Date is required")  
        try:
            nr = str(request.registry['ip.auto_ship']._calculate_number_remaining(float(interval), end_date))
            return jsend.jsend_success({'number_remaining': nr})
        except ValueError as e:
            raise jsend.JsendValueError("end_date", "End Date must be a valid date in YYYY-MM-DD format")
