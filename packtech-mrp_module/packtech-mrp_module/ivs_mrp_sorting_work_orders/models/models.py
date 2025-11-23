# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import Counter


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mo_width = fields.Boolean(string='MO by Width')


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_product_variant_width_values(self):
        attr_width_values = self.product_template_variant_value_ids._get_attribute_values_width()
        return attr_width_values

class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    has_width = fields.Boolean(string='Width')
    
    def _is_attribute_has_width(self):
        return self.has_width
    
    def _get_attribute_line_ids_with_width(self):
        width_ids = []
        for rec in self:
            width_ids = rec.id if rec.has_width else None
        return width_ids
    
    def _get_attribute_with_width(self):
        return self.search([('has_width', '=', True)], limit=1)
    
    def find_duplicates(self, lst):
        counts = Counter(lst)
        duplicates = [item for item, count in counts.items() if count > 1 and item != 0]
        return duplicates
    
    @api.constrains('has_width')
    def _constrains_has_width(self):
        result = self.env['product.attribute'].search_count([('has_width', '=', True)])
        if result > 1:
            raise ValidationError("Width must unique and marked only once per company.")

    @api.constrains('value_ids')
    def _constrains_value_ids_width_value(self):
        result = self.value_ids.mapped('width_value')
        duplicates = self.find_duplicates(result)
        if duplicates:
            raise ValidationError(f"Width values {duplicates} must be unique across all lines.")


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    width_value = fields.Integer(string='Width Value')
    
    def _is_value_attribute_has_width(self):
        return self.attribute_id.has_width
        
    def _get_attribute_values_width(self):
        width_values = []
        for rec in self:
            if rec.width_value > 0:
                width_values.append(rec.width_value)
        return width_values

class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"
    
    width_value = fields.Integer(string='Width Value', related="product_attribute_value_id.width_value")
    
    def _is_value_attribute_has_width(self):
        return self.attribute_id.has_width
        
    def _get_attribute_values_width(self):
        width_values = []
        for rec in self:
            if rec.width_value > 0:
                width_values.append(rec.width_value)
        return width_values