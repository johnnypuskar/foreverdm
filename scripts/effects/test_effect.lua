subeffects = {
    "test_subeffect": {
        "get_resistances" = function()
            return ["radiant"]
        end
    }
}

function on_start_turn()

end

function on_end_turn()
    
end

function make_attack_roll(target)

end

function recieve_attack_roll(attacker)
    statblock:add_effect("test_subeffect")
end