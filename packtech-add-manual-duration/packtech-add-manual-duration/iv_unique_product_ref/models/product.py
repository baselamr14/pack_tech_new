# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



# class ProductTemplate(models.Model):
#     _inherit = 'product.template'

#     @api.constrains('default_code')
#     def _onchange_default_code(self):
#         pass

    # @api.constrains('default_code')
    # def _constrains_default_code_uniques(self):
    #     domain = [('default_code', '=', self.default_code)]
    #     result = self.env['product.template'].search_count(domain)
    #     if self.default_code and result > 1:
    #         raise ValidationError(f"The Internal Reference {self.default_code} already exists")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.constrains('default_code')
    def _onchange_default_code(self):
        pass

    @api.constrains('default_code')
    def _constrains_default_code_uniques(self):
        domain = [('default_code', '=', self.default_code)]
        result = self.env['product.product'].search_count(domain)
        if self.default_code and result > 1:
            raise ValidationError(f"The Internal Reference {self.default_code} already exists")
