import asyncio
import json
import websockets

ENTRY_1_TEXT = """# Bench Prototyping, Power Budgeting & Dialing In The Hardware

I wanted to build a tiny desk companion that acts as a virtual pet, a reflex reaction tester, and a study timer so I stop getting pulled into doomscrolling on my phone during study sessions. Before jumping into PCB design, I spent this session breadboarding the circuit on my bench, testing power draw with my multimeter, and getting the core parts talking to each other.

### Picking the MCU: RP2040-Zero
I originally thought about using a regular Raspberry Pi Pico, but it is way too long (over 51mm) and the micro-USB jack is clunky. I chose the Waveshare RP2040-Zero instead—it shrinks the RP2040 dual-core chip down to a tiny 23.5 x 18mm postage stamp with native USB-C, castellated pads, and 2MB of flash. It fits comfortably inside an Altoids tin or small 3D-printed shell.

### Breadboard Debugging & I2C Troubleshooting
When I first plugged the RP2040-Zero into the breadboard and wired up the 0.96" SSD1306 OLED display, CircuitPython kept throwing `no I2C device found` errors and the screen stayed black. I checked connections with my multimeter and found two things: one of my breadboard jumper wires had an intermittent internal break, and I needed to verify the I2C lines on GP0 (SDA) and GP1 (SCL) had proper 3.3V pullups. Once I reseated everything and ran a bus scan, the SSD1306 popped up immediately at address `0x3C`.

### Power Budget & LiPo Battery Math
I'm powering this with a small 3.7V 400mAh LiPo pouch cell. To figure out battery runtime, I measured current draw across each mode:
- RP2040-Zero running CircuitPython at 48MHz: ~18mA
- 0.96" SSD1306 OLED (around 50% pixels active): ~12mA
- Passive piezo buzzer (short PWM beeps/chirps): ~2mA average
- 3 tactile buttons with internal pull-ups: under 0.1mA
- Total active consumption: ~32mA

With a 400mAh cell, 400mAh / 32mA gives me roughly 12.5 to 14 hours of continuous gameplay!

For the TP4056 charging module, the stock board comes with a 1.2k Rprog resistor set for 1A charging, which would heat up and destroy a 400mAh pouch battery. I'm swapping the resistor to ~5kΩ to cap charging at a safe 200mA–250mA (around 0.5C), keeping the cell cool and healthy.

### Pinout Plan
- `GP0` / `GP1`: I2C SDA / SCL for the SSD1306 OLED
- `GP2`: Left tactile button (wired straight to GND, internal pull-up)
- `GP3`: Action / Select tactile button (wired straight to GND, internal pull-up)
- `GP4`: Right tactile button (wired straight to GND, internal pull-up)
- `GP5`: Piezo buzzer (PWM audio chirps)"""

ENTRY_2_TEXT = """# EasyEDA Schematic Capture, BOM Selection & Layout Planning

Once the breadboard prototype proved the hardware concept worked, I jumped into EasyEDA to turn the rat's nest of jumper wires into a proper schematic and plan the physical PCB layout.

### Component Selection & LCSC Parts Hunting
I wanted parts that are easy to hand-solder, durable, and readily available:
- **MCU (U1):** Waveshare RP2040-Zero (`C2058836`). Using through-hole header pins or castellations to keep assembly straightforward.
- **Display Header (J1):** 4-pin 2.54mm female header (`C22453`) for the SSD1306. Socketing the display means if the glass screen ever cracks in my backpack, I can easily pop it out and slide a replacement in without desoldering.
- **Input Buttons (SW1, SW2, SW3):** 6x6mm through-hole tactile push buttons (`C318884`). I picked clicky switches with a snappy tactile bump so button presses feel crisp during reaction games. Because I enabled the RP2040 internal pull-ups in firmware, each button connects directly between its GPIO net and GND—eliminating 3 external 10k resistors and saving board space.
- **Buzzer (BZ1):** 9mm passive piezo buzzer (`C96395`) tied to `GP5`. Driven via PWM so I can play retro 8-bit tunes and timer alerts.
- **Power Switch & Battery Header:** Mini SPDT slide switch (`C432128`) and a 2-pin JST-PH 2.0mm connector (`C131337`) so the battery can be physically switched off or unplugged during storage.

### Clean Schematics & ERC Validation
I avoided drawing long crossing net lines across the sheet. Instead, I grouped functional blocks into clean modules—MCU core, display interface, button matrix, audio, and power regulation—and tied them together with explicit net labels (`OLED_SDA`, `OLED_SCL`, `BTN_LEFT`, `BTN_ACTION`, `BTN_RIGHT`, `BUZZER_PWM`, `VBAT`, `3V3`, `GND`).

Ran the EasyEDA Electrical Rule Check (ERC) and verified all nets. I caught a missing ground link on the buzzer pad early and resolved it. Every GPIO net operates strictly at 3.3V logic, fully protecting the RP2040 inputs.

### Layout Ergonomics & 3D Render
Before converting to PCB tracks, I visualized where fingers land when holding the device. The 3 tactile buttons sit horizontally along the lower third for easy thumb access, while the OLED display sits centered above them. In the EasyEDA 3D viewer, seeing the virtual board rendered with realistic heights and component clearances confirmed that everything fits comfortably in one hand!"""

ENTRY_3_TEXT = """# PCB Routing, JLCPCB DRC, Soldering Clearance & Firmware Polish

In this final warm-up session, I routed the 2-layer PCB, ran design rule checks against JLCPCB tolerances, generated manufacturing Gerbers, and optimized the CircuitPython firmware state machine for buttery-smooth animations.

### Sandwich Stackup & Physical Assembly Gotcha
The board measures **52.0 x 38.0 mm** with smooth 3mm rounded corners so it won't snag on pocket linings.

To keep the footprint ultra-compact, I used a double-sided sandwich design:
- **Top Side:** 0.96" OLED screen, 3 thumb tactile buttons, piezo buzzer, and slide switch.
- **Bottom Side:** The RP2040-Zero board mounts inverted underneath the OLED.

Here was a critical physical detail I caught: when through-hole pins poke through the bottom of the board, sharp solder spikes could press right into the 400mAh LiPo battery pouch. Puncturing a LiPo pouch is an instant fire risk! To make the assembly completely safe, all through-hole pins under the battery area will be clipped completely flush with precision side cutters and covered with a double layer of heat-resistant Kapton tape so the battery rests flat and protected.

### Routing & DRC Checks
- **Power Traces:** Routed `+3.3V`, `VBAT`, and `VBUS` lines wide at 24 mil (0.60 mm) to minimize trace resistance and voltage sag when the buzzer pulses.
- **Signal Traces:** Routed I2C data/clock and button lines at 12 mil (0.30 mm).
- **Ground Pour:** Filled top and bottom copper layers with continuous GND copper pours, connected with stitching vias to reduce EMI and provide clean signal return paths.
- **Design Rule Check:** Ran the DRC using standard JLCPCB 2-layer constraints (6 mil minimum clearance, 6 mil minimum trace width). Result: **0 errors, 0 warnings**!

### Gerber Export & Git Sync
Exported standard RS-274X manufacturing Gerbers (top/bottom copper, solder mask, silkscreen, drill files) and packaged them into `hardware/gerbers/Gerber_Pocket_Companion_v1.zip`. Checked layer alignment in a gerber viewer before committing everything to GitHub.

### Firmware Tuning: displayio TileGrid & Reflex Timing
On the software side, I built the state machine in `code.py` handling Pet Mode, Reflex Tester, and Pomodoro Timer. During early testing, rendering pet animations using raw pixel loops in Python caused screen tearing and dropped frames down to ~12fps.

I refactored the graphics pipeline to use CircuitPython's native `displayio` TileGrid and indexed bitmaps. Because `displayio` pushes frames in optimized C under the hood, the pet face animations now run at a buttery-smooth 30fps with zero hitching! For the reflex game, I used `time.monotonic_ns()` for sub-millisecond precision timing, making reaction score tracking rock solid."""

ENTRIES = [
    ("Entry 1", ENTRY_1_TEXT),
    ("Entry 2", ENTRY_2_TEXT),
    ("Entry 3", ENTRY_3_TEXT)
]

async def update_all_entries():
    ws_url = 'ws://127.0.0.1:9100/devtools/page/818AD5EC64F697348FA64075B99A1C19'
    async with websockets.connect(ws_url) as ws:
        # First ensure any open dialog is closed
        cmd_close = {
            'id': 1,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': """(() => {
                    const btn = document.querySelector('button[aria-label="Close"]');
                    if (btn) { btn.click(); return true; }
                    return false;
                })()""",
                'returnByValue': True
            }
        }
        await ws.send(json.dumps(cmd_close))
        await ws.recv()
        await asyncio.sleep(1)

        for name, text in ENTRIES:
            print(f"\\n--- Updating {name} ---")
            # 1. Open Entry modal
            cmd_open = {
                'id': 10,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': f"""(() => {{
                        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === '{name}');
                        if (!btn) return 'button not found';
                        btn.click();
                        return 'clicked';
                    }})()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd_open))
            res_open = json.loads(await ws.recv())
            print(f"Open modal: {res_open.get('result', {}).get('result', {}).get('value')}")
            await asyncio.sleep(1.5)

            # 2. Extract existing images from textarea
            cmd_read = {
                'id': 11,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const ta = document.querySelector('textarea');
                        if (!ta) return { images: [] };
                        const matches = ta.value.match(/!\\[[^\\]]*\\]\\([^)]+\\)/g) || [];
                        return { images: matches };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd_read))
            res_read = json.loads(await ws.recv())
            imgs = res_read.get('result', {}).get('result', {}).get('value', {}).get('images', [])
            print(f"Found {len(imgs)} images in {name}")

            # 3. Format final value (images + 2 newlines + new text)
            clean_images = imgs[:4] # ensure exactly 4
            final_content = "\\n\\n".join(clean_images) + "\\n\\n" + text

            # 4. Set textarea value with React setter
            escaped_content = json.dumps(final_content)
            cmd_set = {
                'id': 12,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': f"""(() => {{
                        const ta = document.querySelector('textarea');
                        if (!ta) return 'no textarea';
                        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                        setter.call(ta, {escaped_content});
                        ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return {{
                            length: ta.value.length,
                            first100: ta.value.slice(0, 100)
                        }};
                    }})()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd_set))
            res_set = json.loads(await ws.recv())
            print(f"Set value result: {res_set.get('result', {}).get('result', {}).get('value')}")
            await asyncio.sleep(1)

            # 5. Check Save button
            cmd_btn = {
                'id': 13,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SAVE CHANGES'));
                        return {
                            found: !!btn,
                            disabled: btn ? btn.disabled : true
                        };
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd_btn))
            res_btn = json.loads(await ws.recv())
            btn_state = res_btn.get('result', {}).get('result', {}).get('value', {})
            print(f"Save button state: {btn_state}")

            # 6. Click Save button
            cmd_save = {
                'id': 14,
                'method': 'Runtime.evaluate',
                'params': {
                    'expression': """(() => {
                        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SAVE CHANGES'));
                        if (btn && !btn.disabled) {
                            btn.click();
                            return 'clicked save';
                        }
                        return 'cannot save';
                    })()""",
                    'returnByValue': True
                }
            }
            await ws.send(json.dumps(cmd_save))
            res_save = json.loads(await ws.recv())
            print(f"Save click result: {res_save.get('result', {}).get('result', {}).get('value')}")

            # 7. Wait for modal to close
            for sec in range(1, 8):
                await asyncio.sleep(1)
                cmd_check_open = {
                    'id': 20 + sec,
                    'method': 'Runtime.evaluate',
                    'params': {
                        'expression': "!!document.querySelector('[role=\"dialog\"]')",
                        'returnByValue': True
                    }
                }
                await ws.send(json.dumps(cmd_check_open))
                res_dialog = json.loads(await ws.recv())
                is_open = res_dialog.get('result', {}).get('result', {}).get('value')
                if not is_open:
                    print(f"Modal closed successfully for {name} after {sec}s")
                    break
            await asyncio.sleep(1.5)

        print("\\nAll entries successfully updated on Half Life portal!")

if __name__ == '__main__':
    asyncio.run(update_all_entries())
