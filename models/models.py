# -*- coding: utf-8 -*-
import base64
import os
from datetime import datetime, date

from email.policy import default

from cloudinit.config.cc_spacewalk import required_packages
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

from odoo.fields import One2many


class Player (models.Model):
    _name = 'odoo_thrones.player'
    _description = 'Jugador de odooThrones'

    user=fields.Char(string="Nombre de usuario", required=True)
    password=fields.Char(string="Contraseña", password=True, required=True)
    @api.constrains('password')
    def _check_password_length(self):
        for player in self:
            if len(player.password) < 6:
                raise ValidationError("La contraseña debe tener al menos 6 caracteres.")
    name = fields.Char(string="Nombre del jugador",required=True)
    birth_date = fields.Date(string="Año de nacimiento", required=True)

    @api.constrains("birth_date")
    def _chech_birthdate(self):
        for player in self:
            if player.birth_date:
                today = date.today()
                age = today.year - player.birth_date.year
                if today.month < player.birth_date.month or (today.month == player.birth_date.month and today.day < player.birth_date.day):
                    age -= 1
                if age < 16:
                    raise ValidationError("No se pueden registrar jugadores menores de 16 años.")
    enrollment_date=fields.Datetime(default=lambda s:fields.Datetime.now(), readonly=True)
    avatar=fields.Image(max_width=200, max_height=200)
    house= fields.Selection([("stark","Stark"),
                             ("lannister","Lannister"),
                             ('targaryen', 'Targaryen'),
                             ('greyjoy', 'Greyjoy'),
                             ('baratheon', 'Baratheon'),
                             ('martell', 'Martell'),
                             ('tyrell', 'Tyrell'),
                             ('tully', 'Tully'),
                             ('arryn', 'Arryn')],
                            string="Linaje", required=True)

    @api.depends("house")
    def _get_houseFlag(self):
        module_path = os.path.dirname(os.path.abspath(__file__))
        flags_path = os.path.join(module_path, '../static/images/flags')

        # Relacionamos los linajes con los archivos de las banderas
        house_flags = {
            "stark": "stark.png",
            "lannister": "lannister.png",
            "bolton":"bolton.png",
            "targaryen": "targaryen.png",
            "greyjoy": "greyjoy.png",
            "baratheon": "baratheon.png",
            "martell": "martell.png",
            "tyrell": "tyrell.png",
            "tully": "tully.png",
            "arryn": "arryn.png",
        }

        for player in self:
            image_file = house_flags.get(player.house)
            if image_file:
                image_path = os.path.join(flags_path, image_file)
                try:
                   with open(image_path, 'rb') as f:
                        player.flag = base64.b64encode(f.read())
                except FileNotFoundError:
                    player.flag = False
            else:
               player.flag = False


    flag=fields.Image(string="Casa", compute="_get_houseFlag")

    level=fields.Integer(default=1)

    @api.constrains('level')
    def _check_level(self):
        for player in self:
            if player.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")


    #Recursos
    gold=fields.Integer(string="Oro",default=10000, readonly=True)
    wood=fields.Integer(string="Madera",default=100, readonly=True)
    iron=fields.Integer(string="Hierro",default=0, readonly=True)

    #Propiedades
    buildings=fields.One2many("odoo_thrones.player_building", "player_id","Edificios")

    #Propiedades para batalla
    units=fields.One2many("odoo_thrones.player_unit","player_id",string="Unidades ejercito")
    creatures = fields.One2many("odoo_thrones.player_creature","player_id", string="Criaturas")
    ships=fields.One2many("odoo_thrones.player_ship","player_id",string="Barcos")

    def increment_gold(self):
        self.gold += 100

    def increment_wood(self):
        self.wood+=100

    def increment_iron(self):
        self.iron+=100

    def increment_level(self):
        self.level+=1

    def decrement_gold(self):
        self.gold -= 100

    def decrement_wood(self):
        self.wood -= 100

    def decrement_iron(self):
        self.iron -= 100

    def decrement_level(self):
        if self.level >1:
            self.level -= 1



class Building (models.Model):
    _name = "odoo_thrones.building"
    _description = "Edificios"

    name=fields.Char(string="Nombre del edificio",required=True)

    level=fields.Integer(string="Nivel", default=1, required=True)

    @api.constrains('level')
    def _check_level(self):
        for building in self:
            if building.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")

    gold_cost = fields.Integer(string="Coste en oro", required=True)
    wood_cost=fields.Integer(string="Coste en madera", required=True)
    iron_cost=fields.Integer(string="Coste en hierro", required=True)
    resource=fields.Selection([('gold','Oro'),('iron','Hierro'),('wood','Madera')], string="Aporta recurso", required=True)
    resource_amount_turn=fields.Integer(string="Aporta por turno", default=0, required=True)

class PlayerBuilding(models.Model):
    _name = "odoo_thrones.player_building"
    _description = "Edificios del jugador"

    name=fields.Char(related="building_id.name")
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    building_id = fields.Many2one("odoo_thrones.building", string="Edificio")
    amount=fields.Integer(default=0)
    _sql_constraints = [
        ('unique_player_building', 'unique(player_id, building_id)',
         'Cada jugador solo puede tener un registro por tipo de edificio.'),]


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
                             string="Casa", required=True)

    health = fields.Integer(string="Vida", required=True)
    gold_cost=fields.Integer(string="Coste en oro")
    level=fields.Integer(string="Nivel")

    @api.constrains('level')
    def _check_level(self):
        for creature in self:
            if creature.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")

    attack=fields.Integer(string="Ataque", required=True)
    defense=fields.Integer(string="Defensa", required=True)



class PlayerCreature(models.Model):
    _name = "odoo_thrones.player_creature"
    _description = "Criaturas del jugador"

    name=fields.Char(related="creature_id.name")
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    creature_id = fields.Many2one("odoo_thrones.creature", string="Criatura")
    level = fields.Integer(related='creature_id.level', string="Nivel requerido", readonly=True)
    amount=fields.Integer(default=0)
    _sql_constraints = [
        ('unique_player_creature', 'unique(player_id, creature_id)',
         'Cada jugador solo puede tener un registro por tipo de criatura.'),]


class Unit (models.Model):
    _name = "odoo_thrones.unit"
    _description = "Unidades de ejercito"

    name = fields.Char(string="Nombre de la unidad", required=True)
    health = fields.Integer(string="Puntos de vida", required=True)
    level=fields.Integer(string="Nivel requerido", required=True)

    @api.constrains('level')
    def _check_level(self):
        for unit in self:
            if unit.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")

    attack = fields.Integer(string="Puntos de ataque", required=True)
    defense = fields.Integer(string="Puntos de defensa", required=True)
    gold_cost = fields.Integer(string="Coste en oro", required=True)
    wood_cost = fields.Integer(string="Coste en madera", required=True)
    iron_cost = fields.Integer(string="Coste en hierro", required=True)


class PlayerUnit(models.Model):
    _name = "odoo_thrones.player_unit"
    _description = "Unidades del jugador"

    name = fields.Char(related="unit_id.name")
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    unit_id = fields.Many2one("odoo_thrones.unit", string="Unidad")
    level = fields.Integer(related='unit_id.level', string="Nivel requerido", readonly=True)
    amount=fields.Integer(string="Cantidad",default=0)

    _sql_constraints = [('unique_player_unit', 'unique(player_id, unit_id)', 'Cada jugador solo puede tener un registro por tipo de unidad.'),]

class Ship(models.Model):
    _name = "odoo_thrones.ship"
    _description = "Barcos"

    name=fields.Char(string="Nombre del barco", required=True)
    level=fields.Integer(string="Nivel", required=True)
    @api.constrains('level')
    def _check_level(self):
        for ship in self:
            if ship.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")

    health = fields.Integer(string="Puntos de vida", required=True)
    cannons= fields.Integer(string="Cañones",required=True)
    attack = fields.Integer(string="Puntos de ataque", required=True)
    defense = fields.Integer(string="Puntos de defensa", required=True)
    gold_cost=fields.Integer(string="Coste en oro", required=True)
    wood_cost = fields.Integer(string="Coste en madera", required=True)
    iron_cost = fields.Integer(string="Coste en hierro", required=True)

class PlayerShip(models.Model):
    _name = "odoo_thrones.player_ship"
    _description = "Barcos del jugador"

    name=fields.Char(related="ship_id.name")
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador", required=True)
    ship_id = fields.Many2one("odoo_thrones.ship", string="Barco", required=True)
    level = fields.Integer(related='ship_id.level', string="Nivel requerido", readonly=True)
    amount = fields.Integer(string="Cantidad", default=0)


    _sql_constraints = [('unique_player_ship', 'unique(player_id, ship_id)','Cada jugador solo puede tener un registro por tipo de barco.'),]







#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


