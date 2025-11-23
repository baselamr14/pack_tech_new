# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('ref')
    def _check_ref_unique(self):
        result = self.env['res.partner'].search_count([('ref', '=', self.ref)]) 
        if self.ref and result > 1:
            raise ValidationError('Reference field must be unique.')
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = default or {}
        default['ref'] = False
        return super(ResPartner, self).copy(default=default)