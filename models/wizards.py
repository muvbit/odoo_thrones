# models/wizards.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


## REGISTRAR JUGADORES

class PlayerRegistrationWizard(models.TransientModel):
    _name = 'odoo_thrones.player_registration_wizard'
    _description = 'Wizard para registro de jugadores'

    user = fields.Char(string="Nombre de usuario", required=True)
    password = fields.Char(string="Contraseña", required=True)
    name = fields.Char(string="Nombre del jugador", required=True)
    birth_date = fields.Date(string="Año de nacimiento", required=True)
    house = fields.Selection([
        ("stark", "Stark"),
        ("lannister", "Lannister"),
        ('targaryen', 'Targaryen'),
        ('greyjoy', 'Greyjoy'),
        ('baratheon', 'Baratheon'),
        ('martell', 'Martell'),
        ('tyrell', 'Tyrell'),
        ('tully', 'Tully'),
        ('arryn', 'Arryn')
    ], string="Linaje", required=True)
    avatar = fields.Image(max_width=200, max_height=200)

    def action_register_player(self):
        Player = self.env['odoo_thrones.player']
        Player.create({
            'user': self.user,
            'password': self.password,
            'name': self.name,
            'birth_date': self.birth_date,
            'house': self.house,
            'avatar': self.avatar,
        })
        return {'type': 'ir.actions.act_window_close'}


## WIZARD DE ATAQUE
class AttackWizard(models.TransientModel):
    _name = 'odoo_thrones.attack_wizard'
    _description = 'Wizard para atacar a otros jugadores'

    attacker_id = fields.Many2one('odoo_thrones.player', string="Atacante", required=True)
    defender_id = fields.Many2one('odoo_thrones.player', string="Defensor", required=True)
    units_to_attack = fields.Many2many('odoo_thrones.player_unit', string="Unidades para atacar")
    ships_to_attack = fields.Many2many('odoo_thrones.player_ship', string="Barcos para atacar")
    creatures_to_attack = fields.Many2many('odoo_thrones.player_creature', string="Criaturas para atacar")

    def action_attack(self):
        # Lógica de ataque mejorada
        total_attack = sum(unit.unit_id.attack * unit.amount for unit in self.units_to_attack)
        total_attack += sum(ship.ship_id.attack * ship.amount for ship in self.ships_to_attack)
        total_attack += sum(creature.creature_id.attack * creature.amount for creature in self.creatures_to_attack)

        total_defense = sum(unit.unit_id.defense * unit.amount for unit in self.defender_id.units)
        total_defense += sum(ship.ship_id.defense * ship.amount for ship in self.defender_id.ships)
        total_defense += sum(creature.creature_id.defense * creature.amount for creature in self.defender_id.creatures)

        # Calcular el daño total
        damage = max(0, total_attack - total_defense)

        if damage > 0:
            # El atacante gana
            self.defender_id.gold -= damage // 2
            self.attacker_id.gold += damage // 2
            self.attacker_id.level += 1
            message = f"¡{self.attacker_id.name} ha ganado la batalla y ha robado {damage // 2} de oro!"
        else:
            # El defensor gana
            self.attacker_id.gold -= total_defense // 2
            self.defender_id.gold += total_defense // 2
            self.defender_id.level += 1
            message = f"¡{self.defender_id.name} ha defendido con éxito y ha robado {total_defense // 2} de oro!"

        # Mostrar un mensaje al usuario
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Resultado de la Batalla',
                'message': message,
                'sticky': False,
            }
        }

    class DefenseWizard(models.TransientModel):
        _name = 'odoo_thrones.defense_wizard'
        _description = 'Wizard para defenderte de un ataque'

        battle_id = fields.Many2one('odoo_thrones.battle', string="Batalla", required=True)
        defense_units = fields.Many2many('odoo_thrones.player_unit', string="Unidades de Defensa")
        defense_ships = fields.Many2many('odoo_thrones.player_ship', string="Barcos de Defensa")
        defense_creatures = fields.Many2many('odoo_thrones.player_creature', string="Criaturas de Defensa")

        def action_defend(self):
            self.battle_id.write({
                'defense_units': [(6, 0, self.defense_units.ids)],
                'defense_ships': [(6, 0, self.defense_ships.ids)],
                'defense_creatures': [(6, 0, self.defense_creatures.ids)],
            })
            self.battle_id.action_calculate_battle()
            return {'type': 'ir.actions.act_window_close'}

class RepairWizard(models.TransientModel):
    _name = 'odoo_thrones.repair_wizard'
    _description = 'Wizard para reparar barcos, sanar unidades y criaturas'

    player_id = fields.Many2one('odoo_thrones.player', string="Jugador", required=True)
    unit_id = fields.Many2one('odoo_thrones.player_unit', string="Unidad a sanar")
    ship_id = fields.Many2one('odoo_thrones.player_ship', string="Barco a reparar")
    creature_id = fields.Many2one('odoo_thrones.player_creature', string="Criatura a sanar")

    gold_cost = fields.Integer(string="Costo en oro", compute="_compute_cost")
    wood_cost = fields.Integer(string="Costo en madera", compute="_compute_cost")
    iron_cost = fields.Integer(string="Costo en hierro", compute="_compute_cost")

    @api.depends('unit_id', 'ship_id', 'creature_id')
    def _compute_cost(self):
        for wizard in self:
            if wizard.unit_id:
                # Costo de reparación es la mitad del costo inicial de la unidad
                wizard.gold_cost = wizard.unit_id.unit_id.gold_cost // 2
                wizard.wood_cost = wizard.unit_id.unit_id.wood_cost // 2
                wizard.iron_cost = wizard.unit_id.unit_id.iron_cost // 2
            elif wizard.ship_id:
                # Costo de reparación es la mitad del costo inicial del barco
                wizard.gold_cost = wizard.ship_id.ship_id.gold_cost // 2
                wizard.wood_cost = wizard.ship_id.ship_id.wood_cost // 2
                wizard.iron_cost = wizard.ship_id.ship_id.iron_cost // 2
            elif wizard.creature_id:
                # Costo de sanación es la mitad del costo inicial de la criatura
                wizard.gold_cost = wizard.creature_id.creature_id.gold_cost // 2
                wizard.wood_cost = 0  # Las criaturas no requieren madera
                wizard.iron_cost = 0  # Las criaturas no requieren hierro
            else:
                wizard.gold_cost = 0
                wizard.wood_cost = 0
                wizard.iron_cost = 0

    def action_repair(self):
        self.ensure_one()
        player = self.player_id

        # Verificar recursos
        if player.gold < self.gold_cost:
            raise ValidationError("No tienes suficiente oro.")
        if player.wood < self.wood_cost:
            raise ValidationError("No tienes suficiente madera.")
        if player.iron < self.iron_cost:
            raise ValidationError("No tienes suficiente hierro.")

        # Descontar recursos
        player.gold -= self.gold_cost
        player.wood -= self.wood_cost
        player.iron -= self.iron_cost

        # Reparar o sanar
        if self.unit_id:
            self.unit_id.current_health = self.unit_id.max_health
        elif self.ship_id:
            self.ship_id.current_health = self.ship_id.max_health
        elif self.creature_id:
            self.creature_id.current_health = self.creature_id.max_health

        return {'type': 'ir.actions.act_window_close'}



class BuyBuildingWizard(models.TransientModel):
    _name = 'odoo_thrones.buy_building_wizard'
    _description = 'Wizard para comprar edificios'

    player_id = fields.Many2one('odoo_thrones.player', string="Jugador", required=True)
    building_id = fields.Many2one('odoo_thrones.building', string="Edificio")
    amount = fields.Integer(string="Cantidad", default=1)
    total_cost_gold = fields.Integer(string="Costo total en oro", compute="_compute_total_cost")
    total_cost_wood = fields.Integer(string="Costo total en madera", compute="_compute_total_cost")
    total_cost_iron = fields.Integer(string="Costo total en hierro", compute="_compute_total_cost")

    @api.depends('building_id', 'amount')
    def _compute_total_cost(self):
        for wizard in self:
            wizard.total_cost_gold = wizard.building_id.gold_cost * wizard.amount if wizard.building_id else 0
            wizard.total_cost_wood = wizard.building_id.wood_cost * wizard.amount if wizard.building_id else 0
            wizard.total_cost_iron = wizard.building_id.iron_cost * wizard.amount if wizard.building_id else 0

    @api.onchange('player_id')
    def _onchange_player_id(self):
        self.building_id = False  # Limpiar la selección del edificio al cambiar el jugador
        return {
            'domain': {
                'building_id': [('level', '<=', self.player_id.level)]
            }
        }

    def action_buy_building(self):
        self.ensure_one()
        player = self.player_id
        building = self.building_id

        # Verificar que el jugador tenga el nivel necesario
        if building.level > player.level:
            raise ValidationError("No tienes el nivel necesario para comprar este edificio.")

        # Verificar recursos
        if player.gold < self.total_cost_gold:
            raise ValidationError("No tienes suficiente oro.")
        if player.wood < self.total_cost_wood:
            raise ValidationError("No tienes suficiente madera.")
        if player.iron < self.total_cost_iron:
            raise ValidationError("No tienes suficiente hierro.")

        # Descontar recursos
        player.gold -= self.total_cost_gold
        player.wood -= self.total_cost_wood
        player.iron -= self.total_cost_iron

        # Añadir el edificio al jugador
        player.buildings = [(0, 0, {
            'building_id': building.id,
            'amount': self.amount
        })]

        return {'type': 'ir.actions.act_window_close'}

class BuyUnitWizard(models.TransientModel):
    _name = 'odoo_thrones.buy_unit_wizard'
    _description = 'Wizard para comprar unidades'

    player_id = fields.Many2one('odoo_thrones.player', string="Jugador", required=True)
    unit_id = fields.Many2one('odoo_thrones.unit', string="Unidad")
    amount = fields.Integer(string="Cantidad", default=1)
    total_cost_gold = fields.Integer(string="Costo total en oro", compute="_compute_total_cost")
    total_cost_wood = fields.Integer(string="Costo total en madera", compute="_compute_total_cost")
    total_cost_iron = fields.Integer(string="Costo total en hierro", compute="_compute_total_cost")

    @api.depends('unit_id', 'amount')
    def _compute_total_cost(self):
        for wizard in self:
            wizard.total_cost_gold = wizard.unit_id.gold_cost * wizard.amount if wizard.unit_id else 0
            wizard.total_cost_wood = wizard.unit_id.wood_cost * wizard.amount if wizard.unit_id else 0
            wizard.total_cost_iron = wizard.unit_id.iron_cost * wizard.amount if wizard.unit_id else 0

    @api.onchange('player_id')
    def _onchange_player_id(self):
        self.unit_id = False  # Limpiar la selección de la unidad al cambiar el jugador
        return {
            'domain': {
                'unit_id': [('level', '<=', self.player_id.level)]
            }
        }

    def action_buy_unit(self):
        self.ensure_one()
        player = self.player_id
        unit = self.unit_id

        # Verificar que el jugador tenga el nivel necesario
        if unit.level > player.level:
            raise ValidationError("No tienes el nivel necesario para comprar esta unidad.")

        # Verificar recursos
        if player.gold < self.total_cost_gold:
            raise ValidationError("No tienes suficiente oro.")
        if player.wood < self.total_cost_wood:
            raise ValidationError("No tienes suficiente madera.")
        if player.iron < self.total_cost_iron:
            raise ValidationError("No tienes suficiente hierro.")

        # Descontar recursos
        player.gold -= self.total_cost_gold
        player.wood -= self.total_cost_wood
        player.iron -= self.total_cost_iron

        # Añadir la unidad al jugador
        player.units = [(0, 0, {
            'unit_id': unit.id,
            'amount': self.amount
        })]

        return {'type': 'ir.actions.act_window_close'}

class BuyShipWizard(models.TransientModel):
    _name = 'odoo_thrones.buy_ship_wizard'
    _description = 'Wizard para comprar barcos'

    player_id = fields.Many2one('odoo_thrones.player', string="Jugador", required=True)
    ship_id = fields.Many2one('odoo_thrones.ship', string="Barco")
    amount = fields.Integer(string="Cantidad", default=1)
    total_cost_gold = fields.Integer(string="Costo total en oro", compute="_compute_total_cost")
    total_cost_wood = fields.Integer(string="Costo total en madera", compute="_compute_total_cost")
    total_cost_iron = fields.Integer(string="Costo total en hierro", compute="_compute_total_cost")

    @api.depends('ship_id', 'amount')
    def _compute_total_cost(self):
        for wizard in self:
            wizard.total_cost_gold = wizard.ship_id.gold_cost * wizard.amount if wizard.ship_id else 0
            wizard.total_cost_wood = wizard.ship_id.wood_cost * wizard.amount if wizard.ship_id else 0
            wizard.total_cost_iron = wizard.ship_id.iron_cost * wizard.amount if wizard.ship_id else 0

    @api.onchange('player_id')
    def _onchange_player_id(self):
        self.ship_id = False  # Limpiar la selección del barco al cambiar el jugador
        return {
            'domain': {
                'ship_id': [('level', '<=', self.player_id.level)]
            }
        }

    def action_buy_ship(self):
        self.ensure_one()
        player = self.player_id
        ship = self.ship_id

        # Verificar que el jugador tenga el nivel necesario
        if ship.level > player.level:
            raise ValidationError("No tienes el nivel necesario para comprar este barco.")

        # Verificar recursos
        if player.gold < self.total_cost_gold:
            raise ValidationError("No tienes suficiente oro.")
        if player.wood < self.total_cost_wood:
            raise ValidationError("No tienes suficiente madera.")
        if player.iron < self.total_cost_iron:
            raise ValidationError("No tienes suficiente hierro.")

        # Descontar recursos
        player.gold -= self.total_cost_gold
        player.wood -= self.total_cost_wood
        player.iron -= self.total_cost_iron

        # Añadir el barco al jugador
        player.ships = [(0, 0, {
            'ship_id': ship.id,
            'amount': self.amount
        })]

        return {'type': 'ir.actions.act_window_close'}




class BuyCreatureWizard(models.TransientModel):
    _name = 'odoo_thrones.buy_creature_wizard'
    _description = 'Wizard para comprar criaturas'

    player_id = fields.Many2one('odoo_thrones.player', string="Jugador", required=True)
    creature_id = fields.Many2one('odoo_thrones.creature', string="Criatura")
    amount = fields.Integer(string="Cantidad", default=1)
    total_cost_gold = fields.Integer(string="Costo total en oro", compute="_compute_total_cost")

    @api.depends('creature_id', 'amount')
    def _compute_total_cost(self):
        for wizard in self:
            wizard.total_cost_gold = wizard.creature_id.gold_cost * wizard.amount if wizard.creature_id else 0

    @api.onchange('player_id')
    def _onchange_player_id(self):
        self.creature_id = False  # Limpiar la selección de la criatura al cambiar el jugador
        return {
            'domain': {
                'creature_id': [('level', '<=', self.player_id.level)]
            }
        }

    def action_buy_creature(self):
        self.ensure_one()
        player = self.player_id
        creature = self.creature_id

        # Verificar que el jugador tenga el nivel necesario
        if creature.level > player.level:
            raise ValidationError("No tienes el nivel necesario para comprar esta criatura.")

        # Verificar recursos
        if player.gold < self.total_cost_gold:
            raise ValidationError("No tienes suficiente oro.")

        # Descontar recursos
        player.gold -= self.total_cost_gold

        # Añadir la criatura al jugador
        player.creatures = [(0, 0, {
            'creature_id': creature.id,
            'amount': self.amount
        })]

        return {'type': 'ir.actions.act_window_close'}
