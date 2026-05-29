from typing import Final

FILE_TYPE_SHORT_HAND: Final[dict[str, str]] = dict(
    # Level 1
    ATL_NOM_1B="A-NOM",
    ATL_DCC_1B="A-DCC",
    ATL_CSC_1B="A-CSC",
    ATL_FSC_1B="A-FSC",
    MSI_NOM_1B="M-NOM",
    MSI_BBS_1B="M-BBS",
    MSI_SD1_1B="M-SD1",
    MSI_SD2_1B="M-SD2",
    MSI_RGR_1C="M-RGR",
    BBR_NOM_1B="B-NOM",
    BBR_SNG_1B="B-SNG",
    BBR_SOL_1B="B-SOL",
    BBR_LIN_1B="B-LIN",
    CPR_NOM_1B="C-NOM",  # JAXA product
    # Level 2a
    ATL_FM__2A="A-FM",
    ATL_AER_2A="A-AER",
    ATL_ICE_2A="A-ICE",
    ATL_TC__2A="A-TC",
    ATL_EBD_2A="A-EBD",
    ATL_CTH_2A="A-CTH",
    ATL_ALD_2A="A-ALD",
    MSI_CM__2A="M-CM",
    MSI_COP_2A="M-COP",
    MSI_AOT_2A="M-AOT",
    CPR_FMR_2A="C-FMR",
    CPR_CD__2A="C-CD",
    CPR_TC__2A="C-TC",
    CPR_CLD_2A="C-CLD",
    CPR_APC_2A="C-APC",
    ATL_CLA_2A="A-CLA",  # JAXA product
    MSI_CLP_2A="M-CLP",  # JAXA product
    CPR_ECO_2A="C-ECO",  # JAXA product
    CPR_CLP_2A="C-CLP",  # JAXA product
    # Level 2b
    AM__MO__2B="AM-MO",
    AM__CTH_2B="AM-CTH",
    AM__ACD_2B="AM-ACD",
    AC__TC__2B="AC-TC",
    BM__RAD_2B="BM-RAD",
    BMA_FLX_2B="BMA-FLX",
    ACM_CAP_2B="ACM-CAP",
    ACM_COM_2B="ACM-COM",
    ACM_RT__2B="ACM-RT",
    ALL_DF__2B="ALL-DF",
    ALL_3D__2B="ALL-3D",
    AC__CLP_2B="AC-CLP",  # JAXA product
    ACM_CLP_2B="ACM-CLP",  # JAXA product
    ALL_RAD_2B="ALL-RAD",  # JAXA product
    # Auxiliary data
    AUX_MET_1D="X-MET",
    AUX_JSG_1D="X-JSG",
    # Orbit data
    MPL_ORBSCT="MPL-ORBSCT",
    AUX_ORBPRE="X-ORBPRE",
    AUX_ORBRES="X-ORBRES",
)
