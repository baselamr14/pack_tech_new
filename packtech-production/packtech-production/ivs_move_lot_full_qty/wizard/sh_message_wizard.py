# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models

class FullQtyMessageWizard(models.TransientModel):
    _name = "full.qty.message"
    name = fields.Text(string="Message")
    line_ids= fields.One2many(
        comodel_name='full.qty.message.lines',
        inverse_name='wiz_id',
        string='Products',
        required=False)

    def action_confirm(self):
        for line in self.line_ids:
            line.move_line.sudo().write({
                  'qty_done':line.full_qty
              })
            line.transfer_id.sudo().button_validate()



class FullQtyMessageWizardLines(models.TransientModel):
    _name = "full.qty.message.lines"
    wiz_id = fields.Many2one( comodel_name='full.qty.message',string='wiz')
    move_line = fields.Many2one( comodel_name='stock.move.line',string='move line')
    transfer_id = fields.Many2one( comodel_name='stock.picking',string='Transfer')
    product_id = fields.Many2one( comodel_name='product.product',string='Product')
    full_qty = fields.Float(string='Full Quantity')
    lot = fields.Char(string='Lot')