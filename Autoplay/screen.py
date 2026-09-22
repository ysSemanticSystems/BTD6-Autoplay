"""Retina-aware screen mapping from the 1920x1080 design space."""
from __future__ import annotations

from dataclasses import dataclass

from PIL import ImageGrab

from config import DESIGN_HEIGHT, DESIGN_WIDTH


@dataclass
class ScreenInfo:
    logical_width: int
    logical_height: int
    pixel_width: int
    pixel_height: int
    scale: float

    def to_logical(self, design_x: float, design_y: float) -> tuple[int, int]:
        return (
            int(round(design_x / DESIGN_WIDTH * self.logical_width)),
            int(round(design_y / DESIGN_HEIGHT * self.logical_height)),
        )

    def to_pixel_bbox(self, left: float, top: float, right: float, bottom: float) -> tuple[int, int, int, int]:
        """Convert a 1920x1080 design bbox into an ImageGrab pixel bbox."""
        lx, ty = self.to_logical(left, top)
        rx, by = self.to_logical(right, bottom)
        return (
            int(lx * self.scale),
            int(ty * self.scale),
            int(rx * self.scale),
            int(by * self.scale),
        )

    def pixel_to_logical(self, px: float, py: float) -> tuple[int, int]:
        return int(round(px / self.scale)), int(round(py / self.scale))

    def template_scale(self) -> tuple[float, float]:
        """How much to resize a 1920x1080-era template to match a current screenshot."""
        return (
            self.pixel_width / DESIGN_WIDTH,
            self.pixel_height / DESIGN_HEIGHT,
        )


_INFO: ScreenInfo | None = None


def detect_screen() -> ScreenInfo:
    try:
        import Quartz

        display = Quartz.CGMainDisplayID()
        logical_w = Quartz.CGDisplayPixelsWide(display)
        logical_h = Quartz.CGDisplayPixelsHigh(display)
        mode = Quartz.CGDisplayCopyDisplayMode(display)
        pixel_w = int(Quartz.CGDisplayModeGetPixelWidth(mode))
        pixel_h = int(Quartz.CGDisplayModeGetPixelHeight(mode))
        scale = pixel_w / logical_w if logical_w else 1.0
        return ScreenInfo(logical_w, logical_h, pixel_w, pixel_h, scale)
    except Exception:
        pass

    import pyautogui

    logical_w, logical_h = pyautogui.size()
    shot = ImageGrab.grab()
    pixel_w, pixel_h = shot.size
    scale = pixel_w / logical_w if logical_w else 1.0
    return ScreenInfo(logical_w, logical_h, pixel_w, pixel_h, scale)


def get_screen() -> ScreenInfo:
    global _INFO
    if _INFO is None:
        _INFO = detect_screen()
    return _INFO


def refresh_screen() -> ScreenInfo:
    global _INFO
    _INFO = detect_screen()
    return _INFO
