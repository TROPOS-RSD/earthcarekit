from typing import Sequence

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ....utils.constants import (
    CM_AS_INCH,
    FIGURE_HEIGHT_CURTAIN,
    FIGURE_HEIGHT_LINE,
    FIGURE_HEIGHT_SWATH,
    FIGURE_MAP_WIDTH,
    FIGURE_WIDTH_CURTAIN,
    FIGURE_WIDTH_PROFILE,
)
from ..figure_type import FigureType


def create_fig_layout_map_main_zoom_profile(
    main_rows: Sequence[FigureType | int],
    zoom_rows: Sequence[FigureType | int] | None = None,
    profile_rows: Sequence[FigureType | int] | None = None,
    map_rows: Sequence[FigureType | int] | None = None,
    wspace: float | Sequence[float] = 3.0 * CM_AS_INCH,
    hspace: float | Sequence[float] = 3.0 * CM_AS_INCH,
    wmain: float = FIGURE_WIDTH_CURTAIN,
    hrow: float = FIGURE_HEIGHT_CURTAIN,
    hswath: float = FIGURE_HEIGHT_SWATH,
    hline: float = FIGURE_HEIGHT_LINE,
    wprofile: float = FIGURE_WIDTH_PROFILE,
    wmap: float = FIGURE_MAP_WIDTH,
    wzoom: float = FIGURE_WIDTH_CURTAIN / 3.0,
) -> tuple[Figure, Sequence[Axes], Sequence[Axes], Sequence[Axes], Sequence[Axes]]:
    """
    Creates a complex figure layout with columns for map, main, zoom, and profile panels (in that order from left to right).

    Each panel column can have a custom sequence of figure types (e.g., row heights), and the layout
    supports both uniform and per-gap horizontal/vertical spacing.

    Args:
        main_rows (Sequence[FigureType | int]): List of figure types for the rows of the main column.
        zoom_rows (Sequence[FigureType | int], optional): List of figure types for the rows in the optional zoom column.
        profile_rows (Sequence[FigureType | int], optional): List of figure types for the rows in the optional profile column.
        map_rows (Sequence[FigureType | int], optional): List of figure types for the rows in the optional map column.
        wspace (float | Sequence[float], optional): Horizontal spacing between columns. Can be a single value
            or list defining spacing before, between, and after columns.
        hspace (float | Sequence[float], optional): Vertical spacing between rows. Similar behavior as `wspace`.
        wmain (float, optional): Width of the main column. Default is `FIGURE_WIDTH_CURTAIN`.
        hrow (float, optional): Height of a standard row. Default is `FIGURE_HEIGHT_CURTAIN`.
        hswath (float, optional): Height of a `SwathFigure`-type row. Default is `FIGURE_HEIGHT_SWATH`.
        wprofile (float, optional): Width of the profile column.
        wmap (float, optional): Width of the map column.
        wzoom (float, optional): Width of the zoom column.

    Returns:
        tuple: A tuple containing:
            - Figure: The matplotlib figure object.
            - Sequence[Axes]: Axes for map panels (may be empty).
            - Sequence[Axes]: Axes for main panels.
            - Sequence[Axes]: Axes for zoom panels (may be empty).
            - Sequence[Axes]: Axes for profile panels (may be empty).

    Raises:
        ValueError: If the provided spacing sequences are of invalid length.
        TypeError: If spacing arguments are of unsupported types.
    """
    # Calculate number of columns
    is_map_col: bool = isinstance(map_rows, list) and len(map_rows) > 0
    is_main_col: bool = isinstance(main_rows, list) and len(main_rows) > 0
    is_zoom_col: bool = isinstance(zoom_rows, list) and len(zoom_rows) > 0
    is_profile_col: bool = isinstance(profile_rows, list) and len(profile_rows) > 0
    col_present: list[bool] = [is_map_col, is_main_col, is_zoom_col, is_profile_col]

    ncols: int = sum(col_present)

    # Calculate number of rows
    nrows_min: int = len(main_rows)
    if isinstance(map_rows, list):
        for ft in map_rows:
            nrows_min += 1
            if ft == FigureType.MAP_2_ROW:
                nrows_min += 1

    nrows: int = max(nrows_min, len(main_rows))

    # Calulate spaces between figures
    def _calulate_spaces(
        space: float | Sequence[float],
        n: int,
        name: str,
        name_col_row: str,
    ) -> list[float]:
        if isinstance(space, Sequence):
            space = list(space)
            if len(space) < n - 1 or len(space) > n + 1:
                raise ValueError(
                    f"{name} was given as a list (size={len(space)}) and thus needs to have a size between number of {name_col_row} ({n}) -1 (i.e. only spaces between {name_col_row}) and +1 (i.e. spaces before, between and after {name_col_row})."
                )
            elif len(space) == n - 1:
                space = [0.0] + space + [0.0]
            elif len(space) == n:
                space = space + [0.0]
        elif isinstance(space, float):
            space = [0.0] + [space] * (n - 1) + [0.0]
        else:
            raise TypeError(
                f"{name} has wrong type '{type(space).__name__}'. expected types: '{float.__name__}' or ''{list.__name__}'[{float.__name__}]'"
            )
        return space

    wspace = _calulate_spaces(wspace, ncols, "wspace", "columns")
    hspace = _calulate_spaces(hspace, nrows, "hspace", "rows")

    # Calculate size ratios of figures
    def _get_ratios(
        ratios_figs: list[float],
        space: list[float],
    ) -> list[float]:
        assert len(space) == len(ratios_figs) + 1

        ratios: list[float] = []
        for i, r in enumerate(ratios_figs):
            ratios.append(space[i])
            ratios.append(r)
        ratios.append(space[-1])

        return ratios

    wratios_figs: list[float] = np.array([wmap, wmain, wzoom, wprofile])[
        col_present
    ].tolist()
    hratios_figs: list[float] = []
    for fig_type in main_rows:
        if fig_type == FigureType.SWATH:
            hratios_figs.append(hswath)
        elif fig_type == FigureType.LINE:
            hratios_figs.append(hline)
        else:
            hratios_figs.append(hrow)
    if len(main_rows) < nrows_min:
        for i in range(nrows_min - len(main_rows)):
            hratios_figs.append(hrow)

    wratios = _get_ratios(wratios_figs, wspace)
    hratios = _get_ratios(hratios_figs, hspace)

    # Create the figure
    wfig = sum(wratios)
    hfig = sum(hratios)
    figsize = (wfig, hfig)

    fig = plt.figure(figsize=figsize)

    # Create the grid layout
    gs = gridspec.GridSpec(
        nrows=len(hratios),
        ncols=len(wratios),
        width_ratios=wratios,
        height_ratios=hratios,
        figure=fig,
        wspace=0,
        hspace=0,
        bottom=0.0,
        top=1.0,
        right=1.0,
        left=0.0,
    )

    # Create the plots
    # Create maps
    current_col: int = 1
    current_row: int = 1
    axs_map: list[Axes] = []
    axs_main: list[Axes] = []
    axs_zoom: list[Axes] = []
    axs_profile: list[Axes] = []
    ax: Axes | None
    if isinstance(map_rows, list):
        for fig_type in map_rows:
            if fig_type == FigureType.MAP_2_ROW:
                ax = fig.add_subplot(gs[current_row : current_row + 3, current_col])
                current_row += 2
            elif fig_type == FigureType.NONE:
                ax = None
            else:
                ax = fig.add_subplot(gs[current_row, current_col])
            if isinstance(ax, Axes):
                axs_map.append(ax)
            current_row += 2
        current_col += 2
        current_row = 1

    if isinstance(main_rows, list):
        for fig_type in main_rows:
            if fig_type == FigureType.NONE:
                ax = None
            else:
                ax = fig.add_subplot(gs[current_row, current_col])
            if isinstance(ax, Axes):
                axs_main.append(ax)
            current_row += 2
        current_col += 2
        current_row = 1

    if isinstance(zoom_rows, list):
        for fig_type in zoom_rows:
            if fig_type == FigureType.NONE:
                ax = None
            else:
                ax = fig.add_subplot(gs[current_row, current_col])
            if isinstance(ax, Axes):
                axs_zoom.append(ax)
            current_row += 2
        current_col += 2
        current_row = 1

    if isinstance(profile_rows, list):
        for fig_type in profile_rows:
            if fig_type == FigureType.NONE:
                ax = None
            else:
                ax = fig.add_subplot(gs[current_row, current_col])
            if isinstance(ax, Axes):
                axs_profile.append(ax)
            current_row += 2
        current_col += 2
        current_row = 1

    return fig, axs_map, axs_main, axs_zoom, axs_profile
