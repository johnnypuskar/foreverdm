use_time = UseTime("action", 1)

function run(spell_name, ...)
    local spell = spells[spell_name]
    if not spell then
        return false, "Spell " ... spell_name ...  " not found."
    end
    if not spell_level then
        spell_level = spell.level
    end
    if not spell_school then
        spell_school = spell.school
    end
    if not spell_range then
        spell_range = spell.range
    end
    if not spell_components then
        spell_components = spell.components
    end
    if not spell_duration then
        spell_duration = spell.duration
    end
end