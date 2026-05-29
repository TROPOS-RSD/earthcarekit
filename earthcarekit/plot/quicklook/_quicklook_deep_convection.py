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
    """
    Creates a 4 panel quicklook of a storm or deep convective event, displaying:

    - 1st row: RGB image from MSI_RGR_1C
    - 2nd row: Radar reflectivity from CPR_FMR_2A
    - 3rd row: Doppler velocity from CPR_CD__2A
    - 4th row: Total attenuated backscatter from ATL_EBD_2A

    Args:
        ds_mrgr (Dataset):
            The MSI_RGR_1C product filepath or dataset.
        ds_cfmr (Dataset):
            The CPR_FMR_2A product filepath or dataset.
        ds_ccd (Dataset):
            The CPR_CD__2A product filepath or dataset.
        ds_aebd (Dataset):
            The ATL_EBD_2A product filepath or dataset.
        ds_xmet (Dataset | None, optional):
            The AUX_MET_1D product filepath or dataset.
            If given, temperature contour lines will be added to the plots. Defaults to None.
        height_range (DistanceRangeLike | None, optional):
            A height range (i.e., min, max) in meters. Defaults to (-250, 20e3).
        time_range (TimeRangeLike | None, optional):
            A time range to filter the displayed data. Defaults to None.
        info_text_loc (str | None, optional):
            The positioning of the orbt, frame and product info text (e.g., "upper right").
            Defaults to None.
        trim_to_frame (bool, optional):
            Wether the read products should be trimmed to the EarthCARE frame bounds.
        mrgr_kwargs (dict[str, Any] | None, optional):
            Additional keyword arguemnts passed to the `SwathFigure.ecplot()` function.
            Defaults to None.
        cfmr_kwargs (dict[str, Any] | None, optional):
            Additional keyword arguemnts passed to the `CurtainFigure.ecplot()` function.
            Defaults to None.
        ccd_kwargs (dict[str, Any] | None, optional):
            Additional keyword arguemnts passed to the `CurtainFigure.ecplot()` function.
            Defaults to None.
        aebd_kwargs (dict[str, Any] | None, optional):
            Additional keyword arguemnts passed to the `CurtainFigure.ecplot()` function.
            Defaults to None.
        map_kwargs (dict[str, Any] | None, optional):
            Additional keyword arguemnts passed to the `MapFigure.ecplot()` function.
            Defaults to None.
        map_style (MapStyleLike, optional):
            Style of the map's background image. Defaults to "gray".
        map_timestamp (TimeRangeLike | None, optional):
            Time reference used for nightshade overlay. Defaults to None.
        marble_style (MapStyleLike, optional):
            Style of the "marble" map's background image. Defaults to "gray".
        marble_timestamp (TimeRangeLike | None, optional):
            Time reference used for nightshade overlay for the "marble" map. Defaults to None.
        show_mrgr (bool, optional):
            If True, displays the MSI_RGR_1C sub-figure. Defaults to True.
        show_cfmr (bool, optional):
            If True, displays the CPR_FMR_2A sub-figure. Defaults to True.
        show_ccd (bool, optional):
            If True, displays the CPR_CD__2A sub-figure. Defaults to True.
        show_aebd (bool, optional):
            If True, displays the ATL_EBD_2A sub-figure. Defaults to True.
        show_marble (bool | None, optional):
            If True, displays the "marble" sub-figure (MSI_RGR_1C-based). Defaults to None.
        show_map (bool | None, optional):
            If True, displays the map sub-figure (MSI_RGR_1C-based). Defaults to None.
        show_maps (bool | None, optional):
            If True, two maps will be plotted in column before the along-track plots.
            The first map shows the EC track on a global earth map (i.e., "marble").
            The second map shows swath data from MSI_RGR_1C zoomed to the selected `time_range`.
            Defaults to None.
        small_marble (bool, optional):
            If True, the size of the "marble" map will be reduced to the first figure row;
            otherwise it will take the space of the first two rows. Defaults to False.

    Returns:
        QuicklookFigure: The quicklook object.

    Examples:
        ```python
        import earthcarekit as eck

        df = eck.search_product(
            file_type=["mrgr", "cfmr", "ccd", "aebd", "xmet"],
            orbit_and_frame="07590D",
        ).filter_latest()

        fp_mrgr = df.filter_file_type("mrgr").filepath[-1]
        fp_cfmr = df.filter_file_type("cfmr").filepath[-1]
        fp_ccd = df.filter_file_type("ccd").filepath[-1]
        fp_aebd = df.filter_file_type("aebd").filepath[-1]
        fp_xmet = df.filter_file_type("xmet").filepath[-1]

        ql = eck.ecquicklook_deep_convection(
            mrgr=fp_mrgr,
            cfmr=fp_cfmr,
            ccd=fp_ccd,
            aebd=fp_aebd,
            xmet=fp_xmet,
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
