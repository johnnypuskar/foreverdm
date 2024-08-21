function run()
    if not statblock:has_action() then
        return false, "No actions available."
    end

    statblock:add_temp_movement(statblock.base_speed)
    statblock:use_action()
    return true, "Dashed."
end