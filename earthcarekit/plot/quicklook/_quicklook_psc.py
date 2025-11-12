from contextlib import nullcontext
from typing import Sequence

import numpy as np
from numpy.typing import NDArray
from xarray import Dataset

from ...utils.geo import geodesic, get_coords
from ...utils.read import read_product, read_products, trim_to_latitude_frame_bounds
from ...utils.read.product._rebin_xmet_to_vertical_track import (
    rebin_xmet_to_vertical_track,
)
from ...utils.time import TimeRangeLike
from ...utils.typing import DistanceRangeLike
from ...utils.xarray_utils import concat_datasets, filter_time
from ..figure import CurtainFigure, ECKFigure, FigureType, MapFigure, SwathFigure
from ..figure.multi_panel import create_multi_figure_layout
from ._quicklook_results import QuicklookFigure


def ecquicklook_psc(
    anom: str | Sequence[str] | NDArray[np.str_] | Dataset,
    xmet: str | Sequence[str] | NDArray[np.str_] | Dataset | None = None,
    zoom_at: float | None = 0.5,
    height_range: DistanceRangeLike | None = (0, 40e3),
    time_range: TimeRangeLike | None = None,
    info_text_loc: str | None = None,
) -> QuicklookFigure:
    """
    Creates a two-column multi-panel quicklook of a PSC event, displaying:

    - 1st column: Two maps showing the EarthCARE track.
    - 2nd column: Three rows showing co- and cross-polar attenuated backscatter and the calculated depolarization ratio.

    Args:
        anom (str | Sequence[str] | Dataset):  The ATL_NOM_1B product filepath(s) or dataset(s).
        xmet (str | Sequence[str] | Dataset | None, optional): The AUX_MET_1D product filepath(s) or dataset(s).
            If given, temperature contour lines will be added to the plots. Defaults to None.
        zoom_at (float | None, optional): In case two frames are given, selects only a zoomed-in portion of the
            frames around this fractional index (0 -> only 1st frame, 0.5 -> half of end of 1st and half of beginning
            of 2nd frame, 1 -> only 2nd frame). Defaults to 0.5.
        height_range (DistanceRangeLike | None, optional): _description_. Defaults to (0, 40e3).
        time_range (TimeRangeLike | None, optional): A time range to filter the displayed data. Defaults to None.
        info_text_loc (str | None, optional): The positioning of the orbt, frame and product info text (e.g., "upper right").
            Defaults to None.

    Raises:
        ValueError: If none or more than 2 frames are given.
        ValueError: If given number X-MET files does not match number of A-NOM files.

    Returns:
        QuicklookFigure: The quicklook object.

    Examples:
        ```python
        import earthcarekit as eck

        df = eck.search_product(
            file_type=["anom", "xmet"],
            orbit_and_frame=["3579B", "3579C"],
        ).filter_latest()

        fps_anom = df.filter_file_type("anom").filepath
        fps_xmet = df.filter_file_type("xmet").filepath

        ql = eck.ecquicklook_psc(
            anom=fps_anom,
            xmet=fps_xmet,
        )
        ```

        ![ecquicklook_psc.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/quicklooks/ecquicklook_psc.png)
    """

    if not isinstance(anom, str) and isinstance(anom, (Sequence, np.ndarray)):
        if len(anom) == 0 or len(anom) > 2:
            raise ValueError(
                f"supports input of either 1 or 2 consecutive frames, but got {len(anom)} A-NOM frames"
            )
        if not isinstance(xmet, str) and isinstance(xmet, (Sequence, np.ndarray)):
            if len(anom) != len(xmet):
                raise ValueError(
                    f"number of X-MET frames ({len(xmet)}) must match number of A-NOM frames ({len(anom)})"
                )

    def _load_full_anom() -> Dataset:
        if isinstance(anom, Dataset):
            return anom
        elif isinstance(anom, str):
            return read_product(anom)
        return read_products(anom)

    def _load_anom() -> Dataset:
        if isinstance(anom, Dataset):
            return anom
        elif isinstance(anom, str):
            return read_product(anom)
        return read_products(anom, zoom_at=zoom_at)

    def _load_xmet() -> Dataset | None:
        if isinstance(xmet, Dataset):
            return xmet
        elif isinstance(xmet, str):
            return read_product(xmet)
        elif isinstance(xmet, (Sequence, np.ndarray)) and len(xmet) > 0:
            return read_product(xmet[0])
        return None

    def _load_xmet2() -> Dataset | None:
        if (
            not isinstance(xmet, Dataset)
            and not isinstance(xmet, str)
            and isinstance(xmet, (Sequence, np.ndarray))
            and len(xmet) > 1
        ):
            return read_product(xmet[1])
        return None

    with (
        _load_full_anom() as ds_full,
        _load_anom() as ds,
        nullcontext(_load_xmet()) as ds_xmet,
        nullcontext(_load_xmet2()) as ds_xmet2,
    ):
        if isinstance(ds_xmet, Dataset):
            ds_xmet = rebin_xmet_to_vertical_track(ds_xmet, ds_full)
            ds_xmet = trim_to_latitude_frame_bounds(ds_xmet)

            if isinstance(ds_xmet2, Dataset):
                ds_xmet2 = rebin_xmet_to_vertical_track(ds_xmet2, ds_full)
                ds_xmet2 = trim_to_latitude_frame_bounds(ds_xmet2)

                ds_xmet = concat_datasets(ds_xmet, ds_xmet2, "along_track")

        ds = filter_time(ds, time_range)

        figs: list[list[ECKFigure]] = [[], []]
        layout = create_multi_figure_layout(
            rows=[
                FigureType.CURTAIN,
                FigureType.CURTAIN,
                FigureType.CURTAIN,
            ],
            hspace=0.4,
            wspace=1.0,
            map_rows=[
                FigureType.MAP_1_ROW,
                FigureType.MAP_2_ROW,
            ],
        )

        mf1 = MapFigure(
            ax=layout.axs_map[0],
            show_grid_labels=False,
        )
        mf1.ecplot(ds)
        mf1.plot_track(
            latitude=ds_full.latitude.values,
            longitude=ds_full.longitude.values,
            color="white",
            linestyle="dashed",
            linewidth=1,
            zorder=2,
            highlight_first=False,
            highlight_last=False,
            alpha=0.8,
        )
        figs[0].append(mf1)

        mf2 = MapFigure(
            ax=layout.axs_map[1],
            show_top_labels=False,
            show_right_labels=False,
            style="blue_marble",
            coastlines_resolution="50m",
            show_text_time=False,
            show_text_frame=False,
        )
        mf2.ecplot(ds)
        mf2.plot_track(
            latitude=ds_full.latitude.values,
            longitude=ds_full.longitude.values,
            color="white",
            linestyle="dashed",
            linewidth=1,
            zorder=2,
            highlight_first=False,
            highlight_last=False,
            alpha=0.8,
        )

        coords = get_coords(ds)
        zoom_radius_meters = geodesic(coords[0], coords[-1], units="m") * 0.4
        mf2.ax.set_xlim(-zoom_radius_meters, zoom_radius_meters)  # type: ignore
        mf2.ax.set_ylim(-zoom_radius_meters, zoom_radius_meters)  # type: ignore
        figs[0].append(mf2)

        vars = [
            "mie_attenuated_backscatter",
            "crosspolar_attenuated_backscatter",
            "depol_ratio",
        ]

        for i, (var, ax) in enumerate(zip(vars, layout.axs)):
            if i == 0:
                ax_style_top = "utc"
                ax_style_bottom = "lat"
            elif i == 1:
                ax_style_top = "lat_nolabels"
                ax_style_bottom = "lon"
            elif i == 2:
                ax_style_top = "lon_nolabels"
                ax_style_bottom = "distance"

            cf = CurtainFigure(
                ax=ax,
                ax_style_top=ax_style_top,
                ax_style_bottom=ax_style_bottom,
                num_ticks=8,
            )
            cf.ecplot(
                ds=ds,
                var=var,
                label_length=55,
                height_range=height_range,
                info_text_loc=info_text_loc,
            )
            cf.ecplot_temperature(
                ds=ds,
                colors="#fffffff0",
                levels=[-90, -80, -60, -40, -20, 0, 10],
                label_levels=[-90, -80, -60, -40, -20, 0, 10],
                linestyles="solid",
                linewidths=[1, 0.7, 0.5, 1, 0.5, 1, 0.5],
            )
            if isinstance(ds_xmet, Dataset):
                cf.ecplot_tropopause(ds_xmet)
            figs[1].append(cf)

        return QuicklookFigure(
            fig=layout.fig,
            subfigs=figs,
        )
