"""
Fitness & Running view — describe a fitness goal, get a full AI workout
plan, browse and manage saved plans.
"""

import flet as ft
import threading
from core import database as db
from core import ollama_client as ai
from core import theme as T


# Quick-start goal templates
TEMPLATES = [
    ("5 km Run", "5km run at moderate pace, I'm an intermediate runner"),
    ("10 km Run", "10km long run with negative splits for half-marathon training"),
    ("Gym: Chest & Triceps", "Gym chest and triceps hypertrophy day, intermediate lifter, 60 minutes"),
    ("Gym: Back & Biceps", "Gym back and biceps day, focus on pull movements, intermediate"),
    ("Gym: Legs", "Gym leg day, squats and deadlifts focus, intermediate lifter"),
    ("Full Body HIIT", "30-minute full body HIIT workout, no equipment needed, at home"),
    ("Morning Stretch", "15-minute morning flexibility and mobility routine"),
    ("Core Workout", "20-minute core and abs workout, bodyweight only"),
]


def build(page: ft.Page) -> ft.Control:

    # ── State ────────────────────────────────────────────────────────
    result_md = ft.Markdown(
        "",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        auto_follow_links=True,
        on_tap_link=lambda e: page.launch_url(e.data),
        code_style_sheet=ft.MarkdownStyleSheet(code_text_style=ft.TextStyle(color=T.LIGHT_CYAN, size=13)),
    )
    result_card = ft.Container(visible=False)
    history_column = ft.Ref[ft.Column]()
    goal_field = T.text_field(
        "Your fitness goal",
        hint="e.g. 5km tempo run, gym push day, 30-min HIIT...",
        multiline=True,
        expand=True,
    )

    models = ai.list_models()
    model_dd = ft.Dropdown(
        label="AI Model",
        options=[ft.dropdown.Option(m) for m in models] if models else [ft.dropdown.Option(ai.DEFAULT_MODEL)],
        value=models[0] if models else ai.DEFAULT_MODEL,
        width=220,
        bgcolor=T.SURFACE_ALT,
        border_color=T.BORDER,
        focused_border_color=T.PRIMARY,
        color=T.TEXT,
        label_style=ft.TextStyle(color=T.TEXT_MUTED),
        border_radius=8,
        text_size=13,
    )

    # ── Template chips ───────────────────────────────────────────────
    def on_chip(e):
        for label, prompt in TEMPLATES:
            if label == e.control.label.value:
                goal_field.value = prompt
                page.update()
                return

    chips = ft.Row(
        [
            ft.Chip(
                label=ft.Text(label, size=12),
                bgcolor=T.SURFACE_ALT,
                selected_color=T.PRIMARY + "30",
                on_click=on_chip,
            )
            for label, _ in TEMPLATES
        ],
        spacing=8,
        wrap=True,
    )

    # ── Generate workout ─────────────────────────────────────────────
    def on_generate(e):
        goal = goal_field.value.strip()
        if not goal:
            sb = ft.SnackBar(ft.Text("Describe your fitness goal first."), bgcolor=T.WARNING, open=True)
            page.overlay.append(sb)
            page.update()
            return

        result_md.value = ""
        result_card.visible = True
        result_card.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.ProgressRing(width=20, height=20, stroke_width=2, color=T.PRIMARY),
                        ft.Text("Generating workout plan...", size=13, color=T.TEXT_MUTED),
                    ],
                    spacing=10,
                ),
                result_md,
            ],
            spacing=12,
        )
        page.update()

        collected: list[str] = []

        def stream_worker():
            model = model_dd.value or ai.DEFAULT_MODEL
            for token in ai.generate_workout(goal, model=model):
                collected.append(token)
                result_md.value = "".join(collected)
                page.update()

            full_text = "".join(collected)
            if not full_text.startswith("[Error"):
                db.save_workout(goal, full_text)

            result_card.content = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.SUCCESS, size=18),
                            ft.Text("Workout saved", size=13, color=T.SUCCESS),
                        ],
                        spacing=8,
                    ),
                    result_md,
                ],
                spacing=12,
            )
            refresh_history()
            page.update()

        threading.Thread(target=stream_worker, daemon=True).start()

    # ── History ──────────────────────────────────────────────────────
    def _build_history_items() -> list[ft.Control]:
        workouts = db.get_workouts(30)
        items: list[ft.Control] = []
        for w in workouts:
            wid = w["id"]

            def make_delete(workout_id):
                def handler(e):
                    db.delete_workout(workout_id)
                    refresh_history()
                    page.update()
                return handler

            exp = ft.ExpansionTile(
                title=ft.Text(
                    w["goal"][:80] + ("..." if len(w["goal"]) > 80 else ""),
                    size=13,
                    color=T.TEXT,
                    max_lines=1,
                ),
                subtitle=ft.Text(w["created_at"], size=11, color=T.TEXT_FAINT),
                controls=[
                    ft.Container(
                        content=ft.Markdown(
                            w["plan_text"],
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            code_style_sheet=ft.MarkdownStyleSheet(code_text_style=ft.TextStyle(color=T.LIGHT_CYAN, size=13)),
                        ),
                        padding=ft.Padding.only(left=16, right=16, bottom=12),
                    ),
                ],
                trailing=ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color=T.TEXT_FAINT,
                    icon_size=18,
                    tooltip="Delete",
                    on_click=make_delete(wid),
                ),
                collapsed_icon_color=T.TEXT_MUTED,
                icon_color=T.PRIMARY,
                bgcolor=T.SURFACE_ALT,
                collapsed_bgcolor=T.SURFACE,
            )
            items.append(exp)

        if not items:
            items.append(ft.Text("No saved workouts yet.", size=13, color=T.TEXT_FAINT))
        return items

    def refresh_history():
        """Rebuild history list (call only after view is mounted on page)."""
        history_column.current.controls = _build_history_items()
        history_column.current.update()

    # ── Layout ───────────────────────────────────────────────────────
    gen_section = T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        T.icon_circle(ft.Icons.FITNESS_CENTER, T.SUCCESS),
                        T.heading("Generate Workout", 18),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=1, color=T.BORDER),
                ft.Text("Quick start:", size=12, color=T.TEXT_MUTED),
                chips,
                goal_field,
                ft.Row(
                    [
                        model_dd,
                        T.primary_button("Generate Plan", on_generate, ft.Icons.AUTO_AWESOME),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.END,
                ),
                result_card,
            ],
            spacing=14,
        ),
    )

    history_section = T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        T.icon_circle(ft.Icons.HISTORY, T.TEAL),
                        T.heading("Workout History", 18),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=1, color=T.BORDER),
                ft.Column(_build_history_items(), ref=history_column, spacing=6),
            ],
            spacing=14,
        ),
    )

    return ft.Container(
        content=ft.Column(
            [gen_section, history_section],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
        padding=ft.Padding.only(bottom=20),
    )
