from xarray import Dataset

from ...utils.read.product.auxiliary.aux_met_1d import rebin_xmet_to_vertical_track
from ...utils.time import TimeRangeLike
from ...utils.typing import DistanceRangeLike
from ..figure import CurtainFigure, ECKFigure, FigureType, SwathFigure
from ..figure.multi_panel import create_multi_figure_layout
from ._quicklook_results import QuicklookFigure


def ecquicklook_deep_convection(
    ds_mrgr: Dataset,
    ds_cfmr: Dataset,
    ds_ccd: Dataset,
    ds_aebd: Dataset,
    ds_xmet: Dataset | None = None,
    height_range: DistanceRangeLike | None = (-250, 20e3),
    time_range: TimeRangeLike | None = None,
    info_text_loc: str | None = None,
) -> QuicklookFigure:

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
