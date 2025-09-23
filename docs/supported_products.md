# Supported EarthCARE products

The following tables describe the coverage for EarthCARE products for the latest version {{ version }} of `earthcarekit`.

!!! note
    Here, reading support means that the product can be opend using the [`read_product`][earthcarekit.read_product] function. Products that are not yet supported can also be opened as a `xarray.Dataset` by using the more basic [`read_science_data`][earthcarekit.read_science_data] function. The latter function reads the data unmodified, without adding metadata or harmonising dimension names, which can lead to errors when using other utility functions of the package.

### Level 1 products

| File type | Read | Quicklook | Notes |
| --------- | ---- | --------- | ----- |
| ATL_NOM_1B | ✓ | ✓ |  |
| MSI_NOM_1B |  |  |  |
| BBR_NOM_1B |  |  |  |
| CPR_NOM_1B | ✓ |  | JAXA product |
| MSI_RGR_1C | ✓ |  |  |

### Level 2a products

| File type | Read | Quicklook | Notes |
| --------- | ---- | --------- | ----- |
| ATL_FM__2A | ✓ |  |  |
| ATL_AER_2A | ✓ | ✓ |  |
| ATL_ICE_2A | ✓ |  |  |
| ATL_TC__2A | ✓ | ✓ |  |
| ATL_EBD_2A | ✓ | ✓ |  |
| ATL_CTH_2A | ✓ | ✓ | QL needs additional products for background curtain (e.g., A-EBD bsc.) |
| ATL_ALD_2A | ✓ | ✓ | QL needs additional products for background curtain (e.g., A-EBD bsc.) |
| MSI_CM__2A |  |  |  |
| MSI_COP_2A |  |  |  |
| MSI_AOT_2A |  |  |  |
| CPR_FMR_2A |  |  |  |
| CPR_CD__2A |  |  |  |
| CPR_TC__2A |  |  |  |
| CPR_CLD_2A |  |  |  |
| CPR_APC_2A |  |  |  |
| ATL_CLA_2A | ✓ |  | JAXA product |
| MSI_CLP_2A |  |  | JAXA product |
| CPR_ECO_2A |  |  | JAXA product |
| CPR_CLP_2A |  |  | JAXA product |

### Level 2b products

| File type | Read | Quicklook | Notes |
| --------- | ---- | --------- | ----- |
| AM__MO__2B |  |  |  |
| AM__CTH_2B | ✓ |  |  |
| AM__ACD_2B | ✓ |  |  |
| AC__TC__2B | ✓ |  |  |
| BM__RAD_2B |  |  |  |
| BMA_FLX_2B |  |  |  |
| ACM_CAP_2B | ✓ |  |  |
| ACM_COM_2B |  |  |  |
| ACM_RT__2B |  |  |  |
| ALL_3D__2B |  |  |  |
| ALL_DF__2B |  |  |  |
| AC__CLP_2B |  |  | JAXA product |
| ACM_CLP_2B |  |  | JAXA product |
| ALL_RAD_2B |  |  | JAXA product |