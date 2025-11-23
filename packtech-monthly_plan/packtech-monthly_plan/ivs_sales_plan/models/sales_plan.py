# -- coding: utf-8 --
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, AccessError
BLOCKED_STATUS = ['approved']
USER_BLOCKED_STATUS = BLOCKED_STATUS + ['waiting']
VALIDATE_BLOCKED_STATUS = BLOCKED_STATUS + ['waiting']
APPROVED_BLOCKED_STATUS = BLOCKED_STATUS + ['waiting']
MANAGER_BLOCKED_STATUS = BLOCKED_STATUS + []


class SalesPlan(models.Model):
    _name = 'sales.plan'
    _description = "Sales Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', default="New",
                       required=True, index=True, copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env.company)
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse', required=True)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    sales_lines = fields.One2many(
        comodel_name='sales.plan.lines', inverse_name='sales_id', string='Lines')
    sales_validations = fields.One2many(comodel_name='sales.plan.validations', inverse_name='sales_id',
                                          string='Validations', compute="_compute_sales_validations", store=True, precompute=True)
    state = fields.Selection(string='Status', selection=[
        ('new', 'New'),
        ('validation', 'Validation Requested'),
        ('waiting', 'Waiting Approval'),
        ('approved', 'Approved'),
    ], default="new", index=True, required=True, readonly=True, copy=False, tracking=True)

    user_group = fields.Boolean(string="Readonly User", compute="_compute_readonly_based_on_current_group",)
    validation_group = fields.Boolean(string="Readonly Validation", compute="_compute_readonly_based_on_current_group",)
    approved_group = fields.Boolean(string="Readonly Approved", compute="_compute_readonly_based_on_current_group",)
    manager_group = fields.Boolean(string="Readonly Manager", compute="_compute_readonly_based_on_current_group",)

    purchase_ids = fields.Many2many('purchase.order', string="Purchase", compute="_get_purchse_ids", store=True, precompute=True)
    show_replenishment = fields.Boolean(string="Show Replenishment", compute="_get_purchse_ids")
    purchase_count = fields.Integer(string="Purchase Count", compute="_get_purchse_ids")

    product_ids = fields.Many2many(comodel_name='product.product', string="Products", compute="_compute_products_with_main_bom")

    @api.depends("sales_validations")
    def _get_purchse_ids(self):
        for rec in self:
            is_there_line_need_to_generate_replenishment = rec.sales_validations.filtered(lambda line: line.needed_qty != 0 and not line.purchase_id)
            purchase_ids = rec.sales_validations.mapped('purchase_id')
            show_replenishment = False
            if is_there_line_need_to_generate_replenishment:
                show_replenishment = True
            rec.update({
                'purchase_ids': purchase_ids.ids, 
                'purchase_count': len(purchase_ids), 
                'show_replenishment': show_replenishment
            })
    
    def unlink(self):
        if self.state in ['approve']:
            if not self.env.user.has_group('ivs_sales_plan.sales_plan_manager'):
                raise AccessError("You don't have permission to delete this record.")
        return super(SalesPlan, self).unlink()

    def action_view_purchases(self, purchases=False):
        if not purchases:
            purchases = self.purchase_ids

        result = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        # choose the view_mode accordingly
        if len(purchases) > 1:
            result['domain'] = [('id', 'in', purchases.ids)]
        elif len(purchases) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = purchases.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result

    def action_request_validation(self):
        self.write({'state': 'validation'})
        self._send_email_notification()

    def action_validate_plan(self):
        self.write({'state': 'waiting'})
        self._send_email_notification()

    def action_approved(self):
        self.write({'state': 'approved'})

    @api.depends('name', 'sales_lines')
    def _compute_products_with_main_bom(self):
        for rec in self:
            bom_ids = self.env['mrp.bom'].search([('main_bom', '=', True)])
            if bom_ids:
                rec.product_ids = bom_ids.mapped('product_id').ids
            else:
                rec.product_ids = []

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = default or {}
        default['name'] = self.name + _(' (copy)')
        return super().copy(default=default)

    @api.constrains('sales_lines')
    def _check_sales_lines(self):
        sales_lines = self.sales_lines
        if len(set(sales_lines.mapped('product_id'))) != len(sales_lines.ids):
            raise ValidationError(
                "Sorry you can not use same product twice inside lines.")

    def _get_product_needed_qty(self):
        # this method responsbile for get products for validation tab
        products = {}
        product_has_bom = {}
        for line in self.sales_lines:
            multiply_qty = line.needed_qty
            bom_lines = line.bom_id.bom_line_ids
            for line in bom_lines:
                quantity = self._convert_qty_based_on_uom(qty=line.product_qty * multiply_qty, from_uom=line.product_uom_id, to_uom=line.product_id.uom_po_id)
                if line.product_id.bom_count > 0:
                    if not line.product_id in products:
                        product_has_bom[line.product_id] = quantity
                    else:
                        product_has_bom[line.product_id] += quantity
                else:
                    if not line.product_id in products:
                        products[line.product_id] = quantity
                    else:
                        products[line.product_id] += quantity
        if product_has_bom:
            result = self._get_multi_level_product_needed_qty(products=product_has_bom)
            for key,val in result.items():
                if key not in products:
                    products[key] = val
                else:
                    products[key] += val
        return products

    def _get_multi_level_product_needed_qty(self, products={}):
        # this method responsbile for get products for validation tab
        _products = {}
        for product,value in products.items():
            multiply_qty = value
            bom_id = self.env['mrp.bom'].search([('product_id', '=', product.id)], limit=1)
            bom_lines = bom_id.bom_line_ids
            if bom_lines and bom_id.type == 'normal':
                for line in bom_lines:
                    quantity = self._convert_qty_based_on_uom(
                        qty=line.product_qty * multiply_qty, 
                        from_uom=line.product_uom_id, 
                        to_uom=line.product_id.uom_po_id
                    )
                    if line.product_id.bom_count == 0:
                        # this condition means that the product doesn't has bom count
                        if not line.product_id in _products:
                            _products[line.product_id] = quantity
                        else:
                            _products[line.product_id] += quantity
                    else:
                        # if the product has bom count then we must repeat the proccess again until there is no bom count
                        new_products = {line.product_id: quantity}
                        _products.update(self._get_multi_level_product_needed_qty(products=new_products))
        return _products
    
    @api.depends(
        'sales_lines',
        'sales_lines.product_id',
        'sales_lines.bom_id',
        'sales_lines.expected_demand',
        'sales_lines.bom_id.bom_line_ids.product_id',
        'sales_lines.bom_id.bom_line_ids.product_qty',
        'sales_lines.bom_id.bom_line_ids.product_uom_id',
    )
    def _compute_sales_validations(self):
        for rec in self:
            if rec.state not in BLOCKED_STATUS + ['new']:
                rec.sales_validations = [(5, 0, 0)]
                products = self._get_product_needed_qty()
                sales_validations = []
                for product in products:
                    available = rec._convert_qty_based_on_uom(
                        qty=product.virtual_available, from_uom=product.uom_id, to_uom=product.uom_po_id)
                    data = {
                        'sales_id': rec.id,
                        'product_id': product.id,
                        'qty': products[product],
                        'available': available,
                        'safety_stock': self._get_safety_stock(product),
                    }
                    if (data['available'] - data['safety_stock']) > data['qty']:
                        data['needed_qty'] = 0
                    else:
                        data['needed_qty'] = (
                            data['qty'] - data['available']) + data['safety_stock']
                    sales_validations.append((0, 0, data))
                rec.write({'sales_validations': sales_validations})
    
    def action_update_planned_material(self):
        self._compute_sales_validations()

    def _get_locations_by_warehouse(self, warehouse_id):
        return self.env['stock.location'].search([('id', 'child_of', warehouse_id.lot_stock_id.id)]).ids

    def _get_safety_stock(self, product_id):
        domain = [
            ('location_id', 'in', self._get_locations_by_warehouse(self.warehouse_id)),
            ('product_id', '=', product_id.id)
        ]
        orderpoints = self.env['stock.warehouse.orderpoint'].search(domain)
        qty = 0
        uom = product_id.uom_id
        if orderpoints:
            qty = sum(orderpoints.mapped('product_min_qty'))
            uom = orderpoints[0].product_uom
        return self._convert_qty_based_on_uom(qty=qty, from_uom=uom, to_uom=product_id.uom_po_id)

    def _convert_qty_based_on_uom(self, qty, from_uom, to_uom):
        if from_uom == to_uom:
            return qty
        return from_uom._compute_quantity(qty, to_uom)

    @api.depends('state', 'name', 'sales_lines', 'sales_validations')
    def _compute_readonly_based_on_current_group(self):
        for rec in self:
            rec.update({
                'user_group': True if rec.env.user.has_group('ivs_sales_plan.sales_plan_user') else False,
                'validation_group': True if rec.env.user.has_group('ivs_sales_plan.sales_plan_validation') else False,
                'approved_group': True if rec.env.user.has_group('ivs_sales_plan.sales_plan_approver') else False,
                'manager_group': True if rec.env.user.has_group('ivs_sales_plan.sales_plan_manager') else False,
            })
   
    @api.model
    def _send_email_notification(self):
        if self.state == 'validation':
            users = self.env.ref('ivs_sales_plan.sales_plan_validation').users
            subject = f'Please Validate this Sales Plan ({self.name})'
        else:
            users = self.env.ref('ivs_sales_plan.sales_plan_approver').users
            subject = f'Please Approve this Sales Plan ({self.name})'
        if users:
            emails_list = users.mapped('email')
            try:
                emails_str = ','.join(emails_list)
            except TypeError:
                emails_str = ''
                for email in emails_list:
                    emails_str += f'{str(email)},'
            notification_temp = self.env.ref('ivs_sales_plan.sales_plan_email_template')
            email_values = {
                'email_from': self.env.company.partner_id.email_formatted,
                'email_to':emails_str,
                'subject':subject,
            }
            notification_temp.with_context().send_mail(self.id, 
                force_send=True,
                email_values=email_values,
                email_layout_xmlid='mail.mail_notification_light'
            )
            return True
        return False

    def _absloute_url(self):
        menu_id = self.env.ref('ivs_sales_plan.sales_plan_sales_menu').id
        action_id = self.env.ref('ivs_sales_plan.sales_plan_action').id
        url= f'#id={self.id}&cids=1&menu_id={menu_id}&action={action_id}&model=sales.plan&view_type=form'
        return url

    def generate_rfq_replenishments(self):
        buy_route = self.env.ref('purchase_stock.route_warehouse0_buy')
        for line in self.sales_validations:
            if line.needed_qty > 0 and not line.purchase_id:
                vals = {
                    'product_id': line.product_id.id,
                    'product_tmpl_id': line.product_id.product_tmpl_id.id,
                    'quantity': line.needed_qty,
                    'product_uom_id': line.product_id.uom_po_id.id,
                    'route_ids': [(4, buy_route.id)],
                    'warehouse_id': self.warehouse_id.id,
                    'sales_plan_id': line.id,
                }
                replinish_id = self.env['product.replenish'].create(vals)
                replinish_id.launch_replenishment()
        return True


class SalesPlanLines(models.Model):
    _name = 'sales.plan.lines'
    _description = "Sales Plan Lines"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sales_id'

    sales_id = fields.Many2one(
        comodel_name='sales.plan', string='Sales Plan', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    bom_id = fields.Many2one(comodel_name='mrp.bom', string='Bom',
                             domain="[('product_id', '=', product_id)]", required=True)
    expected_demand = fields.Float(string='Expected Demand', required=True)
    available = fields.Float(
        string='Available', compute='_compute_available', store=True, precompute=True)
    needed_qty = fields.Float(
        string='Needed Qty', compute='_compute_needed_qty', store=True, precompute=True)
    alternative = fields.Boolean(
        string='Alternative', compute='_compute_alternative', store=True, precompute=True)
    state = fields.Selection(string='Status', related='sales_id.state')

    @api.depends('product_id.virtual_available')
    def _compute_available(self):
        for rec in self:
            if rec.state not in BLOCKED_STATUS:
                available = rec.available
                if rec.product_id:
                    available = rec.product_id.virtual_available
                rec.update({'available': available})

    @api.depends('expected_demand', 'available')
    def _compute_needed_qty(self):
        for rec in self:
            if rec.state not in BLOCKED_STATUS:
                needed_qty = 0
                if rec.expected_demand != 0:
                    needed_qty = rec.expected_demand - rec.available
                rec.update({'needed_qty': needed_qty})

    @api.depends('bom_id', 'bom_id.main_bom')
    def _compute_alternative(self):
        for rec in self:
            if rec.state not in BLOCKED_STATUS:
                alternative = True
                if rec.bom_id and rec.bom_id.main_bom:
                    alternative = False
                rec.update({'alternative': alternative})

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.state not in BLOCKED_STATUS:
            if self.product_id:
                bom_id = self.env['mrp.bom'].search([('product_id', '=', self.product_id.id), ('main_bom', '=', True)], limit=1)
                self.bom_id = bom_id.id if bom_id else False
            else:
                self.bom_id = False

class SalesPlanValidations(models.Model):
    _name = 'sales.plan.validations'
    _description = "Sales Plan Validations"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sales_id'
    
    sales_id = fields.Many2one(
        comodel_name='sales.plan', string='Sales Plan')
    purchase_id = fields.Many2one(
        comodel_name='purchase.order', string='Purchase Order')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Planned Material', required=True)
    qty = fields.Float(string='QTY', digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        related='product_id.uom_po_id',
        store=True,
        precompute=True,
        ondelete="restrict",
    )
    available = fields.Float(string='Available', digits='Product Unit of Measure', required=True)
    safety_stock = fields.Float(string='Safety Stock', digits='Product Unit of Measure', required=True)
    needed_qty = fields.Float(string='Needed Qty', digits='Product Unit of Measure', required=True)
    state = fields.Selection(string='Status', related='sales_id.state')

