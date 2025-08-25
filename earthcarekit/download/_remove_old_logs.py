import os
import re
import time

import pandas as pd


def remove_old_logs(
    max_num_logs: int | None = None,
    max_age_logs: pd.Timedelta | None = None,
    log_file_prefix: str = "",
) -> None:
    """Deletes old log files depending on given maximum file number and/or age"""
    logs_dirpath = os.path.abspath("logs")

    if os.path.exists(logs_dirpath):
        pattern = r".*" + log_file_prefix + r"[0-9]{8}T[0-9]{6}(|_[0-9]*).log"
        if max_num_logs:
            old_logs = [
                os.path.abspath(os.path.join(logs_dirpath, fp))
                for fp in os.listdir(logs_dirpath)
                if re.search(pattern, fp)
            ]
            if len(old_logs) > max_num_logs - 1:
                old_logs.sort(reverse=True)
                for log in old_logs[max_num_logs - 1 : :]:
                    os.remove(log)

        if max_age_logs:
            current_time = pd.Timestamp(
                time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time()))
            )
            last_allowed_time = current_time - max_age_logs
            old_logs = [
                os.path.abspath(os.path.join(logs_dirpath, fp))
                for fp in os.listdir(logs_dirpath)
                if re.search(pattern, fp)
            ]
            for log in old_logs:
                log_time = pd.Timestamp(
                    os.path.basename(log).split(".")[0].split("_")[-1]
                )
                if log_time < last_allowed_time:
                    os.remove(log)
