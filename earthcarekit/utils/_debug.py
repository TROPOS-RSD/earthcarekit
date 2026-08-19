import inspect


def get_calling_function_name(level: int = 1) -> str:
    """
    Returns the name of the function at a specified `level` in the call stack.

    Parameters:
        level:
            Number of levels up the call stack to look for a caller
            (e.g., 1=immediate caller, 2=caller of the immediate caller, etc.).

    Returns:
        Name of the function at the given `level` in the call hierarchy.
    """
    stack = inspect.stack()
    if len(stack) >= level:
        return stack[level].function
    return ""
