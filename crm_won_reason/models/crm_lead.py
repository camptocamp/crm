# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    won_reason_id = fields.Many2one("crm.lost.reason")

    # override action to consider won reason
    def action_set_won(self, **additional_args):
        res = super().action_set_won()
        if additional_args:
            self.write(dict(additional_args))
        return res
