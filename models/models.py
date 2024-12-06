# -*- coding: utf-8 -*-
from email.policy import default

from cloudinit.config.cc_spacewalk import required_packages
from odoo import models, fields, api

from odoo.fields import One2many


class Player (models.Model):
    _name = 'odoo_thrones.player'
    _description = 'Jugador de GOT'

    name = fields.Char(string="Nombre del jugador",required=True)
    house= fields.Selection([("stark","Stark"),
                             ("lannister","Lannister"),
                             ('targaryen', 'Targaryen'),
                             ('greyjoy', 'Greyjoy'),
                             ('baratheon', 'Baratheon'),
                             ('martell', 'Martell'),
                             ('tyrell', 'Tyrell'),
                             ('tully', 'Tully'),
                             ('arryn', 'Arryn')],
                            string="Selecciona la casa", required=True)

    level=fields.Integer(default=0, readonly=True)
    gold=fields.Integer(default=10000, readonly=True)
    food=fields.Integer(default=15000, readonly=True)
    wood=fields.Integer(default=1000, readonly=True)
    iron=fields.Integer(default=0, readonly=True)
    total_population=fields.Integer(default=100, readonly=True)
    workers=fields.Integer(readonly=True)
    soldiers=fields.Integer(readonly=True)

    houses=fields.One2many("odoo_thrones.house","player_id",string="Casa")
    buildings=fields.One2many("odoo_thrones.building","player_id",string="Casas")
    units=fields.One2many("odoo_thrones.unit","player_id",string="Unidades ejercito")
    weapons=fields.One2many("odoo_thrones.weapon","player_id",string="Armas")
    creatures=fields.One2many("odoo_thrones.creature","player_id",string="Criaturas")
    boats=fields.One2many("odoo_thrones.boat","player_id",string="Barcos")



class Building (models.Model):
    _name = "odoo_thrones.building"
    _description = "Edificios"

    name=fields.Char(string="Nombre del edificio",required=True)
    description=fields.Char(string="Tipo de edificio")

    health=fields.Integer(string="Puntos de vida", required=True)
    gold_cost = fields.Integer(string="Coste en oro", required=True)
    wood_cost=fields.Integer(string="Coste en madera", required=True)
    iron_cost=fields.Integer(string="Coste en hierro", required=True)
    workers_required=fields.Integer(string="Mano de obra necesaria", required=True)
    player_id=fields.Many2one("odoo_thrones.player",string="Jugador")

class House (models.Model):
    _name = "odoo_thrones.house"
    _description = "Casas"

    name = fields.Char(string="Nombre del edificio", required=True)
    description = fields.Char(string="Tipo de casa")
    gold_cost = fields.Integer(string="Coste en oro", required=True)
    wood_cost = fields.Integer(string="Coste en madera", required=True)
    iron_cost = fields.Integer(string="Coste en hierro", required=True)
    citizen=fields.Integer(string="Capacidad ciudadanos",required=True)
    player_id=fields.Many2one("odoo_thrones.player",string="Jugador")

class Weapon (models.Model):
    _name = "odoo_thrones.weapon"
    _description = "Armas"

    name = fields.Char(string="Nombre del arma", required=True)
    description = fields.Char(string="Descripción")
    type=fields.Char(string="Tipo de arma", required=True)
    max_uses=fields.Integer(string="Número de usos", required=True)

    gold_cost = fields.Integer(string="Coste en oro", required=True)
    wood_cost = fields.Integer(string="Coste en madera", required=True)
    iron_cost = fields.Integer(string="Coste en hierro", required=True)
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")

class PlayerWeapon(models.Model):
    _name = "odoo_thrones.player_weapon"
    _description = "Armas del jugador"

    player_id=fields.Many2one("odoo_thrones.player",string="Jugador")
    weapon_id=fields.Many2one("odoo_thrones.weapon",string="Arma")


class Creature (models.Model):
    _name="odoo_thrones.creature"
    _description = "Criatura"

    name=fields.Char(string="Nombre de la criatura", required=True)
    house = fields.Selection([("stark", "Stark"),
                              ("lannister", "Lannister"),
                              ('targaryen', 'Targaryen'),
                              ('greyjoy', 'Greyjoy'),
                              ('baratheon', 'Baratheon'),
                              ('martell', 'Martell'),
                              ('tyrell', 'Tyrell'),
                              ('tully', 'Tully'),
                              ('arryn', 'Arryn')],
                             string="Selecciona la casa", required=True)
    health = fields.Integer(string="Puntos de vida", required=True)
    level=fields.Integer(default=0, required=True)
    attack=fields.Integer(string="Puntos de ataque", required=True)
    defense=fields.Integer(string="Puntos de defensa", required=True)
    vulnerability=fields.Selection([("fire","Fuego"),("water","Agua"),("ice","Hielo"),("dragonglass","Vidriagon"),("nothing","No tiene")],string="Vulnerable a", required=True)
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")


class PlayerCreature(models.Model):
    _name = "odoo_thrones.player_creature"
    _description = "Criaturas del jugador"

    name=fields.Char(string="Nombre de la criatura")
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    creature_id = fields.Many2one("odoo_thrones.creature", string="Criatura")


class Unit (models.Model):
    _name = "odoo_thrones.unit"
    _description = "Unidades de ejercito"

    name = fields.Char(string="Nombre de la unidad", required=True)
    health = fields.Integer(string="Puntos de vida", required=True)
    level = fields.Integer(default=0, required=True)
    attack = fields.Integer(string="Puntos de ataque", required=True)
    defense = fields.Integer(string="Puntos de defensa", required=True)
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")


class PlayerUnit(models.Model):
    _name = "odoo_thrones.player_unit"
    _description = "Unidades del jugador"

    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    weapon_id = fields.Many2one("odoo_thrones.unit", string="Unidad")

class Boat(models.Model):
    _name = "odoo_thrones.boat"
    _description = "Barcos"

    name=fields.Char(string="Nombre del barco", required=True)
    health = fields.Integer(string="Puntos de vida", required=True)
    cannons= fields.Integer(string="Cañones",required=True)
    max_cannons=fields.Integer(string="Cañones máximos",required=True)
    attack = fields.Integer(string="Puntos de ataque", required=True)
    defense = fields.Integer(string="Puntos de defensa", required=True)
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    assigned_weapon=fields.Many2one("odoo_thrones.player_boat_weapon", string="Armas asignadas")

class PlayerBoat(models.Model):
    _name = "odoo_thrones.player_boat"
    _description = "Barcos del jugador"

    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    weapon_id = fields.Many2one("odoo_thrones.boat", string="Barco")

class PlayerBoatWeapon(models.Model):
    _name = "odoo_thrones.player_boat_weapon"
    _description = "Armas del barco del jugador"

    player_weapon_id = fields.Many2one("odoo_thrones.player_weapon", string="Arma")
    boat_id= fields.Many2one("odoo_thrones.boat", string="Barco")
    remainingUses=fields.Integer(string="Usos restantes")






#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


