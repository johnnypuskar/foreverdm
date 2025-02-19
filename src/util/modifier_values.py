from __future__ import annotations

class ModifierValues:
    def __init__(self, modifier_tables: list):
        self._add_sum = 0
        self._mult_total = 1
        self._set_min = None
        self._set_max = None

        """Aggregates all given modifier tables (from AddValue, MultiplyValue, and SetValue script functions) into a single set of values per operation, two for setting in case of minimum or maximum preference"""
        for modifer in modifier_tables:
            if modifer["operation"] == "add":
                self._add_sum += modifer["value"]
            elif modifer["operation"] == "multiply":
                self._mult_total *= modifer["value"]
            elif modifer["operation"] == "set":
                if self._set_min is None:
                    self._set_min = modifer["value"]
                    self._set_max = modifer["value"]
                elif modifer["value"] < self._set_min:
                    self._set_min = modifer["value"]
                elif modifer["value"] > self._set_max:
                    self._set_max = modifer["value"]
    
    def process_add(self, base):
        """Returns the given base plus the sum of all add values"""
        return base + self._add_sum
    
    def process_mult(self, base):
        """Returns the given base times all of the multiply values"""
        return int(base * self._mult_total)
    
    def process_set_min(self, base):
        """Returns the smallest set value minimum if it exists, otherwise returns the base"""
        if self._set_min is not None:
            return self._set_min
        return base
    
    def process_set_max(self, base):
        """Returns the largest set value minimum if it exists, otherwise returns the base"""
        if self._set_max is not None:
            return self._set_max
        return base
    
    def merge(self, other: ModifierValues):
        """Merges the values of another ModifierValues object into this one"""
        self._add_sum += other._add_sum
        self._mult_total *= other._mult_total
        if self._set_min is None:
            self._set_min = other._set_min
            self._set_max = other._set_max
        elif other._set_min is not None:
            self._set_min = min(self._set_min, other._set_min)
            self._set_max = max(self._set_max, other._set_max)
                    
class ModifierRolls:
    def __init__(self, modifier_tables: list = []):
        self.advantage = False
        self.disadvantage = False
        self.bonus = 0
        self.auto_succeed = False
        self.auto_fail = False
        
        critical_threshold_modifiers = []

        for modifier in modifier_tables:
            if not self.advantage and modifier.get("advantage", False):
                self.advantage = True
            if not self.disadvantage and modifier.get("disadvantage", False):
                self.disadvantage = True
            self.bonus += modifier.get("bonus", 0)
            if not self.auto_succeed and modifier.get("auto_succeed", False):
                self.auto_succeed = True
            if not self.auto_fail and modifier.get("auto_fail", False):
                self.auto_fail = True
            if "critical_threshold_modifier" in modifier:
                critical_threshold_modifiers.append(modifier["critical_threshold_modifier"])
        
        self._crit_modifier = ModifierValues(critical_threshold_modifiers)
    
    def process_crit_threshold_add(self, base):
        """Returns the given base plus the sum of all add values for the critical threshold"""
        return self._crit_modifier.process_add(base)
    
    def process_crit_threshold_mult(self, base):
        """Returns the given base times all of the multiply values for the critical threshold"""
        return self._crit_modifier.process_mult(base)
    
    def process_crit_threshold_set_min(self, base):
        """Returns the smallest set value minimum for the critical threshold if it exists, otherwise returns the base"""
        return self._crit_modifier.process_set_min(base)
    
    def process_crit_threshold_set_max(self, base):
        """Returns the largest set value minimum for the critical threshold if it exists, otherwise returns the base"""
        return self._crit_modifier.process_set_max(base)
    
    def merge(self, other: ModifierRolls):
        """Merges the values of another ModifierRolls object into this one"""
        self.advantage = self.advantage or other.advantage
        self.disadvantage = self.disadvantage or other.disadvantage
        self.bonus += other.bonus
        self.auto_succeed = self.auto_succeed or other.auto_succeed
        self.auto_fail = self.auto_fail or other.auto_fail
        self._crit_modifier.merge(other._crit_modifier)

class ModifierSpeed:
    def __init__(self, modifier_tables: list = []):
        self.walk = ModifierValues([modifier for modifier in modifier_tables if modifier["type"] == "walk"])
        self.fly = ModifierValues([modifier for modifier in modifier_tables if modifier["type"] == "fly"])
        self.swim = ModifierValues([modifier for modifier in modifier_tables if modifier["type"] == "swim"])
        self.climb = ModifierValues([modifier for modifier in modifier_tables if modifier["type"] == "climb"])
        self.burrow = ModifierValues([modifier for modifier in modifier_tables if modifier["type"] == "burrow"])
        
        hover_list = [modifier for modifier in modifier_tables if modifier["type"] == "hover"]
        self.hover = None if len(hover_list) == 0 else all(hover_list)
    
    def _sub_process(self, base, modifier):
        base = modifier.process_mult(base)
        base = modifier.process_add(base)
        base = modifier.process_set_min(base)
        return base

    def process_walk(self, base):
        return self._sub_process(base, self.walk)
    
    def process_fly(self, base):
        return self._sub_process(base, self.fly)
    
    def process_swim(self, base):
        return self._sub_process(base, self.swim)
    
    def process_climb(self, base):
        return self._sub_process(base, self.climb)
    
    def process_burrow(self, base):
        return self._sub_process(base, self.burrow)
    
    def process_hover(self, base):
        return base if self.hover is None else self.hover