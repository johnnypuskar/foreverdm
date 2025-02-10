from enum import Enum
from src.util.modifier_values import ModifierValues
from src.util.return_status import ReturnStatus
from src.util.dice import DiceParser, DiceInstance
from src.util.constants import EventType
from src.events.event_context import NumericRollEventContext, DamageEventContext, EventContext, DamageRollContext
from src.stats.handlers.ability_roll_handler import AbilityRollHandler

class HitPointHandler:
    class DamageType(Enum):
        ACID = "acid"
        BLUDGEONING = "bludgeoning"
        COLD = "cold"
        FIRE = "fire"
        FORCE = "force"
        LIGHTNING = "lightning"
        NECROTIC = "necrotic"
        PIERCING = "piercing"
        POISON = "poison"
        PSYCHIC = "psychic"
        RADIANT = "radiant"
        SLASHING = "slashing"
        THUNDER = "thunder"
        TRUE = "true"

    def __init__(self, statblock):
        self._statblock = statblock
    
    def get_max_hp(self):
        """Returns the maximum hit points of the statblock."""
        modifiers = ModifierValues(self._statblock._effects.get_function_results("modify_stat", self._statblock, "max_hp"))
        base_max_hp = self._statblock._hit_points._max_hp
        base_max_hp = modifiers.process_mult(base_max_hp)
        base_max_hp = modifiers.process_add(base_max_hp)
        base_max_hp = modifiers.process_set_max(base_max_hp)
        return base_max_hp

    def restore_hp(self, amount: int):
        """
        Restores an amount of hit points, up to the maximum.
        
        param amount: int - amount of hit points to restore.
        
        returns: ReturnStatus - true if successful, false if not.
        """
        # Get the Statblock's maximum hit points
        max_hp = self.get_max_hp()
        # Check if the Statblock is already at maximum hit points
        if self._statblock._hit_points._hp >= max_hp:
            return ReturnStatus(False, "Already at maximum hit points.")
        
        # Restore hit points up to the maximum
        healing_amount = min(amount, max_hp - self._statblock._hit_points._hp)
        self._statblock._hit_points._hp += healing_amount
        return ReturnStatus(True, f"Restored {healing_amount} HP.")

    def take_damage(self, damage_string: str, die_multiplier: int = 1):
        """
        Rolls damage dice and applies the damage to the Statblock's hit points, downing or killing them if necessary.

        param damage_string: str - the string representing the damage dice to roll
        param die_multiplier (optional): int - the multiplier to apply to the amount of damage dice rolled

        return: int - the total amount of damage dealt
        """
        if isinstance(damage_string, int):
            damage_string = str(damage_string)

        # Split the damage string into individual damage type instances
        damage_instances = [d.strip() for d in damage_string.split(",")]

        # Create dictionary of DiceInstances split by damage type to store damage dice
        overall_damage_table = {}
        for damage_instance in damage_instances:
            # If no damage type is specified, default to true damage which ignores resistances and immunities
            if " " not in damage_instance:
                damage_instance += f" {self.DamageType.TRUE.value}"
            damage_amount, damage_type = damage_instance.split(" ", 1)
            
            # Verify the damage type is valid
            if damage_type not in [damage_type.value for damage_type in self.DamageType]:
                raise ValueError(f"Invalid damage type ({damage_type})")

            dice = DiceParser.parse_string(damage_amount)
            if damage_type not in overall_damage_table:
                overall_damage_table[damage_type] = dice
            else:
                overall_damage_table[damage_type].merge(dice)
        
        # Get damage immunities, and for any damage types not immune to, roll the damage dice into a table to be passed to the damage roll reaction event.
        damage_immunities = list(set([immunity for sublist in self._statblock._effects.get_function_results("get_immunities", self._statblock) for immunity in sublist]))
        
        damage_dice_events = []
        for damage_type in overall_damage_table.keys():
            if damage_type not in damage_immunities:
                damage_dice_events.append((EventType.TRIGGER_ROLL_DAMAGE, DamageRollContext(self._statblock, damage_type, overall_damage_table[damage_type].roll_to_list(die_multiplier))))
        
        if not damage_dice_events:
            return 0
        rolled_events = [event for event in damage_dice_events if event[1].die_list]
        if rolled_events:
            self._statblock._controller.trigger_reactions(rolled_events)
        
        # If damage remains to be dealt, get each damage roll's die values after any reactions, apply resistances and vulnerabilities, and track the total damage dealt total and by type.
        damage_resistances = list(set([resistance for sublist in self._statblock._effects.get_function_results("get_resistances", self._statblock) for resistance in sublist]))
        damage_vulnerabilities = list(set([vulnerability for sublist in self._statblock._effects.get_function_results("get_vulnerabilities", self._statblock) for vulnerability in sublist]))

        damage_tally = {}
        total_damage = 0
        for _, damage_roll_context in damage_dice_events:
            if damage_roll_context.damage_type not in damage_immunities:
                subtotal = overall_damage_table[damage_roll_context.damage_type].roll_from_list(damage_roll_context.die_list)
                if subtotal > 0:
                    damage_tally[damage_roll_context.damage_type] = subtotal
                    if damage_roll_context.damage_type in damage_vulnerabilities:
                        damage_tally[damage_roll_context.damage_type] *= 2
                    if damage_roll_context.damage_type in damage_resistances:
                        damage_tally[damage_roll_context.damage_type] = damage_tally[damage_type] // 2
                    total_damage += damage_tally[damage_roll_context.damage_type]
        
        # Immunities are checked again in case of a reaction ability that changes a damage roll context's damage type
        if not damage_tally:
            return 0

        damage_contexts = [(EventType.TRIGGER_TAKE_DAMAGE, DamageEventContext(self._statblock, damage_amount, damage_type)) for damage_type, damage_amount in damage_tally.items()]
        self._statblock._controller.trigger_reactions(damage_contexts)

        # Actually decrement the hit points by the total damage dealt, and check for death or concentration loss        
        for _, damage_context in damage_contexts:
            if damage_context.proceed and damage_context.amount > 0:
                self._statblock._hit_points.reduce_hp(damage_context.amount)

        if self._statblock._hit_points.get_hp() <= 0:
            if self._statblock._abilities._concentration_tracker.concentrating:
                self._statblock._abilities._concentration_tracker.end_concentration()
            if abs(self._statblock._hit_points.get_hp()) >= self.get_max_hp():
                # TODO: Instant death
                self._statblock._controller.trigger_event(EventType.TRIGGER_DEATH, EventContext(self._statblock))
            else:
                self._statblock._hit_points._hp = 0
                self._statblock._controller.trigger_event(EventType.TRIGGER_ZERO_HP, EventContext(self._statblock))
        
        if self._statblock._abilities._concentration_tracker.concentrating:
            concentration_check_dc = max(10, total_damage // 2)
            save_result = AbilityRollHandler(self._statblock).saving_throw(
                concentration_check_dc, AbilityRollHandler.ABILITIES.CONSTITUTION.value, None,
                [EventType.TRIGGER_CONCENTRATION_SAVING_THROW_ROLL], [EventType.TRIGGER_CONCENTRATION_SAVING_THROW_SUCCEED], [EventType.TRIGGER_CONCENTRATION_SAVING_THROW_FAIL]
            )
            if not save_result.success:
                self._statblock._abilities._concentration_tracker.end_concentration()
        
        return total_damage