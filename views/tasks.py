"""
Task Manager — full Kanban board with three columns (To Do, Doing, Done),
drag-and-drop-style move buttons, inline editing, category filters,
priority markers, and due-date support.
"""

import flet as ft
from datetime import datetime
from core import database as db
from core import theme as T

STATUS_META = {
    "todo":  {"label": "To Do",  "color": T.TEXT,    "icon": ft.Icons.RADIO_BUTTON_UNCHECKED},
    "doing": {"label": "Doing",  "color": T.WARNING, "icon": ft.Icons.TIMELAPSE},
    "done":  {"label": "Done",   "color": T.SUCCESS, "icon": ft.Icons.CHECK_CIRCLE},
}

CATEGORY_OPTIONS = ["work", "school", "personal"]
PRIORITY_LABELS = {0: "Low", 1: "Medium", 2: "High"}
PRIORITY_COLORS = {0: T.TEXT_FAINT, 1: T.GOLD, 2: T.ERROR}


def build(page: ft.Page) -> ft.Control:

    kanban_columns: dict[str, ft.Ref[ft.Column]] = {
        "todo":  ft.Ref[ft.Column](),
        "doing": ft.Ref[ft.Column](),
        "done":  ft.Ref[ft.Column](),
    }
    active_filter = {"category": None}  # None = show all

    # ── Refresh board ────────────────────────────────────────────────
    _empty_col = lambda: [
        ft.Container(
            content=ft.Text("No tasks", size=12, color=T.TEXT_FAINT, text_align=ft.TextAlign.CENTER),
            alignment=ft.Alignment(0, 0),
            padding=20,
        )
    ]

    def _build_column_items(status_key: str, all_tasks: list[dict]) -> list[ft.Control]:
        items = [
            _task_card(t, page, refresh)
            for t in all_tasks
            if t["status"] == status_key
        ]
        return items if items else _empty_col()

    def refresh():
        """Rebuild all kanban columns (call only after view is mounted on page)."""
        all_tasks = db.get_tasks(active_filter["category"])
        for status_key, col_ref in kanban_columns.items():
            col_ref.current.controls = _build_column_items(status_key, all_tasks)
            col_ref.current.update()

    # ── Add-task dialog ──────────────────────────────────────────────
    title_f = T.text_field("Title", hint="What needs doing?")
    desc_f = T.text_field("Description (optional)", multiline=True)
    cat_dd = ft.Dropdown(
        label="Category",
        options=[ft.dropdown.Option(c.title()) for c in CATEGORY_OPTIONS],
        value="Work",
        width=160,
        bgcolor=T.SURFACE_ALT,
        border_color=T.BORDER,
        focused_border_color=T.PRIMARY,
        color=T.TEXT,
        label_style=ft.TextStyle(color=T.TEXT_MUTED),
        border_radius=8,
        text_size=13,
    )
    pri_dd = ft.Dropdown(
        label="Priority",
        options=[ft.dropdown.Option(key=str(k), text=v) for k, v in PRIORITY_LABELS.items()],
        value="0",
        width=140,
        bgcolor=T.SURFACE_ALT,
        border_color=T.BORDER,
        focused_border_color=T.PRIMARY,
        color=T.TEXT,
        label_style=ft.TextStyle(color=T.TEXT_MUTED),
        border_radius=8,
        text_size=13,
    )
    due_f = T.text_field("Due date", hint="YYYY-MM-DD")

    def on_add_task(e):
        title = title_f.value.strip()
        if not title:
            sb = ft.SnackBar(ft.Text("Task title is required."), bgcolor=T.WARNING, open=True)
            page.overlay.append(sb)
            page.update()
            return
        db.add_task(
            title=title,
            description=desc_f.value.strip(),
            category=(cat_dd.value or "work").lower(),
            priority=int(pri_dd.value or 0),
            due_date=due_f.value.strip() or None,
        )
        title_f.value = ""
        desc_f.value = ""
        due_f.value = ""
        page.pop_dialog()
        refresh()
        page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Task", color=T.TEXT),
        bgcolor=T.SURFACE,
        content=ft.Container(
            content=ft.Column(
                [title_f, desc_f, ft.Row([cat_dd, pri_dd], spacing=12), due_f],
                spacing=14,
                tight=True,
            ),
            width=420,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog(), style=ft.ButtonStyle(color=T.TEXT_MUTED)),
            T.primary_button("Add Task", on_add_task, ft.Icons.ADD),
        ],
    )

    def open_add(e):
        page.show_dialog(dlg)
        page.update()

    # ── Filter chips ─────────────────────────────────────────────────
    def on_filter(e):
        clicked = e.control.data
        if active_filter["category"] == clicked:
            active_filter["category"] = None
        else:
            active_filter["category"] = clicked
        _update_chip_styles(filter_chips, active_filter["category"])
        refresh()
        page.update()

    filter_chips = ft.Row(
        [
            ft.Chip(
                label=ft.Text("All", size=12),
                bgcolor=T.PRIMARY + "25" if active_filter["category"] is None else T.SURFACE_ALT,
                on_click=on_filter,
                data=None,
            ),
        ]
        + [
            ft.Chip(
                label=ft.Text(c.title(), size=12),
                bgcolor=T.SURFACE_ALT,
                on_click=on_filter,
                data=c,
            )
            for c in CATEGORY_OPTIONS
        ],
        spacing=8,
    )

    # ── Kanban columns ───────────────────────────────────────────────
    def make_kanban_col(status_key: str):
        meta = STATUS_META[status_key]
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(meta["icon"], color=meta["color"], size=18),
                            ft.Text(meta["label"], size=14, weight=ft.FontWeight.W_600, color=meta["color"]),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=1, color=T.BORDER),
                    ft.Column(
                        _build_column_items(status_key, db.get_tasks(active_filter["category"])),
                        ref=kanban_columns[status_key],
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            bgcolor=T.SURFACE,
            border_radius=12,
            border=ft.Border.all(1, T.BORDER),
            padding=14,
            expand=True,
        )

    board = ft.Row(
        [make_kanban_col(s) for s in ("todo", "doing", "done")],
        spacing=16,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    # ── Top bar ──────────────────────────────────────────────────────
    top_bar = ft.Row(
        [
            ft.Row(
                [
                    T.icon_circle(ft.Icons.VIEW_KANBAN, T.PRIMARY),
                    T.heading("Task Board", 18),
                ],
                spacing=12,
            ),
            ft.Row([filter_chips, T.primary_button("New Task", open_add, ft.Icons.ADD)], spacing=12),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    return ft.Container(
        content=ft.Column(
            [top_bar, board],
            spacing=16,
            expand=True,
        ),
        expand=True,
        padding=ft.Padding.only(bottom=20),
    )


# ═══════════════════════════════════════════════════════════════════════
# Helper: single task card
# ═══════════════════════════════════════════════════════════════════════

def _task_card(task: dict, page: ft.Page, refresh_cb) -> ft.Control:
    tid = task["id"]
    status = task["status"]
    pri = task.get("priority", 0)
    due = task.get("due_date")
    is_overdue = False
    if due:
        try:
            is_overdue = datetime.strptime(due, "%Y-%m-%d").date() < datetime.now().date() and status != "done"
        except ValueError:
            pass

    # Priority dot
    pri_dot = ft.Container(
        width=8, height=8,
        bgcolor=PRIORITY_COLORS.get(pri, T.TEXT_FAINT),
        border_radius=4,
        tooltip=PRIORITY_LABELS.get(pri, ""),
    )

    # Move buttons
    move_buttons: list[ft.Control] = []
    if status != "todo":
        move_buttons.append(
            ft.IconButton(ft.Icons.ARROW_BACK, icon_size=15, icon_color=T.TEXT_FAINT, tooltip="Move left",
                          on_click=lambda e, t=tid, s=status: _move(t, s, -1, refresh_cb, page))
        )
    if status != "done":
        move_buttons.append(
            ft.IconButton(ft.Icons.ARROW_FORWARD, icon_size=15, icon_color=T.TEXT_FAINT, tooltip="Move right",
                          on_click=lambda e, t=tid, s=status: _move(t, s, 1, refresh_cb, page))
        )
    move_buttons.append(
        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=15, icon_color=T.TEXT_FAINT, tooltip="Delete",
                      on_click=lambda e, t=tid: (_del(t, refresh_cb, page)))
    )

    # Category badge
    cat_badge = ft.Container(
        content=ft.Text(task.get("category", "").title(), size=10, color=T.PRIMARY),
        bgcolor=T.PRIMARY + "1A",
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
    )

    # Due date
    due_text = ft.Container()
    if due:
        due_text = ft.Text(
            f"Due: {due}",
            size=11,
            color=T.ERROR if is_overdue else T.TEXT_FAINT,
            weight=ft.FontWeight.W_600 if is_overdue else ft.FontWeight.W_400,
        )

    title_style = ft.TextStyle(
        size=13,
        weight=ft.FontWeight.W_600,
        color=T.TEXT if status != "done" else T.TEXT_FAINT,
        decoration=ft.TextDecoration.LINE_THROUGH if status == "done" else None,
    )
    title_text = ft.Text(
        task["title"],
        style=title_style,
        text_align=ft.TextAlign.LEFT,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    desc_ctrl = ft.Container()
    if task.get("description"):
        desc_ctrl = ft.Text(task["description"], size=11, color=T.TEXT_MUTED, max_lines=3,
                            overflow=ft.TextOverflow.ELLIPSIS)

    return ft.Container(
        content=ft.Column(
            [
                ft.Row([pri_dot, title_text], spacing=8, expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
                desc_ctrl,
                ft.Row([cat_badge, due_text], spacing=8),
                ft.Row(move_buttons, spacing=0, alignment=ft.MainAxisAlignment.END),
            ],
            spacing=6,
        ),
        bgcolor=T.SURFACE_ALT,
        border_radius=8,
        border=ft.Border.all(1, T.BORDER),
        padding=12,
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )


_STATUS_ORDER = ["todo", "doing", "done"]


def _move(task_id: int, current: str, direction: int, refresh_cb, page: ft.Page):
    idx = _STATUS_ORDER.index(current) + direction
    if 0 <= idx < len(_STATUS_ORDER):
        db.update_task(task_id, status=_STATUS_ORDER[idx])
        refresh_cb()
        page.update()


def _del(task_id: int, refresh_cb, page: ft.Page):
    db.delete_task(task_id)
    refresh_cb()
    page.update()


def _update_chip_styles(chip_row: ft.Row, active_cat):
    for chip in chip_row.controls:
        if chip.data == active_cat:
            chip.bgcolor = T.PRIMARY + "25"
        else:
            chip.bgcolor = T.SURFACE_ALT
