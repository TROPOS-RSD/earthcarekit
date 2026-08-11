def confirm(msg: str, *, default: bool = False):
    prompt = "[Y/n]" if default else "[y/N]"

    while True:
        response = input(f"{msg} {prompt} ").strip().lower()

        if response == "":
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False

        print("Invalid input. Please enter 'y' or 'n'.")
