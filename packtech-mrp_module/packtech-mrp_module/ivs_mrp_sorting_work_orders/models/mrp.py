# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import Counter


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    width_value = fields.Integer(related="production_id.width_value", string='Width Value', store=True)

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    width_value = fields.Integer(compute='_compute_width_value', string='Width Value', store=True)
    
    @api.depends('move_raw_ids', 'state')
    def _compute_width_value(self):
        for rec in self:
            values = set(rec._get_all_component_width_values())
            if len(values) == 1:
                width_value = list(values)[0]
            else:        
                width_value = 0    
            rec.update({'width_value': width_value})

    def _get_all_component_width_values(self):
        products = self.move_raw_ids.mapped('product_id')
        return products._get_product_variant_width_values()
    
    # def button_plan(self):
    #     for rec in self:
    #         values = rec._get_all_component_width_values()
    #         if values:
    #             if len(set(values)) > 1:
    #                 msg = f"""
    #                     MO: '{rec.name}' includes a component that is different in 
    #                     'field: Attribute Name of the attribute with the check {list(set(values))},
    #                     all lines must have the same width
    #                 """
    #                 raise ValidationError(msg)
    #             rec._plan_workorders
    #     return super(MrpProduction, self).button_plan()

    def _get_last_inprogress_workorder(self):
        return self.env['mrp.workorder'].search([('state', '=', 'progress')],order="date_planned_start desc",  limit=1)

    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. """
        orders_to_plan = self.filtered(lambda order: not order.is_planned)
        orders_to_confirm = orders_to_plan.filtered(lambda mo: mo.state == 'draft')
        orders_to_confirm.action_confirm()
        values = orders_to_plan.mapped('width_value')
        sorted_values = sorted(list(set(values)))
        progress_work_order = self._get_last_inprogress_workorder()
        if progress_work_order:
            for order in orders_to_plan.filtered(lambda mo: mo.width_value == progress_work_order.width_value):
                values = order._get_all_component_width_values()
                if values:
                    if len(set(values)) > 1:
                        msg = f"""
                            MO: '{order.name}' includes a component that is different in 
                            'field: Attribute Name of the attribute with the check {list(set(values))},
                            all lines must have the same width
                        """
                        raise ValidationError(msg)
                order._plan_workorders()
        for width in sorted_values:
            for order in orders_to_plan.filtered(lambda mo: mo.width_value == width and mo.width_value != 0 and mo.id != progress_work_order.production_id.id):
                values = order._get_all_component_width_values()
                if values:
                    if len(set(values)) > 1:
                        msg = f"""
                            MO: '{order.name}' includes a component that is different in 
                            'field: Attribute Name of the attribute with the check {list(set(values))},
                            all lines must have the same width
                        """
                        raise ValidationError(msg)
                order._plan_workorders()
        else:
            for order in orders_to_plan:
                values = order._get_all_component_width_values()
                if values:
                    if len(set(values)) > 1:
                        msg = f"""
                            MO: '{order.name}' includes a component that is different in 
                            'field: Attribute Name of the attribute with the check {list(set(values))},
                            all lines must have the same width
                        """
                        raise ValidationError(msg)
                order._plan_workorders()
        return True

    # def _plan_workorders(self, replan=False, width=[]):
    #     """ Plan all the production's workorders depending on the workcenters
    #     work schedule.

    #     :param replan: If it is a replan, only ready and pending workorder will be taken into account
    #     :type replan: bool.
    #     """
    #     self.ensure_one()
    #     if not self.workorder_ids:
    #         return

    #     self._link_workorders_and_moves()

    #     # Plan workorders starting from final ones (those with no dependent workorders)
    #     final_workorders = self.workorder_ids.filtered(lambda wo: not wo.needed_by_workorder_ids)
    #     print("width", width)
    #     print("final_workorders", final_workorders)
    #     for workorder in final_workorders:
    #         workorder._plan_workorder(replan)
    #     if width:
    #         workorders = self.workorder_ids.filtered(lambda w: w.state not in ['done', 'cancel'])
    #         ordered_workorders = sorted(workorders, key=lambda w: (w.workcenter_id, w.width_value))
    #         print("workorders", workorders)
    #         print("ordered_workorders", ordered_workorders)
    #     else:
    #         workorders = self.workorder_ids.filtered(lambda w: w.state not in ['done', 'cancel'])
    #     if not workorders:
    #         return
    #     self.with_context(force_date=True).write({
    #         'date_planned_start': min([workorder.leave_id.date_from for workorder in workorders]),
    #         'date_planned_finished': max([workorder.leave_id.date_to for workorder in workorders])
    #     })
