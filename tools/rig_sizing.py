#!/usr/bin/env python3
"""
Sizing calculator for the MX motion rig (single stalk, 4 motion axes + FFB bars).

Every number in docs/DESIGN.md marked "(sizing script)" comes from here.
Change a parameter, re-run, and check every line still says OK.

Coordinates: origin = PIVOT (where the roll and pitch axes cross).
x forward, y left, z up. The pivot sits on the "virtual ground" plane: where
the tyres would touch the dirt if the bike still had wheels.

Usage:
    python3 tools/rig_sizing.py                        # rated 300 kg payload (design case)
    python3 tools/rig_sizing.py --rider 90 --bike 77   # e.g. stripped bike, lighter rider
"""
import argparse
import math
from dataclasses import dataclass

G = 9.81
DEG = math.pi / 180


@dataclass
class Body:
    name: str
    m: float            # kg
    x: float            # CoM position from pivot, m
    y: float
    z: float
    ixx: float = 0.0    # own inertia about own CoM, kg m^2
    iyy: float = 0.0
    izz: float = 0.0


RATED_PAYLOAD = 300.0   # kg on top of the rod: rider + bike + everything bolted to the bike


def mass_model(rider_kg: float, bike_kg: float, drop: float = 0.0):
    """Groups, from the top down:
    heave      - rides the heave carriage (rider, bike)
    pitched    - fixed to the pitch hub (pitches + rolls + yaws)
    rolled     - fixed to the roll ring (rolls + yaws)
    yawed      - fixed to the yaw table (yaws only)
    drop       - how far the pivot sits BELOW the virtual ground (engine-in layout
                 puts the heave cartridge in a longer rod under the frame)
    """
    k = rider_kg / 110
    kb = bike_kg / 77
    heave = [
        Body("rider, standing attack position", rider_kg, 0.00, 0.0, 1.35 + drop,
             ixx=15 * k, iyy=15 * k, izz=4 * k),
        # design case 170 kg = complete 450 incl. engine (~110 kg wet) + ~45 kg rig
        # hardware on the bike (cradle, FFB motor + belt, shakers, sensors, DAQ) + spare.
        # The recommended engine-out build is ~77 kg. Own inertia scales with mass.
        Body("bike assembly + rig hardware on it", bike_kg, 0.10, 0.0, 0.62 + drop,
             ixx=6 * kb, iyy=16 * kb, izz=14 * kb),
        Body("heave carriage", 15, 0.00, 0.0, 0.45 + drop, ixx=0.3, iyy=0.3, izz=0.2),
    ]
    pitched = [
        Body("stalk sleeve + rails + screw jack", 35 + 50 * drop, 0.00, 0.0, 0.26 + drop / 2, ixx=0.7, iyy=0.7, izz=0.2),
        Body("pitch hub", 20, 0.00, 0.0, 0.00, ixx=0.3, iyy=0.3, izz=0.3),
        Body("pitch sector gear (hangs below)", 25, 0.00, 0.0, -0.20, ixx=0.5, iyy=0.5, izz=0.25),
    ]
    rolled = [
        Body("roll ring", 60, 0.00, 0.0, -0.05, ixx=2.4, iyy=4.8, izz=6.0),
        Body("pitch drives, 2x (hang below)", 50, 0.00, 0.0, -0.32, ixx=0.8, iyy=0.8, izz=0.8),
        Body("roll sector gear (hangs below)", 40, 0.40, 0.0, -0.20, ixx=0.8, iyy=0.4, izz=0.4),
    ]
    yawed = [
        Body("yaw table frame", 80, 0.00, 0.0, -0.40, izz=12.9),
        Body("roll uprights + bearings", 40, 0.00, 0.0, -0.25, izz=40 * 0.6 ** 2),
        Body("roll drives, 2x (front)", 50, 0.62, 0.0, -0.32),
        Body("electronics bay (rear)", 50, -0.86, 0.0, -0.31),
    ]
    return heave, pitched, rolled, yawed


def rot_x(b: Body, phi: float) -> Body:
    c, s = math.cos(phi), math.sin(phi)
    return Body(b.name, b.m, b.x, b.y * c - b.z * s, b.y * s + b.z * c, b.ixx,
                b.iyy * c * c + b.izz * s * s, b.iyy * s * s + b.izz * c * c)


def I_x(bs): return sum(b.m * (b.y ** 2 + b.z ** 2) + b.ixx for b in bs)
def I_y(bs): return sum(b.m * (b.x ** 2 + b.z ** 2) + b.iyy for b in bs)
def I_z(bs): return sum(b.m * (b.x ** 2 + b.y ** 2) + b.izz for b in bs)
def mz(bs): return sum(b.m * b.z for b in bs)


def ok(cond): return "OK" if cond else "**FAIL**"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rider", type=float, default=130.0, help="rider mass incl. gear, kg")
    ap.add_argument("--bike", type=float, default=170.0,
                    help="bike + everything bolted to it, kg (complete 450 + rig hardware = 170; engine-out = 77)")
    ap.add_argument("--pivot-drop", type=float, default=0.0,
                    help="pivot below the virtual ground, m (0 = recommended; ~0.2 for the engine-in layout)")
    ap.add_argument("--gimbal-servo", type=float, default=5, choices=[5, 7.5],
                    help="roll/pitch servo size, kW (7.5 for the engine-in layout)")
    args = ap.parse_args()

    # ---- motion targets (DESIGN.md §2) ----
    roll_lim, roll_rate, roll_acc = 60 * DEG, 150 * DEG, 500 * DEG
    pitch_up, pitch_dn, pitch_rate, pitch_acc = 45 * DEG, 30 * DEG, 120 * DEG, 400 * DEG
    yaw_rate, yaw_acc_up, yaw_acc_lean = 180 * DEG, 400 * DEG, 200 * DEG
    heave_stroke, heave_v, heave_a = 0.200, 0.6, 1.5 * G

    # ---- drive hardware (DESIGN.md §4) ----
    srv5 = dict(kw=5, rated=15.9, peak=47.7, nmax=3000)    # 5 kW / 3000 rpm AC servo
    srv7 = dict(kw=7.5, rated=23.9, peak=71.6, nmax=3000)  # 7.5 kW (engine-in variant)
    srv3 = dict(kw=3, rated=9.55, peak=28.6, nmax=3000)    # 3 kW (yaw)
    gsrv = srv7 if args.gimbal_servo == 7.5 else srv5      # roll + pitch motors
    sector_r, pinion_r, planet = 0.30, 0.06, 20      # roll + pitch: sector gear, 2 preloaded pinions
    gimbal_ratio = planet * sector_r / pinion_r      # = 100
    gimbal_eff = 0.95 * 0.97                         # planetary x spur mesh
    yaw_ratio, yaw_eff, yaw_friction = 80, 0.85, 250  # 10:1 planetary x 8:1 slew-ring gear
    preload = 2.0                                     # N m per motor, anti-backlash bias
    lead, screw_eff = 0.020, 0.90                     # heave ball screw
    margin = 1.25
    pivot_h = 0.60                                    # pivot height above the floor, m

    drop = args.pivot_drop
    heave, pitched, rolled, yawed = mass_model(args.rider, args.bike, drop)
    payload = args.rider + args.bike
    above_pitch = heave + pitched
    above_roll = above_pitch + rolled

    out = []
    p = out.append
    p(f"# Sizing run — {payload:.0f} kg on the rod ({args.rider:.0f} kg rider standing + {args.bike:.0f} kg bike)\n")
    p(f"Rated payload {RATED_PAYLOAD:.0f} kg → {ok(payload <= RATED_PAYLOAD)}"
      + (f"; pivot {drop * 1000:.0f} mm below the virtual ground" if drop else "") + "\n")
    m_roll = sum(b.m for b in above_roll)
    p(f"Everything that rolls: **{m_roll:.0f} kg**, net CoM **{mz(above_roll) / m_roll:.2f} m** above the pivot "
      f"(drives hanging below the pivot act as part-counterweight)\n")

    def per_motor(T, ratio, eff, n=2):
        return T * margin / ratio / eff / n + preload

    # ---- ROLL ----
    Ir = I_x(above_roll)
    gr = G * mz(above_roll) * math.sin(roll_lim)
    Tr = Ir * roll_acc + gr
    mr = per_motor(Tr, gimbal_ratio, gimbal_eff)
    rpm_r = roll_rate / (2 * math.pi) * 60 * gimbal_ratio
    p("## Roll — outer gimbal axis")
    p(f"- Inertia: {Ir:.0f} kg·m²; gravity moment at ±{roll_lim / DEG:.0f}°: {gr:.0f} N·m")
    p(f"- Peak demand (pulling up out of full lean at full accel): **{Tr:.0f} N·m**")
    p(f"- Sector tooth force: {Tr * margin / sector_r / 1000:.1f} kN shared by 2 pinions")
    p(f"- {gimbal_ratio:.0f}:1 → per motor {mr:.1f} N·m incl. {margin}× margin + preload "
      f"({gsrv['kw']} kW peak {gsrv['peak']}) {ok(mr < gsrv['peak'])}; {rpm_r:.0f} rpm at {roll_rate / DEG:.0f}°/s "
      f"{ok(rpm_r <= gsrv['nmax'])}")
    ke = 0.5 * Ir * roll_rate ** 2
    buffer = 10 * DEG
    p(f"- Runaway into the end stops at full speed: {ke:.0f} J → buffers need {buffer / DEG:.0f}° of travel "
      f"at ≈{ke / buffer / 1000:.1f} kN·m (hard stops at ±63°, fully crushed at ±73°)")
    hold = G * mz(above_roll) * math.sin(30 * DEG) / gimbal_ratio / gimbal_eff / 2
    p(f"- Holding a 30° lean: {hold:.1f} N·m per motor (rated {gsrv['rated']}) {ok(hold < gsrv['rated'])}\n")

    # ---- PITCH ----
    Ip = I_y(above_pitch)
    gp = G * max(mz(above_pitch) * math.sin(pitch_up), mz(above_pitch) * math.sin(pitch_dn)) \
        + G * abs(sum(b.m * b.x for b in above_pitch))
    Tp = Ip * pitch_acc + gp
    mp = per_motor(Tp, gimbal_ratio, gimbal_eff)
    p("## Pitch — inner gimbal axis")
    p(f"- Inertia: {Ip:.0f} kg·m²; gravity moment at +{pitch_up / DEG:.0f}° wheelie: {gp:.0f} N·m")
    p(f"- Peak demand: **{Tp:.0f} N·m** → per motor {mp:.1f} N·m ({gsrv['kw']} kW peak {gsrv['peak']}) {ok(mp < gsrv['peak'])}; "
      f"{pitch_rate / (2 * math.pi) * 60 * gimbal_ratio:.0f} rpm at {pitch_rate / DEG:.0f}°/s\n")

    # ---- YAW ----
    def Iyaw(phi): return I_z([rot_x(b, phi) for b in above_roll]) + I_z(yawed)
    Iy0, Iy60 = Iyaw(0), Iyaw(roll_lim)
    Ty = max(Iy0 * yaw_acc_up, Iy60 * yaw_acc_lean) + yaw_friction
    my = per_motor(Ty, yaw_ratio, yaw_eff)
    p("## Yaw — continuous, slew ring + 2 pinions")
    p(f"- Inertia upright {Iy0:.0f} kg·m², at 60° lean {Iy60:.0f} kg·m²")
    p(f"- Peak demand: **{Ty:.0f} N·m** (incl. {yaw_friction} N·m slew-ring drag)")
    p(f"- {yaw_ratio}:1 → per motor {my:.1f} N·m (3 kW peak {srv3['peak']}) {ok(my < srv3['peak'])}; "
      f"{yaw_rate / (2 * math.pi) * 60 * yaw_ratio:.0f} rpm at {yaw_rate / DEG:.0f}°/s\n")

    # ---- HEAVE ----
    mh = sum(b.m for b in heave)
    Fs, Fp = mh * G, mh * (G + heave_a) + 300
    tq = lambda F: F * lead / (2 * math.pi * screw_eff)
    p("## Heave — along the stalk (the 'suspension')")
    p(f"- Carriage load {mh:.0f} kg → static {Fs / 1000:.2f} kN; peak at {heave_a / G:.1f} g onset **{Fp / 1000:.2f} kN**")
    p(f"- {lead * 1000:.0f} mm lead screw: peak {tq(Fp):.1f} N·m, {tq(Fp) * margin:.1f} incl. margin "
      f"(5 kW peak {srv5['peak']}) {ok(tq(Fp) * margin < srv5['peak'])}; "
      f"static {tq(Fs):.1f} N·m, or {tq(0.25 * Fs):.1f} N·m with the air spring carrying 75 %")
    p(f"- {heave_v} m/s → {heave_v / lead * 60:.0f} rpm; stroke {heave_stroke * 1000:.0f} mm (±{heave_stroke * 500:.0f})\n")

    # ---- STRUCTURE ----
    Tmax = max(Tr, Tp)
    D, t = 0.1143, 0.008
    Zs = math.pi / 64 * (D ** 4 - (D - 2 * t) ** 4) / (D / 2)
    sig = Tmax / Zs / 1e6
    p("## Structure")
    p(f"- Base/anchor design overturning moment (1.5 × peak axis torque): **{1.5 * Tmax / 1000:.1f} kN·m**")
    p(f"- Stalk (114.3×8 CHS equivalent) bending at peak: {sig:.0f} MPa → S355 safety factor {355 / sig:.1f}\n")

    # ---- ENVELOPE ----
    head_top, bar_h, bar_half = 1.93 + drop, 1.12 + drop, 0.40
    head_lat = head_top * math.sin(roll_lim)
    bar_lat = bar_half * math.cos(roll_lim) + bar_h * math.sin(roll_lim)
    fx, fz = -1.05, 0.75 + drop
    fx2 = fx * math.cos(pitch_up) - fz * math.sin(pitch_up)
    fz2 = fx * math.sin(pitch_up) + fz * math.cos(pitch_up)
    sweep = max(head_lat, bar_lat, abs(fx2)) + 0.35
    ceiling = pivot_h + head_top + heave_stroke / 2 + 0.40
    p("## Envelope (pivot {:.2f} m above floor)".format(pivot_h))
    p(f"- Rider's head swings {head_lat:.2f} m sideways at full lean; bar end {bar_lat:.2f} m")
    p(f"- Rear fender at full wheelie: {abs(fx2):.2f} m behind the axis, {fz2 + pivot_h:.2f} m off the floor")
    p(f"- Keep-out radius **{sweep:.1f} m** → fenced cell ≈ {2 * sweep + 0.6:.1f} m × {2 * sweep + 0.6:.1f} m")
    p(f"- Minimum ceiling **{ceiling:.1f} m**; seat height above floor ≈ {pivot_h + drop + 0.95:.2f} m\n")

    # ---- OVERHEAD TETHER CHECK ----
    H, r, ph = 3.2 - pivot_h, 1.40 + drop, 45 * DEG
    d = math.sqrt(r * r + H * H - 2 * r * H * math.cos(ph))
    v = r * H * math.sin(ph) * roll_rate / d
    p("## Why there's no overhead fall-arrest line")
    p(f"- A ceiling tether to the rider's chest pays out at **{v:.1f} m/s** during an ordinary "
      f"{roll_rate / DEG:.0f}°/s whip. Self-retracting lifelines lock at ≈1.5 m/s, so one would "
      f"yank the rider mid-whip.")

    print("\n".join(out))


if __name__ == "__main__":
    main()
