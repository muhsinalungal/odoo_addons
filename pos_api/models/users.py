# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    default_pos = fields.Many2one('pos.config', string="Allowed POS")
    api_token = fields.Char(
        "API Token",
        default=lambda self: self._get_unique_api_token(),
        required=True,
        copy=False,
        help="Authentication token for access to API (/api).",
    )

    def reset_api_token(self):
        for record in self:
            record.write({"api_token": self._get_unique_api_token()})

    def _get_unique_api_token(self):
        api_token = str(uuid.uuid4())
        while self.search_count([("api_token", "=", api_token)]):
            api_token = str(uuid.uuid4())
        return api_token

    @api.model
    def reset_all_api_tokens(self):
        self.search([]).reset_api_token()
