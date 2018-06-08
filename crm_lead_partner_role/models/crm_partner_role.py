# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class CrmPartnerRole(models.Model):
    _name = 'crm.partner.role'

    partner_id = fields.Many2one('res.partner')

    role_id = fields.Many2one('crm.role')

    crm_lead_id = fields.Many2one('crm.lead')
