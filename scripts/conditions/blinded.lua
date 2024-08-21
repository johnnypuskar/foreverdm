function attack_roll(target)
    return {"advantage": false, "disadvantage": true, "bonus": 0}
end

function attacked(attacker)
    return {"advantage": true, "disadvantage": false, "bonus": 0}
end

function check_perception()
    return false
end