from src.stats.abilities.ability import Ability

class MeleeAttackAbility(Ability):
    SCRIPT = '''
        use_time = UseTime("action")

        attack_disadvantage = {
            make_attack_roll = function()
                return RollModifier({disadvantage = true})
            end
        }

        can_make_offhand_attack = {
            get_abilities = function()
                return {"offhand_melee_attack", "offhand_ranged_attack"}
            end
        }

        offhand_melee_attack = {
            use_time = UseTime("bonus_action"),
            validate = function(target)
                offhand_weapon = statblock.get_offhand_item()
                if offhand_weapon == nil or not offhand_weapon.has_tag("weapon_light") then
                    return false, "Need light weapon in offhand."
                end
                if offhand_weapon.has_tag("weapon_reach") then melee_range = 14 else melee_range = 10 end
                if statblock.distance_to(target) >= melee_range then
                    return false, "Target out of attack range."
                end
                return true, nil
            end,
            run = function(target)
                offhand_weapon = statblock.get_offhand_item()
                result, message = statblock.melee_attack_roll(target, offhand_weapon.melee_damage)
                return result, message
            end
        }

        offhand_ranged_attack = {
            use_time = UseTime("bonus_action"),
            validate = function(target)
                offhand_weapon = statblock.get_offhand_item()
                if offhand_weapon == nil or not offhand_weapon.has_tag("weapon_light") then
                    return false, "Need light weapon in offhand."
                end
                if statblock.distance_to(target) > offhand_weapon.long_range then
                    return false, "Target out of attack range."
                end
                return true, nil
            end,
            run = function(target)
                offhand_weapon = statblock.get_offhand_item()
                long_attack = statblock.distance_to(target) > offhand_weapon.normal_range
                if long_attack then
                    statblock.add_effect("attack_disadvantage", 1)
                end
                result, message = statblock.ranged_attack_roll(target, offhand_weapon.ranged_damage)
                if not offhand_weapon.has_tag("ranged_weapon") then
                    statblock.drop_offhand_item(target.get_position())
                end
                if long_attack then
                    statblock.remove_effect("attack_disadvantage")
                end
                return result, message
            end
        }

        function validate(target)
            weapon = statblock.get_equipped_item()
            if weapon.has_tag("weapon_reach") then melee_range = 14 else melee_range = 10 end
            if statblock.distance_to(target) >= melee_range then
                return false, "Target out of attack range."
            end
            return true, nil
        end

        function run(target)
            weapon = statblock.get_equipped_item()
            result = false
            message = ""

            if weapon == nil then
                damage = 1 + statblock.get_ability_modifier("strength")
                result, message = statblock.melee_attack_roll(target, tostring(damage) .. " bludgeoning")
            else
                result, message = statblock.melee_attack_roll(target, weapon.melee_damage)
            end

            statblock.add_effect("can_make_offhand_attack", 1)

            return result, message
        end
    '''

    def __init__(self):
        super().__init__("melee_attack", MeleeAttackAbility.SCRIPT)

class RangedAttackAbility(Ability):
    SCRIPT = '''
        use_time = UseTime("action")

        attack_disadvantage = {
            make_attack_roll = function()
                return RollModifier({disadvantage = true})
            end
        }

        can_make_offhand_attack = {
            get_abilities = function()
                return {"offhand_melee_attack", "offhand_ranged_attack"}
            end
        }

        offhand_melee_attack = {
            use_time = UseTime("bonus_action"),
            validate = function(target)
                offhand_weapon = statblock.get_offhand_item()
                if offhand_weapon == nil or not offhand_weapon.has_tag("weapon_light") then
                    return false, "Need light weapon in offhand."
                end
                if offhand_weapon.has_tag("weapon_reach") then melee_range = 14 else melee_range = 10 end
                if statblock.distance_to(target) >= melee_range then
                    return false, "Target out of attack range."
                end
                return true, nil
            end,
            run = function(target)
                offhand_weapon = statblock.get_offhand_item()
                result, message = statblock.melee_attack_roll(target, offhand_weapon.melee_damage)
                return result, message
            end
        }

        offhand_ranged_attack = {
            use_time = UseTime("bonus_action"),
            validate = function(target)
                offhand_weapon = statblock.get_offhand_item()
                if offhand_weapon == nil or not offhand_weapon.has_tag("weapon_light") then
                    return false, "Need light weapon in offhand."
                end
                if statblock.distance_to(target) > offhand_weapon.long_range then
                    return false, "Target out of attack range."
                end
                return true, nil
            end,
            run = function(target)
                offhand_weapon = statblock.get_offhand_item()
                long_attack = statblock.distance_to(target) > offhand_weapon.normal_range
                if long_attack then
                    statblock.add_effect("attack_disadvantage", 1)
                end
                result, message = statblock.ranged_attack_roll(target, offhand_weapon.ranged_damage)
                if not offhand_weapon.has_tag("ranged_weapon") then
                    statblock.drop_offhand_item(target.get_position())
                end
                if long_attack then
                    statblock.remove_effect("attack_disadvantage")
                end
                return result, message
            end
        }

        function validate(target)
            weapon = statblock.get_equipped_item()
            if weapon == nil then
                return false, "No weapon equipped."
            end
            if statblock.distance_to(target) > weapon.long_range then
                return false, "Target out of attack range."
            end
            return true, nil
        end

        function run(target)
            weapon = statblock.get_equipped_item()
            long_attack = statblock.distance_to(target) > weapon.normal_range

            if long_attack then
                statblock.add_effect("ranged_attack_disadvantage", 1)
            end
            result, message = statblock.ranged_attack_roll(target, weapon.ranged_damage)
            if not weapon.has_tag("ranged_weapon") then
                statblock.drop_equipped_item(target.get_position())
            end
            if long_attack then
                statblock.remove_effect("ranged_attack_disadvantage")
            end
            
            statblock.add_effect("can_make_offhand_attack", 1)

            return result, message
        end
    '''

class DashAbility(Ability):
    SCRIPT = '''
        use_time = UseTime("action")

        dashing = {
            modify_speed = function()
                return SpeedModifier({walk = {value = 2.0, operation = "multiply"}, fly = {value = 2.0, operation = "multiply"}, swim = {value = 2.0, operation = "multiply"}, climb = {value = 2.0, operation = "multiply"}, burrow = {value = 2.0, operation = "multiply"}})
            end,
            end_turn = function()
                RemoveEffect()
            end
        }

        function run()
            statblock.add_effect("dashing", 1)
            return true, "Speed doubled for turn."
        end
    '''

    def __init__(self):
        super().__init__("dash", DashAbility.SCRIPT)