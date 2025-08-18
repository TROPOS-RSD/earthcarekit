# Introduction

This page gives a brief example introducing the earthcarekit module.
First, make sure to complete the [setup](setup.md).

Afterwards, begin by importing the module:

```python
import earthcarekit as eck
```

## Download EarthCARE Data

To download your first EarthCARE product run this:

```python
eck.ecdownload(file_type="ATL_EBD_2A", orbit_and_frame="5976B")
```

<details>
<summary>See output ...</summary>

```terminal
#======================================================================#
#                       EarthCARE Download Tool                        #
#                         earthcarekit 0.2.2                           #
#======================================================================#
# Settings
# - is_download=True
# - is_overwrite=False
# - is_unzip=True
# - is_delete=True
# - is_create_subdirs=True
# - is_log=False
# - is_debug=False
# - is_export_results=False
# - idx_selected_input=None
# - config_filepath=<~/.config/earthcarekit/default_config.toml>
# - data_dirpath=<~/path_to_data>

+----------------------------------------------------------------------+
| STEP 1/2 - Search products                       2025-08-15 14:06:01 |
+----------------------------------------------------------------------+

*[1/1] Search request: ATL_EBD_2A, frame=B, orbits=[5976]
 [1/1] Files found in collection 'EarthCAREL2Validated': 1

List of files found (total number 1):
 [1]  ECA_EXAG_ATL_EBD_2A_20250617T002721Z_20250617T024837Z_05976B
Note: To export this list use the option --export_results
Note: To select only one specific file use the option -i/--select_file_at_index

+----------------------------------------------------------------------+
| STEP 2/2 - Download products                     2025-08-15 14:06:01 |
+----------------------------------------------------------------------+

*[1/1] Starting: ECA_EXAG_ATL_EBD_2A_20250617T002721Z_20250617T024837Z_05976B
 [1/1] Authenticate at dissemination service: ec-pdgs-dissemination2.eo.esa.int
 [1/1] Download completed (00:00:29 - 2.58 MB/s - 76.08/76.08 MB)                   
 [1/1] File extracted and ZIP-file deleted. (see <~/path_to_data/level2a/ATL_EBD_2A/2025/06/17/ECA_EXAG_ATL_EBD_2A_20250617T002721Z_20250617T024837Z_05976B>)

+----------------------------------------------------------------------+
| EXECUTION SUMMARY                                2025-08-15 14:06:09 |
+----------------------------------------------------------------------+
| Time taken          00:00:09                                         |
| API search requests 1                                                |
| Remote files found  1                                                |
| Files downloaded    1 (17.07 MB at ~3.49 MB/s)                       |
| Files unzipped      1                                                |
| Errors occured      0                                                |
+----------------------------------------------------------------------+
```

</details>

This will download the latest ATLID extinction
backscatter, and depolarization product (A-EBD), specifically from the EarthCARE frame B of orbit 5976.
You can monitor the download progress from the output log messages.

## Search Local Files

Now search the file in your local data directory:

```python
dataframe = eck.search_product(file_type="ATL_EBD_2A", orbit_and_frame="5976B")

# View the search results
print(dataframe)

# Or, if in a Jupyter notebook, show in tabular format by using
display(dataframe)
```

<details markdown="block">
<summary>See output ...</summary>

| | mission_id | agency | latency | baseline | file_type | start_sensing_time | start_processing_time | orbit_number | frame_id | orbit_and_frame | name | filepath | hdr_filepath |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | ECA | E | X | AG | ATL_EBD_2A | 2025-06-17 00:27:21 | 2025-06-17 02:48:37 | 5976 | B | 05976B | ECA_EXAG_ATL_EBD_2A_... | ~/path_to_data/... | ~/path_to_data/... |

</details>

## Open/Read a Dataset

Now you can get the file path from the resulting `ProductDataFrame`:

```python
filepath = dataframe.filepath[0]
print(filepath)
```

<details>
<summary>See output ...</summary>

```terminal
~/path_to_data/level2a/ATL_EBD_2A/2025/06/17/ECA_EXAG_ATL_TC__2A_20250617T002721Z_20250617T024837Z_05976B/ECA_EXAG_ATL_TC__2A_20250617T002721Z_20250617T024837Z_05976B.h5
```

</details>

To open a dataset use the `eck.read_product` which is based on [`xarray.open_dataset`](https://docs.xarray.dev/en/stable/generated/xarray.open_dataset.html). To prevent open file handles, memory leaks, and locked dataset files it is best practice to open files using a `with` statement:

```python
with eck.read_product(filepath) as dataset:
    print(dataset)

    # Or, if in a notebook
    display(dataset)
```

<details>
<summary>See output ...</summary>

```terminal
<xarray.Dataset> Size: 234MB
Dimensions:                                                         (
                                                                     along_track: 4946,
                                                                     vertical: 242,
                                                                     layer: 25,
                                                                     n_state: 351)
Dimensions without coordinates: along_track, vertical, layer, n_state
Data variables: (12/74)
    filename                                                        <U60 240B ...
    file_type                                                       <U10 40B ...
    frame_id                                                        <U1 4B 'B'
    orbit_number                                                    uint32 4B ...
    orbit_and_frame                                                 <U6 24B '...
    baseline                                                        <U2 8B 'AG'
    ...                                                              ...
    lidar_ratio_355nm_low_resolution_error                          (along_track, vertical) float32 5MB ...
    retrieved_state_vector                                          (along_track, n_state) float32 7MB ...
    state_vector_prior                                              (along_track, n_state) float32 7MB ...
    state_vector_prior_error                                        (along_track, n_state) float32 7MB ...
    final_chi_square                                                (along_track) float32 20kB ...
    initial_chi_square                                              (along_track) float32 20kB ...
```

</details>

## Create your first plots

`earthcarekit` provides a set of figure objects:

- [`MapFigure`][earthcarekit.MapFigure] - for plotting data on a map (e.g., the satellite's track or geolocated swath data from MSI)
- [`CurtainFigure`][earthcarekit.MapFigure] - for plotting time series of vertical profile data (i.e., 2D time/height plots of ATLID and CPR "curtain" data)
- [`ProfileFigure`][earthcarekit.ProfileFigure] - for plotting single or mean vertical profiles as signal/height line plots
- [`SwathFigure`][earthcarekit.SwathFigure] - for plotting time series of across-track swath data (i.e., 2D time/swath plot)
- [`LineFigure`][earthcarekit.LineFigure] - for plotting time series of 1D along-track data (i.e., tropopause height, latitude, data quality flags, ...)

Each of these implements (among others) two methods:

1. `ecplot` - for handeling EarthCARE datasets
2. `plot` - for manual data input (profiles, values, time, height, etc.)

### Plot a track on a map

To get a general sense of the satellites track, you may start by plotting a simple map:

```python
with eck.read_product(filepath) as dataset:
    map_figure = eck.MapFigure().ecplot(dataset)

    # Save the image
    eck.save_plot(map_figure, filepath="simple_map.png")
```

![`simple_map.png`](./images/simple_map.png)

### Create simple curtain plots

To make a time/height or curtain plot of the vertically resolved atmospheric profile data stored in the current A-EBD dataset, you can use a [`CurtainFigure`][earthcarekit.CurtainFigure] object:

```python
with eck.read_product(filepath) as dataset:
    curtain_figure = eck.CurtainFigure()
    curtain_figure = curtain_figure.ecplot(
        dataset,
        var="particle_backscatter_coefficient_355nm_low_resolution",
        height_range=(0, 20e3),  # Show only data within 20km height
    )

    # Save the image
    eck.save_plot(curtain_figure, filepath="simple_curtain.png")
```

![`simple_curtain.png`](./images/simple_curtain.png) 

You can enhance the plot with overlays of elevation and tropopause height from datasets that store this information (in this case, A-EBD already contains both):

```python
with eck.read_product(filepath) as dataset:
    curtain_figure = eck.CurtainFigure().ecplot(
        dataset,
        var="particle_backscatter_coefficient_355nm_low_resolution",
        height_range=(0, 20e3),  # Show only data within 20km height

    )
    curtain_figure.ecplot_elevation(dataset)  # NEW
    curtain_figure.ecplot_tropopause(dataset)  # NEW

    # Save the image
    eck.save_plot(curtain_figure, filepath="curtain_with_elevation_and_tropopause.png")
```

![`simple_curtain_with_elevation_and_tropopausecurtain.png`](./images/curtain_with_elevation_and_tropopause.png)

### Select along-track data and plot profiles

#### Select by time

```python
time_range = ("2025-06-17T00:29", "2025-06-17T00:30:30")

with eck.read_product(filepath) as dataset:
    dataset_filtered = eck.filter_time(ds=dataset, time_range=time_range)

    # Plot a curtain of the whole EarthCARE frame with the time_range marked
    curtain_figure = eck.CurtainFigure().ecplot(
        ds=dataset,
        var="particle_backscatter_coefficient_355nm_low_resolution",
        height_range=(0, 15e3),  # Show only data within 15km height
        selection_time_range=time_range,
    )

    # Plot the mean profile of the filtered data (with STD error ribbon)
    profile_figure = eck.ProfileFigure().ecplot(
        ds=dataset_filtered,  # Use the filtered dataset here
        var="particle_backscatter_coefficient_355nm_low_resolution",
        height_range=(0, 15e3),  # Show only data within 15km height
        # value_range=(0, 1e-8),  # You may adjust the x-axis plotting range
    )

    # Save the images
    eck.save_plot(curtain_figure, filepath="curtain_selection_time_range.png")
    eck.save_plot(profile_figure, filepath="profile_selection_time_range.png")
```

![`curtain_selection_time_range.png`](./images/curtain_selection_time_range.png)
![`profile_selection_time_range.png`](./images/profile_selection_time_range.png)

#### Select by radius

```python
site = eck.GroundSite(
    name="TROPOS",
    latitude=51.352757,
    longitude=12.43392,
    altitude=125,
)

with eck.read_product(filepath) as dataset:
    dataset_filtered = eck.filter_radius(
        ds=dataset,
        radius_km=100,
        site=site,
        closest=True, # Since we are using a A-EBD dataset, we should only select the closest profile
    )

    # Plot a curtain of the whole EarthCARE frame with the time_range marked
    curtain_figure = eck.CurtainFigure().ecplot(
        ds=dataset,
        var="particle_backscatter_coefficient_355nm_low_resolution",
        height_range=(0, 15e3),  # Show only data within 15km height
        site=site,
    )

    display(dataset_filtered)

    # Plot the mean profile of the filtered data (with STD error ribbon)
    profile_figure = eck.ProfileFigure().ecplot(
        ds=dataset_filtered,  # Use the filtered dataset here
        var="particle_backscatter_coefficient_355nm_low_resolution",
        height_range=(0, 15e3),  # Show only data within 15km height
        value_range=(0, 3e-6),  # You may adjust the x-axis plotting range
    )

    # Save the images
    eck.save_plot(curtain_figure, filepath="curtain_selection_radius_range.png")
    eck.save_plot(profile_figure, filepath="profile_selection_radius_range.png")
```

![`curtain_selection_radius_range.png`](./images/curtain_selection_radius_range.png)
![`profile_selection_radius_range.png`](./images/profile_selection_radius_range.png)