# Bill of Materials and Budget

Prices are **rough planning ranges in USD**, not quotes. They swing a lot by country, new vs second-hand, and brand (Western vs Asian servo brands can differ 2–3×). Get real quotes before committing. Specs reference [DESIGN.md](DESIGN.md).

## Structure and mechanics

| Item | Qty | Spec | Ballpark |
|---|---|---|---|
| Donor MX bike | 1 | Any modern 250/450 frame; non-runner/seized engine is fine | $800–2,500 |
| Base weldment | 1 | X-base, 200×100 RHS, 30 mm centre plate machined flat | |
| Yaw table, roll uprights, roll ring, pitch hub | 1 set | Fabricated steel, machined bearing seats | |
| Rod sleeve + engine-replacement cradle | 1 set | 160×160×8 SHS sleeve; cradle bolted to every engine mount | |
| *Steel, fabrication and machining for the above* | | Outsourced machining dominates | **$4,000–10,000** |
| Slewing ring | 1 | 4-point contact ball, ~800 mm bore class, external gear | $800–2,000 |
| Sector gears | 2 | Pitch radius 0.30 m, module ~8, 60 mm face, case-hardened (roll ±90°, pitch ≈ −85…+70°) | $1,500–4,000 |
| Pinions | 6 | 4 for the sectors, 2 for the yaw ring | incl. above |
| Precision planetary gearboxes | 6 | 20:1 ×4 (roll/pitch), 10:1 ×2 (yaw), low backlash | $2,400–7,200 |
| Roll and pitch bearings + housings | 4 | Compact; roll housings ≤80 mm above the pivot | $500–1,500 |
| Polyurethane end-stop buffers | 4 | Roll ±63° and pitch, 10° crush, ~5 kN·m | $100–300 |
| Anchors | 8 | M16 chemical anchors | $100 |

## Motion drives

| Item | Qty | Spec | Ballpark |
|---|---|---|---|
| AC servo + drive, 5 kW / 3000 rpm, with holding brake | 4 | Roll ×2, pitch ×2; EtherCAT; STO input | |
| AC servo + drive, 2 kW, with holding brake | 2 | Yaw | |
| AC servo + drive, 3 kW, with holding brake | 1 | Heave | |
| *Servos and drives total* | 7 | | **$6,000–18,000** |
| Ball-screw electric cylinder | 1 | 10 kN, 20 mm lead, 200 mm stroke | $1,000–2,500 |
| Profile rails + carriages | 2 + 4 | Size 35 | $300–700 |
| Air spring + regulator | 1 | Adjustable, ~2 kN at working pressure | $150–400 |
| Absolute ring encoder / homing sensors | 1 set | Yaw homing, axis homing | $200–600 |

## Bike: FFB, controls and sensing

| Item | Qty | Spec | Ballpark |
|---|---|---|---|
| Direct-drive steering motor | 1 | 25–32 N·m, USB FFB, safety input | $900–2,500 |
| Toothed belt drive | 1 | 2:1, HTD/GT profile, tensioner, stem pulley clamp | $100–250 |
| Footpeg load cells | 2 | 300 kg shear beam | |
| Seat load cells | 2 | 100 kg | |
| Bar-riser load cells | 2–4 | Compression/2-axis | |
| Brake pressure transducers | 2 | 0–100 bar, with banjo T-fittings | |
| Throttle/clutch sensors | 2 | Contactless magnetic | |
| Shifter detent + Hall switches | 1 set | | |
| Rider DAQ | 1 | Microcontroller + 24-bit ADCs, ≥500 Hz, USB HID + Ethernet | |
| *Sensing total* | | | **$500–1,200** |
| Bass shakers + amp | 3 + 1 | | $300–700 |
| Fan | 1 | 24 V brushless blower, PWM | $80–200 |

## Electronics, compute, VR

| Item | Qty | Spec | Ballpark |
|---|---|---|---|
| Slip ring | 1 | 3-ph + N + 2× PE @ 32 A, 2 safety channels, GigE/fibre, spares; through-bore | $1,000–3,000 |
| Motion controller | 1 | Real-time PC with EtherCAT master | $500–2,000 |
| Game PC | 1 | Strong VR-class GPU, mounted on the yaw table | $1,500–3,500 |
| VR headset | 1 | Wireless | $500–1,500 |
| Wi-Fi access point | 1 | 6E/7, on the yaw table | $150–300 |
| Electrical cabinet | 1 | Isolator, RCD, breakers, contactors, DC-bus braking resistor, 24 V supplies, cable chains | $1,500–3,000 |
| UPS | 1 | Controller + safety PLC only | $150–300 |

## Safety and cell

| Item | Qty | Spec | Ballpark |
|---|---|---|---|
| Safety relay / small safety PLC | 1 | E-stop, STO, brakes, interlocks, limit switches | $400–1,200 |
| E-stop stations | 2 | Operator desk + cell gate | $100–200 |
| Lanyard kill-cord switch | 1 | Magnetic, belt clip | $50–150 |
| Limit switches | 4 | Roll and pitch, hard-wired to safety | $100–300 |
| Laser scanner or light curtain | 1 | Gate side of the cell | $800–3,000 |
| Fence panels + interlocked gate | ~20 m | 5 × 5 m cell | $500–1,500 |
| Mounting stair with dock interlock | 1 | | $200–500 |
| Floor mats | ~20 m² | | $300–800 |

## Total

| | Low | High |
|---|---|---|
| **Ballpark build cost** | **~$27,000** | **~$76,000** |

Where the money goes: servos and drives, machining, and safety. Ways to come in at the low end:

- Second-hand servo/drive sets from decommissioned machines (check that STO and brakes are fitted).
- Do the welding yourself; outsource only the machined seats and the gears.
- Build the static bike (DESIGN.md §9, step 2) first. It costs a few thousand, and you'll know the feel is right before buying motion hardware.
