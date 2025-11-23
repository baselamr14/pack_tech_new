from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit='stock.picking'


    def button_validate(self):
        message="The below product lot full quantity will moved completely to the destination location\n"
        lines=[]
        for picking in self:
            for line in picking.move_line_ids_without_package:
                # qty=line.product_id.virtual_available+line.product_id.qty_available
                qty=line.product_id.virtual_available
                if line.product_id.move_lot_full_qty and line.location_dest_id.move_lot_full_qty and line.qty_done!=qty:
                    lines.append((0,0,{
                        'product_id':line.product_id.id,
                        'lot':line.lot_id.name,
                        'full_qty':qty,
                        'move_line':line.id,
                        'transfer_id':picking.id,
                    }))
        if lines:
            view = self.env.ref('ivs_move_lot_full_qty.full_qty_message')
            return {
                'name': 'Full Qty Check',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'full.qty.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': {'default_name':message,'default_line_ids':lines},
            }



        res=super().button_validate()
        return res



