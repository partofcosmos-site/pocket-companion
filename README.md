# Pocket Companion 🎮

![Pocket Companion Hardware Preview](assets/pocket_companion_preview.jpg)

A low-friction, pocket-sized (approx. 45 mm × 35 mm) handheld device combining a virtual pet, a quick reflex micro-game, and a distraction-free study timer.

Built for beginners — runs on **CircuitPython** with **zero C++ required**.

---

## 🛠️ Hardware Specifications

| Subsystem | Specification | Notes |
| :--- | :--- | :--- |
| **Microcontroller** | Waveshare RP2040-Zero | Dual ARM Cortex-M0+ @ 133 MHz, 2MB Flash, USB-C native |
| **Display** | 0.96-inch Monochrome I2C OLED (SSD1306) | 128×64 resolution, 4-pin interface (VCC, GND, SDA, SCL) |
| **User Inputs** | 3× 6×6 mm tactile momentary buttons | Left (GPIO 2), Action/Select (GPIO 3), Right (GPIO 4) |
| **Audio** | 1× 3.3V/5V passive piezo buzzer | PWM square waves on GPIO 5 for retro 8-bit sounds |
| **Power Storage** | 3.7V 350–400 mAh LiPo battery | 4–6 hours active battery life |
| **Power Management**| TP4056 Type-C Charger Module | DW01 protection + USB-C recharging |
| **Power Switch** | Sub-miniature SPDT slide switch | Physical disconnect to prevent standby battery drain |
| **Enclosure** | Altoids / Mint Tin or 2-plate acrylic | Pocket-friendly form factor |

---

## 💰 Parts List & Budget (~$18 / ~₹1,500)

Fits well within a low-cost $30 budget tier:

| Component | Quantity | Est. Price (USD) | Est. Price (INR) |
| :--- | :--- | :--- | :--- |
| Waveshare RP2040-Zero | 1 | $4.20 | ₹350 |
| 0.96" SSD1306 I2C OLED Display | 1 | $2.20 | ₹180 |
| 3.7V 400 mAh LiPo Battery (502535) | 1 | $3.00 | ₹250 |
| TP4056 Type-C Battery Charger | 1 | $0.50 | ₹40 |
| 6×6 mm Tactile Buttons (Pack) | 1 | $0.40 | ₹30 |
| Mini SPDT Slide Switch | 1 | $0.20 | ₹15 |
| Mini Passive Piezo Buzzer | 1 | $0.30 | ₹25 |
| Double-sided Perfboard (4×6 cm) | 1 | $0.70 | ₹60 |
| 30 AWG Silicone Jumper Wires | 1 | $1.20 | ₹100 |
| Mint Tin / Acrylic Case | 1 | $1.80 | ₹150 |
| Shipping & Buffer | — | $3.50 | ₹300 |
| **Total** | | **~$18.00** | **~₹1,500** |

---

## 🔌 Pinout & Wiring

- **OLED (SSD1306 I2C):**
  - `VCC` -> `3V3`
  - `GND` -> `GND`
  - `SDA` -> `GP0` (Pin 0)
  - `SCL` -> `GP1` (Pin 1)
- **Buttons (active low with internal pull-up):**
  - Left -> `GP2` (Pin 2) & `GND`
  - Action/Select -> `GP3` (Pin 3) & `GND`
  - Right -> `GP4` (Pin 4) & `GND`
- **Buzzer:**
  - `+` -> `GP5` (Pin 5)
  - `-` -> `GND`

---

## 🚀 Getting Started

1. **Simulate first:** Test the logic in [Wokwi RP2040 Simulator](https://wokwi.com/).
2. **Flash CircuitPython:**
   - Hold `BOOT` button on RP2040-Zero, plug into USB-C.
   - Drag & drop the CircuitPython `.uf2` file onto the drive.
3. **Install Libraries:**
   - Copy `adafruit_ssd1306.mpy` and `adafruit_framebuf.mpy` (or `displayio`) into the `lib/` folder on `CIRCUITPY`.
4. **Run Code:**
   - Copy `code.py` to the root of the `CIRCUITPY` drive.

---

## 🛠️ Hardware & PCB Fabrication

The custom 52mm × 38mm PCB files and manufacturing Gerbers are located under `/hardware`:

- **EasyEDA Schematic Source:** [`hardware/easyeda/Pocket_Companion_Schematic.json`](hardware/easyeda/Pocket_Companion_Schematic.json)
- **EasyEDA PCB Layout:** [`hardware/easyeda/Pocket_Companion_PCB.json`](hardware/easyeda/Pocket_Companion_PCB.json)
- **Manufacturing Gerbers (JLCPCB Ready):** [`hardware/gerbers/Gerber_Pocket_Companion_v1.zip`](hardware/gerbers/Gerber_Pocket_Companion_v1.zip)

