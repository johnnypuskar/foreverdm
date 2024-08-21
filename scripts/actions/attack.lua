use_cost = UseCost(1, "action")

function run(target)
    if statblock:attack_roll(target) then
        local damage = statblock:attack_damage()
        target:take_damage(damage)
        return true, "Attack hits for " .. damage .. " damage."
    else
        return false, "Attack missed."
    end
end