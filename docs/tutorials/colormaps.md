# Colormaps

Figure objects such as [`CurtainFigure`][earthcarekit.CurtainFigure] accept `matplotlib.colors.Colormap` objects or a name string, which then retrieves the appropriate colormap from [`matplotlib`](https://matplotlib.org/stable/users/explain/colors/colormaps.html#), [`plotly`](https://plotly.com/python/builtin-colorscales/), [`cmcrameri`](https://github.com/callumrollo/cmcrameri), and from a list of pre-defined colormaps for `earthcarekit`:

<iframe width="100%" height="900" frameBorder="0" background-color="transparent" allowtransparency="true" src="../../images/colormaps.html"></iframe> 

## Create a colormap

### Get by name

```python
def plot_cmap(c):
    import matplotlib.pyplot as plt
    _, ax = plt.subplots(figsize=(6, 0.5))
    plt.colorbar(plt.cm.ScalarMappable(cmap=c), cax=ax, orientation="horizontal", label=c.name)
    plt.show()

cmap = eck.get_cmap("RdBu")
plot_cmap(cmap)
```

![cmap_RdBu.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/colormaps/cmap_RdBu.png){ .skip-lightbox }

### Generate from color list

```python
colors = ["green", "#FFFFE0", (0.5, 0.06, 0.5, 1.0)]
cmap_custom = eck.Cmap(colors, name="custom")
plot_cmap(cmap_custom)
```

![cmap_custom.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/colormaps/cmap_custom.png){ .skip-lightbox }

```python
cmap_custom_gradient = eck.Cmap(colors, gradient=True, , name="custom_gradient")
cmap_custom_gradient.name = "custom_gradient"
plot_cmap(cmap_custom_gradient)
```

![cmap_custom_gradient.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/colormaps/cmap_custom_gradient.png){ .skip-lightbox }

## Convert a continous colormap to discrete

```python
cmap_discrete = eck.get_cmap("RdBu").to_discrete(7)
cmap_discrete.name = "RdBu_discrete"
plot_cmap(cmap_discrete)
```

![cmap_RdBu_discrete.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/colormaps/cmap_RdBu_discrete.png){ .skip-lightbox }

## Shift the midpoint of a colormap

See [`shift_cmap`][earthcarekit.shift_cmap].

```python
cmap_shifted = eck.shift_cmap("RdBu", midpoint=0.2, name="RdBu_shifted")
plot_cmap(cmap_shifted)
```

![cmap_RdBu_shifted.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/colormaps/cmap_RdBu_shifted.png){ .skip-lightbox }

## Combine colormaps

See [`combine_cmaps`][earthcarekit.combine_cmaps].

```python
cmap_combined = eck.combine_cmaps("jet_r", "Greys", name="combined")
cmap_combined
```

![cmap_RdBu_shifted.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/colormaps/cmap_combined.png){ .skip-lightbox }

```python
cmap_combined2 = eck.shift_cmap(cmap_combined, midpoint=0.2, name="combined_and_shifted")
cmap_combined2
```

![cmap_RdBu_shifted.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/colormaps/cmap_combined2.png){ .skip-lightbox }

## Categorical colormaps

For classification data (e.g., ATLID target classification) categorical colormaps can be created using the [`Cmap.to_categorical`][earthcarekit.Cmap.to_categorical] method:

```python
cmap = eck.get_cmap("viridis")
values_to_labels = {
    0: "class 1",
    1: "class 2",
    100: "class 3",
    -1: "missing data",
}
cmap_categorical = cmap.to_categorical(values_to_labels)

# Example plot
eck.CurtainFigure().plot(
    values=[[-1,  0,  1, 100],
            [ 1, -1,  1,   0],
            [ 0,  1, -1,   1]],
    height=[5e3,15e3, 25e3, 35e3],
    time=["20250101", "20250201", "20250301"],
    cmap=cmap_categorical,
)
```

![cmap_RdBu.png](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/colormaps/categorical_cmap.png){ .skip-lightbox }
