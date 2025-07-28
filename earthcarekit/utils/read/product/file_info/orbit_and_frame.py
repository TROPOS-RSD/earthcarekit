import numpy as np


def validate_orbit_number(orbit_number: int | str) -> int:
    """Checks if given orbit number is valid and raises ValueError if the given number is invalid or TypeError if type is wrong."""
    if isinstance(orbit_number, (int, np.integer)) or isinstance(orbit_number, str):
        value_error_msg = f"Given orbit number is invalid: {orbit_number}"
        try:
            orbit_number = int(orbit_number)
        except ValueError:
            raise ValueError(value_error_msg)

        if orbit_number < 0 or orbit_number > 99999:
            raise ValueError(value_error_msg)

        return orbit_number
    raise TypeError(
        f"Given orbit number has invalid type ({type(orbit_number)}: {orbit_number})"
    )


def format_orbit_number(orbit_number: int | str | None) -> str:
    """Returns validated orbit number as a 5 digit string or regex string '.....' if None."""
    if orbit_number is None:
        return "....."
    orbit_number = validate_orbit_number(orbit_number)
    return str(orbit_number).zfill(5)


def validate_frame_id(frame_id: str) -> str:
    """Checks if given frame ID is valid and raises ValueError if the given charater is invalid or TypeError if type is wrong."""
    if isinstance(frame_id, str):
        if frame_id.isalpha() and frame_id.upper() in [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
        ]:
            return frame_id.upper()
        raise ValueError(f"Given frame ID is invalid: '{frame_id}'")
    else:
        raise TypeError(
            f"Given frame ID has invalid type ({type(frame_id)}: {frame_id})"
        )


def format_frame_id(frame_id: str | None) -> str:
    """Returns validated frame ID as one letter string or regex string '.' if None."""
    if frame_id is None:
        return "."
    return validate_frame_id(frame_id)


def format_orbit_and_frame(orbit_and_frame: str) -> str:
    """Returns validated and formatted orbit and frame 6 character string."""
    if isinstance(orbit_and_frame, str):
        try:
            if len(orbit_and_frame) == 1 and orbit_and_frame.isalpha():
                orbit_number = None
                frame_id = orbit_and_frame
            else:
                orbit_and_frame = orbit_and_frame.upper().zfill(6)
                frame_id = orbit_and_frame[-1]
                if str(frame_id).isalpha():
                    orbit_number = orbit_and_frame[:-1]
                else:
                    frame_id = None
                    orbit_number = orbit_and_frame
            frame_id = format_frame_id(frame_id)
            orbit_number = format_orbit_number(orbit_number)
            orbit_and_frame = f"{orbit_number}{frame_id}"
            return orbit_and_frame
        except ValueError:
            raise ValueError(f"Given orbit and frame is invalid: {orbit_and_frame}")
    else:
        raise TypeError(
            f"Given orbit and frame has invalid type ({type(orbit_and_frame)}: {orbit_and_frame})"
        )
