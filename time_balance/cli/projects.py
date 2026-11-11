"""Switching, creating and deleting projects."""

from __future__ import annotations

from collections.abc import Sequence

from .. import config
from ..database.models import Project
from ..ui import interface as ui
from ..utils.calculations import format_duration, format_time, get_balance_color
from ..utils.validation import InputError, parse_duration
from .context import Context


def name_is_taken(projects: Sequence[Project], name: str, ignore_id: int | None = None) -> bool:
    """True if another project already uses this name (compared without case)."""
    wanted = name.strip().lower()
    return any(
        project["name"].lower() == wanted for project in projects if project["id"] != ignore_id
    )


def find_deletable_project(projects: Sequence[Project], active_id: int, target_id: int) -> Project:
    """The project to delete. Raises ``InputError`` if it is the active one or does not exist."""
    if target_id == active_id:
        raise InputError("cannot_delete_active")
    for project in projects:
        if project["id"] == target_id:
            return project
    raise InputError("project_not_found")


def _project_rows(projects: Sequence[Project], active_id: int) -> list[list[str]]:
    rows = []
    for project in projects:
        balance = project["total_balance"] or 0
        color = get_balance_color(balance)
        rows.append(
            [
                str(project["id"]),
                ui.escape(project["name"]),
                format_duration(project["base_hours"], project["base_minutes"]),
                f"[{color}]{format_time(balance)}[/{color}]",
                f"[bold {ui.COLOR_PRIMARY}]●[/bold {ui.COLOR_PRIMARY}]"
                if project["id"] == active_id
                else "",
            ]
        )
    return rows


def _render_menu(ctx: Context, projects: Sequence[Project], active_id: int) -> None:
    ui.clear_screen()
    ui.render_header(ctx.t("option_4_clean"))
    columns: list[ui.Column] = [
        (ctx.t("table_id"), {"justify": "center", "style": "dim"}),
        (ctx.t("table_name"), {"style": "bold"}),
        (ctx.t("table_base"), {"justify": "center", "style": "dim"}),
        (ctx.t("table_balance"), {"justify": "right"}),
        (ctx.t("table_active"), {"justify": "center"}),
    ]
    ui.render_simple_table(columns, _project_rows(projects, active_id))
    ui.render_navigation_help(
        [
            ("ID", ctx.t("project_option_select")),
            ("C", ctx.t("project_option_create")),
            ("D", ctx.t("project_option_delete")),
            ("V", ctx.t("project_option_back")),
        ]
    )


def _create_project(ctx: Context, projects: Sequence[Project]) -> bool:
    """Asks for a name and a daily base, creates the project and makes it active."""
    name = ui.ask_string(
        ctx.t("project_name_prompt", current=ctx.t("project_name_default"))
    ).strip()
    if not name:
        return False
    if name_is_taken(projects, name):
        ui.print_message(ctx.t("project_name_taken", name=ui.escape(name)), style="bold red")
        ctx.pause()
        return False
    try:
        hours, minutes = parse_duration(
            ui.ask_string(
                ctx.t("base_hours_prompt", current=config.BASE_HOURS),
                default=str(config.BASE_HOURS),
            ),
            ui.ask_string(
                ctx.t("base_minutes_prompt", current=config.BASE_MINUTES),
                default=str(config.BASE_MINUTES),
            ),
        )
    except InputError as error:
        ui.print_message(ctx.t(error.message_key), style="bold red")
        ctx.pause()
        return False
    ctx.db.set_active_project_id(ctx.db.create_project(name, hours, minutes))
    return True


def _delete_project(ctx: Context, projects: Sequence[Project], active_id: int) -> None:
    """Asks for an id, makes the user type the name to confirm, and deletes the project."""
    typed_id = ui.ask_string(ctx.t("delete_project_prompt")).strip()
    if not typed_id.isdigit():
        return
    try:
        project = find_deletable_project(projects, active_id, int(typed_id))
    except InputError as error:
        ui.print_message(ctx.t(error.message_key), style="bold red")
        ctx.pause()
        return

    name = ui.escape(project["name"])
    ui.print_message(f"\n{ctx.t('delete_project_warning', name=name)}", style="bold yellow")
    if ui.ask_string(ctx.t("delete_project_confirm_name")) == project["name"]:
        ctx.db.delete_project(project["id"])
        ui.print_message(f"\n{ctx.t('project_deleted', name=name)}", style="bold green")
    else:
        ui.print_message(f"\n{ctx.t('project_name_mismatch')}", style="bold red")
    ctx.pause()


def project_menu(ctx: Context) -> None:
    """Lists the projects and lets the user pick, create or delete one."""
    while True:
        projects = ctx.db.get_projects()
        active_id = ctx.db.get_active_project_id()
        _render_menu(ctx, projects, active_id)

        valid_ids = [str(project["id"]) for project in projects]
        choice = ui.ask_string(f"\n{ctx.t('choose_option')}", choices=[*valid_ids, "c", "d", "v"])
        choice = choice.lower()

        if choice.isdigit():
            ctx.db.set_active_project_id(int(choice))
            return
        if choice == "c":
            if _create_project(ctx, projects):
                return
        elif choice == "d":
            _delete_project(ctx, projects, active_id)
        else:
            return
