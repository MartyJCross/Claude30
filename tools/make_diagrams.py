#!/usr/bin/env python3
"""
Generates docs/img/side-view.svg and docs/img/front-view.svg.

All geometry is in metres from the PIVOT (x forward, y left, z up), the same
frame as tools/rig_sizing.py, so the drawings stay true to the numbers.

    python3 tools/make_diagrams.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "img"
S = 200            # px per metre
PIVOT_H = 0.60     # pivot height above floor, m
W, H = 1000, 1010
X0, Y0 = 500, 640  # pivot position on the canvas
FLOOR_Y = Y0 + PIVOT_H * S

C = dict(
    ink="#111827", dim="#4b5563", fixed="#475569", fixed_fill="#e2e8f0",
    gimbal="#1d4ed8", gimbal_fill="#dbeafe", stalk="#b45309", stalk_fill="#fde68a",
    plastic="#ea580c", plastic_fill="#ffedd5", ffb="#7c3aed", ffb_fill="#ede9fe",
    sensor="#047857", ghost="#94a3b8", dirt="#92400e", rider="#64748b",
)


def P(a, b):
    """model (horizontal, z) in metres -> canvas px"""
    return X0 + a * S, Y0 - b * S


def pts(seq):
    return " ".join(f"{P(a, b)[0]:.1f},{P(a, b)[1]:.1f}" for a, b in seq)


def poly(seq, stroke, fill="none", sw=2, extra=""):
    return f'<polygon points="{pts(seq)}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'


def line(seq, stroke, sw=2, extra=""):
    return f'<polyline points="{pts(seq)}" stroke="{stroke}" fill="none" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def rect(a0, b0, a1, b1, stroke, fill="none", sw=2, extra=""):
    return poly([(a0, b0), (a1, b0), (a1, b1), (a0, b1)], stroke, fill, sw, extra)


def circle(a, b, r, stroke, fill="none", sw=2, extra=""):
    x, y = P(a, b)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * S:.1f}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}" {extra}/>'


def sector(a, b, r, start_deg, end_deg, stroke, fill, sw=2, extra=""):
    """Pie slice; angles measured from straight DOWN, positive toward +horizontal."""
    pts_ = [(a, b)]
    n = 24
    for i in range(n + 1):
        t = math.radians(start_deg + (end_deg - start_deg) * i / n)
        pts_.append((a + r * math.sin(t), b - r * math.cos(t)))
    return poly(pts_, stroke, fill, sw, extra)


def text(a, b, s, size=13, anchor="start", fill=None, weight="normal", px=False):
    x, y = (a, b) if px else P(a, b)
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{fill or C["ink"]}" font-weight="{weight}">{s}</text>')


def callout(n, a, b, ba, bb):
    """Numbered bubble at model point (ba, bb) with a leader to model point (a, b)."""
    x, y = P(a, b)
    tx, ty = P(ba, bb)
    return (f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{C["dim"]}" stroke-width="1"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{C["dim"]}"/>'
            f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="11" fill="#fff" stroke="{C["ink"]}" stroke-width="1.5"/>'
            f'<text x="{tx:.1f}" y="{ty + 4.5:.1f}" font-size="12" text-anchor="middle" font-weight="700" fill="{C["ink"]}">{n}</text>')


def bubble(n, xpx, ypx):
    return (f'<circle cx="{xpx}" cy="{ypx}" r="11" fill="#fff" stroke="{C["ink"]}" stroke-width="1.5"/>'
            f'<text x="{xpx}" y="{ypx + 4.5}" font-size="12" text-anchor="middle" font-weight="700" fill="{C["ink"]}">{n}</text>')


def vdim(xpx, z0, z1, label):
    """Vertical dimension at canvas x, between model heights z0 and z1 (pivot frame)."""
    y0, y1 = Y0 - z0 * S, Y0 - z1 * S
    ym = (y0 + y1) / 2
    return (f'<line x1="{xpx}" y1="{y0:.1f}" x2="{xpx}" y2="{y1:.1f}" stroke="{C["dim"]}" stroke-width="1" '
            f'marker-start="url(#arr)" marker-end="url(#arr)"/>'
            f'<line x1="{xpx - 6}" y1="{y0:.1f}" x2="{xpx + 6}" y2="{y0:.1f}" stroke="{C["dim"]}" stroke-width="1"/>'
            f'<line x1="{xpx - 6}" y1="{y1:.1f}" x2="{xpx + 6}" y2="{y1:.1f}" stroke="{C["dim"]}" stroke-width="1"/>'
            f'<text x="{xpx - 6}" y="{ym:.1f}" font-size="12" fill="{C["dim"]}" text-anchor="middle" '
            f'transform="rotate(-90 {xpx - 6} {ym:.1f})">{label}</text>')


def header(title, subtitle):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif">
<defs>
  <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{C["dim"]}"/>
  </marker>
  <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="8" stroke="{C["fixed"]}" stroke-width="1.2"/>
  </pattern>
  <pattern id="cradle" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
    <rect width="7" height="7" fill="{C["stalk_fill"]}"/>
    <line x1="0" y1="0" x2="0" y2="7" stroke="{C["stalk"]}" stroke-width="1"/>
  </pattern>
</defs>
<rect width="{W}" height="{H}" fill="#ffffff"/>
<text x="30" y="40" font-size="22" font-weight="700" fill="{C["ink"]}">{title}</text>
<text x="30" y="64" font-size="14" fill="{C["dim"]}">{subtitle}</text>
'''


def floor_and_ground(x_from=-2.3, x_to=2.3, label_ground=True):
    o = []
    x0, x1 = X0 + x_from * S, X0 + x_to * S
    o.append(f'<rect x="{x0:.0f}" y="{FLOOR_Y:.0f}" width="{x1 - x0:.0f}" height="14" fill="url(#hatch)"/>')
    o.append(f'<line x1="{x0:.0f}" y1="{FLOOR_Y:.0f}" x2="{x1:.0f}" y2="{FLOOR_Y:.0f}" stroke="{C["fixed"]}" stroke-width="2"/>')
    o.append(text(x0 + 4, FLOOR_Y + 30, "floor / concrete slab", 12, fill=C["dim"], px=True))
    o.append(f'<line x1="{x0:.0f}" y1="{Y0}" x2="{x1:.0f}" y2="{Y0}" stroke="{C["dirt"]}" stroke-width="1.5" stroke-dasharray="10 6"/>')
    if label_ground:
        o.append(text(x0 + 4, Y0 - 8, "virtual ground (where the tyres would touch)", 12, fill=C["dirt"], px=True))
    return o


# --------------------------------------------------------------------------- side view
STEER_DIR = (-math.sin(math.radians(27)), math.cos(math.radians(27)))   # 27 deg rake
FRONT_AXLE = (0.88, 0.36)


def along_steer(d):
    return FRONT_AXLE[0] + STEER_DIR[0] * d, FRONT_AXLE[1] + STEER_DIR[1] * d


def bike_side(ghost=False):
    """Stripped bike + cradle + FFB, side view. Returns svg fragments."""
    o = []
    k = C["ghost"] if ghost else C["ink"]
    pl, plf = (C["ghost"], "none") if ghost else (C["plastic"], C["plastic_fill"])
    dash = 'stroke-dasharray="6 4"' if ghost else ""
    # rear fender + side panel
    o.append(poly([(-0.70, 0.86), (-1.05, 0.79), (-1.07, 0.75), (-0.75, 0.80), (-0.45, 0.74)], pl, plf, 1.5, dash))
    o.append(poly([(-0.08, 0.90), (-0.62, 0.93), (-0.58, 0.72), (-0.10, 0.62)], pl, plf, 1.5, dash))
    # subframe
    o.append(line([(0.10, 0.80), (-0.78, 0.92)], k, 3, dash))
    o.append(line([(0.02, 0.56), (-0.58, 0.88)], k, 3, dash))
    # main frame: spar + downtube + lower rail
    hb, ht = along_steer(0.62), along_steer(0.80)
    o.append(line([(0.56, 1.00), (0.32, 0.86), (0.10, 0.64), (0.04, 0.48)], k, 4, dash))
    o.append(line([(0.58, 0.93), (0.45, 0.56), (0.38, 0.36), (0.36, 0.33), (-0.02, 0.33), (0.04, 0.48)], k, 4, dash))
    o.append(line([hb, ht], k, 7, dash))                    # head tube
    # fork stubs + triple clamps
    fs = along_steer(0.42)
    o.append(line([(fs[0] + 0.03, fs[1]), (hb[0] + 0.03, hb[1] + 0.02)], k, 9, dash))
    for d in (0.62, 0.80):
        a = along_steer(d)
        o.append(line([(a[0] - 0.03, a[1] - 0.015), (a[0] + 0.07, a[1] + 0.035)], k, 4, dash))
    # bars + grip
    o.append(line([(ht[0] + 0.01, ht[1] + 0.01), (0.50, 1.11), (0.43, 1.13)], k, 4, dash))
    o.append(circle(0.43, 1.13, 0.022, k, "#fff" if not ghost else "none", 2, dash))
    # tank / radiator shrouds
    o.append(poly([(0.28, 0.97), (0.55, 1.01), (0.64, 0.82), (0.57, 0.62), (0.36, 0.60), (0.20, 0.86)], pl, plf, 1.5, dash))
    # seat
    o.append(poly([(0.30, 0.90), (0.28, 0.975), (-0.86, 1.0), (-0.89, 0.95), (-0.84, 0.92), (0.20, 0.885)],
                  k, "#1f2937" if not ghost else "none", 1.5, dash))
    if ghost:
        o.append(rect(-0.02, 0.33, 0.40, 0.60, k, "none", 1.5, dash))
        return o
    # engine-replacement cradle (bolts to the engine mounts)
    o.append(poly([(-0.02, 0.33), (0.36, 0.33), (0.41, 0.50), (0.30, 0.61), (0.06, 0.61), (-0.02, 0.46)],
                  C["stalk"], "url(#cradle)", 2))
    # heave sleeve hidden inside the cradle
    o.append(rect(-0.07, 0.33, 0.07, 0.52, C["stalk"], "none", 1.5, 'stroke-dasharray="5 3"'))
    # bass shakers on the cradle
    for a in (0.20, 0.30):
        o.append(circle(a, 0.43, 0.035, C["ink"], "#9ca3af", 1.5))
    # footpeg + rear brake pedal + shifter
    o.append(rect(-0.03, 0.37, 0.05, 0.395, k, "#374151", 1.5))
    o.append(line([(0.02, 0.43), (0.20, 0.40)], k, 3))
    # FFB motor in the radiator position, belt up to the steering stem
    o.append(rect(0.40, 0.62, 0.53, 0.80, C["ffb"], C["ffb_fill"], 2, f'transform="rotate(-27 {P(0.465, 0.71)[0]:.1f} {P(0.465, 0.71)[1]:.1f})"'))
    pul = along_steer(0.58)
    o.append(line([(0.50, 0.79), (pul[0] - 0.02, pul[1] - 0.01)], C["ffb"], 2.5))
    o.append(line([(0.45, 0.77), (pul[0] - 0.05, pul[1] - 0.04)], C["ffb"], 2.5))
    o.append(circle(pul[0] - 0.03, pul[1] - 0.02, 0.035, C["ffb"], C["ffb_fill"], 2))
    # load-cell markers
    for a, b in ((0.01, 0.36), (0.18, 0.885), (-0.55, 0.92), (0.52, 1.08)):
        x, y = P(a, b)
        o.append(f'<path d="M{x - 6:.1f},{y + 5:.1f} L{x + 6:.1f},{y + 5:.1f} L{x:.1f},{y - 6:.1f} z" fill="{C["sensor"]}"/>')
    return o


def rider_side():
    r = C["rider"]
    d = 'stroke-dasharray="7 5" opacity="0.8"'
    o = [line([(0.02, 0.40), (0.14, 0.72), (-0.13, 1.08), (0.10, 1.52), (0.15, 1.65)], r, 3, d),  # leg, torso, neck
         line([(0.10, 1.50), (0.27, 1.34), (0.43, 1.14)], r, 3, d),                       # arm
         circle(0.18, 1.77, 0.13, r, "none", 3, d),
         rect(0.23, 1.73, 0.33, 1.83, r, "#cbd5e1", 2)]                                     # VR headset
    return o


def gimbal_side():
    o = []
    fx, ff, g, gf = C["fixed"], C["fixed_fill"], C["gimbal"], C["gimbal_fill"]
    # base, large-bore slew ring (open centre), yaw table
    o.append(rect(-1.20, -0.60, 1.20, -0.50, fx, "url(#hatch)", 2))
    o.append(rect(-0.42, -0.50, 0.42, -0.42, fx, ff, 2))
    o.append(rect(-0.05, -0.56, 0.05, -0.47, fx, "#fff", 1.5))                  # slip ring on the base
    o.append(rect(-1.08, -0.42, -0.42, -0.40, fx, ff, 2))                        # yaw table: open ring frame
    o.append(rect(0.42, -0.42, 1.0, -0.40, fx, ff, 2))
    # yaw drives (rear-left + rear-right, ride on the yaw table)
    o.append(rect(-0.38, -0.40, -0.28, -0.26, fx, ff, 1.5))
    # electronics bay (rear, under the wheelie sweep but well below it)
    o.append(rect(-1.05, -0.40, -0.68, -0.22, fx, "#f8fafc", 1.5))
    # roll uprights + roll bearings (axis runs fore-aft through the pivot)
    for a in (-0.60, 0.60):
        o.append(rect(a - 0.035, -0.40, a + 0.035, 0.0, fx, ff, 2))
        o.append(circle(a, 0.0, 0.055, g, gf, 2))
    # roll ring (fore-aft member, behind the hub)
    o.append(rect(-0.60, -0.08, 0.60, -0.02, g, gf, 1.5))
    # roll sector (edge-on at x = +0.40, ahead of the pitch hardware) + roll drives
    o.append(rect(0.385, -0.30, 0.415, -0.02, g, gf, 1.5))
    o.append(rect(0.44, -0.38, 0.82, -0.26, g, gf, 1.5))
    # pitch sector (in this plane) + pitch pinions/motors
    o.append(sector(0.0, 0.0, 0.30, -58, 58, g, gf, 2))
    for s in (-1, 1):
        a, b = 0.36 * math.sin(math.radians(40 * s)), -0.36 * math.cos(math.radians(40 * s))
        o.append(circle(a, b, 0.06, g, "#fff", 2))
        o.append(circle(a, b, 0.012, g, g, 1))
    # stalk (the single rod) - visible below the frame
    o.append(rect(-0.07, 0.0, 0.07, 0.33, C["stalk"], C["stalk_fill"], 2.5))
    o.append(rect(-0.07, -0.06, 0.07, 0.06, g, gf, 2))                          # pitch hub
    # pivot marker
    x, y = P(0, 0)
    o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="#fff" stroke="{C["ink"]}" stroke-width="2.5"/>'
             f'<path d="M{x - 9},{y} A9,9 0 0,1 {x},{y - 9} L{x},{y} z M{x + 9},{y} A9,9 0 0,1 {x},{y + 9} L{x},{y} z" fill="{C["ink"]}"/>')
    return o


def side_view():
    o = [header("MX motion rig — side elevation",
                "Neutral pose, bike facing right. Dashed: rider in attack position, and where the wheels would be.")]
    o += floor_and_ground()
    # ghost wheels
    o.append(circle(-0.60, 0.345, 0.345, C["ghost"], "none", 1.5, 'stroke-dasharray="4 5"'))
    o.append(circle(0.88, 0.36, 0.36, C["ghost"], "none", 1.5, 'stroke-dasharray="4 5"'))
    o.append(text(-0.60, 0.30, "rear tyre", 11, "middle", C["ghost"]))
    o.append(text(-0.60, 0.23, "(removed)", 11, "middle", C["ghost"]))
    o.append(text(0.88, 0.30, "front tyre", 11, "middle", C["ghost"]))
    o.append(text(0.88, 0.23, "(removed)", 11, "middle", C["ghost"]))
    o += gimbal_side()
    o += bike_side()
    o += rider_side()
    # pitch range arc
    r = 1.45 * S
    a0, a1 = math.radians(-22), math.radians(45)
    sx, sy = X0 + r * math.cos(a0), Y0 - r * math.sin(a0)
    ex, ey = X0 + r * math.cos(a1), Y0 - r * math.sin(a1)
    o.append(f'<path d="M{sx:.1f},{sy:.1f} A{r},{r} 0 0,0 {ex:.1f},{ey:.1f}" fill="none" stroke="{C["dim"]}" '
             f'stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>')
    o.append(text(1.08, 1.16, "pitch", 13, fill=C["dim"], weight="600"))
    o.append(text(1.08, 1.08, "+45° / −30°", 12, fill=C["dim"]))
    # dimensions (mm)
    o.append(vdim(905, -PIVOT_H, 0.0, "600 mm"))
    o.append(vdim(905, 0.0, 0.33, "330 mm"))
    o.append(vdim(945, 0.0, 0.97, "≈ 950 mm to seat"))
    o.append(text(912, Y0 - 0.15 * S, "rod", 11, fill=C["dim"], px=True))
    o.append(text(912, Y0 + 0.30 * S, "floor", 11, fill=C["dim"], px=True))
    o.append(text(912, Y0 + 0.30 * S + 13, "to pivot", 11, fill=C["dim"], px=True))
    # numbered callouts: (n, target a, b, bubble a, b)
    cs = [
        (1, -0.90, -0.55, -1.00, -0.80), (3, -0.33, -0.33, -0.55, -0.80), (2, -0.20, -0.46, -0.10, -0.80),
        (7, 0.08, -0.24, 0.35, -0.80), (4, -0.88, -0.31, -1.32, -0.22), (5, 0.60, 0.0, 1.30, 0.12),
        (6, 0.72, -0.32, 1.25, -0.31), (8, 0.0, 0.0, -0.22, 0.12), (9, 0.07, 0.20, 0.30, 0.16),
        (10, 0.02, 0.40, -0.22, 0.46),
    ]
    for c in cs:
        o.append(callout(*c))
    legend = [
        "Base weldment, anchored to the slab",
        "Yaw slew ring + slip ring: unlimited 360°",
        "Yaw drives ×2, preloaded against each other",
        "Yaw table + electronics bay (drives, PCs)",
        "Roll uprights: roll axis runs fore–aft",
        "Roll sector gear + 2 drives (front, below)",
        "Pitch sector gear + 2 drives (hangs below)",
        "PIVOT: roll + pitch axes cross on virtual ground",
        "THE ROD: heave cartridge slides inside",
        "Engine-replacement cradle + bass shakers",
    ]
    for i, t in enumerate(legend):
        col, row = divmod(i, 5)
        bx, by = 50 + col * 470, 850 + row * 30
        o.append(bubble(i + 1, bx, by))
        o.append(text(bx + 20, by + 4.5, t, 13, px=True))
    # inline labels
    o.append(text(0.66, 0.62, "FFB steering motor", 12, fill=C["ffb"], weight="600"))
    o.append(text(0.66, 0.55, "+ belt to stem (2:1)", 12, fill=C["ffb"]))
    o.append(text(-1.05, 1.15, "▲ load cells: pegs,", 12, fill=C["sensor"], weight="600"))
    o.append(text(-1.05, 1.08, "seat ×2, bar mount", 12, fill=C["sensor"]))
    o.append(text(0.36, 1.83, "wireless VR", 12, fill=C["rider"]))
    o.append("</svg>")
    return "\n".join(o)


# --------------------------------------------------------------------------- front view
def bike_front():
    """Everything that rolls, seen from the front (horizontal axis = y, viewer's right = bike's left)."""
    o = []
    g, gf = C["gimbal"], C["gimbal_fill"]
    # roll sector (in this plane) + pitch trunnion bar + pitch drives
    o.append(sector(0.0, 0.0, 0.30, -90, 90, g, gf, 2))
    o.append(rect(-0.30, -0.035, 0.30, 0.035, g, gf, 2))
    o.append(rect(-0.16, -0.38, 0.16, -0.27, g, gf, 1.5))
    o.append(rect(-0.07, 0.0, 0.07, 0.33, C["stalk"], C["stalk_fill"], 2.5))     # the rod
    # cradle + frame
    o.append(rect(-0.13, 0.33, 0.13, 0.61, C["stalk"], "url(#cradle)", 2))
    # pegs + boots
    for s in (-1, 1):
        o.append(rect(s * 0.17, 0.37, s * 0.33, 0.395, C["ink"], "#374151", 1.5))
    # shrouds / tank
    o.append(poly([(-0.12, 1.0), (0.12, 1.0), (0.25, 0.86), (0.24, 0.66), (0.13, 0.60), (-0.13, 0.60),
                   (-0.24, 0.66), (-0.25, 0.86)], C["plastic"], C["plastic_fill"], 1.5))
    # FFB motor (left radiator position = viewer's right)
    o.append(rect(0.10, 0.64, 0.20, 0.80, C["ffb"], C["ffb_fill"], 2))
    # fork stubs + clamps + bars
    for s in (-1, 1):
        o.append(rect(s * 0.085, 0.80, s * 0.135, 0.98, C["ink"], "#9ca3af", 1.5))
    o.append(rect(-0.16, 0.97, 0.16, 1.00, C["ink"], "#374151", 1.5))
    o.append(rect(-0.16, 1.05, 0.16, 1.075, C["ink"], "#374151", 1.5))
    o.append(line([(-0.40, 1.13), (-0.25, 1.11), (0.0, 1.10), (0.25, 1.11), (0.40, 1.13)], C["ink"], 4))
    for s in (-1, 1):
        o.append(circle(s * 0.40, 1.13, 0.022, C["ink"], "#fff", 2))
    # rider
    r = C["rider"]
    d = 'stroke-dasharray="7 5" opacity="0.85"'
    for s in (-1, 1):
        o.append(line([(s * 0.25, 0.40), (s * 0.24, 0.74), (s * 0.15, 1.08)], r, 3, d))
        o.append(line([(s * 0.20, 1.52), (s * 0.44, 1.40), (s * 0.40, 1.15)], r, 3, d))
    o.append(poly([(-0.15, 1.08), (0.15, 1.08), (0.21, 1.53), (-0.21, 1.53)], r, "none", 3, d))
    o.append(circle(0.0, 1.78, 0.13, r, "none", 3, d))
    o.append(rect(-0.10, 1.74, 0.10, 1.82, r, "#cbd5e1", 2))
    return o


def gimbal_front_fixed():
    o = []
    fx, ff = C["fixed"], C["fixed_fill"]
    o.append(rect(-1.20, -0.60, 1.20, -0.50, fx, "url(#hatch)", 2))
    o.append(rect(-0.42, -0.50, 0.42, -0.42, fx, ff, 2))
    o.append(rect(-0.05, -0.56, 0.05, -0.47, fx, "#fff", 1.5))
    o.append(rect(-0.62, -0.42, -0.42, -0.40, fx, ff, 2))
    o.append(rect(0.42, -0.42, 0.62, -0.40, fx, ff, 2))
    o.append(rect(-0.08, -0.40, 0.08, 0.0, fx, ff, 1.5, 'opacity="0.7"'))      # front upright
    for s in (-1, 1):                                                            # roll pinions
        a, b = 0.36 * math.sin(math.radians(30 * s)), -0.36 * math.cos(math.radians(30 * s))
        o.append(circle(a, b, 0.06, C["gimbal"], "#fff", 2))
    o.append(circle(0.0, 0.0, 0.055, C["gimbal"], C["gimbal_fill"], 2))         # roll bearing
    return o


def front_view():
    o = [header("MX motion rig — front elevation",
                "Upright (solid) and full 60° lean (ghost). At 60° the inside peg reaches the virtual ground — same as dragging a peg for real.")]
    o += floor_and_ground(-2.4, 2.4)
    # keep-out + ceiling
    for s in (-1, 1):
        xk = X0 + s * 2.0 * S
        o.append(f'<line x1="{xk}" y1="{FLOOR_Y}" x2="{xk}" y2="120" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="3 5"/>')
    o.append(text(X0 + 2.0 * S - 6, 136, "keep-out 2.0 m", 12, "end", "#dc2626", px=True))
    o.append(text(X0 - 2.0 * S + 6, 136, "keep-out 2.0 m", 12, "start", "#dc2626", px=True))
    yc = FLOOR_Y - 3.0 * S
    o.append(f'<line x1="{X0 - 2.4 * S}" y1="{yc}" x2="{X0 + 2.4 * S}" y2="{yc}" stroke="{C["fixed"]}" stroke-width="2" stroke-dasharray="12 4"/>')
    o.append(text(X0, yc - 8, "minimum ceiling 3.0 m", 12, "middle", C["fixed"], px=True))
    o += gimbal_front_fixed()
    o.append(f'<g transform="rotate(60 {X0} {Y0})" opacity="0.32">' + "".join(bike_front()) + "</g>")
    o += bike_front()
    # pivot marker
    o.append(f'<circle cx="{X0}" cy="{Y0}" r="9" fill="#fff" stroke="{C["ink"]}" stroke-width="2.5"/>'
             f'<path d="M{X0 - 9},{Y0} A9,9 0 0,1 {X0},{Y0 - 9} L{X0},{Y0} z M{X0 + 9},{Y0} A9,9 0 0,1 {X0},{Y0 + 9} L{X0},{Y0} z" fill="{C["ink"]}"/>')
    # lean arc
    r = 1.25 * S
    a1 = math.radians(60)
    ex, ey = X0 + r * math.sin(a1), Y0 - r * math.cos(a1)
    o.append(f'<path d="M{X0},{Y0 - r} A{r},{r} 0 0,1 {ex:.1f},{ey:.1f}" fill="none" stroke="{C["dim"]}" stroke-width="1.5" marker-end="url(#arr)"/>')
    o.append(text(X0 + 0.55 * S, Y0 - 1.30 * S, "roll ±60°", 13, fill=C["dim"], weight="600", px=True))
    # head sweep
    hx = X0 + 1.93 * math.sin(a1) * S
    o.append(f'<line x1="{X0}" y1="{Y0 - 2.08 * S}" x2="{hx:.1f}" y2="{Y0 - 2.08 * S}" stroke="{C["dim"]}" stroke-width="1" marker-start="url(#arr)" marker-end="url(#arr)"/>')
    o.append(text((X0 + hx) / 2, Y0 - 2.08 * S - 8, "head moves 1.67 m sideways", 12, "middle", C["dim"], px=True))
    # notes
    notes = [
        "• Roll pivots on the virtual ground, like a real bike leaning on its tyres — so lean feels right with no software fakery.",
        "• All roll and pitch drives hang BELOW the pivot. Nothing pokes up where the boots and the bike's belly swing.",
        "• Inside peg at 60°: the real-world peg-drag angle. Whips past 60° are carried by VR visuals + onset cue.",
        "• Pivot 0.6 m off the floor gives room for the hanging drives and keeps a dangled foot clear of the floor.",
    ]
    for i, n in enumerate(notes):
        o.append(text(30, 880 + i * 26, n, 13, px=True))
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "side-view.svg").write_text(side_view())
    (OUT / "front-view.svg").write_text(front_view())
    print("wrote", OUT / "side-view.svg", "and", OUT / "front-view.svg")
