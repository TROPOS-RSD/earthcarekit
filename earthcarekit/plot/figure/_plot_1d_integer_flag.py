from typing import Any, Literal, Sequence, Type, TypeAlias

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from numpy.typing import NDArray

from ..color.color import Color, ColorLike

ClassIDInt: TypeAlias = int
ClassLabelStr: TypeAlias = str


def plot_1d_integer_flag(
    ax: Axes,
    data: Sequence | NDArray,
    classes: Sequence[ClassIDInt] | dict[ClassIDInt, ClassLabelStr],
    x: Sequence | NDArray | None = None,
    ax2: Axes | None = None,
    color: ColorLike | Sequence[ColorLike | None] | None = None,
    alpha: float | Sequence[float] = 1.0,
    linewidth: float = 10.0,
    show_hline: bool | list[bool] = True,
    hline_color: ColorLike | Sequence[ColorLike | None] | None = "black",
    hline_alpha: float | Sequence[float] = 1.0,
    hline_linestyle: str | Sequence[str] = "solid",
    hline_linewidth: float | Sequence[float] = 1.5,
    tick_color: ColorLike | Sequence[ColorLike | None] | None = "black",
    label_color: ColorLike | Sequence[ColorLike | None] | None = "black",
    yaxis_position: str | Literal["top", "bottom", "both", "default", "none"] = "left",
    ax_label: str | None = None,
) -> None:

    class_labels_dict: dict[ClassIDInt, ClassLabelStr] | None = None
    if not isinstance(classes, dict):
        value_labels_dict = {int(c): str(int(c)) for c in classes}
    else:
        value_labels_dict = {int(k): str(int(k)) for k in classes.keys()}
        class_labels_dict = {int(k): str(v) for k, v in classes.items()}

    def _validate_list(
        var: Any,
        var_name: str,
        non_list_types: tuple[Type] | None = (str,),
        list_types: tuple = (Sequence, np.ndarray),
    ) -> bool:
        is_list = isinstance(var, list_types)
        is_list_exception = (
            False if non_list_types is None else isinstance(var, non_list_types)
        )

        is_list = is_list and not is_list_exception

        if is_list:
            if len(var) != len(classes):
                raise ValueError(
                    f"{var_name} list must have the same length as classes: len({var_name})={len(var)} != {len(classes)=}"
                )

        return is_list

    if _validate_list(color, "color"):
        color = [Color.from_optional(c) for c in color]  # type: ignore
    else:
        color = Color.from_optional(color)  # type: ignore
        color = [color] * len(value_labels_dict)

    if _validate_list(alpha, "alpha"):
        alpha = [a for a in alpha]  # type: ignore
    else:
        alpha = [alpha] * len(value_labels_dict)  # type: ignore

    if _validate_list(show_hline, "show_hline"):
        show_hline = [shl for shl in show_hline]  # type: ignore
    else:
        show_hline = [show_hline] * len(value_labels_dict)  # type: ignore

    if _validate_list(hline_color, "color_hline"):
        hline_color = [Color.from_optional(c) for c in hline_color]  # type: ignore
    else:
        hline_color = Color.from_optional(hline_color)  # type: ignore
        hline_color = [hline_color] * len(value_labels_dict)

    if _validate_list(hline_alpha, "hline_alpha"):
        hline_alpha = [a for a in hline_alpha]  # type: ignore
    else:
        hline_alpha = [hline_alpha] * len(value_labels_dict)  # type: ignore

    if _validate_list(hline_linestyle, "hline_linestyle"):
        hline_linestyle = [ls for ls in hline_linestyle]
    else:
        hline_linestyle = [hline_linestyle] * len(value_labels_dict)  # type: ignore

    if _validate_list(hline_linewidth, "hline_linewidth"):
        hline_linewidth = [lw for lw in hline_linewidth]  # type: ignore
    else:
        hline_linewidth = [hline_linewidth] * len(value_labels_dict)  # type: ignore

    if _validate_list(tick_color, "ticks_color"):
        tick_color = [Color.from_optional(c) for c in tick_color]  # type: ignore
    else:
        tick_color = Color.from_optional(tick_color)  # type: ignore
        tick_color = [tick_color] * len(value_labels_dict)

    if _validate_list(label_color, "label_color"):
        label_color = [Color.from_optional(c) for c in label_color]  # type: ignore
    else:
        label_color = Color.from_optional(label_color)  # type: ignore
        label_color = [label_color] * len(value_labels_dict)

    color_dict: dict[int, Color | None] = {
        k: c for k, c in zip(list(value_labels_dict.keys()), color)
    }
    alpha_dict: dict[int, float] = {
        k: c for k, c in zip(list(value_labels_dict.keys()), alpha)
    }
    show_hline_dict: dict[int, bool] = {
        k: c for k, c in zip(list(value_labels_dict.keys()), show_hline)
    }
    hline_color_dict: dict[int, Color | None] = {
        k: c for k, c in zip(list(value_labels_dict.keys()), hline_color)
    }
    hline_alpha_dict: dict[int, float] = {
        k: c for k, c in zip(list(value_labels_dict.keys()), hline_alpha)
    }
    tick_color_dict: dict[int, Color | None] = {
        k: c for k, c in zip(list(value_labels_dict.keys()), tick_color)
    }
    label_color_dict: dict[int, Color | None] = {
        k: c for k, c in zip(list(value_labels_dict.keys()), label_color)
    }

    class_series = np.asarray(data)
    class_series = np.round(class_series)
    unique_classes = list(value_labels_dict.keys())
    unique_classes = sorted(unique_classes)
    class_categorical = pd.Categorical(
        class_series, categories=unique_classes, ordered=True
    )
    value_labels: list[str] = [value_labels_dict[c] for c in unique_classes]
    class_labels: list[str] | None = (
        []
        if class_labels_dict is None
        else [class_labels_dict[c] for c in unique_classes]
    )

    if x is None:
        x = np.arange(class_series.shape[0])
    else:
        x = np.asarray(x)

    _final_colors = {}
    _final_hline_colors = {}

    for i, class_id in enumerate(unique_classes):
        class_name = (
            value_labels_dict[class_id]
            if class_id in value_labels_dict
            else str(class_id)
        )
        _color = color_dict[class_id]
        _alpha = alpha_dict[class_id]
        _show_hline = show_hline_dict[class_id]
        _hline_color = hline_color_dict[class_id]
        _hline_alpha = hline_alpha_dict[class_id]
        _hline_linestyle = hline_linestyle[class_id]
        _hline_linewidth = hline_linewidth[class_id]
        mask = class_categorical != class_id
        y = np.array(class_categorical.codes).astype(float).copy()
        y[mask] = np.nan
        if _show_hline:
            hl = ax.axhline(
                y=i,
                color=_hline_color,
                alpha=_hline_alpha,
                zorder=1,
                linestyle=_hline_linestyle,
                linewidth=_hline_linewidth,
            )
            _final_hline_colors[class_id] = hl.get_color()
        (p,) = ax.plot(
            x,
            y,
            linewidth=linewidth,
            markersize=linewidth * 0.9,
            marker="",
            color=_color,
            alpha=_alpha,
            solid_capstyle="butt",
            zorder=1.1,
            label=class_name,
        )
        _final_colors[class_id] = p.get_color()

    ax.set_yticks(np.arange(len(unique_classes)), value_labels)
    vpad = 0.5
    ax.set_ylim(-vpad, len(unique_classes) + (vpad - 1.0))
    print(class_labels)
    if isinstance(class_labels, list) and len(class_labels) > 0:
        if not isinstance(ax2, Axes):
            ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())

        ax.yaxis.set_ticks_position(yaxis_position)  # type: ignore
        yaxis_position2 = "right" if yaxis_position == "left" else "left"

        ax2.yaxis.set_ticks_position(yaxis_position2)  # type: ignore
        ax2.set_yticks(np.arange(len(unique_classes)), class_labels)
        for i, class_id in enumerate(unique_classes):
            _color = label_color_dict[class_id]
            _side_idx_offset = 0 if yaxis_position2 == "left" else 1
            ax2.get_yticklines()[i * 2 + _side_idx_offset].set_markeredgecolor(
                "#ffffff00"
            )
            _ticks_color = tick_color_dict[class_id]
            ax2.get_yticklabels()[i].set_color(_color)  # type: ignore

    for i, class_id in enumerate(unique_classes):
        if show_hline_dict[class_id]:
            line_color = _final_hline_colors[class_id]
            _hline_linewidth = hline_linewidth[class_id]
            _side_idx_offset = 0 if yaxis_position == "left" else 1
            ax.get_yticklines()[i * 2 + _side_idx_offset].set_markeredgecolor(
                line_color
            )
            ax.get_yticklines()[i * 2 + _side_idx_offset].set_markeredgewidth(
                _hline_linewidth
            )

        _ticks_color = tick_color_dict[class_id]
        ax.get_yticklabels()[i].set_color(_ticks_color)  # type: ignore

    if isinstance(ax_label, str):
        ax.set_ylabel(ax_label)
