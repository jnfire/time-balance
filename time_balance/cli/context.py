"""What every interactive flow needs: the database and the language."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ..database import get_database
from ..database.manager import SETTING_LANGUAGE, DatabaseManager
from ..i18n.translator import resolve_language, translate
from ..ui import interface as ui


@dataclass(frozen=True)
class Context:
    """The database and the language of the current session.

    Flows receive a context instead of reaching for globals, which keeps them
    easy to test with a temporary database.
    """

    db: DatabaseManager
    lang: str

    @classmethod
    def from_settings(cls, db: DatabaseManager | None = None) -> Context:
        """Builds the context from the stored language setting (``auto`` follows the system)."""
        database = db or get_database()
        return cls(database, resolve_language(database.get_setting(SETTING_LANGUAGE, "auto")))

    def with_lang(self, lang: str) -> Context:
        return replace(self, lang=lang)

    def t(self, key: str, **values: object) -> str:
        """Translates a key into the session language."""
        return translate(key, lang=self.lang, **values)

    def pause(self) -> None:
        """Waits for Enter so the user can read the last message."""
        ui.ask_string(self.t("press_enter"), default="")

    def confirm(self, message: str, default: bool = False) -> bool:
        """Asks a yes/no question with the answer letters of the session language."""
        return ui.ask_confirm(
            message, default=default, yes=self.t("choice_yes"), no=self.t("choice_no")
        )
