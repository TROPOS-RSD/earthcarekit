# Download CLI tool

Search, select, and download EarthCARE data from the command line.

!!! caution
    **Page status: Work in progess**

!!! info
    This tool is adapted from code previously hosted in the separate [oads-download](https://github.com/koenigleon/oads-download/tree/main) repository.

    **Please be aware that the sub-directory names have changed from the original oads-download project.**

## Setup

Please ensure that you've completed the [Setup](install.md#setup) and created an ESA account.
Depending on the data dissemination platform selected in the configuration file, the corresponding login credentials (for [OADS](https://ec-pdgs-dissemination2.eo.esa.int/oads/access/collection)) or non-expired data access token (for the [MAAP](https://portal.maap.eo.esa.int/earthcare/)) must be provided.

## Usage

For detailed explanations on how to use the CLI tool and available search criteria run the help command:
```shell
ecdownload -h
```

By default, products downloaded with the script are unpacked and stored in the local data folder specified in the `data_directory` field of your `~/.config/earthcarekit/default_config.toml` file. Also, products are organized in a subfolder structure depending on the product level and the acquisition date:
```shell
data_directory/
├── level1b/                 # processing level
│   ├── ATL_NOM_1B/          # file type
│   │   ├── 2024/            # year
│   │   │   ├── 11/          # month
│   │   │   │   ├── 01/      # day
│   │   │   │   │   └── BA/  # baseline
│   │   │   │   ├── 02/
│   │   │   │   └── ...
├── level1c/
├── level2a/
├── level2b/
├── auxiliary_files/
└── orbit_files/
```
To prevent this, the `--no_unzip` and `--no_subdirs` options can be used.

### Logging

On execution, log files are created in a folder called `logs` in your current working directory.
These can be used to trace the execution of the script in more detail than from the console.
Logging can be disabled by using the `--no_log` option.

### Examples

Here are selected examples that illustrate some possible use cases.

#### *Example 1: How can I download specific frames?*
To download the ATL_NOM_1B product for the orbit and frame 02163E you can run the command:
```shell
ecdownload ATL_NOM_1B -oaf 2163E
```
If you want to download a product from a specific processor baseline, you can specify its two-letter identifier after a colon or use the `--product_version`/`-pv` option:
```shell
ecdownload ATL_NOM_1B:AC -oaf 2163E
```
You can also download different product types with the same command and also use alternative shorthand aliases (see this [table](#table-of-product-name-aliases) below). For example, the following command downloads the products ATL_NOM_1B (baseline AC), CPR_NOM_1B and MSI_RGR_1C for frame 02163E.
```shell
ecdownload ANOM:AC MRGR CNOM -oaf 2163E
```
You can also specify only a timestamp within the frame, e.g. if you do not know the orbit and frame identifier in advance (the `--time`/`-t` option allows flexible timestamp string formats, like `202410142355`, `2024-10-14T23:55`, ...):
```shell
ecdownload ANOM:AC MRGR CNOM -t 2024-10-14T23:55
```
#### *Example 2: How can I select products within the radius of a ground site?*
```shell
ecdownload ATL_EBD_2A --radius 100000 16.878 -24.995 --start_time 2025-01-20T00:00:00 --end_time 2025-01-28T00:00:00
```
With this command the script downloads all ATL_EBD_2A products that are found within a 100 km radius around Mindelo CPV between the 20th and 28th of January 2025.

#### *Example 3: How do I obtain data for an entire day?*
```shell
ecdownload AALD -st 20250101 -et 20250102
```
This command downloads all ATL_ALD_2A products for the day of January 1 2025 (125 files) by using the `--start_time`/`-st` and `--end_time`/`-et` options.

#### *Example 4: How can I first search for product candidates and then select a single product?*
```shell
ecdownload XORBP -t 20250130 --no_download
```
This lists all AUX_ORBPRE files predicting the orbit on January 30 2025 without downloading them.

The output shows a list of found products with indices:

```shell
...
List of files found (total number 11):
 [ 1]  ECA_EXAA_AUX_ORBPRE_20250120T000000Z_20250130T000000Z_0001
 [ 2]  ECA_EXAA_AUX_ORBPRE_20250121T000000Z_20250131T000000Z_0001
 [ 3]  ECA_EXAA_AUX_ORBPRE_20250122T000000Z_20250201T000000Z_0001
 [ 4]  ECA_EXAA_AUX_ORBPRE_20250123T000000Z_20250202T000000Z_0001
 [ 5]  ECA_EXAA_AUX_ORBPRE_20250124T000000Z_20250203T000000Z_0001
 [ 6]  ECA_EXAA_AUX_ORBPRE_20250125T000000Z_20250204T000000Z_0001
 [ 7]  ECA_EXAA_AUX_ORBPRE_20250126T000000Z_20250205T000000Z_0001
 [ 8]  ECA_EXAA_AUX_ORBPRE_20250127T000000Z_20250206T000000Z_0001
 [ 9]  ECA_EXAA_AUX_ORBPRE_20250128T000000Z_20250207T000000Z_0001
 [10]  ECA_EXAA_AUX_ORBPRE_20250129T000000Z_20250208T000000Z_0001
 [11]  ECA_EXAA_AUX_ORBPRE_20250130T000000Z_20250209T000000Z_0001
Note: To export this list use the option --export_results
Note: To select only one specific file use the option -i/--select_file_at_index
...
```

To download a single file from this list you can specify its index. To select the last file set the index to -1:

```shell
$ ecdownload XORBP -t 20250130 -i -1
...
List of files found (total number 11):
 [ 1]  ECA_EXAA_AUX_ORBPRE_20250120T000000Z_20250130T000000Z_0001
 [ 2]  ECA_EXAA_AUX_ORBPRE_20250121T000000Z_20250131T000000Z_0001
 [ 3]  ECA_EXAA_AUX_ORBPRE_20250122T000000Z_20250201T000000Z_0001
 [ 4]  ECA_EXAA_AUX_ORBPRE_20250123T000000Z_20250202T000000Z_0001
 [ 5]  ECA_EXAA_AUX_ORBPRE_20250124T000000Z_20250203T000000Z_0001
 [ 6]  ECA_EXAA_AUX_ORBPRE_20250125T000000Z_20250204T000000Z_0001
 [ 7]  ECA_EXAA_AUX_ORBPRE_20250126T000000Z_20250205T000000Z_0001
 [ 8]  ECA_EXAA_AUX_ORBPRE_20250127T000000Z_20250206T000000Z_0001
 [ 9]  ECA_EXAA_AUX_ORBPRE_20250128T000000Z_20250207T000000Z_0001
 [10]  ECA_EXAA_AUX_ORBPRE_20250129T000000Z_20250208T000000Z_0001
<[11]> ECA_EXAA_AUX_ORBPRE_20250130T000000Z_20250209T000000Z_0001 <-- Select file (user input: -1)
Note: To export this list use the option --export_results
...
```

#### *Further examples: How to download orbit ranges?*
Download all D and B frames from orbit 3000 to 3009 (20 files):

```shell
ecdownload AALD -f D B -so 3000 -eo 3009
```

Download all frames between 01300D and 01302B (15 files):

```shell
ecdownload AALD -soaf 01300D -eoaf 01302B
```

## Tables of product name aliases

### Level 1 products

| Product name | File type  | Shorthand | Notes        |
| ------------ | ---------- | --------- | ------------ |
| A-NOM        | ATL_NOM_1B | ANOM      |              |
| M-NOM        | MSI_NOM_1B | MNOM      |              |
| B-NOM        | BBR_NOM_1B | BNOM      |              |
| C-NOM        | CPR_NOM_1B | CNOM      | JAXA product |
| M-RGR        | MSI_RGR_1C | MRGR      |              |

<details markdown="block">
<summary>Calibration products</summary>

| Product name | File type  | Shorthand | Notes |
| ------------ | ---------- | --------- | ----- |
| A-DCC        | ATL_DCC_1B | ADCC      |       |
| A-CSC        | ATL_CSC_1B | ACSC      |       |
| A-FSC        | ATL_FSC_1B | AFSC      |       |
| M-BBS        | MSI_BBS_1B | MBBS      |       |
| M-SD1        | MSI_SD1_1B | MSD1      |       |
| M-SD2        | MSI_SD2_1B | MSD2      |       |
| B-SNG        | BBR_SNG_1B | BSNG      |       |
| B-SOL        | BBR_SOL_1B | BSOL      |       |
| B-LIN        | BBR_LIN_1B | BLIN      |       |

</details>

### Level 2a products

| Product name | File type  | Shorthand | Notes        |
| ------------ | ---------- | --------- | ------------ |
| A-FM         | ATL_FM__2A | AFM       |              |
| A-AER        | ATL_AER_2A | AAER      |              |
| A-ICE        | ATL_ICE_2A | AICE      |              |
| A-TC         | ATL_TC__2A | ATC       |              |
| A-EBD        | ATL_EBD_2A | AEBD      |              |
| A-CTH        | ATL_CTH_2A | ACTH      |              |
| A-ALD        | ATL_ALD_2A | AALD      |              |
| M-CM         | MSI_CM__2A | MCM       |              |
| M-COP        | MSI_COP_2A | MCOP      |              |
| M-AOT        | MSI_AOT_2A | MAOT      |              |
| C-FMR        | CPR_FMR_2A | CFMR      |              |
| C-CD         | CPR_CD__2A | CCD       |              |
| C-TC         | CPR_TC__2A | CTC       |              |
| C-CLD        | CPR_CLD_2A | CCLD      |              |
| C-APC        | CPR_APC_2A | CAPC      |              |
| A-CLA        | ATL_CLA_2A | ACLA      | JAXA product |
| M-CLP        | MSI_CLP_2A | MCLP      | JAXA product |
| C-ECO        | CPR_ECO_2A | CECO      | JAXA product |
| C-CLP        | CPR_CLP_2A | CCLP      | JAXA product |

### Level 2b products

| Product name | File type  | Shorthand | Notes        |
| ------------ | ---------- | --------- | ------------ |
| AM-MO        | AM__MO__2B | AMMO      |              |
| AM-CTH       | AM__CTH_2B | AMCTH     |              |
| AM-ACD       | AM__ACD_2B | AMACD     |              |
| AC-TC        | AC__TC__2B | ACTC      |              |
| BM-RAD       | BM__RAD_2B | BMRAD     |              |
| BMA-FLX      | BMA_FLX_2B | BMAFLX    |              |
| ACM-CAP      | ACM_CAP_2B | ACMCAP    |              |
| ACM-COM      | ACM_COM_2B | ACMCOM    |              |
| ACM-RT       | ACM_RT__2B | ACMRT     |              |
| ACMB-3D      | ALL_3D__2B | ALL3D     |              |
| ACMB-DF      | ALL_DF__2B | ALLDF     |              |
| AC-CLP       | AC__CLP_2B | ACCLP     | JAXA product |
| ACM-CLP      | ACM_CLP_2B | ACMCLP    | JAXA product |
| ACMB-RAD     | ALL_RAD_2B | ALLRAD    | JAXA product |

### Auxiliary data

| Product name | File type  | Shorthand | Notes |
| ------------ | ---------- | --------- | ----- |
| X-MET        | AUX_MET_1D | XMET      |       |
| X-JSG        | AUX_JSG_1D | XJSG      |       |

### Orbit data

| Product name | File type  | Shorthand | Notes               |
| ------------ | ---------- | --------- | ------------------- |
| ORBSCT       | MPL_ORBSCT | MPLORBS   | Orbit scenario      |
| ORBPRE       | AUX_ORBPRE | XORBP     | Predicted orbit     |
| ORBRES       | AUX_ORBRES | XORBR     | Reconstructed orbit |
