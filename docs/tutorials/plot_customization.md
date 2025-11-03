# Plot customizations

## Adding or overlaying supplementary data in curtain plots

In this example, the basic curtain plot is created using an A-EBD dataset:

```python
df = eck.search_product(file_type="aebd", orbit_and_frame="01508B")
df = df.filter_latest()

fp = df.filepath[-1]  # ECA_EXBA_ATL_EBD_2A_20240902T210023Z_20250721T110708Z_01508B.h5

df_anom = eck.search_product(file_type="anom", orbit_and_frame="01508B")
df_anom = df_anom.filter_latest()

fp_anom = df_anom.filepath[-1]

with eck.read_product(fp) as ds:
    cf = eck.CurtainFigure(figsize=(9.5, 2.5))
    cf.ecplot(ds, var="particle_extinction_coefficient_355nm", height_range=(0, 15e3))
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/adding_data_to_curtain_basic.png)

### Height data (1D)

One-dimensional height data can be overlayed by using the methods [`CurtainFigure.ecplot_height`][earthcarekit.CurtainFigure.ecplot_height] when working with datasets or [`CurtainFigure.plot_height`][earthcarekit.CurtainFigure.plot_height] when working with arrays.

To overlay common height data like the tropopause height or surface elevation, the methods [`CurtainFigure.ecplot_elevation`][earthcarekit.CurtainFigure.ecplot_elevation] and [`CurtainFigure.ecplot_tropopause`][earthcarekit.CurtainFigure.ecplot_tropopause] can be used with datasets that contain the required information (note: here both surface and tropopause information is available in A-EBD):

```python
with eck.read_product(fp) as ds:
    cf = eck.CurtainFigure(figsize=(9.5, 2.5))
    cf.ecplot(ds, var="particle_extinction_coefficient_355nm", height_range=(0, 15e3))
    cf.ecplot_elevation(ds)
    cf.ecplot_tropopause(ds)
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/adding_data_to_curtain_elevation_tropopause.png)

### Profile data (2D)

To overlay two-dimensional profile data with contour lines the methods [`CurtainFigure.ecplot_contour`][earthcarekit.CurtainFigure.ecplot_contour] (for datasets) or [`CurtainFigure.plot_contour`][earthcarekit.CurtainFigure.plot_contour] (for arrays).

To overlay common profile data like the layer temperature or pressure, the methods [`CurtainFigure.ecplot_temperature`][earthcarekit.CurtainFigure.ecplot_temperature] and [`CurtainFigure.ecplot_pressure`][earthcarekit.CurtainFigure.ecplot_pressure] can be used with datasets that contain the required information (note: since A-EBD does not contain the required data, the related A-NOM product is used for this):

```python
df_anom = eck.search_product(file_type="anom", orbit_and_frame="01508B")
df_anom = df_anom.filter_latest()

fp_anom = df_anom.filepath[-1]  # ECA_EXBA_ATL_NOM_1B_20240902T210023Z_20250630T151754Z_01508B.h5

with (
    eck.read_product(fp) as ds,
    eck.read_product(fp_anom) as ds_anom,
):
    cf = eck.CurtainFigure(figsize=(9.5, 2.5))
    cf.ecplot(ds, var="particle_extinction_coefficient_355nm", height_range=(0, 15e3))
    cf.ecplot_elevation(ds)
    cf.ecplot_tropopause(ds)
    cf.ecplot_temperature(ds_anom)
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/adding_data_to_curtain_temperature.png)

Also, instead of contours area hatchings can be created using [`CurtainFigure.ecplot_hatch`][earthcarekit.CurtainFigure.ecplot_hatch] (for datasets) or [`CurtainFigure.plot_hatch`][earthcarekit.CurtainFigure.plot_hatch] (for arrays).

In case of A-EBD it can be usefull to visualize the attenuated Lidar signal. This can be done by using the [`CurtainFigure.ecplot_hatch_attenuated`][earthcarekit.CurtainFigure.ecplot_hatch_attenuated] method (note: this requires the "simple_classification" variable stored in A-EBD and other L2 ATLID products)

```python
with eck.read_product(fp) as ds:
    cf = eck.CurtainFigure(figsize=(9.5, 2.5))
    cf.ecplot(ds, var="particle_extinction_coefficient_355nm", height_range=(0, 15e3))
    cf.ecplot_elevation(ds)
    cf.ecplot_tropopause(ds)
    cf.ecplot_hatch_attenuated(ds)
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/adding_data_to_curtain_attenuated.png)

## Along-track axis styles

```python
df = eck.search_product(file_type="aebd", orbit_and_frame="01508B")
df = df.filter_latest()

fp = df.filepath[-1]
# fp="path_to/ECA_EXBA_ATL_EBD_2A_20240902T210023Z_20250721T110708Z_01508B.h5"

with eck.read_product(fp) as ds:
    cf = eck.CurtainFigure(
        figsize=(9.5, 1.5),
        ax_style_top="geo",  # default setting
        ax_style_bottom="time",  # default setting
    )
    cf.ecplot(ds, var="mie_attenuated_backscatter", height_range=(0, 15e3))
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/ax_style_default.png)

You can change the displayed axes by setting the `ax_style_top` and `ax_style_bottom` arguments. Here are some examples:

```python
...
ax_style_top="lat",
ax_style_bottom="lon",
...
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/ax_style_lat_lon.png)

```python
...
ax_style_top="utc",
ax_style_bottom="lst",
...
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/ax_style_utc_lst.png)

```python
...
ax_style_top="distance",
ax_style_bottom="samples",
...
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/ax_style_distance_samples.png)

Adding `"_nolabels"` to the ax_style string removes the tick labels and `"_notitle"` removes the title (note: both can be used in the same string).

```python
...
ax_style_top="distance_nolabels",
ax_style_bottom="distance_notitle",
...
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/ax_style_nolabel_notitle.png)

You can also show no labels or change the maximum number of mayor ticks. 

```python
...
ax_style_top="none",
ax_style_bottom="geo",
num_ticks=5,
...
```

![`simple_map.png`](https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/tutorials/plot_customizations/ax_style_none_num_ticks.png)