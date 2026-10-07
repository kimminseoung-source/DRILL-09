"""Run with python -m unittest -v; no display or pico2d needed."""
import math
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import drill09 as game


class MovementTests(unittest.TestCase):
    def test_initial_idle_and_animation_cycle(self):
        boy = game.Boy()
        self.assertEqual((boy.x, boy.y, boy.animation_bottom), (400, 300, 300))
        for frame in range(1, 9):
            boy.update(0.1)
            self.assertEqual(boy.frame, frame % 8)
            self.assertEqual(boy.state, "IDLE")

    def test_each_arrow_moves_correct_axis(self):
        for key, expected in {"right": (420, 300), "left": (380, 300),
                              "up": (400, 320), "down": (400, 280)}.items():
            with self.subTest(key=key):
                boy = game.Boy()
                boy.press(key)
                boy.update(0.1)
                self.assertEqual((boy.x, boy.y), expected)
                self.assertEqual(boy.state, "MOVE")

    def test_vertical_keeps_both_horizontal_facings(self):
        for horizontal in ("left", "right"):
            for vertical in ("up", "down"):
                with self.subTest(horizontal=horizontal, vertical=vertical):
                    boy = game.Boy()
                    boy.press(horizontal)
                    boy.update(0.05)
                    boy.release(horizontal)
                    boy.press(vertical)
                    boy.update(0.05)
                    self.assertEqual(boy.facing, horizontal)
                    self.assertEqual(boy.animation_bottom, 0 if horizontal == "left" else 100)

    def test_release_stops_and_selects_idle_row(self):
        for direction, row in (("left", 200), ("right", 300)):
            boy = game.Boy()
            boy.press(direction)
            boy.update(0.1)
            position = boy.x, boy.y
            boy.release(direction)
            boy.update(0.05)
            self.assertEqual((boy.x, boy.y), position)
            self.assertEqual((boy.state, boy.animation_bottom, boy.frame), ("IDLE", row, 0))

    def test_opposites_cancel_and_remaining_key_continues(self):
        for first, second, axis in (("left", "right", "x"), ("up", "down", "y")):
            boy = game.Boy()
            boy.press(first)
            boy.press(second)
            boy.update(0.1)
            self.assertEqual((boy.x, boy.y, boy.state), (400, 300, "IDLE"))
            boy.release(first)
            boy.update(0.1)
            self.assertNotEqual(getattr(boy, axis), 400 if axis == "x" else 300)
            self.assertEqual(boy.state, "MOVE")

    def test_repeated_keydown_is_idempotent(self):
        boy = game.Boy()
        boy.press("right")
        boy.press("right")
        boy.release("right")
        boy.update(0.1)
        self.assertEqual((boy.x, boy.state), (400, "IDLE"))

    def test_diagonal_speed_matches_straight_speed(self):
        boy = game.Boy()
        boy.press("right")
        boy.press("up")
        boy.update(0.1)
        self.assertAlmostEqual(math.hypot(boy.x - 400, boy.y - 300), 20)

    def test_all_corners_and_return_from_boundary(self):
        for horizontal, x in (("left", 50), ("right", 750)):
            for vertical, y in (("down", 50), ("up", 550)):
                with self.subTest(horizontal=horizontal, vertical=vertical):
                    boy = game.Boy()
                    boy.press(horizontal)
                    boy.press(vertical)
                    for _ in range(100):
                        boy.update(0.1)
                    self.assertEqual((boy.x, boy.y, boy.state), (x, y, "MOVE"))
                    boy.clear_input()
                    boy.update(0)
                    self.assertEqual(boy.state, "IDLE")
                    boy.press("right" if horizontal == "left" else "left")
                    boy.press("up" if vertical == "down" else "down")
                    boy.update(0.1)
                    self.assertTrue(50 < boy.x < 750 and 50 < boy.y < 550)

    def test_time_is_clamped(self):
        boy = game.Boy()
        boy.press("right")
        boy.update(10)
        self.assertEqual(boy.x, 420)
        boy.update(-1)
        self.assertEqual(boy.x, 420)

    def test_frame_rate_independence(self):
        slow, fast = game.Boy(), game.Boy()
        for boy in (slow, fast):
            boy.press("right")
        for _ in range(10):
            slow.update(0.08)
        for _ in range(100):
            fast.update(0.008)
        self.assertAlmostEqual(slow.x, fast.x)
        self.assertEqual(slow.frame, fast.frame)

    def test_state_and_facing_changes_reset_frame(self):
        boy = game.Boy(frame=6, animation_time=0.8)
        boy.press("left")
        boy.update(0.01)
        self.assertEqual((boy.frame, boy.facing, boy.state), (0, "left", "MOVE"))
        boy.release("left")
        boy.press("right")
        boy.update(0.01)
        self.assertEqual((boy.frame, boy.facing), (0, "right"))

    def test_focus_loss_escape_and_quit(self):
        pico = SimpleNamespace(SDL_QUIT=1, SDL_KEYDOWN=2, SDL_KEYUP=3,
                               SDL_WINDOWEVENT=4, SDL_WINDOWEVENT_FOCUS_LOST=5,
                               SDLK_LEFT=10, SDLK_RIGHT=11, SDLK_UP=12,
                               SDLK_DOWN=13, SDLK_ESCAPE=14)
        boy = game.Boy()
        game.handle_events(boy, [SimpleNamespace(type=2, key=10)], pico)
        boy.update(0.1)
        position = boy.x, boy.y
        game.handle_events(boy, [SimpleNamespace(type=4, event=5)], pico)
        boy.update(0.1)
        self.assertEqual((boy.x, boy.y, boy.state), (*position, "IDLE"))
        self.assertFalse(game.handle_events(boy, [SimpleNamespace(type=2, key=14)], pico))
        self.assertFalse(game.handle_events(boy, [SimpleNamespace(type=1)], pico))

    def test_missing_resource_reports_filename(self):
        with patch.object(game, "RESOURCE_DIR", game.RESOURCE_DIR / "missing"):
            with self.assertRaisesRegex(FileNotFoundError, "TUK_GROUND.png"):
                game.load_resources(SimpleNamespace())


if __name__ == "__main__":
    unittest.main()
