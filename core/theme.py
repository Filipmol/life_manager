"""
Centralised dark-mode color palette and style helpers.
Based on the Nexus dark-mode design system.
Compatible with Flet >= 0.82.
"""

from __future__ import annotations
import flet as ft

# ─── Colors ──────────────────────────────────────────────────────────
BG          = "#171614"
SURFACE     = "#1C1B19"
SURFACE_ALT = "#201F1D"
BORDER      = "#393836"
TEXT        = "#CDCCCA"
TEXT_MUTED  = "#797876"
TEXT_FAINT  = "#5A5957"
PRIMARY     = "#4F98A3"
PRIMARY_HVR = "#227F8B"
ERROR       = "#D163A7"
WARNING     = "#BB653B"
SUCCESS     = "#6DAA45"

TEAL        = "#20808D"
TERRA       = "#A84B2F"
DARK_TEAL   = "#1B474D"
LIGHT_CYAN  = "#BCE2E7"
MAUVE       = "#944454"
GOLD        = "#FFC553"

# ─── Helpers ─────────────────────────────────────────────────────────

def card(content: ft.Control, padding: int = 20, width: int | None = None, expand: bool = False) -> ft.Container:
    """Standard card container."""
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border_radius=12,
        border=ft.Border.all(1, BORDER),
        padding=padding,
        width=width,
        expand=expand,
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )


def heading(text: str, size: int = 22) -> ft.Text:
    return ft.Text(text, size=size, weight=ft.FontWeight.W_600, color=TEXT)


def subheading(text: str, size: int = 14) -> ft.Text:
    return ft.Text(text, size=size, color=TEXT_MUTED)


def stat_value(value: str, size: int = 32) -> ft.Text:
    return ft.Text(value, size=size, weight=ft.FontWeight.W_700, color=PRIMARY)


def icon_circle(icon, color: str = PRIMARY, size: int = 40) -> ft.Container:
    return ft.Container(
        content=ft.Icon(icon, color=color, size=20),
        width=size,
        height=size,
        bgcolor=color + "1A",  # ~10% alpha
        border_radius=size // 2,
        alignment=ft.Alignment(0, 0),
    )


def primary_button(label: str, on_click, icon=None, width: int | None = None) -> ft.Button:
    return ft.Button(
        content=label,
        icon=icon,
        on_click=on_click,
        bgcolor=PRIMARY,
        color="#FFFFFF",
        width=width,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        ),
    )


def outline_button(label: str, on_click, icon=None) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        content=label,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=TEXT_MUTED,
            shape=ft.RoundedRectangleBorder(radius=8),
            side=ft.BorderSide(1, BORDER),
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        ),
    )


def text_field(label: str, hint: str = "", multiline: bool = False, expand: bool = False, value: str = "") -> ft.TextField:
    return ft.TextField(
        label=label,
        hint_text=hint,
        value=value,
        multiline=multiline,
        min_lines=1 if not multiline else 3,
        max_lines=1 if not multiline else 8,
        expand=expand,
        bgcolor=SURFACE_ALT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        hint_style=ft.TextStyle(color=TEXT_FAINT),
        cursor_color=PRIMARY,
        border_radius=8,
    )
