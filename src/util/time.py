from enum import Enum

class UseTime():
    class Special(Enum):
        Action = -1
        Bonus_Action = -2
        Reaction = -3
        Free_Action = -4

    def __init__(self, minutes):
        if minutes < -4 or minutes == 0:
            raise ValueError("Invalid time value.")
        self._minutes = minutes
    
    @staticmethod
    def from_table(time_table):
        if time_table["unit"] == "undefined":
            return UseTime(UseTime.Special.Free_Action.value)
        if time_table["unit"] in ["action", "bonus_action", "reaction"]:
            if time_table["unit"] == "action":
                return UseTime(UseTime.Special.Action.value)
            if time_table["unit"] == "bonus_action":
                return UseTime(UseTime.Special.Bonus_Action.value)
            if time_table["unit"] == "reaction":
                return UseTime(UseTime.Special.Reaction.value)
        return UseTime(time_table["value"] * 60) if time_table["unit"] == "hour" else UseTime(time_table["value"])

    @property
    def minutes(self):
        return self._minutes
    
    @property
    def is_special(self):
        return self._minutes < 0
    
    @property
    def is_action(self):
        return self._minutes == UseTime.Special.Action.value
    
    @property
    def is_bonus_action(self):
        return self._minutes == UseTime.Special.Bonus_Action.value
    
    @property
    def is_reaction(self):
        return self._minutes == UseTime.Special.Reaction.value
    
    @property
    def is_free_action(self):
        return self._minutes == UseTime.Special.Free_Action.value

    def __repr__(self) -> str:
        return f"UseTime({self.Special(self._minutes).name.lower()})" if not self.is_special else f"UseTime({self._minutes} minutes)"
    
    def __str__(self) -> str:
        if self.is_special:
            return self.Special(self._minutes).name.replace("_", " ").lower()
        else:
            return f"{self._minutes} minute" + ("s" if self._minutes > 1 else "")

class Timer():
    def __init__(self, time = 0):
        self._time = int(time)
    
    @staticmethod
    def from_table(time_table):
        if time_table["unit"] not in ["round", "minute", "hour"]:
            raise ValueError("Invalid time unit.")
        value = time_table["value"]
        if time_table["unit"] == "minute":
            value *= 10
        if time_table["unit"] == "hour":
            value *= 600
        return Timer(value)

    @property
    def timestamp(self):
        return self._time

    def add_round(self, rounds = 1):
        self._time += rounds

    def add_minute(self, minutes = 1):
        self.add_round(minutes * 10)
    
    def add_hour(self, hours = 1):
        self.add_minute(hours * 60)
    
    def add_day(self, days = 1):
        self.add_hour(days * 24)

    @staticmethod
    def in_minutes(minutes):
        return minutes * 10
    
    @staticmethod
    def in_hours(hours):
        return hours * 600
    
    @staticmethod
    def in_days(days):
        return days * 14400