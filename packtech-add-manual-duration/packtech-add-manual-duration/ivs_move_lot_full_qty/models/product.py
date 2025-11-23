# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    move_lot_full_qty = fields.Boolean(string='Move Lot Full Qty')
