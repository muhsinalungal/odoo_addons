# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
import json
from odoo import fields

_logger = logging.getLogger(__name__)


class UserLogin(http.Controller):

    # Check the access rights
    
    @http.route('/api/login', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def userLogin(self, **kwargs):
        username = request.jsonrequest['auth'].get('username')
        password = request.jsonrequest['auth'].get('password')
        db = request.jsonrequest['auth'].get('db')

        uid = request.session.authenticate(db, username, password)
        if uid:
            default_pos = request.env['res.users'].browse(uid).default_pos
            if default_pos:
                session_list = request.env['pos.session'].search(
                    [('user_id', '=', int(uid)), ('state', '!=', 'closed'), ('rescue', '=', False)], limit=1)
                if session_list:
                    for session in session_list:
                        if session.state != 'opened':
                            session.sudo().action_pos_session_open()
                else:
                    data = {
                        'user_id': int(uid),
                        'config_id': default_pos.id
                    }
                    session_list = session_list.sudo().create(data)
                    session_list.sudo().action_pos_session_open()
                jsondata = {
                    "statusCode": 200,
                    "message": "User login Successfull",
                    "data": {
                        'user_id': int(uid),
                        'pos_session_id': session_list.id
                    }
                }
                return jsondata
            else:
                jsondata = {
                    "statusCode": 200,
                    "message": "There is no default pos set for the user, please contact administrator !",
                }
                return jsondata
        else:
            return "Access failed"

    @http.route('/api/getToken', type="http", auth="public", methods=['GET'], csrf=False, cors='*')
    def user_getToken(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        db = kwargs.get('db')

        uid = request.session.authenticate(db, username, password)
        if uid:
            user = request.env['res.users'].browse(uid)
            user.reset_api_token()
            token = user.api_token
            jsondata = {
                'user_id': uid,
                'token': token
            }

            return jsondata
        else:
            return "Access failed"
