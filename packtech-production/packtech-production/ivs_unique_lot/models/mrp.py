from odoo import api, fields, models
from collections import Counter
from odoo.exceptions import ValidationError


class ProductionOrder(models.Model):
    _inherit='mrp.production'

    def button_mark_done(self):
        dictoftuples=self.get_same_product_lot()
        for i,value in dictoftuples.items():
            for index,count in value.items():
                if count>1:
                    raise ValidationError("""You Must use Different Lot Per Component Line! Product Name {product}, lot {lot}"""
                                          .format(lot=i,product=self.env['product.product'].browse(index).name))
        res=super().button_mark_done()
        return res


    def action_confirm(self):
        self=self.with_context(check_unique_lot=True,mo_id=self.id)
        res=super().action_confirm()
        return res

    def get_same_product_lot(self):
        lots=[]
        for line in self.move_raw_ids:
            if line.product_id.unique_lot:
                for lot in line.lot_ids:
                    lots.append((line.product_id.id,lot.name))
        setoftuples = set((item[1]) for item in lots)
        dictoftuples = {n: [] for n in setoftuples}
        for tup in lots:
            dictoftuples[(tup[1])].append(tup[0])
        for i, value in dictoftuples.items():
            dictoftuples[i] = dict(Counter(value))
        return dictoftuples







