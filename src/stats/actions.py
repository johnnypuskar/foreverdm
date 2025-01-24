from src.stats.abilities import Ability

class Hide(Ability):
    SCRIPT = '''
        use_time = UseTime("action")
        
        hidden = {
            is_noticed = function(perception)
                if perception >= stealth_roll then
                    RemoveEffect()
                    return true
                end
                return false
            end
        }

        function validate(targets)
            if statblock.has_effect("hidden") then
                return false, "Already hidden."
            end
            for i, target in ipairs(targets) do
                if target.sight_to(statblock) > 0 then
                    return false, "Cannot be visible when attempting to hide."
                end
            end
            return true, nil
        end

        function run(targets)
            roll_result = statblock.get_skill_roll("stealth")
            statblock.add_effect("hidden", Duration("indefinite"), {stealth_roll = roll_result})
            return true, "Successfully hid."
        end
    '''
    
    def __init__(self):
        super().__init__("hide", Hide.SCRIPT)