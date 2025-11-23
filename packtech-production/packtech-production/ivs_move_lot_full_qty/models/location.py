# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Location(models.Model):
    _inherit = 'stock.location'
    move_lot_full_qty = fields.Boolean(string='Move Lot Full Qty')
