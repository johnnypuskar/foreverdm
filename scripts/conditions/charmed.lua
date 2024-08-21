charmer = nil

function attack_roll(target)
    if target == charmer then
        return false
    end
    return {"advantage": false, "disadvantage": false, "bonus": 0}
end

function saving_throw_give(type, target)
    if target == charmer then
        return false
    end
    return {"advantage": false, "disadvantage": false, "bonus": 0}
end

function ability_check_rec(type, source)
    if type == "cha" and source == charmer then
        return {"advantage": true, "disadvantage": false, "bonus": 0}
    end
    return {"advantage": false, "disadvantage": false, "bonus": 0}
end