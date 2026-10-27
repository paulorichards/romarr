"""The shape of a cover box, and why one number for every platform is wrong.

A SNES box is landscape, a Super Famicom box is tall, and PlayStation and
Game Boy Advance covers are square. The grid drew all of them in `3/4` with
`background-size: cover`, so `3 Ninjas Kick Back` lost half its width and
read "NJAS / CK BACK". Measured on a 16,522-cover library: with one shape for
everything, 41% of covers cropped by 15% or less.

RomM is the only backend that reports a per-platform shape, and only from
5.4.2 (the column existed since its migration 0027 but never reached the API).
Every other backend reports none, and must keep the layout default.

The value reaches a `style` attribute, so it is parsed and bounded here rather
than trusted: a library server is not the same trust domain as this process.
"""

from __future__ import annotations

import json

from romarr.clients import Romm, RommConfig
from romarr.libraries import COVER_RATIO_MAX, COVER_RATIO_MIN, cover_ratio


# ------------------------------------------------------------- parsing --

def test_reads_the_shapes_romm_stores():
    assert cover_ratio("2 / 3") == 2 / 3
    assert cover_ratio("2/3") == 2 / 3
    assert cover_ratio("1.41") == 1.41
    assert cover_ratio("140 / 188") == 140 / 188
    assert cover_ratio(1.58) == 1.58


def test_refuses_anything_that_is_not_a_ratio():
    """`2/3;background:url(x)` in a style attribute is CSS injection, and the
    server validating on write is not a reason to trust the wire."""
    for value in ("2/3;background:url(x)", "calc(2/3)", "var(--r)",
                  "2 / 3 !important", "abc", "", None, True, [], {}):
        assert cover_ratio(value) is None, value


def test_refuses_a_zero_or_negative_side():
    for value in ("0 / 3", "2 / 0", "-2 / 3", "0", 0, -1.5):
        assert cover_ratio(value) is None, value


def test_refuses_a_slit_or_a_stripe():
    """Outside the bounds the box is a broken page, not a chosen shape."""
    assert cover_ratio(str(COVER_RATIO_MIN / 2)) is None
    assert cover_ratio(str(COVER_RATIO_MAX * 2)) is None
    assert cover_ratio(str(COVER_RATIO_MIN)) == COVER_RATIO_MIN
    assert cover_ratio(str(COVER_RATIO_MAX)) == COVER_RATIO_MAX


# --------------------------------------------------------- the backend --

class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200
        self.ok = True
        self.text = json.dumps(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class PlatformsSession:
    """A RomM 5.4.2: `/api/platforms` carries `aspect_ratio`."""

    ROWS = [
        {"slug": "snes", "display_name": "Super Nintendo Entertainment System",
         "rom_count": 3930, "aspect_ratio": "1.58"},
        {"slug": "psx", "display_name": "PlayStation",
         "rom_count": 2013, "aspect_ratio": "1.10"},
        # No shape reported: this one keeps the layout default.
        {"slug": "gb", "display_name": "Game Boy", "rom_count": 1237},
        # Hostile value from the wire.
        {"slug": "nes", "display_name": "Nintendo Entertainment System",
         "rom_count": 3250, "aspect_ratio": "1;background:url(x)"},
        # RomM ships 393 platforms and most hold nothing.
        {"slug": "empty", "display_name": "Empty", "rom_count": 0,
         "aspect_ratio": "1.0"},
    ]

    def get(self, url, **kw):
        return FakeResponse(self.ROWS)

    def post(self, url, **kw):
        return FakeResponse({"access_token": "t"})


def romm(session):
    return Romm(RommConfig(base_url="http://romm", username="u", password="p"),
                session=session)


def test_platforms_carry_the_shape_romm_reports():
    rows = {p["slug"]: p for p in romm(PlatformsSession()).platforms()}

    assert rows["snes"]["cover_ratio"] == 1.58
    assert rows["psx"]["cover_ratio"] == 1.10


def test_a_platform_without_a_shape_gets_none():
    """Every backend but RomM reports none, and so does an older RomM. The
    grid has to keep the shape it always had rather than collapse."""
    rows = {p["slug"]: p for p in romm(PlatformsSession()).platforms()}

    assert rows["gb"]["cover_ratio"] is None


def test_a_hostile_shape_is_dropped_not_passed_through():
    rows = {p["slug"]: p for p in romm(PlatformsSession()).platforms()}

    assert rows["nes"]["cover_ratio"] is None


def test_an_empty_platform_is_still_left_out():
    """Unchanged behaviour: a shape does not make a platform worth listing."""
    slugs = {p["slug"] for p in romm(PlatformsSession()).platforms()}

    assert "empty" not in slugs
