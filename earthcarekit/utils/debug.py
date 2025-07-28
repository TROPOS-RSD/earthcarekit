import inspect


def get_calling_function_name(level: int = 1):
    """
    Returns the name of the function at a specified `level` in the call stack.

    Parameters:
        level (int):
            The number of levels up the call stack to look for the calling function.
            A level of 1 refers to the immediate caller, 2 to the caller of the caller, etc.

    Returns:
        function_name (str):
            The name of the function at the given `level` in the call hierarchy.
    """
    stack = inspect.stack()
    if len(stack) >= level:
        return stack[level].function
    return ""
