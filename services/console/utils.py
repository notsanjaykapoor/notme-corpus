def print_(s: str, end: str=" ... "):
    print(s, end=end, flush=True)


def print_error(s: str):
    print("\x1b[1;31m" + s + "\x1b[0m", flush=True)


def print_ok(s: str):
    print("\x1b[1;32m" + s + "\x1b[0m", flush=True)


def print_status(s: str):
    print("\x1b[1;36m" + s + "\x1b[0m", flush=True)
