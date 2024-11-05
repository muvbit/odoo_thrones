# -*- coding: utf-8 -*-
# from odoo import http


# class OdooThrones(http.Controller):
#     @http.route('/odoo_thrones/odoo_thrones', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_thrones/odoo_thrones/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_thrones.listing', {
#             'root': '/odoo_thrones/odoo_thrones',
#             'objects': http.request.env['odoo_thrones.odoo_thrones'].search([]),
#         })

#     @http.route('/odoo_thrones/odoo_thrones/objects/<model("odoo_thrones.odoo_thrones"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_thrones.object', {
#             'object': obj
#         })

