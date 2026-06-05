"""Per-troublemaker structured research notes used by research-tms output."""

from __future__ import annotations

_STRUCTURED_TEXT_BY_REF_CACHE: dict[str, dict[str, object]] | None = None


def _load_structured_text_by_ref() -> dict[str, dict[str, object]]:
    global _STRUCTURED_TEXT_BY_REF_CACHE
    if _STRUCTURED_TEXT_BY_REF_CACHE is None:
        from accgram import tm_data

        _STRUCTURED_TEXT_BY_REF_CACHE = tm_data.STRUCTURED_TEXT_BY_REF
    return _STRUCTURED_TEXT_BY_REF_CACHE


def get_structured_text() -> dict[str, dict[str, object]]:
    return _load_structured_text_by_ref()


def __getattr__(name: str) -> object:
    if name == "STRUCTURED_TEXT_BY_REF":
        return _load_structured_text_by_ref()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + ["STRUCTURED_TEXT_BY_REF"])
