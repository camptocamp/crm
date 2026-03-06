# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ast

from odoo import api, models
from odoo.fields import Domain


class Team(models.Model):
    _inherit = "crm.team"

    @api.model
    def action_your_pipeline(self):
        action = super().action_your_pipeline()
        request_type = self.env.context.get("request_type")
        if request_type:
            action["domain"] = (
                Domain(action.get("domain") or Domain.TRUE)
                & Domain("type", "=", "opportunity")
                & Domain("request_type", "=", request_type)
            )
            if action.get("context"):
                action["context"] = ast.literal_eval(action["context"])
            else:
                action["context"] = {}
            action["context"]["default_request_type"] = request_type
        return action
