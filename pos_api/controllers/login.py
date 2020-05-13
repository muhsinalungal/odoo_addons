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
            jsondata = {
                "statusCode": 200,
                "message": "User login Successfull",
                "data": int(uid)
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
