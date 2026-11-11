"""Project settings, language, import and export."""

from __future__ import annotations

import sqlite3

from .. import config
from ..database.manager import SETTING_LANGUAGE
from ..database.models import Project
from ..i18n.translator import resolve_language
from ..ui import interface as ui
from ..utils import files
from ..utils.calculations import format_duration
from ..utils.validation import InputError, parse_duration
from .context import Context
from .projects import name_is_taken

LANGUAGE_CHOICES = ("en", "es", "auto")

# (key, translation of the option, section it belongs to)
_MENU_SECTIONS = (
    (
        "config_section_project",
        (
            ("1", "config_option_edit_name"),
            ("2", "config_option_edit_base"),
            ("3", "config_option_lang"),
        ),
    ),
    (
        "config_section_data",
        (
            ("4", "config_option_import"),
            ("5", "config_option_export"),
            ("6", "config_option_repair"),
        ),
    ),
)


def _render_menu(ctx: Context, project: Project) -> None:
    ui.clear_screen()
    ui.render_header(ctx.t("option_3_clean"))
    ui.render_info_line(ctx.t("project_label"), project["name"])
    ui.render_info_line(
        ctx.t("base_day_label"), format_duration(project["base_hours"], project["base_minutes"])
    )
    ui.render_info_line(ctx.t("language_label"), ctx.db.get_setting(SETTING_LANGUAGE, "auto"))
    for section_key, options in _MENU_SECTIONS:
        ui.render_section_title(ctx.t(section_key))
        for number, label_key in options:
            ui.print_message(f"  [bold blue]{number}.[/bold blue] {ctx.t(label_key)}")
    ui.render_navigation_help([("V", ctx.t("config_option_back"))])


def _edit_name(ctx: Context, project: Project) -> None:
    name = ui.ask_string(
        ctx.t("project_name_prompt", current=ui.escape(project["name"])), default=project["name"]
    ).strip()
    if not name or name == project["name"]:
        return
    if name_is_taken(ctx.db.get_projects(), name, ignore_id=project["id"]):
        ui.print_message(ctx.t("project_name_taken", name=ui.escape(name)), style="bold red")
        ctx.pause()
        return
    ctx.db.update_project(project["id"], name, project["base_hours"], project["base_minutes"])


def _edit_base(ctx: Context, project: Project) -> None:
    try:
        hours, minutes = parse_duration(
            ui.ask_string(
                ctx.t("base_hours_prompt", current=project["base_hours"]),
                default=str(project["base_hours"]),
            ),
            ui.ask_string(
                ctx.t("base_minutes_prompt", current=project["base_minutes"]),
                default=str(project["base_minutes"]),
            ),
        )
    except InputError as error:
        ui.print_message(ctx.t(error.message_key), style="bold red")
        ctx.pause()
        return
    ctx.db.update_project(project["id"], project["name"], hours, minutes)


def _change_language(ctx: Context) -> Context:
    """Stores the chosen language and returns a context that uses it."""
    chosen = ui.ask_string(
        ctx.t("language_prompt", current=ctx.db.get_setting(SETTING_LANGUAGE, "auto")),
        choices=LANGUAGE_CHOICES,
        default="auto",
    ).lower()
    ctx.db.set_setting(SETTING_LANGUAGE, chosen)
    return ctx.with_lang(resolve_language(chosen))


def _import_data(ctx: Context, project: Project) -> None:
    path = ui.ask_string(ctx.t("import_src_prompt")).strip()
    if not path:
        return
    mode = ui.ask_string(
        ctx.t("import_mode_prompt", merge=config.MODE_MERGE, overwrite=config.MODE_OVERWRITE),
        choices=config.VALID_IMPORT_MODES,
        default=config.MODE_MERGE,
    )
    try:
        source = files.read_history_file(path)
        if mode == config.MODE_OVERWRITE:
            ctx.db.clear_project_records(project["id"])
        count = ctx.db.import_records(project["id"], source["records"])
        ui.print_message(ctx.t("import_success", count=count), style="bold green")
    except (ValueError, OSError, sqlite3.Error) as error:
        ui.print_message(ctx.t("import_error", error=ui.escape(str(error))), style="bold red")
    ctx.pause()


def _export_data(ctx: Context, project: Project) -> None:
    path = ui.ask_string(ctx.t("export_dest_prompt")).strip()
    if not path:
        return
    data = {
        "metadata": {
            "project_name": project["name"],
            "hours_base": project["base_hours"],
            "minutes_base": project["base_minutes"],
            "version": files.FORMAT_VERSION,
            "language": ctx.db.get_setting(SETTING_LANGUAGE, "auto"),
        },
        "records": ctx.db.get_records_dict(project["id"]),
    }
    try:
        destination = files.export_history(data, path)
        ui.print_message(
            ctx.t("export_success", path=ui.escape(str(destination))), style="bold green"
        )
    except (ValueError, OSError) as error:
        ui.print_message(ctx.t("export_error", error=ui.escape(str(error))), style="bold red")
    ctx.pause()


def _repair_balance(ctx: Context, project: Project) -> None:
    if ctx.confirm(ctx.t("recalculate_confirm")):
        ctx.db.recalculate_project_balance(project["id"])
        ui.print_message(f"\n{ctx.t('recalculate_done')}", style="bold green")
    ctx.pause()


def config_menu(ctx: Context) -> Context:
    """Settings screen. Returns the context, which carries the language if it was changed."""
    handlers = {
        "1": _edit_name,
        "2": _edit_base,
        "4": _import_data,
        "5": _export_data,
        "6": _repair_balance,
    }
    while True:
        project = ctx.db.get_active_project()
        _render_menu(ctx, project)
        choice = ui.ask_string(f"\n{ctx.t('choose_option')}", choices=[*handlers, "3", "v"]).lower()
        if choice == "3":
            ctx = _change_language(ctx)
        elif choice in handlers:
            handlers[choice](ctx, project)
        else:
            return ctx
