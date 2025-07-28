_file_type_aliases = dict(
    # Level 1
    ATLNOM1B="ATL_NOM_1B",
    ANOM="ATL_NOM_1B",
    ATLDCC1B="ATL_DCC_1B",
    ADCC="ATL_DCC_1B",
    ATLCSC1B="ATL_CSC_1B",
    ACSC="ATL_CSC_1B",
    ATLFSC1B="ATL_FSC_1B",
    AFSC="ATL_FSC_1B",
    MSINOM1B="MSI_NOM_1B",
    MNOM="MSI_NOM_1B",
    MSIBBS1B="MSI_BBS_1B",
    MBBS="MSI_BBS_1B",
    MSISD11B="MSI_SD1_1B",
    MSD1="MSI_SD1_1B",
    MSISD21B="MSI_SD2_1B",
    MSD2="MSI_SD2_1B",
    MSIRGR1C="MSI_RGR_1C",
    MRGR="MSI_RGR_1C",
    BBRNOM1B="BBR_NOM_1B",
    BNOM="BBR_NOM_1B",
    BBRSNG1B="BBR_SNG_1B",
    BSNG="BBR_SNG_1B",
    BBRSOL1B="BBR_SOL_1B",
    BSOL="BBR_SOL_1B",
    BBRLIN1B="BBR_LIN_1B",
    BLIN="BBR_LIN_1B",
    CPRNOM1B="CPR_NOM_1B",  # JAXA product
    CNOM="CPR_NOM_1B",  # JAXA product
    # Level 2a
    ATLFM2A="ATL_FM__2A",
    AFM="ATL_FM__2A",
    ATLAER2A="ATL_AER_2A",
    AAER="ATL_AER_2A",
    ATLICE2A="ATL_ICE_2A",
    AICE="ATL_ICE_2A",
    ATLTC2A="ATL_TC__2A",
    ATC="ATL_TC__2A",
    ATLEBD2A="ATL_EBD_2A",
    AEBD="ATL_EBD_2A",
    ATLCTH2A="ATL_CTH_2A",
    ACTH="ATL_CTH_2A",
    ATLALD2A="ATL_ALD_2A",
    AALD="ATL_ALD_2A",
    MSICM2A="MSI_CM__2A",
    MCM="MSI_CM__2A",
    MSICOP2A="MSI_COP_2A",
    MCOP="MSI_COP_2A",
    MSIAOT2A="MSI_AOT_2A",
    MAOT="MSI_AOT_2A",
    CPRFMR2A="CPR_FMR_2A",
    CFMR="CPR_FMR_2A",
    CPRCD2A="CPR_CD__2A",
    CCD="CPR_CD__2A",
    CPRTC2A="CPR_TC__2A",
    CTC="CPR_TC__2A",
    CPRCLD2A="CPR_CLD_2A",
    CCLD="CPR_CLD_2A",
    CPRAPC2A="CPR_APC_2A",
    CAPC="CPR_APC_2A",
    ATLCLA2A="ATL_CLA_2A",  # JAXA product
    ACLA="ATL_CLA_2A",  # JAXA product
    MSICLP2A="MSI_CLP_2A",  # JAXA product
    MCLP="MSI_CLP_2A",  # JAXA product
    CPRECO2A="CPR_ECO_2A",  # JAXA product
    CECO="CPR_ECO_2A",  # JAXA product
    CPRCLP2A="CPR_CLP_2A",  # JAXA product
    CCLP="CPR_CLP_2A",  # JAXA product
    # Level 2b
    AMMO2B="AM__MO__2B",
    AMMO="AM__MO__2B",
    AMCTH2B="AM__CTH_2B",
    AMCTH="AM__CTH_2B",
    AMACD2B="AM__ACD_2B",
    AMACD="AM__ACD_2B",
    ACTC2B="AC__TC__2B",
    ACTC="AC__TC__2B",
    BMRAD2B="BM__RAD_2B",
    BMRAD="BM__RAD_2B",
    BMAFLX2B="BMA_FLX_2B",
    BMAFLX="BMA_FLX_2B",
    ACMCAP2B="ACM_CAP_2B",
    ACMCAP="ACM_CAP_2B",
    ACMCOM2B="ACM_COM_2B",
    ACMCOM="ACM_COM_2B",
    ACMRT2B="ACM_RT__2B",
    ACMRT="ACM_RT__2B",
    ALLDF2B="ALL_DF__2B",
    ACMBDF="ALL_DF__2B",
    ALLDF="ALL_DF__2B",
    ALL3D2B="ALL_3D__2B",
    ACMB3D="ALL_3D__2B",
    ALL3D="ALL_3D__2B",
    ACCLP2B="AC__CLP_2B",  # JAXA product
    ACCLP="AC__CLP_2B",  # JAXA product
    ACMCLP2B="ACM_CLP_2B",  # JAXA product
    ACMCLP="ACM_CLP_2B",  # JAXA product
    ALLRAD2B="ALL_RAD_2B",  # JAXA product
    ACMBRAD="ALL_RAD_2B",  # JAXA product
    ALLRAD="ALL_RAD_2B",  # JAXA product
    # Auxiliary data
    AUXMET1D="AUX_MET_1D",
    XMET="AUX_MET_1D",
    AUXJSG1D="AUX_JSG_1D",
    XJSG="AUX_JSG_1D",
    # Orbit data
    MPLORBSCT="MPL_ORBSCT",
    MPLORBS="MPL_ORBSCT",
    ORBSCT="MPL_ORBSCT",
    AUXORBPRE="AUX_ORBPRE",
    XORBP="AUX_ORBPRE",
    ORBPRE="AUX_ORBPRE",
    AUXORBRES="AUX_ORBRES",
    XORBR="AUX_ORBRES",
    ORBRES="AUX_ORBRES",
)


def _format_file_type_string(file_type: str) -> str:
    try:
        cleaned_file_type = file_type.replace("-", "").replace("_", "").upper()
        formatted_file_type = _file_type_aliases[cleaned_file_type]
    except KeyError as e:
        raise KeyError(f"'{file_type}' is not a valid FileType alias.")
    return formatted_file_type
