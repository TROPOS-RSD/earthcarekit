from typing import Final, Literal

from ..color import Color
from .cmap import Cmap

STYLES: Final[list[Literal["qualitative", "intense", "dark", "light", "pastel"]]] = [
    "qualitative",
    "intense",
    "dark",
    "light",
    "pastel",
]


def get_cmap(
    style: Literal["qualitative", "intense", "dark", "light", "pastel"] = "intense",
    name: str | None = None,
) -> Cmap:
    if style not in STYLES:
        raise ValueError(f"""invalid style "{style}", valid styles are: {STYLES}""")

    colors = [
        "#E99590",
        "#D4A263",
        "#AEB050",
        "#79BB6B",
        "#22C198",
        "#00C0C3",
        "#59B5E2",
        "#A6A4EC",
        "#D793DF",
        "#EC8DBD",
    ]
    if style == "intense":
        colors = [
            "#F8766D",
            "#D89000",
            "#A3A500",
            "#39B600",
            "#00BF7D",
            "#00BFC4",
            "#00B0F6",
            "#9590FF",
            "#E76BF3",
            "#FF62BC",
        ]
    elif style == "dark":
        colors = [
            "#DC726B",
            "#C18500",
            "#959700",
            "#46A423",
            "#00AC77",
            "#00ABB0",
            "#009ED7",
            "#8A86E6",
            "#CA6AD4",
            "#E164A9",
        ]
    elif style == "light":
        colors = [
            "#FDB4B0",
            "#EABE8E",
            "#C9CA82",
            "#9ED494",
            "#71D9B7",
            "#63D7DA",
            "#8BCEF4",
            "#C3C1FD",
            "#ECB4F1",
            "#FFAED6",
        ]
    elif style == "pastel":
        colors = [
            "#FDC7C4",
            "#EECEAE",
            "#D6D7A7",
            "#B7DEB1",
            "#9EE1C9",
            "#9AE0E3",
            "#B0DAF6",
            "#D1D0FC",
            "#EEC7F3",
            "#FDC4DE",
        ]
    tmp_cmap = Cmap(colors, gradient=True)
    if not isinstance(name, str):
        name = f"HCL_{style}"
    n: int = 10
    final_cmap = Cmap(
        [Color(tmp_cmap(i / (n * 0.9)), is_normalized=True) for i in range(n)],
        name=name,
        gradient=True,
        circular=True,
    )
    return final_cmap


def get_cmaps() -> list[Cmap]:
    return [get_cmap("intense", name="HCL")] + [get_cmap(s) for s in STYLES]


def sample_hcl_colors(
    n: int,
    style: Literal["qualitative", "intense", "dark", "light", "pastel"] = "intense",
) -> list[Color]:
    cmap = get_cmap(style=style)
    return [Color(cmap(i / (n * 0.9)), is_normalized=True) for i in range(n)]


def sample_hcl_cmap(
    n: int,
    style: Literal["qualitative", "intense", "dark", "light", "pastel"] = "intense",
) -> Cmap:
    cmap = get_cmap(style=style)
    name = f"HCL_{style}_descrete"
    return Cmap(
        [Color(cmap(i / (n * 0.9)), is_normalized=True) for i in range(n)],
        name=name,
        gradient=False,
        circular=True,
    )
