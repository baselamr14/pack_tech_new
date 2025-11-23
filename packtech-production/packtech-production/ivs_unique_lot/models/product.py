# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)



class ProductTemplate(models.Model):
    _inherit = 'product.template'
    unique_lot = fields.Boolean(string='Unique Lot For  Components')

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def get_used_lots(self, product_id,production_id):
        mo=self.env['mrp.production'].browse(production_id)
        lots = []
        for raw in mo.move_raw_ids:
            for line in raw.move_line_ids:
                if line.product_id.id == product_id:
                    lots.append(line.lot_id.id)
        return lots


    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        lots=[]
        flag=False
        if self._context.get('check_unique_lot') and product_id.unique_lot:
            flag=True
            lots=self.get_used_lots(product_id.id, self._context.get('mo_id'))

        removal_strategy = self._get_removal_strategy(product_id, location_id)
        removal_strategy_order = self._get_removal_strategy_order(removal_strategy)

        domain = [('product_id', '=', product_id.id)]
        if not strict:
            if lot_id:
                domain = expression.AND([['|', ('lot_id', '=', lot_id.id), ('lot_id', '=', False)], domain])
            if lots and flag:
                domain = expression.AND([[ ('lot_id', 'not in', lots)], domain])
            if package_id:
                domain = expression.AND([[('package_id', '=', package_id.id)], domain])
            if owner_id:
                domain = expression.AND([[('owner_id', '=', owner_id.id)], domain])
            domain = expression.AND([[('location_id', 'child_of', location_id.id)], domain])
        else:
            domain = expression.AND([['|', ('lot_id', '=', lot_id.id), ('lot_id', '=', False)] if lot_id else [('lot_id', '=', False)], domain])
            domain = expression.AND([[('package_id', '=', package_id and package_id.id or False)], domain])
            domain = expression.AND([[('owner_id', '=', owner_id and owner_id.id or False)], domain])
            domain = expression.AND([[('location_id', '=', location_id.id)], domain])

        return self.search(domain, order=removal_strategy_order).sorted(lambda q: not q.lot_id)
