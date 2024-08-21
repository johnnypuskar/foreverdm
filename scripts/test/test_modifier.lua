function modify(self_damage)
    statblock:take_damage(self_damage)
    return true, "Took " .. self_damage .. " self damage."
end