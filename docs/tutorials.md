# Tutorial: First Steps

> ⚠️ **Page status: Work in progess**

Import the `earthcarekit` package in your Python code:

```python
import earthcarekit as eck
```

## How to search your local EarthCARE products?

```python
# Search for a file type
df = eck.search_product(file_type="ATL_NOM_1B")

# You can use file type shorthands (not case sensitive) and select specific baselines:
df = eck.search_product(file_type="anom", baseline="ae")

# You may also search for multiple products at once:
df = eck.search_product(file_type=["anom", "cnom", "mrgr"])

# Refine your search by given more filter arguments.
# Note: Most arguments accept single values or lists of values.

# Search for orbit numbers and/or frame IDs
df = eck.search_product(file_type="ATL_NOM_1B", orbit_and_frame="5976B")
df = eck.search_product(file_type="ATL_NOM_1B", orbit_number=5976, frame_id="B")

# Search by time
df = eck.search_product(file_type="ATL_NOM_1B", timestamp="2025-06-17 00:30")
df = eck.search_product(file_type="ATL_NOM_1B", start_time="2025-06-17 00:30", end_time="2025-06-17 00:35")

# Search by creating a regular expression pattern
df = eck.search_product(filename=".*ATL_NOM_1B.*5976B.h5")
```

## How to open an EarthCARE dataset?

```python
# Search for a files
df = eck.search_product(file_type="ATL_NOM_1B")

# Select a file
fp = df.filepath[-1] # last file path in the dataframe

# Open the dataset
with eck.read_product(fp) as ds:
    display(ds) # in case you are using a Jupyter notebook
```

## How to rebin X-MET to a vertical grid?

```python
# Get X-MET file
df = eck.search_product(file_type="xmet", orbit_and_frame="03947E")
fp_xmet = df.filepath[-1]

# Get product with time/vertical grid, e.g. A-NOM
df = eck.search_product(file_type="anom", orbit_and_frame="03947E")
fp_anom = df.filepath[-1]

# Open both products
with eck.read_product(fp_anom) as ds_anom, eck.read_product(fp_xmet) as ds_xmet:
    # Rebin X-MET to A-NOM grid
    ds_xmet_on_anom_grid = eck.rebin_xmet_to_vertical_track(ds_xmet=ds_xmet, ds_vert=ds_anom)

display(ds_xmet_on_anom_grid) # in case you are using a Jupyter notebook
```

## How to plot EarthCARE data?

```python
# Get a quicklook
with eck.read_product(fp) as ds:
    fig, _ = eck.ecquicklook(ds)
    eck.save_plot(fig, "quicklook.png")

# Create a map plot
with eck.read_product(fp) as ds:
    mf = eck.MapFigure()
    mf = mf.ecplot(ds)
    eck.save_plot(fig, "map.png")

# Create a curtain plot
with eck.read_product(fp) as ds:
    cf = eck.CurtainFigure()
    cf = cf.ecplot(ds, var="mie_attenuated_backscatter")
    eck.save_plot(fig, "curtain.png")
```
