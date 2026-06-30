from typing import Any, Literal, Self, Sequence

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
from numpy.typing import ArrayLike

from ...color import Color, ColorLike
from ...stats import get_hist_mean, get_hist_median, get_hist_percentile
from ...utils.numpy import bins_to_centers, centers_to_bins
from ..text import add_shade_to_text, format_var_label
from ._figure import BaseFigure


class HistFigure(BaseFigure):
    def __init__(
        self: Self,
        ax: Axes | None = None,
        fig: Figure | None = None,
        figsize: tuple[float, float] = (5.0, 5.0),
        dpi: float | None = None,
        title: str | None = None,
        fig_height_scale: float = 1.0,
        fig_width_scale: float = 1.0,
        axes_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        show_grid: bool | None = False,
        grid_kwargs: dict[str, Any] = {},
        title_kwargs: dict[str, Any] = {},
        # base
        box_aspect: float | None = None,
    ):
        super().__init__(
            ax=ax,
            fig=fig,
            figsize=figsize,
            dpi=dpi,
            title=title,
            fig_height_scale=fig_height_scale,
            fig_width_scale=fig_width_scale,
            axes_rect=axes_rect,
            show_grid=show_grid,
            grid_kwargs=grid_kwargs,
            title_kwargs=title_kwargs,
        )
        self._ax.remove()

        self._gs: GridSpec | None = None
        self._ax = self._fig.add_subplot()

        # self._ax.tick_params(bottom=True, top=True, left=True, right=True)
        self._ax.set_box_aspect(box_aspect)

        self._xlabel: str | None = None
        self._ylabel: str | None = None
        self._xunits: str | None = None
        self._yunits: str | None = None
        self._xvalue_range: tuple[float, float] | None = None
        self._yvalue_range: tuple[float, float] | None = None

        self._show_legend: bool = True

    def set_ax(
        self: Self,
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

        self.set_grid()

    def plot(
        self: Self,
        values: ArrayLike,
        edges: ArrayLike | None = None,
        *,
        show_mean: bool = False,
        show_median: bool = False,
        show_percentiles: bool = True,
        show_vlines: bool = True,
        show_texts: bool = False,
        show_line: bool = True,
        show_bar: bool = True,
        linealpha: float | None = 1.0,
        mode: Literal["step", "line"] = "step",
        mean: float | None = None,
        median: float | None = None,
        percentiles: float | Sequence[float] | None = None,
        centers: ArrayLike | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        xunits: str | None = None,
        yunits: str | None = None,
        xvalue_range: tuple[float, float] | None = None,
        yvalue_range: tuple[float, float] | None = None,
        color: ColorLike | None = None,
        alpha: float | None = 0.25,
        linewidth: float | None = None,
        text_xpos: float = 0.02,
        text_ypos: float = 0.98,
        legend_label: str | None = None,
        bar_kwargs: dict[str, Any] | None = None,
        line_kwargs: dict[str, Any] | None = None,
    ) -> Self:
        if mode not in ["step", "line"]:
            raise ValueError(f'Invalid mode "{mode}"; expected "step" or "line".')

        # Histogram
        values = np.asarray(values)
        if edges is None:
            if centers is None:
                raise ValueError(
                    "Missing 'edges' or 'centers' argument; at least one must be provided."
                )
            edges = centers_to_bins(centers)
        elif centers is None:
            centers = bins_to_centers(edges)
        edges = np.asarray(edges)
        centers = np.asarray(centers)
        bin_widths = np.diff(edges)

        if not show_bar:
            alpha = 0.0
        elif alpha is None:
            alpha = 1.0

        _bar_kwargs: dict[str, Any] = dict(
            linewidth=0,
            color=color,
        )
        if bar_kwargs is not None:
            _bar_kwargs.update(bar_kwargs)
        bars = self._ax.bar(
            x=centers,
            height=values,
            width=bin_widths,
            alpha=None,
            **_bar_kwargs,
        )
        _color = Color(color if color is not None else bars.patches[0].get_facecolor())  # type: ignore
        for bar in bars:
            bar.set_facecolor(_color.set_alpha(alpha))

        if show_line:
            _line_kwargs: dict[str, Any] = dict(
                color=_color,
                linewidth=linewidth,
                alpha=linealpha,
            )
            if line_kwargs is not None:
                _line_kwargs.update(line_kwargs)
            if mode == "step":
                _step_kwargs = _line_kwargs.copy()
                _step_kwargs.update({"marker": "none"})
                self._ax.step(
                    x=edges,
                    y=np.append(values, values[-1]),
                    where="post",
                    **_step_kwargs,
                )
                if "marker" in _line_kwargs:
                    _marker_kwargs = _line_kwargs.copy()
                    _marker_kwargs.update({"linestyle": "none"})
                    self._ax.plot(
                        centers,
                        values,
                        **_marker_kwargs,
                    )
            else:
                self._ax.plot(
                    centers,
                    values,
                    **_line_kwargs,
                )
        else:
            linealpha = 0.0

        texts: list[str] = []
        if show_mean:
            mean = self._add_mean(
                value=mean,
                counts=values,
                centers=centers,
                color=_color,
                show_vlines=show_vlines,
            )
            texts.append(f"mean: {mean:.2f}\n")

        _percentiles: np.ndarray
        if percentiles is None:
            _percentiles = np.array([])
        else:
            _percentiles = np.atleast_1d(percentiles)

        if show_median:
            _percentiles = np.unique(np.append(_percentiles, [50]))

        percentile_values: list[float] = []
        if show_percentiles and _percentiles.size > 0:
            for p in _percentiles:
                if p == 50:
                    median = self._add_median(
                        value=median,
                        counts=values,
                        edges=edges,
                        color=_color,
                        show_vlines=show_vlines,
                    )
                    texts.append(f"P$_{{50}}$ = {median:.2f}")
                else:
                    p_val = self._add_percentile(
                        counts=values,
                        edges=edges,
                        percentile=p,
                        color=_color,
                        linestyle="dashed",
                        linewidth=1,
                        show_vlines=show_vlines,
                    )
                    percentile_values.append(p_val)
                    p_text = f"{p:.2f}".rstrip("0").rstrip(".")
                    texts.append(f"P$_{{{p_text}}}$ = {p_val:.2f}")

        if show_texts and len(texts) > 0:
            text_obj = self._ax.text(
                text_xpos,
                text_ypos,
                "\n".join(texts),
                transform=self._ax.transAxes,
                ha="left",
                va="top",
                color=_color,
            )
            add_shade_to_text(text_obj, color="white")

        self._legend_handles.append(
            Patch(
                facecolor=_color.set_alpha(alpha if alpha is not None else 1),
                edgecolor=_color.set_alpha(linealpha if linealpha is not None else 1),
                linewidth=1.5,
            )
        )
        self._legend_labels.append(
            legend_label if legend_label is not None else f"Dataset {len(self._legend_handles)}"
        )

        # Update axes
        self.set_ax(
            xlabel=xlabel,
            ylabel=ylabel,
            xunits=xunits,
            yunits=yunits,
            xvalue_range=xvalue_range,
            yvalue_range=yvalue_range,
        )

        return self

    def _add_median(
        self: Self,
        value: float | None = None,
        counts: ArrayLike | None = None,
        edges: ArrayLike | None = None,
        show_vlines: bool = True,
        **kwargs,
    ) -> float:
        if value is None:
            if counts is None or edges is None:
                return np.nan
            value = get_hist_median(counts, edges)

        if show_vlines:
            self._ax.axvline(value, **kwargs)
        return value

    def _add_mean(
        self: Self,
        value: float | None = None,
        counts: ArrayLike | None = None,
        centers: ArrayLike | None = None,
        show_vlines: bool = True,
        **kwargs,
    ) -> float:
        if value is None:
            if counts is None or centers is None:
                return np.nan
            value = get_hist_mean(counts, centers)

        if show_vlines:
            self._ax.axvline(value, **kwargs)
        return value

    def _add_percentile(
        self: Self,
        value: float | None = None,
        counts: ArrayLike | None = None,
        edges: ArrayLike | None = None,
        percentile: float | None = None,
        show_vlines: bool = True,
        **kwargs,
    ) -> float:
        if value is None:
            if counts is None or edges is None or percentile is None:
                return np.nan
            value = get_hist_percentile(counts, edges, percentile)

        if show_vlines:
            self._ax.axvline(value, **kwargs)
        return value
