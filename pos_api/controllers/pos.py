# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
import json
from odoo import fields
from .login import UserLogin

_logger = logging.getLogger(__name__)


class POSapis(http.Controller):

    # Check the access rights
    def userLogin(self, auth, **kwargs):
        username = auth['username']
        password = auth['password']
        db = auth['db']

        uid = request.session.authenticate(db, username, password)
        if uid:
            jsondata = json.dumps(uid)

            return jsondata
        else:
            return False

    # pos list
    @http.route('/api/pos/list', type="json", auth="public", methods=['POST'], csrf=False, cors='*')
    def get_all_pos(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            pos_list = request.env['pos.config'].search([])
            pos_info = []
            for pos in pos_list:
                session = pos.session_ids.filtered(lambda r: r.user_id.id == int(uid) and \
                                                                    not r.state == 'closed' and \
                                                                    not r.rescue)

                pos_details = {
                    'id': pos.id,
                    'status': pos.active,
                    'name': pos.name,
                    'current_session_id': session and session[0].id or False,
                    'pos_session_state': pos.pos_session_state,
                    'pos_session_username': pos.pos_session_username

                }
                pos_info.append(pos_details)

            jsondata = {
                "statusCode": 200,
                "message": "POS list",
                "page": {
                    "totalCount": len(pos_list),
                    "limit": ""
                },
                "data": pos_info
            }
            return jsondata
        else:
            return "User Access Failed"

    # create new pos session
    @http.route('/api/pos/session', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def create_new_pos_session(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:

            session_list = request.env['pos.session'].search([('user_id', '=', int(uid)), ('state', '!=', 'closed'), ('rescue', '=', False)], limit=1)
            session_info = []
            if session_list:
                for session in session_list:
                    if session.state != 'opened':
                        session.sudo().action_pos_session_open()
                    session_details = {
                        'id': session.id
                    }
                    session_info.append(session_details)

            else:
                data = {
                    'user_id': int(uid),
                    'config_id': int(request.jsonrequest['data'].get('config_id'))
                }
                session = session_list.sudo().create(data)
                session.sudo().action_pos_session_open()
                session_info.append({
                        'id': session.id
                    })
            jsondata = {
                "statusCode": 200,
                "message": "New session started.",
                "data": session_info
            }
            return jsondata
        else:
            return "User Access Failed"

    # create new pos order
    @http.route('/api/pos/order', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def create_new_pos_order(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            PosOrder = request.env['pos.order']
            order_lines = []
            for line in request.jsonrequest['data'].get('order_line'):
                if 'tax_ids' in line:
                    line.update({
                        'tax_ids': [(6, 0, line['tax_ids'])]
                    })

                order_lines.append((0, 0, line))
            order_data = {
                'session_id': int(request.jsonrequest['data'].get('session_id')),
                'amount_paid': request.jsonrequest['data'].get('amount_paid'),
                'amount_return': request.jsonrequest['data'].get('amount_return'),
                'amount_tax': request.jsonrequest['data'].get('amount_tax'),
                'amount_total': request.jsonrequest['data'].get('amount_total'),
                'user_id': int(uid),
                'lines': order_lines
            }
            if request.jsonrequest['data'].get('partner_id'):
                order_data.update({'partner_id': int(request.jsonrequest['data'].get('partner_id'))})
            if request.jsonrequest['data'].get('pos_reference'):
                order_data.update({'pos_reference': request.jsonrequest['data'].get('pos_reference')})

            order = PosOrder.sudo().create(order_data)
            order.add_payment({
                'pos_order_id': order.id,
                'amount': request.jsonrequest['data']['payment_line'].get('amount'),
                'name': request.jsonrequest['data']['payment_line'].get('payment_name'),
                'payment_method_id': request.jsonrequest['data']['payment_line'].get('payment_method_id'),
            })
            order.action_pos_order_paid()

            data = {
                    'order_id': order.id,
                    'order_status': order.state
                }
            jsondata = {
                "statusCode": 200,
                "message": "New order created successfully.",
                "data": data
            }
            return jsondata
        else:
            return "User Access Failed"

    # create new payment against pos order
    @http.route('/api/pos/payment', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def create_new_pos_payment(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            PosOrder = request.env['pos.order'].search([('id', '=', request.jsonrequest['data'].get('order_id'))])

            payment_data = {
                'session_id': PosOrder.session_id and PosOrder.session_id.id,
                'journal': PosOrder.session_id.config_id.journal_ids and PosOrder.session_id.config_id.journal_ids.id,
                'amount': request.jsonrequest['data'].get('amount'),
                # 'payment_date': fields.Date.today(self)
            }
            payment = PosOrder.sudo().add_payment(payment_data)
            if PosOrder.test_paid():
                PosOrder.action_pos_order_paid()
            jsondata = {
                "statusCode": 200,
                "message": "New payment added to the order successfully.",
                "data": payment
            }
            return jsondata
        else:
            return "User Access Failed"

    # get last order id for user
    @http.route('/api/pos/getLatestOrder', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def get_latest_order(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            uid = int(uid)
            PosOrder = request.env['pos.order'].search([('user_id', '=', uid)])

            request.env.cr.execute("""
                        SELECT pos_reference
                          FROM pos_order WHERE user_id = %s AND date_order IN (
                            SELECT MAX( date_order )
                              FROM pos_order
                          ) """, (uid,))
            order_ref = request.env.cr.fetchall()

            jsondata = {
                "statusCode": 200,
                "message": "New payment added to the order successfully.",
                "data": order_ref
            }
            return jsondata
        else:
            return "User Access Failed"

    # get pricelist
    @http.route('/api/pos/getPricelist', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def get_pricelist(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            pricelists = request.env['product.pricelist'].search([])
            pricelist = []
            for rec in pricelists:
                pricelist.append({
                    'id': rec.id,
                    'name': rec.name
                })

            jsondata = {
                "statusCode": 200,
                "message": "list of Pricelists.",
                "data": pricelist
            }
            return jsondata
        else:
            return "User Access Failed"

    # get pricelist items
    @http.route('/api/pos/getPricelistItems', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def get_pricelist_items(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            pricelist_items = request.env['product.pricelist.item'].search([], limit=limit, offset=offset)
            products = []
            for rec in pricelist_items:
                item = {
                    'product_tmpl_id': rec.product_tmpl_id.id,
                    'product_id': rec.product_id.id,
                    'product_name': rec.product_tmpl_id.name,
                    'product_price': rec.fixed_price,
                    'pricelist_id': rec.pricelist_id.id
                }
                products.append(item)

            jsondata = {
                "statusCode": 200,
                "message": "list of Pricelists.",
                "data": products
            }
            return jsondata
        else:
            return "User Access Failed"

    # get pos payment methods
    @http.route('/api/pos/getPaymentMethods', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def get_payment_methods(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            payments = request.env['pos.payment.method'].search([])
            payment_methods = []
            for rec in payments:
                payment_methods.append({
                    'id': rec.id,
                    'name': rec.name,
                    'is_cash_count': rec.is_cash_count
                })

            jsondata = {
                "statusCode": 200,
                "message": "list of Pricelists.",
                "data": payment_methods
            }
            return jsondata
        else:
            return "User Access Failed"

    # get pos restaurant seating
    @http.route('/api/pos/getSeating', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def get_floor_plan(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            floor_plan = request.env['restaurant.floor'].search([])
            seating = []
            for rec in floor_plan:
                floor_details = {
                    'floor_id': rec.id,
                    'floor_name': rec.name,
                    'pos_id': rec.pos_config_id.id,
                    'pos_name': rec.pos_config_id.name,
                    'tables': [{
                        'table_id': table.id,
                        'table_name': table.name,
                        'seats': table.seats,
                        'table_shape': table.shape
                    } for table in rec.table_ids]
                }
                seating.append(floor_details)

            jsondata = {
                "statusCode": 200,
                "message": "Seating arrangements available in the Restaurant.",
                "data": seating
            }
            return jsondata
        else:
            return "User Access Failed"
