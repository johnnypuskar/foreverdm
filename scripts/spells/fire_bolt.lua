spell_level = 0
spell_school = "evocation"
use_cost = UseTime("action")
spell_range = 120
spell_components = {V = true, S = true}
spell_duration = nil
spell_concentration = false

local function calculate_damage(level)
    local dice = 1
    if level >= 17 then
        dice = 4
    elseif level >= 11 then
        dice = 3
    elseif level >= 5 then
        dice = 2
    end
    return dice
end

function run(target)
    if not target then
        return false, "No target specified"
    end
    
    if statblock:distance_to(target) > spell_range then
        return false, "Target is out of range"
    end
    
    local hit = statblock:spell_attack_roll(target)
    if hit then
        local damage_dice = calculate_damage(statblock.level)
        local damage = 0
        for i = 1, damage_dice do
            damage = damage + math.random(1, 10)
        end
        
        target:take_damage(damage, "fire")
        
        return true, string.format("Fire Bolt hits for %d fire damage", damage)
    else
        return true, "Fire Bolt misses"
    end
end