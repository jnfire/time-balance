from .. import config
from ..database.manager import db
from ..i18n.translator import translate
from ..ui import interface as ui
from ..utils.calculations import format_duration, format_time, get_balance_color


def project_menu(lang: str = "en"):
    """Submenu for switching, creating and deleting projects directly."""
    while True:
        projects_list = db.get_projects()
        active_project_id = db.get_active_project_id()

        ui.clear_screen()
        ui.render_header(translate("option_4_clean", lang=lang))

        table_columns = [
            (translate("table_id", lang=lang), {"justify": "center", "style": "dim"}),
            (translate("table_name", lang=lang), {"style": "bold"}),
            (translate("table_base", lang=lang), {"justify": "center", "style": "dim"}),
            (translate("table_balance", lang=lang), {"justify": "right"}),
            (translate("table_active", lang=lang), {"justify": "center"}),
        ]

        table_rows = []
        for project in projects_list:
            is_active_marker = (
                "[bold blue]●[/bold blue]" if project["id"] == active_project_id else ""
            )

            # Use cached balance or calculate if NULL
            total_balance = project["total_balance"] if project["total_balance"] is not None else 0
            balance_fmt = format_time(total_balance)
            balance_color = get_balance_color(total_balance)

            table_rows.append(
                [
                    str(project["id"]),
                    project["name"],
                    format_duration(project["base_hours"], project["base_minutes"]),
                    f"[{balance_color}]{balance_fmt}[/{balance_color}]",
                    is_active_marker,
                ]
            )

        ui.render_simple_table(table_columns, table_rows)

        # Unified navigation help
        ui.render_navigation_help(
            [
                ("ID", translate("project_option_select", lang=lang)),
                ("C", translate("project_option_create", lang=lang)),
                ("D", "Borrar"),  # Temporary hardcoded or use translation if exists
                ("V", translate("project_option_back", lang=lang)),
            ]
        )

        # We accept IDs (numbers) or navigation keys
        valid_ids = [str(project["id"]) for project in projects_list]
        choice_options = valid_ids + ["c", "d", "v"]

        user_choice = ui.ask_string(
            f"\n{translate('choose_option', lang=lang)}", choices=choice_options
        ).lower()

        if user_choice.isdigit():
            selected_id = int(user_choice)
            if any(project["id"] == selected_id for project in projects_list):
                db.set_active_project_id(selected_id)
                break
        elif user_choice == "c":
            new_project_name = ui.ask_string(
                translate("project_name_prompt", lang=lang, current="New")
            ).strip()
            if new_project_name:
                try:
                    base_hours_input = int(
                        ui.ask_string(
                            translate("base_hours_prompt", lang=lang, current=config.BASE_HOURS),
                            default=str(config.BASE_HOURS),
                        )
                    )
                    base_minutes_input = int(
                        ui.ask_string(
                            translate(
                                "base_minutes_prompt", lang=lang, current=config.BASE_MINUTES
                            ),
                            default=str(config.BASE_MINUTES),
                        )
                    )
                    new_project_id = db.create_project(
                        new_project_name, base_hours_input, base_minutes_input
                    )
                    db.set_active_project_id(new_project_id)
                    break
                except ValueError:
                    ui.print_message(translate("error_integers", lang=lang), style="bold red")
                    ui.ask_string(translate("press_enter", lang=lang), default="")
        elif user_choice == "d":
            id_to_delete_input = ui.ask_string(translate("delete_project_prompt", lang=lang))
            if id_to_delete_input.isdigit():
                target_id = int(id_to_delete_input)
                if target_id == active_project_id:
                    ui.print_message(translate("cannot_delete_active", lang=lang), style="bold red")
                else:
                    target_project = next(
                        (project for project in projects_list if project["id"] == target_id), None
                    )
                    if target_project:
                        ui.print_message(
                            f"\n{translate('delete_project_warning', lang=lang, name=target_project['name'])}",
                            style="bold yellow",
                        )
                        confirmation_name = ui.ask_string(
                            translate("delete_project_confirm_name", lang=lang)
                        )

                        if confirmation_name == target_project["name"]:
                            db.delete_project(target_id)
                            ui.print_message(
                                f"\n{translate('project_deleted', lang=lang, name=target_project['name'])}",
                                style="bold green",
                            )
                        else:
                            ui.print_message(
                                f"\n{translate('project_name_mismatch', lang=lang)}",
                                style="bold red",
                            )
                    else:
                        ui.print_message(
                            f"\n{translate('project_not_found', lang=lang)}", style="bold red"
                        )
                ui.ask_string(translate("press_enter", lang=lang), default="")
        elif user_choice == "v":
            break
