import unittest
from unittest.mock import MagicMock, patch
from src.stats.handlers.effect_handler import EffectHandler

class TestEffectHandler(unittest.TestCase):
    STATBLOCK = None
    
    @patch("src.stats.statblock.Statblock")
    def setUp(self, statblock):
        self.STATBLOCK = statblock
    
    def test_add_effect(self):
        statblock = self.STATBLOCK
        effect = MagicMock(name = "test_effect")

        EffectHandler(statblock).add_effect(effect, 1)
        statblock._effects.add.assert_called_with(effect, 1, statblock)
    
    def test_remove_effect(self):
        statblock = self.STATBLOCK
        
        EffectHandler(statblock).remove_effect("test_effect")
        statblock._effects.remove.assert_called_with("test_effect")
        