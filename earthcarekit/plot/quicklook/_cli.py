from logging import Logger


def print_progress(
    msg: str,
    log_msg_prefix: str = "",
    line_length: int = 70,
    is_last: bool = False,
    logger: Logger | None = None,
):
    plt_msg: str = "Plotting ... "

    if is_last:
        plt_msg = ""

    _msg = f"{log_msg_prefix}{plt_msg}{msg}"
    num_spaces = line_length - len(_msg)
    if num_spaces < 0:
        _msg = f"{log_msg_prefix}{plt_msg}{msg[0 : num_spaces - 3]}..."
    else:
        _msg = f"{log_msg_prefix}{plt_msg}{msg}{' '*num_spaces}"

    if is_last:
        if logger:
            logger.info(_msg)
    else:
        print(_msg, end="\r")
