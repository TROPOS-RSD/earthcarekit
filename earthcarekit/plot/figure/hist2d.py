import warnings
from typing import Any, Iterable, Literal

import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import LogNorm, Normalize
from matplotlib.figure import Figure, SubFigure
from matplotlib.typing import CoordsType
from numpy.typing import ArrayLike, NDArray

from ...stats import get_mean_from_histogram, get_median_from_histogram
from ..colorbar import add_colorbar
from ..text import add_shade_to_text, format_var_label


class Histogram2DFigure:
    def __init__(
        self,
        fig: Figure | SubFigure | None = None,
        figsize: tuple[float, float] | None = (5, 5),
        box_aspect: float | None = None,
        show_marginals: bool = True,
    ):
        if fig is not None:
            self._fig = fig
        else:
            self._fig = plt.figure(figsize=figsize)

        self._ax: Axes
        self._ax_top: Axes | None
        self._ax_right: Axes | None
        if show_marginals is True:
            self._gs = self._fig.add_gridspec(
                nrows=2,
                ncols=2,
                width_ratios=(5, 1),
                height_ratios=(1, 5),
                hspace=0,
                wspace=0 - 0.01,
            )

            self._ax = self._fig.add_subplot(self._gs[1, 0])
            self._ax_top = self._fig.add_subplot(self._gs[0, 0], sharex=self._ax)
            self._ax_right = self._fig.add_subplot(self._gs[1, 1], sharey=self._ax)
        else:
            self._ax = self._fig.add_subplot()
            self._ax_top = None
            self._ax_right = None

        self._ax.tick_params(bottom=True, top=True, left=True, right=True)
        self._ax.set_box_aspect(box_aspect)

        self._ax.set_zorder(2)
        for ax in (self._ax_top, self._ax_right):
            if ax:
                ax.set_zorder(0)
                ax.patch.set_alpha(0)

        if self._ax_top:
            for i, spine in enumerate(self._ax_top.spines.values()):
                if i != 2:
                    spine.set_visible(False)
        if self._ax_right:
            for i, spine in enumerate(self._ax_right.spines.values()):
                if i != 0:
                    spine.set_visible(False)

        show_marginals_ticks = False
        if self._ax_top:
            self._ax_top.tick_params(
                bottom=show_marginals_ticks, labelbottom=False, left=False, labelleft=False
            )
        if self._ax_right:
            self._ax_right.tick_params(
                bottom=False, labelbottom=False, left=show_marginals_ticks, labelleft=False
            )

        self._xlabel: str | None = None
        self._ylabel: str | None = None
        self._xunits: str | None = None
        self._yunits: str | None = None
        self._xvalue_range: tuple[float, float] | None = None
        self._yvalue_range: tuple[float, float] | None = None

    @property
    def fig(self):
        return self._fig

    @property
    def ax(self):
        return self._ax

    @property
    def ax_top(self):
        return self._ax_top

    @property
    def ax_right(self):
        return self._ax_right

    def _set_ax(
        self,
        xlabel: str | None = None,
        ylabel: str | None = None,
        xunits: str | None = None,
        yunits: str | None = None,
        xvalue_range: tuple[float, float] | None = None,
        yvalue_range: tuple[float, float] | None = None,
    ) -> None:
        if xlabel is not None:
            self._xlabel = xlabel
        if xunits is not None:
            self._xunits = xunits
        if xlabel or xunits:
            self._ax.set_xlabel(format_var_label(self._xlabel, self._xunits))

        if ylabel is not None:
            self._ylabel = ylabel
        if yunits is not None:
            self._yunits = yunits
        if ylabel or yunits:
            self._ax.set_ylabel(format_var_label(self._ylabel, self._yunits))

        if xvalue_range is not None:
            self._xvalue_range = xvalue_range
            self._ax.set_xlim(xvalue_range)
        if yvalue_range is not None:
            self._yvalue_range = yvalue_range
            self._ax.set_ylim(yvalue_range)

    def plot(
        self,
        values: ArrayLike,
        xedges: ArrayLike,
        yedges: ArrayLike,
        *,
        cmap: str = "viridis",
        log_scale: bool = False,
        xlabel: str | None = None,
        ylabel: str | None = None,
        xunits: str | None = None,
        yunits: str | None = None,
        xvalue_range: tuple[float, float] | None = None,
        yvalue_range: tuple[float, float] | None = None,
        show_median: bool = False,
        show_mean: bool = False,
        decimals: int = 3,
        xmean: float | None = None,
        ymean: float | None = None,
        xmedian: float | None = None,
        ymedian: float | None = None,
        show_colorbar: bool = False,
        show_shade: bool = True,
        kwargs_bars: dict[str, Any] = {},
        kwargs_colorbar: dict[str, Any] = {},
        kwargs_shade: dict[str, Any] = {},
        kwargs_annotate: dict[str, Any] = {},
    ) -> "Histogram2DFigure":
        # Histogram
        values = np.asarray(values)
        xedges = np.asarray(xedges)
        yedges = np.asarray(yedges)

        x_meshgrid, y_meshgrid = np.meshgrid(xedges, yedges)
        z_values = values.copy()
        norm = LogNorm() if log_scale else Normalize()
        pcm = self._ax.pcolormesh(x_meshgrid, y_meshgrid, z_values, cmap=cmap, norm=norm)

        # Marginals
        xvalues = np.nansum(values, axis=0)
        yvalues = np.nansum(values, axis=1)

        xcenters = 0.5 * (xedges[:-1] + xedges[1:])
        ycenters = 0.5 * (yedges[:-1] + yedges[1:])

        if self._ax_top and self._ax_right:
            self._ax_top.bar(
                x=xcenters,
                height=xvalues,
                width=np.diff(xedges),
                align="center",
                **{"color": "#B2B2B2", "alpha": 1.0, **kwargs_bars},
            )
            self._ax_right.barh(
                y=ycenters,
                width=yvalues,
                height=np.diff(yedges),
                align="center",
                **{"color": "#B2B2B2", "alpha": 1.0, **kwargs_bars},
            )

        # Optionally, show mean and/or median
        self._show_mean_median(
            xvalues=xvalues,
            yvalues=yvalues,
            xedges=xedges,
            yedges=yedges,
            xcenters=xcenters,
            ycenters=ycenters,
            show_median=show_median,
            show_mean=show_mean,
            decimals=decimals,
            xmean=xmean,
            ymean=ymean,
            xmedian=xmedian,
            ymedian=ymedian,
            show_shade=show_shade,
            kwargs_shade=kwargs_shade,
            kwargs_annotate=kwargs_annotate,
        )

        # Optionally, add colorbar
        if show_colorbar:
            ax = self._ax_right or self._ax
            cbar = add_colorbar(
                fig=self._fig,
                ax=ax,
                data=pcm,
                **{
                    "label": "Frequency",
                    "position": "right",
                    "cmap": cmap,
                    **kwargs_colorbar,
                },
            )

        # Update axes
        self._set_ax(
            xlabel=xlabel,
            ylabel=ylabel,
            xunits=xunits,
            yunits=yunits,
            xvalue_range=xvalue_range,
            yvalue_range=yvalue_range,
        )

        return self

    def _show_mean_median(
        self,
        xvalues: NDArray,
        yvalues: NDArray,
        xedges: NDArray,
        yedges: NDArray,
        xcenters: NDArray,
        ycenters: NDArray,
        show_median: bool = False,
        show_mean: bool = False,
        decimals: int = 3,
        xmean: float | None = None,
        ymean: float | None = None,
        xmedian: float | None = None,
        ymedian: float | None = None,
        show_shade: bool = True,
        kwargs_shade: dict[str, Any] = {},
        kwargs_annotate: dict[str, Any] = {},
    ) -> None:
        if show_median is False and show_mean is False:
            return

        if xmedian is None:
            if show_median is True:
                warnings.warn("'xmedian' not given, estimating from histogram instead")
                xmedian = get_median_from_histogram(xvalues, xedges)
            else:
                xmedian = np.nan

        if ymedian is None:
            if show_median is True:
                warnings.warn("'ymedian' not given, estimating from histogram instead")
                ymedian = get_median_from_histogram(yvalues, yedges)
            else:
                ymedian = np.nan

        xmedian_label = np.round(xmedian, decimals)
        ymedian_label = np.round(ymedian, decimals)

        if xmean is None:
            if show_median is True:
                warnings.warn("'xmean' not given, estimating from histogram instead")
                xmean = get_mean_from_histogram(xvalues, xcenters)
            else:
                xmean = np.nan

        if ymean is None:
            if show_mean is True:
                warnings.warn("'ymean' not given, estimating from histogram instead")
                ymean = get_mean_from_histogram(yvalues, ycenters)
            else:
                ymean = np.nan

        xmean_label = np.round(xmean, decimals)
        ymean_label = np.round(ymean, decimals)

        linestyle_mean = "dashed"
        linestyle_median = "dotted"
        color_mean = "tab:red"
        color_median = "black"

        if show_mean is True:
            self._ax.axhline(ymean, color=color_mean, linestyle=linestyle_mean)
            self._ax.axvline(xmean, color=color_mean, linestyle=linestyle_mean, label="mean")

        if show_median is True:
            self._ax.axhline(ymedian, color=color_median, linestyle=linestyle_median)
            self._ax.axvline(
                xmedian, color=color_median, linestyle=linestyle_median, label="median"
            )

        annotations: list = []

        trans = transforms.blended_transform_factory(self._ax.transData, self._ax.transAxes)
        common = dict(va="bottom", textcoords="offset points", xycoords=trans, **kwargs_annotate)
        if xmean > xmedian:
            annotations.append(
                self._ax.annotate(
                    xmean_label,
                    color=color_mean,
                    xy=(xmean, 1.0),
                    xytext=(7, 5),
                    ha="left",
                    **common,
                ),
            )
            annotations.append(
                self._ax.annotate(
                    xmedian_label,
                    color=color_median,
                    xy=(xmedian, 1.0),
                    xytext=(-7, 5),
                    ha="right",
                    **common,
                ),
            )
        else:
            annotations.append(
                self._ax.annotate(
                    xmean_label,
                    color=color_mean,
                    xy=(xmean, 1.0),
                    xytext=(-7, 5),
                    ha="right",
                    **common,
                ),
            )
            annotations.append(
                self._ax.annotate(
                    xmedian_label,
                    color=color_median,
                    xy=(xmedian, 1.0),
                    xytext=(7, 5),
                    ha="left",
                    **common,
                ),
            )

        trans = transforms.blended_transform_factory(self._ax.transAxes, self._ax.transData)
        common = dict(ha="left", textcoords="offset points", xycoords=trans, **kwargs_annotate)
        if ymean > ymedian:
            annotations.append(
                self._ax.annotate(
                    ymean_label,
                    color=color_mean,
                    xy=(1.0, ymean),
                    xytext=(7, 5),
                    va="bottom",
                    **common,
                ),
            )
            annotations.append(
                self._ax.annotate(
                    ymedian_label,
                    color=color_median,
                    xy=(1.0, ymedian),
                    xytext=(7, -5),
                    va="top",
                    **common,
                ),
            )
        else:
            annotations.append(
                self._ax.annotate(
                    ymean_label,
                    color=color_mean,
                    xy=(1.0, ymean),
                    xytext=(7, -5),
                    va="top",
                    **common,
                ),
            )
            annotations.append(
                self._ax.annotate(
                    ymedian_label,
                    color=color_median,
                    xy=(1.0, ymedian),
                    xytext=(7, 5),
                    va="bottom",
                    **common,
                ),
            )

        if show_shade:
            for a in annotations:
                add_shade_to_text(a, **{"alpha": 0.2, **kwargs_shade})

        if self._ax_right:
            self._ax_right.axhline(ymean, color=color_mean, linestyle=linestyle_mean)
            self._ax_right.axhline(ymedian, color=color_median, linestyle=linestyle_median)

        if self._ax_top:
            self._ax_top.axvline(xmean, color=color_mean, linestyle=linestyle_mean)
            self._ax_top.axvline(xmedian, color=color_median, linestyle=linestyle_median)

        self._ax.legend(
            bbox_to_anchor=(1.01, 1.05),
            loc="lower left",
            borderaxespad=0,
            frameon=True,
            fancybox=False,
            framealpha=1,
            edgecolor="black",
        )

    def plot_scatter(
        self,
        x: NDArray,
        y: NDArray,
        *,
        texts: Iterable[str] | None = None,
        xytext: tuple[float, float] | None = (10, 0),
        textcoords: CoordsType | None = "offset points",
        ha: Literal["left", "center", "right"] = "left",
        va: Literal["baseline", "bottom", "center", "center_baseline", "top"] = "center",
        show_shade: bool = True,
        kwargs_annotate: dict[str, Any] = {},
        kwargs_shade: dict[str, Any] = {},
        **kwargs_scatter,
    ) -> "Histogram2DFigure":
        sc = self._ax.scatter(x, y, **kwargs_scatter)

        if texts is not None:
            for (
                text,
                _x,
                _y,
            ) in zip(texts, x, y):
                annotation = self._ax.annotate(
                    text=text,
                    xy=(_x, _y),
                    xytext=xytext,
                    textcoords=textcoords,
                    ha=ha,
                    va=va,
                    **kwargs_annotate,
                )
                if show_shade:
                    add_shade_to_text(annotation, **kwargs_shade)

        return self
