# -*- coding: utf-8 -*-
import base64
import os
import random
from datetime import datetime, date

from email.policy import default

from cloudinit.config.cc_spacewalk import required_packages
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

from odoo.fields import One2many, _logger


class Player(models.Model):
    _name = 'odoo_thrones.player'
    _description = 'Jugador de odooThrones'

    user = fields.Char(string="Nombre de usuario", required=True)
    password = fields.Char(string="Contraseña", password=True, required=True)

    @api.constrains('password')
    def _check_password_length(self):
        for player in self:
            if len(player.password) < 6:
                raise ValidationError("La contraseña debe tener al menos 6 caracteres.")

    name = fields.Char(string="Nombre del jugador", required=True)
    birth_date = fields.Date(string="Año de nacimiento", required=True)

    @api.constrains("birth_date")
    def _chech_birthdate(self):
        for player in self:
            if player.birth_date:
                today = date.today()
                age = today.year - player.birth_date.year
                if today.month < player.birth_date.month or (
                        today.month == player.birth_date.month and today.day < player.birth_date.day):
                    age -= 1
                if age < 16:
                    raise ValidationError("No se pueden registrar jugadores menores de 16 años.")

    enrollment_date = fields.Datetime(default=lambda s: fields.Datetime.now(), readonly=True)
    avatar = fields.Image(max_width=200, max_height=200)
    house = fields.Selection([("stark", "Stark"),
                              ("lannister", "Lannister"),
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
            "bolton": "bolton.png",
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

    flag = fields.Image(string="Casa", compute="_get_houseFlag")

    level = fields.Integer(default=1)

    @api.constrains('level')
    def _check_level(self):
        for player in self:
            if player.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")

    # Recursos
    gold = fields.Integer(string="Oro", default=10000, readonly=True)
    wood = fields.Integer(string="Madera", default=100, readonly=True)
    iron = fields.Integer(string="Hierro", default=0, readonly=True)

    # Propiedades
    buildings = fields.One2many("odoo_thrones.player_building", "player_id", "Edificios")

    # Propiedades para batalla
    units = fields.One2many("odoo_thrones.player_unit", "player_id", string="Unidades ejercito")
    creatures = fields.One2many("odoo_thrones.player_creature", "player_id", string="Criaturas")
    ships = fields.One2many("odoo_thrones.player_ship", "player_id", string="Barcos")

    def increment_gold(self):
        self.gold += 100

    def increment_wood(self):
        self.wood += 100

    def increment_iron(self):
        self.iron += 100

    def increment_level(self):
        self.level += 1

    def decrement_gold(self):
        self.gold -= 100

    def decrement_wood(self):
        self.wood -= 100

    def decrement_iron(self):
        self.iron -= 100

    def decrement_level(self):
        if self.level > 1:
            self.level -= 1

    @api.model
    def simulate_turn(self):
        """Simula acciones de los jugadores en cada turno del cron."""
        players = self.search([])  # Obtiene todos los jugadores
        for player in players:
            # Generar recursos de los edificios
            for building in player.buildings:
                if building.building_id.resource == 'gold':
                    player.gold += building.building_id.resource_amount_turn * building.amount
                elif building.building_id.resource == 'wood':
                    player.wood += building.building_id.resource_amount_turn * building.amount
                elif building.building_id.resource == 'iron':
                    player.iron += building.building_id.resource_amount_turn * building.amount

            # Subir de nivel con baja probabilidad
            if random.randint(1, 10) == 1:  # 10% de probabilidad de subir de nivel
                player.level += 1

            # Mensaje en el log de Odoo
            self.env.cr.commit()
            _logger.info(f"Simulación: {player.user} ha ganado recursos y ha progresado en el juego.")


class Building(models.Model):
    _name = "odoo_thrones.building"
    _description = "Edificios"

    name = fields.Char(string="Nombre del edificio", required=True)

    level = fields.Integer(string="Nivel", default=1, required=True)

    @api.constrains('level')
    def _check_level(self):
        for building in self:
            if building.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")

    gold_cost = fields.Integer(string="Coste en oro", required=True)
    wood_cost = fields.Integer(string="Coste en madera", required=True)
    iron_cost = fields.Integer(string="Coste en hierro", required=True)
    resource = fields.Selection([('gold', 'Oro'), ('iron', 'Hierro'), ('wood', 'Madera')], string="Aporta recurso",
                                required=True)
    resource_amount_turn = fields.Integer(string="Aporta por turno", default=0, required=True)


class PlayerBuilding(models.Model):
    _name = "odoo_thrones.player_building"
    _description = "Edificios del jugador"

    name = fields.Char(related="building_id.name")
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    building_id = fields.Many2one("odoo_thrones.building", string="Edificio")
    amount = fields.Integer(default=0)
    _sql_constraints = [
        ('unique_player_building', 'unique(player_id, building_id)',
         'Cada jugador solo puede tener un registro por tipo de edificio.'), ]


class Creature(models.Model):
    _name = "odoo_thrones.creature"
    _description = "Criatura"

    name = fields.Char(string="Nombre de la criatura", required=True)
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
    gold_cost = fields.Integer(string="Coste en oro")
    level = fields.Integer(string="Nivel")

    @api.constrains('level')
    def _check_level(self):
        for creature in self:
            if creature.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")

    attack = fields.Integer(string="Ataque", required=True)
    defense = fields.Integer(string="Defensa", required=True)

    # Añadir un dominio para que solo se muestren las criaturas de la misma casa
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get('filter_by_house'):
            player = self.env['odoo_thrones.player'].browse(self.env.context.get('player_id'))
            args += [('house', '=', player.house)]
        return super(Creature, self).search(args, offset=offset, limit=limit, order=order, count=count)


class PlayerCreature(models.Model):
    _name = "odoo_thrones.player_creature"
    _description = "Criaturas del jugador"

    name = fields.Char(related="creature_id.name")
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador")
    creature_id = fields.Many2one("odoo_thrones.creature", string="Criatura")
    max_health = fields.Integer(related='creature_id.health', string="Vida Máxima", readonly=True)
    current_health = fields.Integer(string="Vida Restante", default=0)
    level = fields.Integer(related='creature_id.level', string="Nivel requerido", readonly=True)
    amount = fields.Integer(default=0)

    @api.model
    def create(self, vals):
        if 'creature_id' in vals:
            creature = self.env['odoo_thrones.creature'].browse(vals['creature_id'])
            vals['current_health'] = creature.health
        return super(PlayerCreature, self).create(vals)

    @api.constrains('current_health')
    def _check_current_health(self):
        for creature in self:
            if creature.current_health > creature.max_health:
                raise ValidationError("La vida restante no puede ser mayor que la vida máxima.")

    _sql_constraints = [
        ('unique_player_creature', 'unique(player_id, creature_id)',
         'Cada jugador solo puede tener un registro por tipo de criatura.'), ]


class Unit(models.Model):
    _name = "odoo_thrones.unit"
    _description = "Unidades de ejercito"

    name = fields.Char(string="Nombre de la unidad", required=True)
    health = fields.Integer(string="Puntos de vida", required=True)
    level = fields.Integer(string="Nivel requerido", required=True)

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
    max_health = fields.Integer(related='unit_id.health', string="Vida Máxima", readonly=True)
    current_health = fields.Integer(string="Vida Restante", default=0)
    level = fields.Integer(related='unit_id.level', string="Nivel requerido", readonly=True)
    amount = fields.Integer(string="Cantidad", default=0)

    @api.model
    def create(self, vals):
        if 'unit_id' in vals:
            unit = self.env['odoo_thrones.unit'].browse(vals['unit_id'])
            vals['current_health'] = unit.health
        return super(PlayerUnit, self).create(vals)

    @api.constrains('current_health')
    def _check_current_health(self):
        for unit in self:
            if unit.current_health > unit.max_health:
                raise ValidationError("La vida restante no puede ser mayor que la vida máxima.")

    _sql_constraints = [('unique_player_unit', 'unique(player_id, unit_id)',
                         'Cada jugador solo puede tener un registro por tipo de unidad.'), ]


class Ship(models.Model):
    _name = "odoo_thrones.ship"
    _description = "Barcos"

    name = fields.Char(string="Nombre del barco", required=True)
    level = fields.Integer(string="Nivel", required=True)

    @api.constrains('level')
    def _check_level(self):
        for ship in self:
            if ship.level < 0:
                raise ValidationError("El nivel no puede ser menor que 0.")

    health = fields.Integer(string="Puntos de vida", required=True)
    cannons = fields.Integer(string="Cañones", required=True)
    attack = fields.Integer(string="Puntos de ataque", required=True)
    defense = fields.Integer(string="Puntos de defensa", required=True)
    gold_cost = fields.Integer(string="Coste en oro", required=True)
    wood_cost = fields.Integer(string="Coste en madera", required=True)
    iron_cost = fields.Integer(string="Coste en hierro", required=True)


class PlayerShip(models.Model):
    _name = "odoo_thrones.player_ship"
    _description = "Barcos del jugador"

    name = fields.Char(related="ship_id.name")
    player_id = fields.Many2one("odoo_thrones.player", string="Jugador", required=True)
    ship_id = fields.Many2one("odoo_thrones.ship", string="Barco", required=True)
    max_health = fields.Integer(related='ship_id.health', string="Vida Máxima", readonly=True)
    current_health = fields.Integer(string="Vida Restante", default=0)
    level = fields.Integer(related='ship_id.level', string="Nivel requerido", readonly=True)
    amount = fields.Integer(string="Cantidad", default=0)

    @api.model
    def create(self, vals):
        if 'ship_id' in vals:
            ship = self.env['odoo_thrones.ship'].browse(vals['ship_id'])
            vals['current_health'] = ship.health
        return super(PlayerShip, self).create(vals)

    @api.constrains('current_health')
    def _check_current_health(self):
        for ship in self:
            if ship.current_health > ship.max_health:
                raise ValidationError("La vida restante no puede ser mayor que la vida máxima.")

    _sql_constraints = [('unique_player_ship', 'unique(player_id, ship_id)',
                         'Cada jugador solo puede tener un registro por tipo de barco.'), ]

    class Battle(models.Model):
        _name = 'odoo_thrones.battle'
        _description = 'Batalla entre jugadores'

        attacker_id = fields.Many2one('odoo_thrones.player', string="Atacante", required=True)
        defender_id = fields.Many2one('odoo_thrones.player', string="Defensor", required=True)
        state = fields.Selection(
            [('draft', 'Borrador'), ('attack', 'Ataque'), ('defense', 'Defensa'), ('done', 'Finalizada')],
            default='draft')

        # Especifica tablas de relación diferentes para attack_units y defense_units
        attack_units = fields.Many2many(
            'odoo_thrones.player_unit',
            'battle_attack_units_rel',  # Nombre de la tabla de relación para attack_units
            'battle_id', 'unit_id',
            string="Unidades de Ataque"
        )
        attack_ships = fields.Many2many(
            'odoo_thrones.player_ship',
            'battle_attack_ships_rel',  # Nombre de la tabla de relación para attack_ships
            'battle_id', 'ship_id',
            string="Barcos de Ataque"
        )
        attack_creatures = fields.Many2many(
            'odoo_thrones.player_creature',
            'battle_attack_creatures_rel',  # Nombre de la tabla de relación para attack_creatures
            'battle_id', 'creature_id',
            string="Criaturas de Ataque"
        )

        defense_units = fields.Many2many(
            'odoo_thrones.player_unit',
            'battle_defense_units_rel',  # Nombre de la tabla de relación para defense_units
            'battle_id', 'unit_id',
            string="Unidades de Defensa"
        )
        defense_ships = fields.Many2many(
            'odoo_thrones.player_ship',
            'battle_defense_ships_rel',  # Nombre de la tabla de relación para defense_ships
            'battle_id', 'ship_id',
            string="Barcos de Defensa"
        )
        defense_creatures = fields.Many2many(
            'odoo_thrones.player_creature',
            'battle_defense_creatures_rel',  # Nombre de la tabla de relación para defense_creatures
            'battle_id', 'creature_id',
            string="Criaturas de Defensa"
        )

        result = fields.Text(string="Resultado de la Batalla")

        def action_start_battle(self):
            self.state = 'attack'
            # Notificar al defensor
            self.defender_id.message_post(body=f"¡{self.attacker_id.name} te está atacando! Prepárate para defenderte.")

        def action_defend(self):
            self.state = 'defense'
            # Lógica para que el defensor seleccione sus unidades, barcos y criaturas

        def action_calculate_battle(self):
            self.state = 'done'
            # Lógica para calcular el resultado de la batalla
            total_attack = sum(unit.unit_id.attack * unit.amount for unit in self.attack_units)
            total_attack += sum(ship.ship_id.attack * ship.amount for ship in self.attack_ships)
            total_attack += sum(creature.creature_id.attack * creature.amount for creature in self.attack_creatures)

            total_defense = sum(unit.unit_id.defense * unit.amount for unit in self.defense_units)
            total_defense += sum(ship.ship_id.defense * ship.amount for ship in self.defense_ships)
            total_defense += sum(creature.creature_id.defense * creature.amount for creature in self.defense_creatures)

            # Aleatoriedad en la batalla
            attack_roll = random.randint(1, 20)
            defense_roll = random.randint(1, 20)

            if (total_attack * attack_roll) > (total_defense * defense_roll):
                self.result = f"¡{self.attacker_id.name} ha ganado la batalla!"
                self.defender_id.gold -= total_attack // 2
                self.attacker_id.gold += total_attack // 2
                self.attacker_id.level += 1
            else:
                self.result = f"¡{self.defender_id.name} ha defendido con éxito!"
                self.attacker_id.gold -= total_defense // 2
                self.defender_id.gold += total_defense // 2
                self.defender_id.level += 1

            # Notificar a ambos jugadores
            self.attacker_id.message_post(body=f"Resultado de la batalla: {self.result}")
            self.defender_id.message_post(body=f"Resultado de la batalla: {self.result}")

#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
