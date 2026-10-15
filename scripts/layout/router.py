"""Channel router for the neuron layout.

Every connection is a pin -> channel hookup:
  via1 on the pin's metal1, a metal2 riser to the channel, via2 onto the net's metal3 track.
Hookups are collected first; finalize() then assigns tracks per channel with the left-edge
algorithm (nets whose spans do not overlap share a track) and draws everything.
Nets present in several channels are joined by metal2 spines at given x positions.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from maglib import (Cell, Inst, Rect, RISER_W, TRACK_PITCH, TRACK_W, VIA1_PAD, VIA2_PAD_M2,
                    VIA2_PAD_M3, snap)

M3_SPACE = 0.30
M2_SPACE = 0.14


@dataclass
class Channel:
    name: str
    y0: float                 # centre y of track 0
    max_tracks: int
    down: bool = False        # tracks stack downward from y0
    fixed: dict = field(default_factory=dict)    # net -> track index (e.g. power rails)
    track: dict = field(default_factory=dict)    # net -> track index (after finalize)

    def y(self, net):
        k = self.track[net]
        return snap(self.y0 - k * TRACK_PITCH if self.down else self.y0 + k * TRACK_PITCH)

    def span_y(self):
        """(lowest, highest) metal extent the channel may use."""
        far = self.y0 + (-1 if self.down else 1) * (self.max_tracks - 1) * TRACK_PITCH
        lo, hi = min(self.y0, far), max(self.y0, far)
        return lo - VIA2_PAD_M3 / 2, hi + VIA2_PAD_M3 / 2


@dataclass
class Hook:
    chan: str
    net: str
    x: float
    via1_y: float | None      # riser start y (None for a plain via2 tap, e.g. a spine end)
    start: str = "via1"       # "via1": starts on metal1; "via2": starts on metal3 (macro port, cap plate)


class Router:
    def __init__(self, cell: Cell):
        self.cell = cell
        self.channels: dict[str, Channel] = {}
        self.hooks: list[Hook] = []
        self.extents: dict[tuple, list] = {}     # (chan, net) -> extra x the track must reach
        self.spines: list[tuple] = []            # (net, x, chans)
        self.ports: list[tuple] = []

    def channel(self, name, y0, max_tracks, down=False, fixed=None):
        ch = Channel(name, y0, max_tracks, down, dict(fixed or {}))
        self.channels[name] = ch
        return ch

    # ------------------------------------------------------------ requests
    def hook(self, inst: Inst, pin: str, chan: str, net: str, x: float | None = None,
             inset: float = 0.45, dx: float = 0.0):
        """Connect inst.pin to net's track in chan.

        Vertical metal1 strips (drain/source/ring/resistor head) get the via `inset` um inside
        the strip end facing the channel. Horizontal pads (gates) get the via flush with the pad
        edge nearest the device body, so the metal1 pad only grows away from the device.
        dx moves the via sideways off a vertical strip with a metal1 jog (used on short-L devices
        where the drain/source riser would pass too close to the gate via).
        """
        r = inst.pin(pin)
        ch = self.channels[chan]
        up = ch.y0 > r.cy
        vx = snap(x if x is not None else r.cx)
        if r.h >= r.w:
            vy = snap(r.y2 - inset if up else r.y1 + inset)
            if r.h < 2 * inset:                    # short pad: centre it
                vy = snap(r.cy)
            if dx:
                vx = snap(r.cx + dx)
                self.cell.rect("metal1", Rect(min(r.cx, vx) - VIA1_PAD / 2, vy - VIA1_PAD / 2,
                                              max(r.cx, vx) + VIA1_PAD / 2, vy + VIA1_PAD / 2))
        else:
            away_up = r.cy > inst.box.cy
            vy = snap(r.y1 + VIA1_PAD / 2 if away_up else r.y2 - VIA1_PAD / 2)
        self.hooks.append(Hook(chan, net, vx, vy))

    def hook_m3(self, x, y, chan, net):
        """Connect a metal3 point (macro port extension, capacitor plate tab) to net's track:
        via2 at (x, y), metal2 riser, via2 on the track."""
        self.hooks.append(Hook(chan, net, snap(x), snap(y), "via2"))

    def tap(self, chan, net, x):
        self.hooks.append(Hook(chan, net, snap(x), None))

    def spine(self, net, x, chans):
        self.spines.append((net, snap(x), tuple(chans)))
        for ch in chans:
            self.tap(ch, net, x)

    def extend(self, chan, net, x):
        self.extents.setdefault((chan, net), []).append(snap(x))

    def port(self, chan, net, x, index, use="signal"):
        self.extend(chan, net, x)
        self.ports.append((chan, net, snap(x), index, use))

    # ------------------------------------------------------------ solve + draw
    RISER_SEP = 0.60    # risers closer than this (centre to centre) must not overlap in y

    def _assign(self):
        """Left-edge track assignment with vertical constraints.

        A riser arriving from above (via1 above the channel) at x and one arriving from below at
        x' with |x - x'| < RISER_SEP would overlap if the upper net's track lay below the lower
        net's track; such pairs force track(upper) > track(lower) (in geometric terms). Tracks are
        then filled bottom-up: at each level, nets whose lower neighbours are already placed are
        packed left to right.
        """
        for name, ch in self.channels.items():
            spans, above, below = {}, [], []
            for h in self.hooks:
                if h.chan != name:
                    continue
                spans.setdefault(h.net, []).append(h.x)
                if h.via1_y is not None:
                    (above if h.via1_y > ch.y0 else below).append((h.x, h.net))
            for (cn, net), xs in self.extents.items():
                if cn == name:
                    spans.setdefault(net, []).extend(xs)
            # same-side risers of different nets must be far enough apart that one can pass the
            # other's via2 pad (0.37 wide) with metal2 spacing: pad/2 + riser/2 + 0.14
            min_same = VIA2_PAD_M2 / 2 + RISER_W / 2 + M2_SPACE
            for side in (above, below):
                for i, (xa, na) in enumerate(side):
                    for xb, nb in side[i + 1:]:
                        if na != nb and abs(xa - xb) < min_same - 1e-9:
                            raise RuntimeError(f"channel {name}: risers {na}@{xa} and {nb}@{xb} "
                                               f"closer than {min_same:.3f} um on the same side")
            # constraint: hi must be geometrically above lo
            must_below = {n: set() for n in spans}       # net -> nets that must be under it
            for xa, na in above:
                for xb, nb in below:
                    if na != nb and abs(xa - xb) < self.RISER_SEP:
                        must_below[na].add(nb)
            half = VIA2_PAD_M3 / 2 + M3_SPACE / 2
            ext = {n: (min(xs) - half, max(xs) + half) for n, xs in spans.items()}
            # work in "levels" counted geometrically upward
            nlev = ch.max_tracks
            to_level = (lambda k: nlev - 1 - k) if ch.down else (lambda k: k)
            level = {}
            for net, k in ch.fixed.items():
                if net in spans:
                    level[net] = to_level(k)
            lev = 0
            while len(level) < len(spans):
                if lev >= nlev:
                    raise RuntimeError(f"channel {name}: needs more than {nlev} tracks; placed "
                                       f"{level}, left {sorted(set(spans) - set(level))}")
                occupied = [ext[n] for n, l in level.items() if l == lev]
                fixed_here = any(to_level(k) == lev for k in ch.fixed.values())
                ready = sorted((ext[n][0], n) for n in spans if n not in level
                               and all(m in level and level[m] < lev for m in must_below[n]))
                if not fixed_here:
                    for _, n in ready:
                        x1, x2 = ext[n]
                        if all(x2 <= a or x1 >= b for a, b in occupied):
                            level[n] = lev
                            occupied.append((x1, x2))
                lev += 1
            for net, l in level.items():
                ch.track[net] = (nlev - 1 - l) if ch.down else l
            # sanity: constraints hold
            for n, lows in must_below.items():
                for m in lows:
                    if not level[n] > level[m]:
                        raise RuntimeError(f"channel {name}: constraint {n} above {m} violated")

    def finalize(self):
        self._assign()
        c = self.cell
        vias = {}
        for h in self.hooks:
            ty = self.channels[h.chan].y(h.net)
            if h.via1_y is not None:
                (c.via1 if h.start == "via1" else c.via2)(h.x, h.via1_y)
                c.vwire("metal2", h.x, h.via1_y, ty, RISER_W)
            c.via2(h.x, ty)
            vias.setdefault((h.chan, h.net), []).append(h.x)
        for net, x, chans in self.spines:
            ys = [self.channels[ch].y(net) for ch in chans]
            c.vwire("metal2", x, min(ys), max(ys), RISER_W)
        keys = set(vias) | set(self.extents)
        for key in keys:
            chan, net = key
            y = self.channels[chan].y(net)
            pts = sorted(set(vias.get(key, [])))
            for a, b in zip(pts, pts[1:]):                       # bridge close metal2 pads
                if b - a < VIA2_PAD_M2 + M2_SPACE + 0.01:
                    c.rect("metal2", Rect(a, y - VIA2_PAD_M2 / 2, b, y + VIA2_PAD_M2 / 2))
            xs = pts + self.extents.get(key, [])
            x1, x2 = min(xs), max(xs)
            if x2 - x1 < VIA2_PAD_M3:
                x1, x2 = (x1 + x2) / 2 - VIA2_PAD_M3 / 2, (x1 + x2) / 2 + VIA2_PAD_M3 / 2
            c.hwire("metal3", x1, x2, y, TRACK_W)
        for chan, net, x, index, use in self.ports:
            y = self.channels[chan].y(net)
            c.label(net, "metal3", Rect(x - 0.1, y - 0.1, x + 0.1, y + 0.1), index, use)
