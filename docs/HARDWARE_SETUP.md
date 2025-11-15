# Hardware Setup

This guide walks through the physical build of the weather display: stacking the Pi Zero 2 W with the Witty Pi 4 L3V7 power board, wiring the Waveshare 7.3" e-Paper HAT (E), and making the limited pass-through pins work for this project.

## 1. Bill of materials

| Item | Notes |
| --- | --- |
| Raspberry Pi Zero 2 W | 1 GHz quad-core Cortex-A53, 512 MB RAM, built-in Wi-Fi/BLE. |
| Witty Pi 4 L3V7 | Provides UPS, RTC, power sequencing, I²C telemetry at address `0x08`. |
| Waveshare 7.3" e-Paper HAT (E) | 800×480, 6-color (B/W/R/Y/Blu/Grn) SPI panel, works with 3.3 V logic. |
| Li-Ion/Poly battery pack (3.7 V) | Connect to the Witty Pi battery terminals for UPS behavior. |
| 8× 28–30 AWG wire leads + heat-shrink | For tapping SPI pins from the back side of the Witty Pi header. |
| FFC/PH2.0 cable (included with Waveshare HAT) | Carries VCC/GND/DIN/CLK/CS/DC/RST/BUSY to the display. |
| Standoffs + nylon screws | Maintain spacing between boards and mount the display. |

## 2. Mechanical stack

1. Solder a 40-pin male header on the Pi Zero 2 W (if it is not already assembled).
2. Plug the Pi into the underside of the Witty Pi 4 L3V7 so that the Pi is at the bottom and the Witty Pi board sits on top. The Witty board completely covers the GPIO header, so plan to pull signals from the exposed solder tails on top of the Witty header or from Pi test pads.
3. Mount the Waveshare driver board on a small standoff frame so its 8-pin JST/SPI header faces the Pi stack. Leave enough slack for the ribbon cable to reach the solder points described below.

## 3. Using the available Witty Pi headers

With the Pi Zero 2 W sandwiched underneath the Witty Pi 4 L3V7, the only solderable points you can access without removing the stack are the two factory headers shown in the photos above:

- **P3 (edge-facing)**: `GND`, `CATHODE`, `SWITCH`, `ALARM`, `LED`, `3V3`, `VOUT`. These are tied directly to the power-management circuitry. Use `CATHODE` for the Pi ground reference, `VOUT` when you need the 5 V rail, and `SWITCH/ALARM/LED` if you want to monitor the Witty Pi state. The `3V3` pin is for the Witty Pi microcontroller only; do **not** power external loads from it.
- **P5 (center row)**: `CLKOUT`, `INTRPT`, `3V3`, `OTEMP`, `I-SCL`, `I-SDA`, `GND`. These expose the RTC alarm, temperature comparator, and internal I²C bus used by the Witty Pi firmware. They are great for diagnostics but they do not carry the Pi’s SPI lines.

Because the Waveshare 7.3" e-paper requires SPI (MOSI/SCLK/CS/DC/RST/BUSY), and none of those signals appear on P3/P5, you must run light-gauge jumpers from the Pi’s GPIO pads to the display. The Witty Pi does not break those signals out elsewhere.

### 3.1 Header orientation diagrams

```
P3  (toward PCB edge)                      P5  (center header)
┌──────┬──────┬────────┬───────┬────┬─────┬──────┐     ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐
| GND  |CATH- |SWITCH  | ALARM | LED| 3V3 | VOUT |     |CLKOUT|INTRPT| 3V3  |OTEMP | I-SCL| I-SDA| GND  |
└──────┴──────┴────────┴───────┴────┴─────┴──────┘     └──────┴──────┴──────┴──────┴──────┴──────┴──────┘
(closest to battery connector)             (closest to USB-C port)
```

Use the diagrams above when labeling the harness. Mark the outer edge of your 3D-printed bracket or enclosure with small arrows so you always know which direction the text on the PCB should face.

## 4. Waveshare e-Paper wiring plan (using P3/P5 for power + Pi test pads for SPI)

1. **Power**  
   - Feed the display’s VCC from the Pi’s 3.3 V rail. The cleanest option with the Witty Pi installed is to solder a thin wire to the Pi Zero 2 W test pad `PP3` (3V3) or directly to the Pi’s pin 1 solder tail, then bring that wire up to the display connector.  
   - Tie all grounds to the Witty Pi’s **CATHODE** pad on P3. This is the same node the Pi uses internally and keeps current sensing intact.
   - If you need 5 V for the display’s associated driver board, use `VOUT` on P3—it mirrors the Pi’s 5 V rail.

2. **SPI / control lines**  
   With the 40-pin header blocked, solder 28–30 AWG jumpers directly to the Pi test pads on the underside of the board and route them around the edge of the Witty Pi to your display harness. The table below lists the pad numbers that correspond to each e-paper signal:

| e-Paper pin | Signal | Pi pad / pin | Where to grab the signal when only P3/P5 are exposed |
| --- | --- | --- | --- |
| DIN | MOSI (`GPIO10`) | Test pad `PP10` (or 40-pin pin 19) | Tack a magnet wire to `PP10`, run it along the PCB edge, and secure it near P3 with Kapton tape. |
| CLK | SCLK (`GPIO11`) | Test pad `PP11` (pin 23) | Same approach as above; keep the run under 10 cm and twist with a ground drain. |
| CS | CE0 (`GPIO8`) | Test pad `PP8` (pin 24) | Route beside the CLK lead to minimise loop area. |
| DC | Data/Command (`GPIO25`) | Test pad `PP25` (pin 22) | Bring this wire up alongside the power bundle; label it before crimping into the e-paper JST. |
| RST | Reset (`GPIO17`) | Test pad `PP17` (pin 11) | Optional but recommended for reliable recovery. |
| BUSY | Busy (`GPIO24`) | Test pad `PP24` (pin 18) | This is an input to the Pi—keep it away from noisy power traces. |

3. **Strain relief + routing tips**
   - After each jumper exits the Pi test pad, add a dab of UV resin or hot glue so accidental tugs do not rip the pad.
   - Bundle the SPI lines and tape them to the Witty Pi PCB before they fan out into the 8-pin JST that plugs into the Waveshare driver board (wire order: VCC, GND, DIN, CLK, CS, DC, RST, BUSY).
   - Keep the SPI bundle twisted with a spare ground wire whenever the run exceeds ~15 cm to avoid ringing on the 1 MHz data lines.

### 4.1 Printable harness checklist for P3/P5

Use the table below as a build worksheet. Print it, tape it to the workbench, and check each row after crimping/soldering the connection.

| ✔ | Header | Pin label | Destination / action | Notes |
| - | ------ | --------- | -------------------- | ----- |
| [ ] | P3 | GND | Tie to display ground shield if you need chassis bonding | Usually left unused—prefer `CATHODE` for logic ground. |
| [ ] | P3 | CATHODE | Main ground reference for Pi + display | Land all SPI returns here. |
| [ ] | P3 | SWITCH | Optional remote wake button (GPIO4) | Leave accessible for future buttons. |
| [ ] | P3 | ALARM | Optional LED/microcontroller input | Mirrors RTC alarm used by Witty Pi. |
| [ ] | P3 | LED | Optional external LED | Add 1 kΩ series resistor if used. |
| [ ] | P3 | 3V3 | **Do not load** | Only powers the Witty Pi MCU. |
| [ ] | P3 | VOUT | 5 V accessories (if needed) | Use for powering the Waveshare driver if it requires 5 V. |
| [ ] | P5 | CLKOUT | Optional test point | 32.768 kHz clock for calibration. |
| [ ] | P5 | INTRPT | Bring to debug pad if desired | Same as ALARM on P3. |
| [ ] | P5 | 3V3 | **Do not load** | Same warning as P3. |
| [ ] | P5 | OTEMP | Optional over-temp indicator | Pulls low above threshold. |
| [ ] | P5 | I-SCL | Internal I²C (RTC/temp) | Only for diagnostics when the Pi is off. |
| [ ] | P5 | I-SDA | Internal I²C (RTC/temp) | Companion to I-SCL. |
| [ ] | P5 | GND | Secondary ground point | Convenient return for probes. |

### 4.2 Pi Zero 2 W test-pad coordinates

The official Pi Zero 2 W test-pad drawing lists each pad’s label plus its offset from the origin (the lower-left mounting hole on the board underside). Use those values when plotting drill holes or aligning a 3D-printed jig:

| E-paper signal | Pi net | Test-pad label (datasheet) | X (mm) | Y (mm) | Notes |
| --- | --- | --- | --- | --- | --- |
| VCC (3.3 V) | 3V3 rail | `3V3` | 48.55 | 22.44 | Same pad as in the official drawing. Solder a thin wire; avoid pulling more than a few hundred mA. |
| Ground | System ground | `GND` (near USB jack) | 49.38 | 3.05 | Tie directly to Witty Pi `CATHODE`. Any of the `GND` pads from the drawing work if this one is inconvenient. |
| MOSI | GPIO10 | *(no labelled test pad in Raspberry Pi drawing)* | — | — | Use the corresponding 40-pin header tail (pin 19) or gently scrape to the unlabelled `PP10` pad adjacent to the center test-pad cluster. |
| SCLK | GPIO11 | *(no labelled test pad)* | — | — | Same approach as MOSI; solder to the pin 23 tail. |
| CE0 | GPIO8 | *(no labelled test pad)* | — | — | Solder to pin 24’s tail. |
| DC | GPIO25 | *(no labelled test pad)* | — | — | Use pin 22 tail. |
| RST | GPIO17 | *(no labelled test pad)* | — | — | Use pin 11 tail. |
| BUSY | GPIO24 | *(no labelled test pad)* | — | — | Use pin 18 tail. |

> Tip: if you do decide to hunt down the unlabelled PP-series pads for the SPI lines, reference the Raspberry Pi Zero 2 W schematic where PP10, PP11, PP8, PP25, PP17, and PP24 are annotated. Their footprints sit directly behind the corresponding header pins, roughly 6 mm inboard from the board edge.

## 5. Power and battery considerations

- Connect your 3.7 V Li-Ion pack to the Witty Pi 4 L3V7 battery input. The board will charge it and expose input/output voltages via registers `0–5` over I²C (address `0x08`).
- The Pi is powered between `VOUT` and `CATHODE`. That sampling resistor (0.05 Ω) is how the firmware measures current. Do **not** tie external loads to `GND` on P3; always use `CATHODE` if the load also touches the Pi.
- Leave the white push button on the Witty accessible—the software listens to GPIO4/`SWITCH` so you can still perform a manual wake/shutdown.
- If you need the RTC alarm output elsewhere, run `INTRPT` (P5) to an external LED or microcontroller input.

## 6. Display refresh cadence

The software renders a full 800×480 frame every 10 minutes. A cached SHA-1 of the last frame prevents unnecessary full refreshes; if the rendered bitmap is identical to the previous run, the e-paper update is skipped. This dramatically reduces ghosting on the 7.3" six-color panel.

## 7. Verification checklist

1. With only the Pi + Witty connected, run `i2cdetect -y 1` and confirm that `0x08` appears.
2. Attach the display harness and power on; use a continuity tester to ensure each SPI lead matches the assignment above.
3. Enable SPI in firmware (`sudo raspi-config` → *Interface Options* → *SPI*). Reboot.
4. Run `python src/main.py --verbose --env .env` with `MOCK_DISPLAY=1` first. Inspect `var/cache/last_frame.png` to confirm the layout renders as expected.
5. Flip `MOCK_DISPLAY` to `0`, rerun, and watch for the panel refresh. Initial refresh takes ~20 s on the 7.3" module.
6. Check the Witty Pi battery telemetry by reading registers `0–11` (for example with `i2cget -y 1 0x08 0`). Compare against a multimeter on `VOUT`/`CATHODE`.

## 8. Troubleshooting

- **BUSY never clears**: make sure the BUSY lead is really tied to GPIO24. If it is floating, the driver waits forever.
- **Display stays blank**: verify you are feeding 3.3 V, not 5 V. The IO level must match the supply voltage (per Waveshare manual, “Operating voltage 3.3 V/5 V (The IO level voltage should be the same as the supply voltage)”).
- **Pi randomly resets**: check that external loads are on `VOUT/CATHODE` and not stealing current from the Witty’s internal 3.3 V rail.
- **Witty Pi LED blinking fast**: register `7` indicates you are in LDO (battery) mode. Connect USB-C to charge or adjust the low-voltage threshold via register `19`.
