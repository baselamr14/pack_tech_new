# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Loaded before installing the module.

    None of this module's DB modifications will be available yet.

    If you plan to raise an exception to abort install, put all code inside a
    ``with cr.savepoint():`` block to avoid broken databases.

    :param odoo.sql_db.Cursor cr:
        Database cursor.
    :example
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['ir.model.data'].search([
            ('model', 'like', '%stock%'),
            ('module', '=', 'stock')
        ]).unlink()
    """
    pass
    
def post_init_hook(cr, registry):
    """Loaded after installing the module.

    This module's DB modifications will be available.

    :param odoo.sql_db.Cursor cr:
        Database cursor.

    :param odoo.modules.registry.RegistryManager registry:
        Database registry, using v7 api.
    :example
        env = api.Environment(cr, SUPERUSER_ID, {})
        modules = env['ir.module.module'].search([('name', '=', 'account_edi_ubl_cii'), ('state', '=', 'uninstalled')])
        modules.sudo().button_install()
    """
    pass


def uninstall_hook(cr, registry):
    """Loaded before uninstalling the module.

    This module's DB modifications will still be available. Raise an exception
    to abort uninstallation.

    :param odoo.sql_db.Cursor cr:
        Database cursor.

    :param odoo.modules.registry.RegistryManager registry:
        Database registry, using v7 api.

    To-do:
     * update stock if this module is uninstalled
    :example
        env = api.Environment(cr, SUPERUSER_ID, {})
        models_to_clean = env['ir.model'].search([('ref_merge_ir_act_server_id', '!=', False)])
        actions_to_remove = models_to_clean.mapped('ref_merge_ir_act_server_id')
        actions_to_remove.unlink()
    """
    pass


def post_load():
    """Loaded before any model or data has been initialized.

    This is ok as the post-load hook is for server-wide
    (instead of registry-specific) functionalities.
    """
    pass
