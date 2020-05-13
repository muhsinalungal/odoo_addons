# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    time_taken = fields.Float("Time taken")
    responsible = fields.Many2one("res.users", string='Responsible')


class Product(models.Model):
    _inherit = "product.template"

    cooking_time = fields.Float("Cooking Time (minutes)", default='1')
