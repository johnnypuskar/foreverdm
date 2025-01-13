from src.stats.effects import Effect


class Condition(Effect):
    def __init__(self, name, script, globals = {}, duration = -1):
        super().__init__(name, script, globals, duration)

class Blinded(Condition):
    SCRIPT = '''
        function make_attack_roll(target)
            return RollModifier({disadvantage = true})
        end

        function recieve_attack_roll(attacker)
            return RollModifier({advantage = true})
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

        function ability_check_impose(type, trigger)
            if type == "cha" and trigger == charmer then
                return RollModifier({advantage = true})
            end
            return RollModifier({})
        end
    '''

    def __init__(self, charmer, duration = -1):
        super().__init__("charmed", Charmed.SCRIPT, {"charmer": charmer}, duration)

