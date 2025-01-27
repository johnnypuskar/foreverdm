from src.stats.effects import Effect

class Condition(Effect):
    def __init__(self, name, script, globals = {}, duration = -1):
        super().__init__(name, script, globals, duration)
        self._derived = False

class Blinded(Condition):
    SCRIPT = '''
        function make_attack_roll(target)
            return RollModifier({disadvantage = true})
        end

        function recieve_attack_roll(attacker)
            return RollModifier({advantage = true})
        end

        function notice_target(target)
            return false
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("blinded", Blinded.SCRIPT, {}, duration)

class Charmed(Condition):
    SCRIPT = '''
        function make_attack_roll(target)
            if target == charmer then
                return RollModifier({auto_fail = true})
            end
            return RollModifier({})
        end

        function recieve_ability_check(type, trigger)
            if type == "cha" and trigger == charmer then
                return RollModifier({advantage = true})
            end
            return RollModifier({})
        end
    '''

    def __init__(self, charmer, duration = -1):
        super().__init__("charmed", Charmed.SCRIPT, {"charmer": charmer}, duration)

class Deafened(Condition):
    # TODO: Implement Deafened condition once senses are functional
    SCRIPT = '''
        function ability_check_impose(type)
            -- Not implemented yet due to only affecting senses
            return RollModifier({})
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("deafened", Deafened.SCRIPT, {}, duration)

class Frightened(Condition):
    SCRIPT = '''
        function move(old_pos, new_pos)
            if Distance(new_pos, frightener.get_position()) < Distance(old_pos, frightener.get_position()) then
                return false
            end
            return true
        end

        function make_attack_roll(target)
            if PositionVisible(frightener.get_position()) then
                return RollModifier({disadvantage = true})
            end
            return RollModifier({})
        end

        function ability_check_make(type)
            if PositionVisible(frightener.get_position()) then
                return RollModifier({disadvantage = true})
            end
            return RollModifier({})
        end
    '''

    def __init__(self, frightener, duration = -1):
        super().__init__("frightened", Frightened.SCRIPT, {"frightener": frightener}, duration)

class Grappled(Condition):
    SCRIPT = '''
        function move(old_pos, new_pos)
            if not statblock.in_melee(grappler) then
                RemoveEffect()
                return true
            end
            return false
        end
    '''

    def __init__(self, grappler, duration = -1):
        super().__init__("grappled", Grappled.SCRIPT, {"grappler": grappler}, duration)

class Incapacitated(Condition):
    SCRIPT = '''
        function allow_actions()
            return false
        end

        function allow_reactions()
            return false
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("incapacitated", Incapacitated.SCRIPT, {}, duration)


class Invisible(Condition):
    SCRIPT = '''
        function make_attack_roll(target)
            return RollModifier({advantage = true})
        end

        function recieve_attack_roll(attacker)
            return RollModifier({disadvantage = true})
        end

        function modify_visibility()
            return SetValue(0)
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("invisible", Invisible.SCRIPT, {}, duration)

class Paralyzed(Condition):
    SCRIPT = '''
        conditions = {"incapacitated"}

        function make_saving_throw(type, trigger)
            if type == "str" or type == "dex" then
                return RollModifier({auto_fail = true})
            end
            return RollModifier({})
        end

        function recieve_attack_roll(attacker)
            modifier = {advantage = true}
            if attacker.in_melee(statblock) then
                modifier["critical_threshold_modifier"] = SetValue(0)
            end
            return RollModifier(modifier)
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("paralyzed", Paralyzed.SCRIPT, {}, duration)

class Poisoned(Condition):
    SCRIPT = '''
        function make_attack_roll(target)
            return RollModifier({disadvantage = true})
        end

        function make_ability_check(type)
            return RollModifier({disadvantage = true})
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("poisoned", Poisoned.SCRIPT, {}, duration)

class Prone(Condition):
    SCRIPT = '''
        prone_get_up = {
            use_time = UseTime("action"),
            function run()
                statblock.remove_condition("prone")
            end
        }

        function on_remove()
            statblock.expend_speed(SpeedModifier({walk = MultiplyValue(0.5), fly = SetValue(0), swim = SetValue(0), climb = SetValue(0), burrow = SetValue(0)}))
        end

        function modify_speed()
            return SpeedModifier({walk = MultiplyValue(0.5), fly = SetValue(0), swim = SetValue(0), climb = SetValue(0), burrow = SetValue(0), hover = false})
        end

        function make_attack_roll(target)
            return RollModifier({disadvantage = true})
        end

        function recieve_attack_roll(attacker)
            if attacker.in_melee(statblock) then
                return RollModifier({advantage = true})
            end
            return RollModifier({disadvantage = true})
        end

        function get_abilities()
            return {"prone_get_up"}
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("prone", Prone.SCRIPT, {}, duration)

class Restrained(Condition):
    SCRIPT = '''
            function move(old_pos, new_pos)
                return false
            end

            function make_attack_roll(target)
                return RollModifier({disadvantage = true})
            end

            function recieve_attack_roll(attacker)
                return RollModifier({advantage = true})
            end

            function make_saving_throw(type)
                if type == "dex" then
                    return RollModifier({disadvantage = true})
                end
                return RollModifier({})
            end
        '''
    
    def __init__(self, duration = -1):
        super().__init__("restrained", Restrained.SCRIPT, {}, duration)

class Stunned(Condition):
    SCRIPT = '''
        conditions = {"incapacitated"}

        function make_saving_throw(type)
            if type == "str" or type == "dex" then
                return RollModifier({auto_fail = true})
            end
            return RollModifier({})
        end

        function recieve_attack_roll(attacker)
            return RollModifier({advantage = true})
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("stunned", Stunned.SCRIPT, {}, duration)

class Unconscious(Condition):
    SCRIPT = '''
        conditions = {"incapacitated", "prone"}

        function on_apply()
            -- TODO: Drop what the statblock is holding on the ground.
        end

        function make_saving_throw(type)
            if type == "str" or type == "dex" then
                return RollModifier({auto_fail = true})
            end
            return RollModifier({})
        end

        function recieve_attack_roll(attacker)
            modifier = {advantage = true}
            if attacker.in_melee(statblock) then
                modifier["critical_threshold_modifier"] = SetValue(0)
            end
            return RollModifier(modifier)
        end
    '''

    def __init__(self, duration = -1):
        super().__init__("unconscious", Unconscious.SCRIPT, {}, duration)