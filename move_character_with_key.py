"""Drill 09: arrow-key movement, facing, idle animation and screen bounds."""

from dataclasses import dataclass, field
from ctypes import byref
from math import hypot
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600
CELL_SIZE = 100
FRAME_COUNT = 8
ANIMATION_FPS = 10
MOVE_SPEED = 200.0
MAX_DELTA_TIME = 0.1
RESOURCE_DIR = Path(__file__).resolve().parent
ARROW_KEYS = {"left", "right", "up", "down"}
ANIMATION_ROWS = {
    ("IDLE", "right"): 300,
    ("IDLE", "left"): 200,
    ("MOVE", "right"): 100,
    ("MOVE", "left"): 0,
}


@dataclass
class Boy:
    x: float = CANVAS_WIDTH / 2
    y: float = CANVAS_HEIGHT / 2
    facing: str = "right"
    state: str = "IDLE"
    frame: int = 0
    animation_time: float = 0.0
    pressed_keys: set[str] = field(default_factory=set)

    def press(self, key):
        if key in ARROW_KEYS:
            self.pressed_keys.add(key)

    def release(self, key):
        self.pressed_keys.discard(key)

    def clear_input(self):
        self.pressed_keys.clear()

    def update(self, elapsed):
        dt = max(0.0, min(elapsed, MAX_DELTA_TIME))
        dx = int("right" in self.pressed_keys) - int("left" in self.pressed_keys)
        dy = int("up" in self.pressed_keys) - int("down" in self.pressed_keys)
        facing = "right" if dx > 0 else "left" if dx < 0 else self.facing
        state = "MOVE" if dx or dy else "IDLE"
        if (state, facing) != (self.state, self.facing):
            self.frame = 0
            self.animation_time = 0.0
        self.state, self.facing = state, facing

        length = hypot(dx, dy)
        if length:
            self.x += dx / length * MOVE_SPEED * dt
            self.y += dy / length * MOVE_SPEED * dt
        half = CELL_SIZE / 2
        self.x = max(half, min(self.x, CANVAS_WIDTH - half))
        self.y = max(half, min(self.y, CANVAS_HEIGHT - half))

        # Fractional frames preserve animation speed independently of rendering.
        self.animation_time += dt * ANIMATION_FPS
        advance = int(self.animation_time + 1e-9)
        self.frame = (self.frame + advance) % FRAME_COUNT
        self.animation_time = max(0.0, self.animation_time - advance)

    @property
    def animation_bottom(self):
        return ANIMATION_ROWS[self.state, self.facing]


def poll_events(pico):
    # pico2d.get_events() drops SDL window events, including focus loss.
    events = []
    raw = pico.SDL_Event()
    while pico.SDL_PollEvent(byref(raw)):
        event = SimpleNamespace(type=raw.type)
        if raw.type in (pico.SDL_KEYDOWN, pico.SDL_KEYUP):
            event.key = raw.key.keysym.sym
        elif raw.type == pico.SDL_WINDOWEVENT:
            event.event = raw.window.event
        events.append(event)
    return events


def handle_events(boy, events, pico):
    key_names = {
        pico.SDLK_LEFT: "left", pico.SDLK_RIGHT: "right",
        pico.SDLK_UP: "up", pico.SDLK_DOWN: "down",
    }
    for event in events:
        if event.type == pico.SDL_QUIT:
            return False
        if event.type == pico.SDL_KEYDOWN:
            if event.key == pico.SDLK_ESCAPE:
                return False
            boy.press(key_names.get(event.key))
        elif event.type == pico.SDL_KEYUP:
            boy.release(key_names.get(event.key))
        elif (event.type == pico.SDL_WINDOWEVENT
              and event.event == pico.SDL_WINDOWEVENT_FOCUS_LOST):
            boy.clear_input()
    return True


def load_resources(pico):
    images = []
    for name in ("TUK_GROUND.png", "animation_sheet.png"):
        path = RESOURCE_DIR / name
        if not path.is_file():
            raise FileNotFoundError(f"Required image is missing: {path}")
        try:
            images.append(pico.load_image(str(path)))
        except (OSError, RuntimeError) as error:
            raise RuntimeError(f"Cannot load image: {path}") from error
    return images


def draw_scene(pico, background, character, boy):
    pico.clear_canvas()
    background.draw(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2,
                    CANVAS_WIDTH, CANVAS_HEIGHT)
    character.clip_draw(boy.frame * CELL_SIZE, boy.animation_bottom,
                        CELL_SIZE, CELL_SIZE, boy.x, boy.y)


def main():
    try:
        import pico2d as pico
    except ImportError:
        print("Install dependencies first: python -m pip install -r requirements.txt")
        return 1
    background = character = None
    pico.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        background, character = load_resources(pico)
        boy = Boy()
        previous_time = perf_counter()
        while handle_events(boy, poll_events(pico), pico):
            current_time = perf_counter()
            boy.update(current_time - previous_time)
            previous_time = current_time
            draw_scene(pico, background, character, boy)
            pico.update_canvas()
            pico.delay(0.01)
    except (OSError, RuntimeError) as error:
        print(f"DRILL 09: {error}")
        return 1
    finally:
        # Destroy textures before destroying their SDL renderer.
        background = character = None
        pico.close_canvas()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
