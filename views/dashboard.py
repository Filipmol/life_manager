"""
Dashboard view — real-time summary of today's stats, Ollama status,
and quick-access cards for every section.
"""

import flet as ft
from datetime import datetime
from core import database as db
from core import ollama_client as ai
from core import theme as T


def build(page: ft.Page, navigate_cb) -> ft.Control:
    """Return the dashboard view. navigate_cb(index) switches tabs."""

    stats = db.get_dashboard_stats()
    ollama_ok = ai.is_ollama_running()
    models = ai.list_models() if ollama_ok else []
    now = datetime.now()

    # ── Greeting ─────────────────────────────────────────────────────
    hour = now.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    greeting_row = ft.Column(
        [
            ft.Text(
                f"{greeting}.",
                size=28,
                weight=ft.FontWeight.W_700,
                color=T.TEXT,
            ),
            ft.Text(
                now.strftime("%A, %B %d, %Y"),
                size=14,
                color=T.TEXT_MUTED,
            ),
        ],
        spacing=4,
    )

    # ── AI status chip ───────────────────────────────────────────────
    if ollama_ok:
        model_label = models[0] if models else "no models"
        ai_chip = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=8, height=8, bgcolor=T.SUCCESS,
                        border_radius=4,
                    ),
                    ft.Text(f"Ollama online  ·  {model_label}", size=12, color=T.SUCCESS),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=T.SUCCESS + "15",
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=14, vertical=6),
        )
    else:
        ai_chip = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=8, height=8, bgcolor=T.ERROR,
                        border_radius=4,
                    ),
                    ft.Text("Ollama offline", size=12, color=T.ERROR),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=T.ERROR + "15",
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=14, vertical=6),
        )

    header = ft.Row(
        [greeting_row, ai_chip],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    # ── Stat cards ───────────────────────────────────────────────────
    def stat_card(icon, icon_color, label, value, sub=""):
        return T.card(
            ft.Column(
                [
                    ft.Row(
                        [
                            T.icon_circle(icon, icon_color),
                            ft.Column(
                                [
                                    ft.Text(label, size=12, color=T.TEXT_MUTED),
                                    ft.Text(
                                        str(value),
                                        size=28,
                                        weight=ft.FontWeight.W_700,
                                        color=T.TEXT,
                                    ),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                        ],
                        spacing=14,
                    ),
                    ft.Text(sub, size=11, color=T.TEXT_FAINT) if sub else ft.Container(),
                ],
                spacing=8,
            ),
            expand=True,
        )

    tasks_done_pct = (
        f"{round(stats['done_tasks'] / stats['total_tasks'] * 100)}% done"
        if stats["total_tasks"] > 0
        else "No tasks yet"
    )

    stat_row = ft.Row(
        [
            stat_card(
                ft.Icons.CHECK_CIRCLE_OUTLINE,
                T.PRIMARY,
                "Tasks",
                stats["total_tasks"],
                tasks_done_pct,
            ),
            stat_card(
                ft.Icons.RESTAURANT,
                T.GOLD,
                "Recipes",
                stats["total_recipes"],
                f"{stats['recipes_today']} today",
            ),
            stat_card(
                ft.Icons.FITNESS_CENTER,
                T.SUCCESS,
                "Workouts",
                stats["total_workouts"],
                f"{stats['workouts_today']} today",
            ),
            stat_card(
                ft.Icons.WARNING_AMBER_ROUNDED,
                T.WARNING if stats["overdue_tasks"] > 0 else T.TEXT_FAINT,
                "Overdue",
                stats["overdue_tasks"],
                "Need attention" if stats["overdue_tasks"] > 0 else "All clear",
            ),
        ],
        spacing=16,
    )

    # ── Kanban mini-preview ──────────────────────────────────────────
    def mini_column(title, count, color):
        return ft.Column(
            [
                ft.Text(title, size=12, color=T.TEXT_MUTED),
                ft.Text(str(count), size=24, weight=ft.FontWeight.W_700, color=color),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

    kanban_preview = T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        T.heading("Task Board", 18),
                        T.outline_button("Open", lambda _: navigate_cb(3), ft.Icons.ARROW_FORWARD),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=1, color=T.BORDER),
                ft.Row(
                    [
                        mini_column("To Do", stats["todo_tasks"], T.TEXT),
                        ft.VerticalDivider(width=1, color=T.BORDER),
                        mini_column("Doing", stats["doing_tasks"], T.WARNING),
                        ft.VerticalDivider(width=1, color=T.BORDER),
                        mini_column("Done", stats["done_tasks"], T.SUCCESS),
                    ],
                    spacing=0,
                    height=70,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=12,
        ),
    )

    # ── Quick-access cards ───────────────────────────────────────────
    def quick_card(icon, icon_color, title, desc, tab_index):
        return ft.GestureDetector(
            on_tap=lambda _: navigate_cb(tab_index),
            content=T.card(
                ft.Row(
                    [
                        T.icon_circle(icon, icon_color, 44),
                        ft.Column(
                            [
                                ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=T.TEXT),
                                ft.Text(desc, size=12, color=T.TEXT_MUTED),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color=T.TEXT_FAINT, size=20),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True,
            ),
            mouse_cursor=ft.MouseCursor.CLICK,
        )

    quick_row = ft.Row(
        [
            quick_card(ft.Icons.RESTAURANT, T.GOLD, "Food & Recipes", "Generate AI recipes", 1),
            quick_card(ft.Icons.FITNESS_CENTER, T.SUCCESS, "Fitness", "AI workout plans", 2),
            quick_card(ft.Icons.VIEW_KANBAN, T.PRIMARY, "Tasks", "Kanban board", 3),
        ],
        spacing=16,
    )

    # ── Setup guide (shown when Ollama is offline) ───────────────────
    setup_guide = ft.Container() if ollama_ok else T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=T.WARNING, size=20),
                        ft.Text(
                            "Ollama is not running",
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color=T.WARNING,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "AI features (recipe generation, workout plans) require Ollama.\n"
                    "1. Install Ollama from https://ollama.com\n"
                    "2. Open a terminal and run: ollama pull llama3.2\n"
                    "3. Keep Ollama running, then restart this app.",
                    size=13,
                    color=T.TEXT_MUTED,
                ),
            ],
            spacing=8,
        ),
    )

    return ft.Container(
        content=ft.Column(
            [
                header,
                stat_row,
                kanban_preview,
                quick_row,
                setup_guide,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
        padding=ft.Padding.only(bottom=20),
    )
