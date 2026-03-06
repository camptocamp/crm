# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    request_type = fields.Selection(
        [
            ("customer", "Customer Lead"),
            ("supplier", "Supplier Lead"),
        ],
    )
    purchase_amount_total = fields.Monetary(
        compute="_compute_purchase_data",
        string="Sum of Purchase Orders",
        help="Untaxed Total of Confirmed Purchase Orders",
        currency_field="company_currency",
    )
    request_for_quotation_count = fields.Integer(
        compute="_compute_purchase_data", string="Number of Request for Quotations"
    )
    purchase_order_count = fields.Integer(
        compute="_compute_purchase_data", string="Number of Purchase Orders"
    )
    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="opportunity_id",
        string="Purchase Orders",
    )

    @api.depends(
        "order_ids.state",
        "order_ids.currency_id",
        "order_ids.amount_untaxed",
        "order_ids.date_order",
        "order_ids.company_id",
    )
    def _compute_purchase_data(self):
        for lead in self:
            company_currency = lead.company_currency or self.env.company.currency_id
            purchase_orders = lead.purchase_order_ids.filtered_domain(
                self._get_lead_purchase_order_domain()
            )
            lead.purchase_amount_total = sum(
                order.currency_id._convert(
                    order.amount_untaxed,
                    company_currency,
                    order.company_id,
                    order.date_order or fields.Date.today(),
                )
                for order in purchase_orders
            )
            lead.request_for_quotation_count = len(
                lead.purchase_order_ids.filtered_domain(
                    self._get_lead_request_for_quotation_domain()
                )
            )
            lead.purchase_order_count = len(purchase_orders)

    def _get_lead_purchase_order_domain(self):
        return [("state", "not in", ("draft", "sent", "cancel"))]

    def _get_lead_request_for_quotation_domain(self):
        return [("state", "in", ("draft", "sent"))]

    def _create_customer(self):
        """It can be a customer or supplier depending on lead request type"""
        self = self.with_context(res_partner_search_mode=self.request_type)
        return super()._create_customer()

    def action_lead_rfq_new(self):
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id(
                "srm.srm_rfq_partner_action"
            )
        else:
            return self.action_rfq_new()

    def action_rfq_new(self):
        action = self.env["ir.actions.actions"]._for_xml_id("srm.action_lead_rfq_new")
        action["context"] = self._prepare_rfq_context()
        return action

    def _prepare_rfq_context(self):
        self.ensure_one()
        rfq_context = {
            "default_partner_id": self.partner_id.id,
            "default_opportunity_id": self.id,
        }
        if self.user_id:
            rfq_context["default_user_id"] = self.user_id.id
        return rfq_context
