"""Mock CircuitPython Hardware Modules for Headless Simulation.

Provides bit-accurate simulation of:
- board (RP2040-Zero pin mapping)
- digitalio (active-low pushbuttons with internal pull-ups)
- busio (Hardware I2C master)
- pwmio (Piezo buzzer PWM tone generator)
- displayio (Display subsystem)
- adafruit_ssd1306 (128x64 monochrome OLED display)
- time (Simulated controllable virtual clock)
"""

import sys
import types
from typing import Dict, List, Optional, Tuple, Any


class MockPin:
    """Represents a microcontroller GPIO pin."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Pin({self.name})"

    def __str__(self) -> str:
        return self.name


class MockBoard(types.ModuleType):
    """Mock `board` module representing Waveshare RP2040-Zero."""

    def __init__(self):
        super().__init__("board")
        # Define RP2040 GPIO pins
        for i in range(29):
            setattr(self, f"GP{i}", MockPin(f"GP{i}"))
        self.LED = MockPin("LED")
        self.NEOPIXEL = MockPin("NEOPIXEL")


class Direction:
    INPUT = 0
    OUTPUT = 1


class Pull:
    UP = 0
    DOWN = 1


class MockDigitalInOut:
    """Mock `digitalio.DigitalInOut` representing a GPIO pin with direction/pull."""

    def __init__(self, pin: Any):
        self.pin = pin
        self.direction = Direction.INPUT
        self.pull = Pull.UP
        # Default value for active-low button with pull-up is True (not pressed)
        self.value = True
        self._deinited = False

    def press(self):
        """Simulate physical button press (active low -> False)."""
        self.value = False

    def release(self):
        """Simulate physical button release (pull-up -> True)."""
        self.value = True

    def toggle(self):
        """Toggle button state."""
        self.value = not self.value

    def deinit(self):
        self._deinited = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deinit()


class MockDigitalio(types.ModuleType):
    """Mock `digitalio` module."""

    def __init__(self):
        super().__init__("digitalio")
        self.DigitalInOut = MockDigitalInOut
        self.Direction = Direction
        self.Pull = Pull


class MockI2C:
    """Mock hardware I2C bus."""

    def __init__(self, scl: Any, sda: Any, frequency: int = 400000):
        self.scl = scl
        self.sda = sda
        self.frequency = frequency
        self._locked = False
        self._deinited = False

    def try_lock(self) -> bool:
        self._locked = True
        return True

    def unlock(self):
        self._locked = False

    def scan(self) -> List[int]:
        return [0x3C]  # Standard SSD1306 7-bit I2C address

    def deinit(self):
        self._deinited = True


class MockBusio(types.ModuleType):
    """Mock `busio` module."""

    def __init__(self):
        super().__init__("busio")
        self.I2C = MockI2C


class MockPWMOut:
    """Mock `pwmio.PWMOut` for passive piezo buzzer audio output."""

    def __init__(
        self,
        pin: Any,
        duty_cycle: int = 0,
        frequency: int = 440,
        variable_frequency: bool = True,
    ):
        self.pin = pin
        self._duty_cycle = duty_cycle
        self._frequency = frequency
        self.variable_frequency = variable_frequency
        self.tone_log: List[Tuple[int, int]] = []
        self._deinited = False

    @property
    def duty_cycle(self) -> int:
        return self._duty_cycle

    @duty_cycle.setter
    def duty_cycle(self, val: int):
        self._duty_cycle = int(val)
        if self._duty_cycle > 0 and self._frequency > 0:
            self.tone_log.append((self._frequency, self._duty_cycle))

    @property
    def frequency(self) -> int:
        return self._frequency

    @frequency.setter
    def frequency(self, val: int):
        self._frequency = int(val)

    def deinit(self):
        self._deinited = True


class MockPwmio(types.ModuleType):
    """Mock `pwmio` module."""

    def __init__(self):
        super().__init__("pwmio")
        self.PWMOut = MockPWMOut


class MockSSD1306_I2C:
    """Mock `adafruit_ssd1306.SSD1306_I2C` OLED display driver with pixel & text framebuffer."""

    def __init__(self, width: int = 128, height: int = 64, i2c: Any = None, addr: int = 0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.display_buffer = [[0] * width for _ in range(height)]
        self.drawn_texts: List[Dict[str, Any]] = []
        self.draw_commands: List[Tuple[Any, ...]] = []
        self.frames: List[List[Dict[str, Any]]] = []

    def fill(self, color: int):
        """Fill entire display with 0 (black) or 1 (white)."""
        color = 1 if color else 0
        self.draw_commands.append(("fill", color))
        self.drawn_texts.clear()
        for y in range(self.height):
            self.display_buffer[y] = [color] * self.width

    def pixel(self, x: int, y: int, color: int = 1):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.display_buffer[y][x] = 1 if color else 0
            self.draw_commands.append(("pixel", x, y, color))

    def hline(self, x: int, y: int, w: int, color: int = 1):
        self.draw_commands.append(("hline", x, y, w, color))
        c = 1 if color else 0
        if 0 <= y < self.height:
            for px in range(max(0, x), min(self.width, x + w)):
                self.display_buffer[y][px] = c

    def vline(self, x: int, y: int, h: int, color: int = 1):
        self.draw_commands.append(("vline", x, y, h, color))
        c = 1 if color else 0
        if 0 <= x < self.width:
            for py in range(max(0, y), min(self.height, y + h)):
                self.display_buffer[py][x] = c

    def line(self, x0: int, y0: int, x1: int, y1: int, color: int = 1):
        self.draw_commands.append(("line", x0, y0, x1, y1, color))

    def rect(self, x: int, y: int, w: int, h: int, color: int = 1):
        self.draw_commands.append(("rect", x, y, w, h, color))
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def fill_rect(self, x: int, y: int, w: int, h: int, color: int = 1):
        self.draw_commands.append(("fill_rect", x, y, w, h, color))
        c = 1 if color else 0
        for py in range(max(0, y), min(self.height, y + h)):
            for px in range(max(0, x), min(self.width, x + w)):
                self.display_buffer[py][px] = c

    def text(self, string: str, x: int, y: int, color: int = 1):
        entry = {"text": str(string), "x": x, "y": y, "color": color}
        self.drawn_texts.append(entry)
        self.draw_commands.append(("text", str(string), x, y, color))

    def show(self):
        """Commit framebuffer to display frame history."""
        self.frames.append(list(self.drawn_texts))
        self.draw_commands.append(("show",))

    def has_text(self, substring: str) -> bool:
        """Check if substring was rendered in the active frame."""
        return any(substring in item["text"] for item in self.drawn_texts)

    def get_text_strings(self) -> List[str]:
        """Return list of text strings currently on screen."""
        return [item["text"] for item in self.drawn_texts]


class MockAdafruitSSD1306(types.ModuleType):
    """Mock `adafruit_ssd1306` module."""

    def __init__(self):
        super().__init__("adafruit_ssd1306")
        self.SSD1306_I2C = MockSSD1306_I2C


class MockDisplayio(types.ModuleType):
    """Mock `displayio` module."""

    def __init__(self):
        super().__init__("displayio")

        class Group:
            def __init__(self, *args, **kwargs):
                self.items = []

            def append(self, item):
                self.items.append(item)

        class TileGrid:
            def __init__(self, *args, **kwargs):
                pass

        class Bitmap:
            def __init__(self, width, height, value_count=2):
                self.width = width
                self.height = height

        class Palette:
            def __init__(self, color_count=2):
                self.colors = [0] * color_count

            def __setitem__(self, index, val):
                self.colors[index] = val

        self.Group = Group
        self.TileGrid = TileGrid
        self.Bitmap = Bitmap
        self.Palette = Palette

        def release_displays():
            pass

        self.release_displays = release_displays


class SimulatedClock:
    """High-precision simulated monotonic clock and time module."""

    def __init__(self, initial_time: float = 1000.0, fast_forward: bool = True):
        self.current_time = initial_time
        self.fast_forward = fast_forward
        self.sleep_calls: List[float] = []

    def monotonic(self) -> float:
        return self.current_time

    def sleep(self, seconds: float):
        self.sleep_calls.append(seconds)
        if self.fast_forward:
            self.current_time += seconds

    def advance(self, seconds: float):
        """Manually step simulated clock by `seconds`."""
        self.current_time += seconds

    def set_time(self, t: float):
        self.current_time = t


class MockAnalogIn:
    """Mock `analogio.AnalogIn` ADC pin."""

    def __init__(self, pin: Any):
        self.pin = pin
        self._reference_voltage = 3.3
        # Default ~4.2V with 2.0x divider: 4.2 / 6.6 * 65535 = 41704
        self._value = 41704
        self._deinited = False

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, val: int):
        self._value = max(0, min(65535, int(val)))

    @property
    def reference_voltage(self) -> float:
        return self._reference_voltage

    def set_voltage(self, volts: float, divider_ratio: float = 2.0):
        """Set simulated voltage in Volts."""
        fraction = max(0.0, volts / (self._reference_voltage * divider_ratio))
        self._value = max(0, min(65535, int(fraction * 65535)))

    def deinit(self):
        self._deinited = True


class MockAnalogio(types.ModuleType):
    """Mock `analogio` module."""

    def __init__(self):
        super().__init__("analogio")
        self.AnalogIn = MockAnalogIn


_ORIGINAL_MODULES = {}


def install_mock_modules(sim_clock: Optional[SimulatedClock] = None) -> Dict[str, Any]:
    """Inject mock hardware modules into sys.modules."""
    board_mock = MockBoard()
    digitalio_mock = MockDigitalio()
    busio_mock = MockBusio()
    pwmio_mock = MockPwmio()
    analogio_mock = MockAnalogio()
    ssd1306_mock = MockAdafruitSSD1306()
    displayio_mock = MockDisplayio()

    mocks = {
        "board": board_mock,
        "digitalio": digitalio_mock,
        "busio": busio_mock,
        "pwmio": pwmio_mock,
        "analogio": analogio_mock,
        "adafruit_ssd1306": ssd1306_mock,
        "displayio": displayio_mock,
    }

    for name, mock in mocks.items():
        if name in sys.modules:
            _ORIGINAL_MODULES[name] = sys.modules[name]
        sys.modules[name] = mock

    return mocks


def uninstall_mock_modules():
    """Restore original sys.modules state."""
    for name in ["board", "digitalio", "busio", "pwmio", "analogio", "adafruit_ssd1306", "displayio"]:
        if name in _ORIGINAL_MODULES:
            sys.modules[name] = _ORIGINAL_MODULES[name]
        elif name in sys.modules:
            del sys.modules[name]
    _ORIGINAL_MODULES.clear()
