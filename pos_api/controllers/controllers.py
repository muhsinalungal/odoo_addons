# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
import json
from .login import UserLogin

_logger = logging.getLogger(__name__)


class POSMasters(http.Controller):

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

    # customers list
    @http.route('/api/pos/customer', type="json", methods=['POST'], auth='public', csrf=False)
    def get_customer_details(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            customer_list = request.env['res.partner'].search([], limit=limit, offset=offset)
            customer_info = []
            for customer in customer_list:
                customer_details = {
                    'id': customer.id,
                    'company_type': customer.company_type,
                    'status': customer.active,
                    'name': customer.name,
                    'phone': customer.phone,
                    'mobile': customer.mobile,
                    'address1': customer.street,
                    'address2': customer.street2,
                    'pincode': customer.zip,
                    'city': customer.city,
                    'state_id': customer.state_id.name,
                    'country_id': customer.country_id.name,
                    'email': customer.email,

                }
                customer_info.append(customer_details)

            jsondata = {
                "statusCode": 200,
                "message": "Customer list",
                "page": {
                    "totalCount": len(customer_list),
                    "limit": limit
                },
                "data": customer_info
            }
            
            return jsondata
        else:
            return "User Access Failed"

    # users list
    @http.route('/api/pos/user', type="json", methods=['POST'], auth='public', csrf=False)
    def get_user_details(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            user_list = request.env['res.users'].search([], limit=limit, offset=offset)
            user_info = []
            for user in user_list:
                user_details = {
                    'id': user.id,
                    'email': user.login,
                    'status': user.active,
                    'name': user.name,
                    'mobile': user.mobile

                }
                user_info.append(user_details)

            jsondata = {
                "statusCode": 200,
                "message": "User list",
                "page": {
                    "totalCount": len(user_list),
                    "limit": limit
                },
                "data": user_info
            }
            return jsondata
        else:
            return "User  Access Failed"

    # pos category list
    @http.route('/api/pos/category', type="json", methods=['POST'], auth='public', csrf=False)
    def get_pos_category_details(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            category_list = request.env['pos.category'].search([], limit=limit, offset=offset)
            category_info = []
            for category in category_list:
                category_details = {
                    'id': category.id,
                    'name': category.name,
                    'parent_category': {
                        'id': category.parent_id.id,
                        'name': category.parent_id.name
                    }

                }
                category_info.append(category_details)

            jsondata = {
                "statusCode": 200,
                "message": "Category list",
                "page": {
                    "totalCount": len(category_list),
                    "limit": limit
                },
                "data": category_info
            }
            return jsondata
        else:
            return "User  Access Failed"

    # pos product list
    @http.route('/api/pos/product', type="json", methods=['POST'], auth='public', csrf=False)
    def get_pos_product_details(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            product_list = request.env['product.product'].search([('available_in_pos', '=', True)], limit=limit, offset=offset)
            product_info = []
            for product in product_list:
                product_details = {
                    'id': product.id,
                    'name': product.name,
                    'type': product.type,
                    'internal_reference': product.default_code,
                    'barcode': product.barcode,
                    'sale_price': product.lst_price,
                    'cost_price': product.standard_price,
                    'pos_categ_id': {
                        'id': product.pos_categ_id.id,
                        'name': product.pos_categ_id.name
                    },
                    'qty_available': product.qty_available,
                    'cooking_time': product.cooking_time
                }
                product_info.append(product_details)

            jsondata = {
                "statusCode": 200,
                "message": "Product list",
                "page": {
                    "totalCount": len(product_list),
                    "limit": limit
                },
                "data": product_info
            }
            return jsondata
        else:
            return "User  Access Failed"

    # UOM category list
    @http.route('/api/uom/category', type="json", methods=['POST'], auth='public', csrf=False)
    def get_pos_uom_category_details(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            category_list = request.env['uom.category'].search([], limit=limit, offset=offset)
            category_info = []
            for category in category_list:
                category_details = {
                    'id': category.id,
                    'name': category.name,
                    'measure_type': category.measure_type,

                }
                category_info.append(category_details)

            jsondata = {
                "statusCode": 200,
                "message": "UOM Category list",
                "page": {
                    "totalCount": len(category_list),
                    "limit": limit
                },
                "data": category_info
            }
            return jsondata
        else:
            return "User  Access Failed"

    # Unit Of Measure list
    @http.route('/api/uom/uom', type="json", methods=['POST'], auth='public', csrf=False)
    def get_pos_uom_details(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            uom_list = request.env['uom.uom'].search([], limit=limit, offset=offset)
            uom_info = []
            for uom in uom_list:
                uom_details = {
                    'id': uom.id,
                    'name': uom.name,
                    'category': {
                        'id': uom.category_id.id,
                        'name': uom.category_id.name
                    },
                    'type': uom.uom_type,
                    'active': uom.active,
                    'rounding': uom.rounding

                }
                uom_info.append(uom_details)

            jsondata = {
                "statusCode": 200,
                "message": "Unit Of Measure list",
                "page": {
                    "totalCount": len(uom_list),
                    "limit": limit
                },
                "data": uom_info
            }
            return jsondata
        else:
            return "User  Access Failed"

    # Tax list
    @http.route('/api/GetTaxes', type="json", methods=['POST'], auth='public', csrf=False)
    def get_product_taxes(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            tax_list = request.env['account.tax'].search([])
            tax_info = []
            for tax in tax_list:
                tax_details = {
                    'id': tax.id,
                    'name': tax.name,
                    'amount_type': tax.amount_type,
                    'active': tax.active,
                    'tax_scope': tax.type_tax_use,
                    'amount': tax.amount,
                    'price_include': tax.price_include

                }
                tax_info.append(tax_details)

            jsondata = {
                "statusCode": 200,
                "message": "Tax list",
                "data": tax_info
            }
            return jsondata
        else:
            return "User  Access Failed"

    # pos product images
    @http.route('/api/pos/ProductImages', type="json", methods=['POST'], auth='public', csrf=False)
    def get_pos_product_images(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            product_list = request.env['product.product'].search([('available_in_pos', '=', True)], limit=limit, offset=offset)
            product_info = []
            for product in product_list:
                product_details = {
                    'id': product.id,
                    'image': product.image_1024
                }
                product_info.append(product_details)

            jsondata = {
                "statusCode": 200,
                "message": "Product Image",
                "page": {
                    "totalCount": len(product_list),
                    "limit": limit
                },
                "data": product_info
            }
            return jsondata
        else:
            return "User  Access Failed"

    # pos category images
    @http.route('/api/pos/CategoryImages', type="json", methods=['POST'], auth='public', csrf=False)
    def get_pos_category_images(self, **kwargs):
        uid = self.userLogin(request.jsonrequest.get('auth'))
        if uid:
            limit = int(request.jsonrequest['auth'].get('limit'))
            offset = int(request.jsonrequest['auth'].get('offset'))
            category_list = request.env['pos.category'].search([], limit=limit, offset=offset)
            category_info = []
            for category in category_list:
                category_details = {
                    'id': category.id,
                    'image': category.image_128
                }
                category_info.append(category_details)

            jsondata = {
                "statusCode": 200,
                "message": "Product Image",
                "page": {
                    "totalCount": len(category_list),
                    "limit": limit
                },
                "data": category_info
            }
            return jsondata
        else:
            return "User  Access Failed"
