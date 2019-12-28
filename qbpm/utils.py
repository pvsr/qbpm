from sys import stderr


def error(msg: str) -> None:
    print(f"Error: {msg}", file=stderr)
