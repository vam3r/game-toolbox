import argparse
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "flooders"))

import blooket_flooder
import kahoot_flooder


class FlooderTests(unittest.TestCase):
    def test_answer_names_and_indexes(self):
        for module in (blooket_flooder, kahoot_flooder):
            self.assertEqual(module.parse_answer_choice("Triangle"), 0)
            self.assertEqual(module.parse_answer_choice("diamond"), 1)
            self.assertEqual(module.parse_answer_choice("Circle"), 2)
            self.assertEqual(module.parse_answer_choice("3"), 3)

    def test_invalid_answer_choice(self):
        for module in (blooket_flooder, kahoot_flooder):
            with self.assertRaises(argparse.ArgumentTypeError):
                module.parse_answer_choice("Star")
            with self.assertRaises(argparse.ArgumentTypeError):
                module.parse_answer_choice("4")

    def test_generated_names(self):
        names = list(kahoot_flooder.bot_names("Bot_", 3))
        self.assertEqual(names, ["Bot_1", "Bot_2", "Bot_3"])


if __name__ == "__main__":
    unittest.main()
