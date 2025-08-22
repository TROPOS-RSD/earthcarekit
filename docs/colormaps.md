# Colormaps

Figure objects such as [`CurtainFigure`][earthcarekit.CurtainFigure] accept `matplotlib.colors.Colormap` objects or a name string, which then retrieves the appropriate colormap from [`matplotlib`](https://matplotlib.org/stable/users/explain/colors/colormaps.html#), [`plotly`](https://plotly.com/python/builtin-colorscales/), [`cmcrameri`](https://github.com/callumrollo/cmcrameri), and from a list of pre-defined colormaps for `earthcarekit`:

![colormaps.png](./images/colormaps.png){ .skip-lightbox }

!!! Advanced
    In case you want to get an `matplotlib.Colormap` object and call by name, use the [`get_cmap`][earthcarekit.get_cmap] function.

    All pre-defined colour tables for `earthcarekit` are also listed in [`earthcarekit.cmaps`][earthcarekit.cmaps].