import logging


def info(msg: str) -> None:
    logging.info(msg)


def error(msg: str) -> None:
    logging.error(msg)


def or_phrase(items: list) -> str:
    strings = list(map(str, items))
    size = len(strings)
    if size == 0:
        return "[]"
    elif size == 1:
        return strings[0]
    elif size == 2:  # noqa: PLR2004
        return " or ".join(strings)
    else:
        return ", or ".join([", ".join(strings[0:-1]), strings[-1]])
