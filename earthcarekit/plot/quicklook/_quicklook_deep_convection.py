from contextlib import nullcontext
from typing import Any

import numpy as np
from xarray import Dataset

from ...color import Color
from ...filter import filter_time
from ...geo import get_central_latitude, get_central_longitude
from ...read import read_product, rebin_xmet_to_vertical_track
from ...typing import DistanceRangeLike
from ...utils.time import TimeRangeLike, TimestampLike
from ..figure import CurtainFigure, ECKFigure, FigureType, MapFigure, SwathFigure
from ..figure.map import MapStyleLike
from ..figure.multi_panel import create_multi_figure_layout
from ._quicklook_results import QuicklookFigure


def ecquicklook_deep_convection(
    mrgr: Dataset | str,
    cfmr: Dataset | str,
    ccd: Dataset | str,
    aebd: Dataset | str,
    xmet: Dataset | str | None = None,
    height_range: DistanceRangeLike | None = (-250, 20e3),
    time_range: TimeRangeLike | None = None,
    info_text_loc: str | None = None,
    trim_to_frame: bool = False,
    mrgr_kwargs: dict[str, Any] | None = None,
    cfmr_kwargs: dict[str, Any] | None = None,
    ccd_kwargs: dict[str, Any] | None = None,
    aebd_kwargs: dict[str, Any] | None = None,
    map_kwargs: dict[str, Any] | None = None,
    marble_kwargs: dict[str, Any] | None = None,
    map_style: MapStyleLike = "gray",
    map_timestamp: TimestampLike | None = None,
    marble_style: MapStyleLike = "gray",
    marble_timestamp: TimestampLike | None = None,
    show_mrgr: bool = True,
    show_cfmr: bool = True,
    show_ccd: bool = True,
    show_aebd: bool = True,
    show_marble: bool | None = None,
    show_map: bool | None = None,
    show_maps: bool | None = None,
    small_marble: bool = False,
) -> QuicklookFigure:
    """Creates a 4-panel quicklook of a storm or deep convective event.

    Displays:
    - Row 1: MSI_RGR_1C RGB image
    - Row 2: CPR_FMR_2A radar reflectivity
    - Row 3: CPR_CD__2A Doppler velocity
    - Row 4: ATL_EBD_2A total attenuated backscatter

    Args:
        mrgr: MSI_RGR_1C product (filepath or dataset).
        cfmr: CPR_FMR_2A product (filepath or dataset).
        ccd: CPR_CD__2A product (filepath or dataset).
        aebd: ATL_EBD_2A product (filepath or dataset).
        xmet: AUX_MET_1D product; adds temperature contours if given.
        height_range: Height range (min, max) in meters; defaults to (-250, 20e3).
        time_range: Time range to filter displayed data.
        info_text_loc: Position of orbit/frame/product info text (e.g., "upper right").
        trim_to_frame: Trim products to EarthCARE frame bounds if True.
        mrgr_kwargs: Passed to `SwathFigure.ecplot()`.
        cfmr_kwargs: Passed to `CurtainFigure.ecplot()`.
        ccd_kwargs: Passed to `CurtainFigure.ecplot()`.
        aebd_kwargs: Passed to `CurtainFigure.ecplot()`.
        map_kwargs: Passed to `MapFigure.ecplot()`.
        map_style: Background style for map; defaults to "gray".
        map_timestamp: Time reference for map nightshade.
        marble_style: Background style for marble map; defaults to "gray".
        marble_timestamp: Time reference for marble map nightshade.
        show_mrgr: Display MSI_RGR_1C if True.
        show_cfmr: Display CPR_FMR_2A if True.
        show_ccd: Display CPR_CD__2A if True.
        show_aebd: Display ATL_EBD_2A if True.
        show_marble: Display marble map (MSI_RGR_1C-based) if True.
        show_map: Display zoomed map (MSI_RGR_1C-based) if True.
        show_maps: Display two maps (global + zoomed) before along-track plots if True.
        small_marble: Reduce marble map to first row if True.

    Returns:
        QuicklookFigure: The quicklook object.

    Examples:
        ```python
        import earthcarekit as eck

        frame = "07590D"
        ds_mrgr = eck.ecload("MSI_RGR_1C", frame, download=True)
        ds_cfmr = eck.ecload("CPR_FMR_2A", frame, download=True)
        ds_ccd = eck.ecload("CPR_CD__2A", frame, download=True)
        ds_aebd = eck.ecload("ATL_EBD_2A", frame, download=True)
        ds_xmet = eck.ecload("AUX_MET_1D", frame, download=True)

        ql = eck.ecquicklook_deep_convection(
            mrgr=ds_mrgr,
            cfmr=ds_cfmr,
            ccd=ds_ccd,
            aebd=ds_aebd,
            xmet=ds_xmet,
            time_range=("2025-09-28T18:27:10", None),
            info_text_loc="upper left",
        )
        ```

        ![ecquicklook_deep_convection.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/quicklooks/ecquicklook_deep_convection.png)
    """
    show_maps = show_maps or show_marble or show_map or False
    show_marble = show_marble or show_maps
    show_map = show_map or show_maps

    def _load_xmet() -> Dataset | None:
        if isinstance(xmet, Dataset):
            return xmet
        elif isinstance(xmet, str):
            return read_product(xmet)
        return None

    with (
        read_product(mrgr, trim_to_frame=trim_to_frame) as ds_mrgr,
        read_product(cfmr, trim_to_frame=trim_to_frame) as ds_cfmr,
        read_product(ccd, trim_to_frame=trim_to_frame) as ds_ccd,
        read_product(aebd, trim_to_frame=trim_to_frame) as ds_aebd,
        nullcontext(_load_xmet()) as ds_xmet,
    ):
        min_time = np.max(
            [
                np.min(ds_mrgr.time.values),
                np.min(ds_cfmr.time.values),
                np.min(ds_ccd.time.values),
                np.min(ds_aebd.time.values),
            ]
        )

        max_time = np.min(
            [
                np.max(ds_mrgr.time.values),
                np.max(ds_cfmr.time.values),
                np.max(ds_ccd.time.values),
                np.max(ds_aebd.time.values),
            ]
        )

        ds_mrgr = filter_time(ds_mrgr, (min_time, max_time))
        ds_cfmr = filter_time(ds_cfmr, (min_time, max_time))
        ds_ccd = filter_time(ds_ccd, (min_time, max_time))
        ds_aebd = filter_time(ds_aebd, (min_time, max_time))
        ds_xmet_vert: Dataset | None = None
        if isinstance(ds_xmet, Dataset):
            ds_xmet_vert = rebin_xmet_to_vertical_track(ds_xmet, ds_aebd)
            ds_xmet_vert = filter_time(ds_xmet_vert, time_range)

        map_rows = (
            [
                FigureType.MAP_1_ROW if small_marble else FigureType.MAP_2_ROW,
                FigureType.MAP_FULL_ROW,
            ]
            if show_maps
            else []
        )
        layout = create_multi_figure_layout(
            rows=[
                FigureType.SWATH,
                FigureType.CURTAIN_75,
                FigureType.CURTAIN_75,
                FigureType.CURTAIN_75,
            ],
            map_rows=map_rows,
            hspace=[0.7, 0.35, 0.35],
        )

        f: SwathFigure | CurtainFigure | MapFigure
        figs: list[ECKFigure] = []

        if show_maps:
            ax = layout.axs_map[0]
            if not show_marble:
                ax.remove()
            else:
                _marble_kwargs: dict[str, Any] = dict(
                    view="global",
                    time_range=time_range,
                    highlight_last=True,
                    highlight_first=False,
                    color=Color("ec:red").set_alpha(0.7),
                    color2="black",
                    linewidth2=1 if small_marble else 1.5,
                    linestyle2="dashed",
                    central_latitude=get_central_latitude(ds_mrgr.latitude.values),
                    central_longitude=get_central_longitude(ds_mrgr.longitude.values),
                    colorbar=False,
                    show_swath_border=False,
                )
                if marble_kwargs:
                    _marble_kwargs.update(marble_kwargs)
                f = MapFigure(
                    ax=ax,
                    show_grid_labels=False,
                    style=marble_style,
                    timestamp=marble_timestamp,
                )
                f.ecplot(ds=ds_mrgr, **_marble_kwargs)
                figs.append(f)

            ax = layout.axs_map[1]
            if not show_map:
                ax.remove()
            else:
                _map_kwargs: dict[str, Any] = dict(
                    style=map_style,
                    timestamp=map_timestamp,
                    show_right_labels=False,
                    show_bottom_labels=False,
                    show_text_frame=False,
                    show_text_time=False,
                )
                _mrgr_map_kwargs: dict[str, Any] = dict(
                    var="tir2",
                    cmap="msi_bt_enhanced",
                    show_nadir=False,
                    show_swath_border=False,
                    view="overpass",
                    time_range=time_range,
                    colorbar_position="bottom",
                    colorbar_spacing=0.1,
                )
                if map_kwargs:
                    if map_kwargs.get("var") != "tir2" and "cmap" not in map_kwargs:
                        map_kwargs["cmap"] = None
                    _mrgr_map_kwargs.update(map_kwargs)

                f = MapFigure(ax=ax, **_map_kwargs)
                f.ecplot(ds=ds_mrgr, **_mrgr_map_kwargs)
                figs.append(f)

        # 1. Row: MSI RGR RGB
        ax = layout.axs[0]
        if not show_mrgr:
            ax.remove()
        else:
            f = SwathFigure(ax=ax, ax_style_top="time", ax_style_bottom="geo")
            _mrgr_kwargs: dict[str, Any] = dict(
                var="rgb",
                time_range=time_range,
                info_text_loc=info_text_loc,
            )
            if mrgr_kwargs:
                _mrgr_kwargs.update(mrgr_kwargs)
            f = f.ecplot(ds=ds_mrgr, **_mrgr_kwargs)
            f = f.ecplot_coastline(ds_mrgr)
            figs.append(f)

        # 2. Row CPR FMR reflectivity (Range -40 - 20 dBz)
        ax = layout.axs[1]
        if not show_cfmr:
            ax.remove()
        else:
            f = CurtainFigure(
                ax=ax,
                ax_style_top="none",
                ax_style_bottom="distance_notitle",
            )
            _cfmr_kwargs: dict[str, Any] = dict(
                var="reflectivity_corrected",
                height_range=height_range,
                time_range=time_range,
                value_range=(-40, 20),
                info_text_loc=info_text_loc,
            )
            if cfmr_kwargs:
                _cfmr_kwargs.update(cfmr_kwargs)
            f = f.ecplot(ds=ds_cfmr, **_cfmr_kwargs)
            f = f.ecplot_elevation(ds_cfmr)
            f = f.ecplot_tropopause(ds_aebd)
            if isinstance(ds_xmet_vert, Dataset):
                f = f.ecplot_temperature(ds_xmet_vert)
            figs.append(f)

        # 3. Row CPR-CD Doppler Velocity best estimate (Range -5 -5 m/s)
        ax = layout.axs[2]
        if not show_ccd:
            ax.remove()
        else:
            f = CurtainFigure(
                ax=ax,
                ax_style_top="none",
                ax_style_bottom="distance_notitle",
            )
            _ccd_kwargs: dict[str, Any] = dict(
                var="doppler_velocity_best_estimate",
                height_range=height_range,
                time_range=time_range,
                value_range=(-5, 5),
                info_text_loc=info_text_loc,
            )
            if ccd_kwargs:
                _ccd_kwargs.update(ccd_kwargs)
            f = f.ecplot(ds=ds_ccd, **_ccd_kwargs)
            f = f.ecplot_elevation(ds_cfmr)
            f = f.ecplot_tropopause(ds_aebd)
            if isinstance(ds_xmet_vert, Dataset):
                f = f.ecplot_temperature(ds_xmet_vert)
            figs.append(f)

        # 4. Row ATL-EBD total attenuated mie backscatter
        ax = layout.axs[3]
        if not show_aebd:
            ax.remove()
        else:
            f = CurtainFigure(
                ax=ax,
                ax_style_top="none",
                ax_style_bottom="distance",
            )
            _aebd_kwargs: dict[str, Any] = dict(
                var="mie_total_attenuated_backscatter_355nm",
                height_range=height_range,
                time_range=time_range,
                info_text_loc=info_text_loc,
            )
            if aebd_kwargs:
                _aebd_kwargs.update(aebd_kwargs)
            f = f.ecplot(ds=ds_aebd, **_aebd_kwargs)
            f = f.ecplot_elevation(ds_cfmr)
            f = f.ecplot_tropopause(ds_aebd)
            if isinstance(ds_xmet_vert, Dataset):
                f = f.ecplot_temperature(ds_xmet_vert, colors="white")
            figs.append(f)

        return QuicklookFigure(
            fig=layout.fig,
            subfigs=[figs],
        )
