import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

from motion import clamp_zoom, orbit_position, step_angle
from planet_data import FACTS, IDS, PLANETS
from storage import clean_note, load_notes, save_notes


class TestSolarSystemLogic(unittest.TestCase):
    def test_planets_count_and_facts(self):
        self.assertEqual(len(PLANETS), 8)
        self.assertEqual(len(FACTS), 8)
        self.assertEqual(len(IDS), 8)

    def test_unique_ids(self):
        self.assertEqual(len(set(IDS)), 8)

    def test_step_angle_moving(self):
        self.assertAlmostEqual(step_angle(10.0, 20.0, 0.5, paused=False), 20.0)

    def test_step_angle_wrap(self):
        self.assertAlmostEqual(step_angle(350.0, 20.0, 1.0, paused=False), 10.0)

    def test_step_angle_paused(self):
        self.assertAlmostEqual(step_angle(45.0, 20.0, 1.0, paused=True), 45.0)

    def test_orbit_position(self):
        x, y, z = orbit_position(10.0, 0.0)
        self.assertAlmostEqual(x, 10.0)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(z, 0.0)

    def test_clamp_zoom(self):
        self.assertAlmostEqual(clamp_zoom(0.1), 0.6)
        self.assertAlmostEqual(clamp_zoom(5.0), 2.4)
        self.assertAlmostEqual(clamp_zoom(1.5), 1.5)

    def test_clean_note(self):
        self.assertEqual(clean_note('  Привет |   мир \n '), 'Привет мир')

    def test_save_and_load_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'notes.txt'
            save_notes({'earth': 'Голубая | планета', 'mars': '  Красная  '}, path)
            loaded = load_notes(path)
            self.assertEqual(loaded, {'earth': 'Голубая планета', 'mars': 'Красная'})


if __name__ == '__main__':
    unittest.main()
