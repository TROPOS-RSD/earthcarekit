from contextlib import nullcontext

import numpy as np
from xarray import Dataset

from ...utils import filter_time
from ...utils.read import read_product
from ...utils.read.product._rebin_xmet_to_vertical_track import (
    rebin_xmet_to_vertical_track,
)
from ...utils.time import TimeRangeLike
from ...utils.typing import DistanceRangeLike
from ..figure import CurtainFigure, ECKFigure, FigureType, SwathFigure
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
) -> QuicklookFigure:
    """
    Creates a 4 panel quicklook of a storm or deep convective event, displaying:

    - 1st row: RGB image from MSI_RGR_1C
    - 2nd row: Radar reflectivity from CPR_FMR_2A
    - 3rd row: Doppler velocity from CPR_CD__2A
    - 4th row: Total attenuated backscatter from ATL_EBD_2A

    Args:
        ds_mrgr (Dataset): The MSI_RGR_1C product filepath or dataset.
        ds_cfmr (Dataset): The CPR_FMR_2A product filepath or dataset.
        ds_ccd (Dataset): The CPR_CD__2A product filepath or dataset.
        ds_aebd (Dataset): The ATL_EBD_2A product filepath or dataset.
        ds_xmet (Dataset | None, optional): The AUX_MET_1D product filepath or dataset.
            If given, temperature contour lines will be added to the plots. Defaults to None.
        height_range (DistanceRangeLike | None, optional): A height range (i.e., min, max) in meters. Defaults to (-250, 20e3).
        time_range (TimeRangeLike | None, optional): A time range to filter the displayed data. Defaults to None.
        info_text_loc (str | None, optional): The positioning of the orbt, frame and product info text (e.g., "upper right").
            Defaults to None.
        trim_to_frame (bool, optional): Wether the read products should be trimmed to the EarthCARE frame bounds.

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

        layout = create_multi_figure_layout(
            rows=[
                FigureType.SWATH,
                FigureType.CURTAIN_75,
                FigureType.CURTAIN_75,
                FigureType.CURTAIN_75,
            ],
            hspace=[0.7, 0.35, 0.35],
        )

        figs: list[ECKFigure] = []

        # 1. Row: MSI RGR RGB
        ax = layout.axs[0]

        f: SwathFigure | CurtainFigure
        f = SwathFigure(ax=ax, ax_style_top="time", ax_style_bottom="geo")
        f = f.ecplot(
            ds=ds_mrgr,
            var="rgb",
            time_range=time_range,
            info_text_loc=info_text_loc,
        )
        f = f.ecplot_coastline(ds_mrgr)
        figs.append(f)

        ds_xmet_vert: Dataset | None = None
        if isinstance(ds_xmet, Dataset):
            ds_xmet_vert = rebin_xmet_to_vertical_track(ds_xmet, ds_aebd)

        # 2. Row CPR FMR reflectivity (Range -40 - 20 dBz)
        ax = layout.axs[1]
        f = CurtainFigure(
            ax=ax,
            ax_style_top="none",
            ax_style_bottom="distance_notitle",
        )
        f = f.ecplot(
            ds=ds_cfmr,
            var="reflectivity_corrected",
            height_range=height_range,
            time_range=time_range,
            value_range=(-40, 20),
            info_text_loc=info_text_loc,
        )
        f = f.ecplot_elevation(ds_cfmr)
        f = f.ecplot_tropopause(ds_aebd)
        if isinstance(ds_xmet_vert, Dataset):
            f = f.ecplot_temperature(ds_xmet_vert)
        figs.append(f)

        # 3. Row CPR-CD Doppler Velocity best estimate (Range -5 -5 m/s)
        ax = layout.axs[2]
        f = CurtainFigure(
            ax=ax,
            ax_style_top="none",
            ax_style_bottom="distance_notitle",
        )
        f = f.ecplot(
            ds=ds_ccd,
            var="doppler_velocity_best_estimate",
            height_range=height_range,
            time_range=time_range,
            value_range=(-5, 5),
            info_text_loc=info_text_loc,
        )
        f = f.ecplot_elevation(ds_cfmr)
        f = f.ecplot_tropopause(ds_aebd)
        if isinstance(ds_xmet_vert, Dataset):
            f = f.ecplot_temperature(ds_xmet_vert)
        figs.append(f)

        # 4. Row ATL-EBD total attenuated mie backscatter
        ax = layout.axs[3]
        f = CurtainFigure(
            ax=ax,
            ax_style_top="none",
            ax_style_bottom="distance",
        )
        f = f.ecplot(
            ds=ds_aebd,
            var="mie_total_attenuated_backscatter_355nm",
            height_range=height_range,
            time_range=time_range,
            info_text_loc=info_text_loc,
        )
        f = f.ecplot_elevation(ds_cfmr)
        f = f.ecplot_tropopause(ds_aebd)
        if isinstance(ds_xmet_vert, Dataset):
            f = f.ecplot_temperature(ds_xmet_vert, colors="white")
        figs.append(f)

        return QuicklookFigure(
            fig=layout.fig,
            subfigs=[figs],
        )
