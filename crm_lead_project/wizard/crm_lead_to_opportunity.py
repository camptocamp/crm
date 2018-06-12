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
        for lead in leads:
            project_values = self._prepare_project_values(leads)
            if self.env.user.has_group(
                    'project.project.group_project_manager'):
                project = self.env['project.project'].create(project_values)
            else:
                project = self.env['project.project'].sudo().create(
                    project_values)
            lead.write({'project_id': project.id})
        return leads.redirect_opportunity_view()


class Lead2OpportunityMassConvert(models.TransientModel):

    _inherit = 'crm.lead2opportunity.partner.mass'

    @api.onchange('name')
    def _onchange_name(self):
        """Restrict deduplication if a project is to create."""
        if self.name == 'convert_create_project':
            self.deduplicate = False
        else:
            self.deduplicate = True
