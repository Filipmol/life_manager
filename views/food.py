"""
Food & Recipes view — enter ingredients, get an AI-generated recipe,
browse saved recipe history, delete old entries.
"""

import flet as ft
import threading
from core import database as db
from core import ollama_client as ai
from core import theme as T


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
    generating = ft.Ref[ft.ProgressRing]()
    gen_label = ft.Ref[ft.Text]()
    history_column = ft.Ref[ft.Column]()
    ingredient_field = T.text_field(
        "Your ingredients",
        hint="e.g. chicken breast, rice, bell pepper, garlic, soy sauce",
        multiline=True,
        expand=True,
    )

    # Model selector
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

    # ── Generate recipe (threaded to keep UI responsive) ─────────────
    def on_generate(e):
        ingredients = ingredient_field.value.strip()
        if not ingredients:
            sb = ft.SnackBar(ft.Text("Enter some ingredients first."), bgcolor=T.WARNING, open=True)
            page.overlay.append(sb)
            page.update()
            return

        # Show progress
        result_md.value = ""
        result_card.visible = True
        result_card.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.ProgressRing(width=20, height=20, stroke_width=2, color=T.PRIMARY, ref=generating),
                        ft.Text("Generating recipe...", size=13, color=T.TEXT_MUTED, ref=gen_label),
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
            for token in ai.generate_recipe(ingredients, model=model):
                collected.append(token)
                result_md.value = "".join(collected)
                page.update()

            # Done — save to DB and refresh history
            full_text = "".join(collected)
            if not full_text.startswith("[Error"):
                db.save_recipe(ingredients, full_text)

            # Remove spinner
            result_card.content = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.SUCCESS, size=18),
                            ft.Text("Recipe saved", size=13, color=T.SUCCESS),
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
        recipes = db.get_recipes(30)
        items: list[ft.Control] = []
        for r in recipes:
            rid = r["id"]

            def make_delete(recipe_id):
                def handler(e):
                    db.delete_recipe(recipe_id)
                    refresh_history()
                    page.update()
                return handler

            exp = ft.ExpansionTile(
                title=ft.Text(
                    r["ingredients"][:80] + ("..." if len(r["ingredients"]) > 80 else ""),
                    size=13,
                    color=T.TEXT,
                    max_lines=1,
                ),
                subtitle=ft.Text(r["created_at"], size=11, color=T.TEXT_FAINT),
                controls=[
                    ft.Container(
                        content=ft.Markdown(
                            r["recipe_text"],
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
                    on_click=make_delete(rid),
                ),
                collapsed_icon_color=T.TEXT_MUTED,
                icon_color=T.PRIMARY,
                bgcolor=T.SURFACE_ALT,
                collapsed_bgcolor=T.SURFACE,
            )
            items.append(exp)

        if not items:
            items.append(ft.Text("No saved recipes yet.", size=13, color=T.TEXT_FAINT))
        return items

    def refresh_history():
        """Rebuild history list and update the page (call after view is mounted)."""
        history_column.current.controls = _build_history_items()
        history_column.current.update()

    # ── Layout ───────────────────────────────────────────────────────
    gen_section = T.card(
        ft.Column(
            [
                ft.Row(
                    [
                        T.icon_circle(ft.Icons.RESTAURANT, T.GOLD),
                        T.heading("Generate Recipe", 18),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=1, color=T.BORDER),
                ingredient_field,
                ft.Row(
                    [
                        model_dd,
                        T.primary_button("Generate", on_generate, ft.Icons.AUTO_AWESOME),
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
                        T.heading("Recipe History", 18),
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
