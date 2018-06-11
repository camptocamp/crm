# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Lead2OpportunityPartner(models.TransientModel):

    _inherit = 'crm.lead2opportunity.partner'

    name = fields.Selection(selection_add=[
        ('convert_create_project', 'Convert to opportunity and create project')
    ])
    use_tasks = fields.Boolean(default=True)

    @api.multi
    def _prepare_project_values(self, lead):
        return {
            'use_tasks': self.use_tasks,
            'alias_name': False,
            'name': lead.name,
            'lead_id': lead.id,
            'crm_project': True,
        }

    @api.multi
    def action_apply(self):
        self.ensure_one()

        if self.name != 'convert_create_project':
            return super(Lead2OpportunityPartner, self).action_apply()
        # TODO Check if really needed
        if len(self.env.context.get('active_ids')) > 1:
            raise UserError(_('Cannot create project with two leads.'))
        # Prepare opportunity conversion as it's done by odoo
        values = {
            'team_id': self.team_id.id,
        }
        if self.partner_id:
            values['partner_id'] = self.partner_id.id
        leads = self.env['crm.lead'].browse(
            self._context.get('active_ids', []))
        # Convert to opportunity as it's done by odoo
        values.update({'lead_ids': leads.ids, 'user_ids': [self.user_id.id]})
        self._convert_opportunity(values)
        # Create the project
        project_values = self._prepare_project_values(leads)
        project = self.env['project.project'].create(project_values)
        leads.write({'project_id': project.id})
        return leads.redirect_opportunity_view()
