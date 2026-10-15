"""Channel router for the neuron layout.

Every connection is a pin -> channel hookup:
  via1 on the pin's metal1, a metal2 riser to the channel, via2 onto the net's metal3 track.
Each channel holds one horizontal metal3 track per net, spanning that net's hookups.
Nets that appear in several channels are joined by metal2 "spines" at given x positions.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from maglib import (Cell, Inst, Rect, RISER_W, TRACK_PITCH, TRACK_W, VIA1_PAD, VIA2_PAD_M2, VIA2_PAD_M3,
                    snap)


@dataclass
class Channel:
    name: str
    y0: float                      # centre y of track 0
    nets: list = field(default_factory=list)   # track order, bottom to top

    def y(self, net):
        return snap(self.y0 + self.nets.index(net) * TRACK_PITCH)

    @property
    def top(self):
        return self.y0 + (len(self.nets) - 1) * TRACK_PITCH + VIA2_PAD_M3 / 2

    @property
    def bottom(self):
        return self.y0 - VIA2_PAD_M3 / 2


class Router:
    def __init__(self, cell: Cell):
        self.cell = cell
        self.channels: dict[str, Channel] = {}
        self.taps: dict[tuple, list] = {}       # (channel, net) -> [x] track extent
        self.vias: dict[tuple, list] = {}       # (channel, net) -> [x] via2 positions

    def channel(self, name, y0, nets):
        ch = Channel(name, y0, list(nets))
        self.channels[name] = ch
        return ch

    def hook(self, inst: Inst, pin: str, chan: str, net: str, x: float | None = None,
             inset: float = 0.45):
        """Connect inst.pin to net's track in channel chan.

        Vertical metal1 strips (drain/source/ring) get the via `inset` um inside the strip end
        facing the channel. Horizontal pads (gates) get the via on the pad, padded away from the
        device so the metal1 extension never approaches the drain/source strips.
        """
        c = self.cell
        r = inst.pin(pin)
        ch = self.channels[chan]
        ty = ch.y(net)
        up = ty > r.cy
        vx = snap(x if x is not None else r.cx)
        if r.h >= r.w:                                    # vertical strip
            vy = snap(r.y2 - inset if up else r.y1 + inset)
            c.via1(vx, vy)
        else:                                             # horizontal pad (gate)
            # metal1 pad grown only on the side facing away from the device body
            body = inst.box
            away_up = r.cy > body.cy
            if away_up:
                vy = snap(r.y1 + VIA1_PAD / 2)
            else:
                vy = snap(r.y2 - VIA1_PAD / 2)
            c.via1(vx, vy)
        c.vwire("metal2", vx, vy, ty, RISER_W)
        c.via2(vx, ty)
        self.taps.setdefault((chan, net), []).append(vx)
        self.vias.setdefault((chan, net), []).append(vx)

    def tap(self, chan, net, x):
        """Register an extra point on a track (e.g. a spine or a port) and drop a via2."""
        self.cell.via2(snap(x), self.channels[chan].y(net))
        self.taps.setdefault((chan, net), []).append(snap(x))
        self.vias.setdefault((chan, net), []).append(snap(x))

    def spine(self, net, x, chans):
        """Metal2 vertical joining net's tracks in several channels at x."""
        ys = [self.channels[ch].y(net) for ch in chans]
        self.cell.vwire("metal2", x, min(ys), max(ys), RISER_W)
        for ch in chans:
            self.tap(ch, net, x)

    def extend(self, chan, net, x):
        """Make net's track reach x (e.g. the block edge for a port) without a via."""
        self.taps.setdefault((chan, net), []).append(snap(x))

    def draw_tracks(self):
        for (chan, net), xs in self.taps.items():
            y = self.channels[chan].y(net)
            # via2 metal2 pads of the same net closer than pad + spacing would leave a
            # sub-minimum metal2 gap: bridge them
            pts = sorted(set(self.vias.get((chan, net), [])))
            for a, b in zip(pts, pts[1:]):
                if b - a < VIA2_PAD_M2 + 0.14 + 0.01:
                    self.cell.rect("metal2", Rect(a, y - VIA2_PAD_M2 / 2, b, y + VIA2_PAD_M2 / 2))
            x1, x2 = min(xs), max(xs)
            if x2 - x1 < VIA2_PAD_M3:
                x1, x2 = (x1 + x2) / 2 - VIA2_PAD_M3 / 2, (x1 + x2) / 2 + VIA2_PAD_M3 / 2
            self.cell.hwire("metal3", x1, x2, y, TRACK_W)

    def port(self, chan, net, x, index, use="signal"):
        """Label net's metal3 track at x as a cell port."""
        y = self.channels[chan].y(net)
        self.extend(chan, net, x)
        self.cell.label(net, "metal3", Rect(snap(x) - 0.1, y - 0.1, snap(x) + 0.1, y + 0.1), index, use)
