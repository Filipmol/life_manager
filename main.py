"""
Ultimate Daily Life Manager — main entry point.
Initialises the database, sets up the dark theme, builds the navigation
rail, and renders each view.
"""

import flet as ft
from core.database import init_db
from core import theme as T
from views import dashboard, food, fitness, tasks


def main(page: ft.Page):
    # ── Window setup ─────────────────────────────────────────────────
    page.title = "Life Manager"
    page.bgcolor = T.BG
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 600
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=T.PRIMARY,
        font_family="Segoe UI, Roboto, sans-serif",
    )

    # ── Database ─────────────────────────────────────────────────────
    init_db()

    # ── Content area ─────────────────────────────────────────────────
    content_area = ft.Container(expand=True, padding=24)

    def navigate(index: int):
        nav_rail.selected_index = index
        load_view(index)
        page.update()

    def load_view(index: int):
        if index == 0:
            content_area.content = dashboard.build(page, navigate)
        elif index == 1:
            content_area.content = food.build(page)
        elif index == 2:
            content_area.content = fitness.build(page)
        elif index == 3:
            content_area.content = tasks.build(page)
        page.update()

    # ── Navigation rail ──────────────────────────────────────────────
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=200,
        bgcolor=T.SURFACE,
        indicator_color=T.PRIMARY + "25",
        on_change=lambda e: load_view(e.control.selected_index),
        leading=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.DASHBOARD_CUSTOMIZE, color=T.PRIMARY, size=28),
                    ft.Text("Life", size=11, weight=ft.FontWeight.W_700, color=T.PRIMARY),
                    ft.Text("Manager", size=9, color=T.TEXT_MUTED),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=ft.Padding.only(top=16, bottom=20),
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.DASHBOARD_OUTLINED, color=T.TEXT_MUTED),
                selected_icon=ft.Icon(ft.Icons.DASHBOARD, color=T.PRIMARY),
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.RESTAURANT_OUTLINED, color=T.TEXT_MUTED),
                selected_icon=ft.Icon(ft.Icons.RESTAURANT, color=T.GOLD),
                label="Food",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.FITNESS_CENTER_OUTLINED, color=T.TEXT_MUTED),
                selected_icon=ft.Icon(ft.Icons.FITNESS_CENTER, color=T.SUCCESS),
                label="Fitness",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.VIEW_KANBAN_OUTLINED, color=T.TEXT_MUTED),
                selected_icon=ft.Icon(ft.Icons.VIEW_KANBAN, color=T.PRIMARY),
                label="Tasks",
            ),
        ],
    )

    # ── Page layout ──────────────────────────────────────────────────
    page.add(
        ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1, color=T.BORDER),
                content_area,
            ],
            expand=True,
            spacing=0,
        )
    )

    # Load dashboard on start
    load_view(0)


if __name__ == "__main__":
    ft.run(main)
