from .....constants import EXT_LABEL
from ....info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs


def _get_transforms_dict() -> dict[str, _VarTransformer]:
    return {
        "ice_water_content": _edit_attrs({"label": "Ice water content", "units": "kg m$^{-3}$"}),
        "ice_effective_radius": _edit_attrs({"label": "Ice effective radius"}),
        "rain_water_content": _edit_attrs({"label": "Rain water content", "units": "kg m$^{-3}$"}),
        "rain_median_volume_diameter": _edit_attrs({"label": "Rain median volume diameter"}),
        "liquid_water_content": _edit_attrs(
            {"label": "Liquid water content", "units": "kg m$^{-3}$"}
        ),
        "liquid_effective_radius": _edit_attrs({"label": "Liquid effective radius"}),
        "aerosol_extinction": _edit_attrs({"label": EXT_LABEL, "units": "m$^{-1}$"}),
        "time": _edit_attrs({"label": "Time"}),
        "temperature": _edit_attrs({"label": "Temperature", "units": "K"}),
        "pressure": _edit_attrs({"label": "Pressure", "units": "Pa"}),
        "specific_humidity": _edit_attrs({"label": "Specific humidity", "units": "kg/kg"}),
        "state_variable_count": _edit_attrs({"label": "Number of elements in state vector"}),
        "observation_variable_count": _edit_attrs(
            {"label": "Number of elements in observation vector"}
        ),
        "cost_function": _edit_attrs({"label": "Cost function"}),
        "iterations_count": _edit_attrs({"label": "Iterations count"}),
        "iterations_first_pass_count": _edit_attrs({"label": "Iterations count after first pass"}),
        "convergence_status": _edit_attrs({"label": "Convergence status"}),
        "synergy_status": _edit_attrs({"label": "Synergy status"}),
        "quality_status": _edit_attrs({"label": "Quality status"}),
        "norm_gradient": _edit_attrs({"label": "Norm gradient"}),
        "ice_state_variable_count": _edit_attrs(
            {"label": "Number of state-vector elements associated with ice"}
        ),
        "ice_cost_function": _edit_attrs({"label": "Contribution to final cost function from ice"}),
        "ice_prior_cost_function": _edit_attrs(
            {
                "label": "Contribution to final cost function from ice prior constraints",
            }
        ),
        "ice_regularization_cost_function": _edit_attrs(
            {
                "label": "Contribution to final cost function from ice regularization constraints",
            }
        ),
        "ice_degrees_of_freedom": _edit_attrs(
            {"label": "Number of degrees of freedom in retrieval of ice"}
        ),
        "ice_extinction": _edit_attrs({"label": "Ice ext. coeff."}),
        "ice_extinction_error": _edit_attrs({"label": "Ice ext. coeff. $\\sigma_{ln}$ error"}),
        "ice_extinction_error_corr_scale": _edit_attrs({"label": "Ice ext. decorr. scale"}),
        "ice_extinction_kernel_sum": _edit_attrs({"label": "Ice ext. kernel sum"}),
        "ice_extinction_kernel_corr_scale": _edit_attrs({"label": "Ice ext. kernel decorr. scale"}),
        "ice_N0prime": _edit_attrs({"label": "Ice primed num. conc."}),
        "ice_N0prime_error": _edit_attrs({"label": "Ice primed num. conc. $\\sigma_{ln}$ error"}),
        "ice_N0prime_error_corr_scale": _edit_attrs(
            {"label": "Ice primed num. conc. decorr. scale"}
        ),
        "ice_N0prime_kernel_sum": _edit_attrs({"label": "Ice primed num. conc. kernel sum"}),
        "ice_N0prime_kernel_corr_scale": _edit_attrs(
            {"label": "Ice primed num. conc. kernel decorr. scale"}
        ),
        "ice_lidar_bscat_extinction_ratio": _edit_attrs({"label": "Ice lidar bsc. to ext. ratio"}),
        "ice_lidar_bscat_extinction_ratio_error": _edit_attrs(
            {"label": "Ice lidar bsc. to ext. ratio $\\sigma_{ln}$ error"}
        ),
        "ice_lidar_bscat_extinction_ratio_error_corr_scale": _edit_attrs(
            {"label": "Ice lidar bsc. to ext. ratio decorr. scale"}
        ),
        "ice_lidar_bscat_extinction_ratio_kernel_sum": _edit_attrs(
            {"label": "Ice lidar bsc. to ext. ratio kernel sum"}
        ),
        "ice_lidar_bscat_extinction_ratio_kernel_corr_scale": _edit_attrs(
            {"label": "Ice lidar bsc. to ext. ratio kernel decorr. scale"}
        ),
        "ice_riming_index": _edit_attrs({"label": "Ice riming index"}),
        "ice_riming_index_error": _edit_attrs({"label": "Ice riming index $\\sigma_{ln}$ error"}),
        "ice_riming_index_error_corr_scale": _edit_attrs(
            {"label": "Ice riming index decorr. scale"}
        ),
        "ice_riming_index_kernel_sum": _edit_attrs({"label": "Ice riming index kernel sum"}),
        "ice_riming_index_kernel_corr_scale": _edit_attrs(
            {"label": "Ice riming index kernel decorr. scale"}
        ),
        "ice_water_content_error": _edit_attrs({"label": "Ice water content $\\sigma_{ln}$ error"}),
        "ice_water_content_error_corr_scale": _edit_attrs(
            {"label": "Ice water content decorr. scale"}
        ),
        "ice_mass_flux": _edit_attrs({"label": "Ice mass flux"}),
        "ice_mass_flux_error": _edit_attrs({"label": "Ice mass flux $\\sigma_{ln}$ error"}),
        "ice_mass_flux_error_corr_scale": _edit_attrs({"label": "Ice mass flux decorr. scale"}),
        "ice_normalized_number_concentration": _edit_attrs({"label": "Ice normalized num. conc."}),
        "ice_normalized_number_concentration_error": _edit_attrs(
            {"label": "Ice normalized num. conc. $\\sigma_{ln}$ error"}
        ),
        "ice_normalized_number_concentration_error_corr_scale": _edit_attrs(
            {"label": "Ice normalized num. conc. decorr. scale"}
        ),
        "ice_effective_radius_error": _edit_attrs(
            {"label": "Ice effective radius $\\sigma_{ln}$ error"}
        ),
        "ice_effective_radius_error_corr_scale": _edit_attrs(
            {"label": "Ice effective radius decorr. scale"}
        ),
        "ice_median_volume_diameter": _edit_attrs({"label": "Ice median vol. diameter"}),
        "ice_median_volume_diameter_error": _edit_attrs(
            {"label": "Ice median vol. diameter $\\sigma_{ln}$ error"}
        ),
        "ice_median_volume_diameter_error_corr_scale": _edit_attrs(
            {"label": "Ice median vol. diameter decorr. scale"}
        ),
        "ice_riming_factor": _edit_attrs({"label": "Ice riming factor"}),
        "ice_riming_factor_error": _edit_attrs({"label": "Ice riming factor error"}),
        "ice_riming_factor_error_corr_scale": _edit_attrs(
            {"label": "Ice riming factor decorr. scale"}
        ),
        "ice_water_path": _edit_attrs({"label": "Ice water path"}),
        "ice_water_path_error": _edit_attrs({"label": "Ice water path $\\sigma_{ln}$ error"}),
        "ice_extinction_N0prime_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and primed num. conc."
            }
        ),
        "ice_extinction_lidar_bscat_extinction_ratio_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and lidar bsc. to ext. ratio",
            }
        ),
        "ice_extinction_riming_index_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and riming index",
            }
        ),
        "ice_N0prime_lidar_bscat_extinction_ratio_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice primed num. conc. and lidar bsc. to ext. ratio",
            }
        ),
        "ice_N0prime_riming_index_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice primed num. conc. and riming index",
            }
        ),
        "ice_lidar_bscat_extinction_ratio_riming_index_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice lidar bsc. to ext. ratio and riming index",
            }
        ),
        "ice_extinction_water_content_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and water content",
            }
        ),
        "ice_extinction_mass_flux_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and mass flux",
            }
        ),
        "ice_extinction_normalized_number_concentration_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and normalized num. conc.",
            }
        ),
        "ice_extinction_effective_radius_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and effective radius",
            }
        ),
        "ice_extinction_median_volume_diameter_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and median volume diameter",
            }
        ),
        "ice_extinction_riming_factor_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of ice geometric ext. coeff. and riming factor",
            }
        ),
        "rain_state_variable_count": _edit_attrs(
            {"label": "Number of state-vector elements associated with rain"}
        ),
        "rain_cost_function": _edit_attrs(
            {"label": "Contribution to final cost function from rain"}
        ),
        "rain_prior_cost_function": _edit_attrs(
            {
                "label": "Contribution to final cost function from rain prior constraints",
            }
        ),
        "rain_regularization_cost_function": _edit_attrs(
            {
                "label": "Contribution to final cost function from rain regularization constraints",
            }
        ),
        "rain_degrees_of_freedom": _edit_attrs(
            {"label": "Number of degrees of freedom in retrieval of rain"}
        ),
        "rain_classification": _edit_attrs({"label": "Rain classification"}),
        "rain_rate": _edit_attrs({"label": "Rain rate"}),
        "rain_rate_error": _edit_attrs({"label": "Rain rate $\\sigma_{ln}$ error"}),
        "rain_rate_error_corr_scale": _edit_attrs({"label": "Rain rate decorr. scale"}),
        "rain_rate_kernel_sum": _edit_attrs({"label": "Row-sum of averaging kernel of rain rate"}),
        "rain_rate_kernel_corr_scale": _edit_attrs({"label": "Rain rate kernel decorr. scale"}),
        "rain_number_concentration_scaling": _edit_attrs({"label": "Rain num. conc. scaling"}),
        "rain_number_concentration_scaling_error": _edit_attrs(
            {"label": "Rain num. conc. scaling $\\sigma_{ln}$ error"}
        ),
        "rain_number_concentration_scaling_error_corr_scale": _edit_attrs(
            {"label": "Rain num. conc. decorr. scale"}
        ),
        "rain_water_content_error": _edit_attrs(
            {"label": "Rain water content $\\sigma_{ln}$ error"}
        ),
        "rain_water_content_error_corr_scale": _edit_attrs(
            {"label": "Rain water content decorr. scale"}
        ),
        "rain_median_volume_diameter_error": _edit_attrs(
            {"label": "Rain median volume diameter $\\sigma_{ln}$ error"}
        ),
        "rain_median_volume_diameter_error_corr_scale": _edit_attrs(
            {"label": "Rain median volume diameter decorr. scale"}
        ),
        "rain_normalized_number_concentration": _edit_attrs(
            {"label": "Rain normalized num. conc."}
        ),
        "rain_normalized_number_concentration_error": _edit_attrs(
            {"label": "Rain normalized num. conc. $\\sigma_{ln}$ error"}
        ),
        "rain_normalized_number_concentration_error_corr_scale": _edit_attrs(
            {"label": "Rain normalized num. conc. decorr. scale"}
        ),
        "rain_rate_water_content_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of rain rate and water content",
            }
        ),
        "rain_rate_median_volume_diameter_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of rain rate and median volume diameter",
            }
        ),
        "rain_rate_normalized_number_concentration_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of rain rate and normalized num. conc.",
            }
        ),
        "melting_ice_state_variable_count": _edit_attrs(
            {"label": "Number of state-vector elements associated with melting_ice"}
        ),
        "melting_ice_cost_function": _edit_attrs(
            {"label": "Contribution to final cost function from melting_ice"}
        ),
        "melting_ice_prior_cost_function": _edit_attrs(
            {
                "label": "Contribution to final cost function from melting_ice prior constraints",
            }
        ),
        "melting_ice_regularization_cost_function": _edit_attrs(
            {
                "label": "Contribution to final cost function from melting_ice regularization constraints",
            }
        ),
        "melting_ice_degrees_of_freedom": _edit_attrs(
            {"label": "Number of degrees of freedom in retrieval of melting_ice"}
        ),
        "melting_layer_scaling_factor": _edit_attrs(
            {
                "label": "Factor by which the radar attenuation by the melting layer has been multiplied",
            }
        ),
        "radar_melting_layer_attenuation": _edit_attrs(
            {"label": "Two-way melting-layer attenuation at a wavelength of -1 m"}
        ),
        "liquid_state_variable_count": _edit_attrs(
            {"label": "Number of state-vector elements associated with liquid"}
        ),
        "liquid_cost_function": _edit_attrs(
            {"label": "Contribution to final cost function from liquid"}
        ),
        "liquid_prior_cost_function": _edit_attrs(
            {
                "label": "Contribution to final cost function from liquid prior constraints",
            }
        ),
        "liquid_regularization_cost_function": _edit_attrs(
            {
                "label": "Contribution to final cost function from liquid regularization constraints",
            }
        ),
        "liquid_degrees_of_freedom": _edit_attrs(
            {"label": "Number of degrees of freedom in retrieval of liquid"}
        ),
        "liquid_classification": _edit_attrs({"label": "Liquid classification"}),
        "liquid_water_content": _edit_attrs({"label": "Liquid water content"}),
        "liquid_water_content_error": _edit_attrs(
            {"label": "Liquid water content $\\sigma_{ln}$ error"}
        ),
        "liquid_water_content_error_corr_scale": _edit_attrs(
            {"label": "Liquid water content decorr. scale decorr. scale"}
        ),
        "liquid_water_content_kernel_sum": _edit_attrs(
            {"label": "Row-sum of averaging kernel of liquid water content"}
        ),
        "liquid_water_content_kernel_corr_scale": _edit_attrs(
            {"label": "Liquid water content kernel decorr. scale"}
        ),
        "liquid_number_concentration": _edit_attrs({"label": "Liquid num. conc."}),
        "liquid_number_concentration_error": _edit_attrs(
            {"label": "Liquid num. conc. $\\sigma_{ln}$ error"}
        ),
        "liquid_number_concentration_error_corr_scale": _edit_attrs(
            {"label": "Liquid num. conc. decorr. scale"}
        ),
        "liquid_lidar_bscat_extinction_ratio": _edit_attrs(
            {"label": "Liquid lidar bsc. to ext. ratio"}
        ),
        "liquid_lidar_bscat_extinction_ratio_error": _edit_attrs(
            {"label": "Liquid lidar bsc. to ext. ratio $\\sigma_{ln}$ error"}
        ),
        "liquid_lidar_bscat_extinction_ratio_error_corr_scale": _edit_attrs(
            {"label": "Liquid lidar bsc. to ext. ratio decorr. scale"}
        ),
        "liquid_extinction": _edit_attrs({"label": "Liquid ext. coeff."}),
        "liquid_extinction_error": _edit_attrs(
            {"label": "Liquid ext. coeff. $\\sigma_{ln}$ error"}
        ),
        "liquid_extinction_error_corr_scale": _edit_attrs(
            {"label": "Liquid ext. coeff. decorr. scale"}
        ),
        "liquid_effective_radius_error": _edit_attrs(
            {"label": "Liquid effective radius $\\sigma_{ln}$ error"}
        ),
        "liquid_effective_radius_error_corr_scale": _edit_attrs(
            {"label": "Liquid effective radius decorr. scale"}
        ),
        "liquid_optical_depth": _edit_attrs({"label": "Liquid optical depth"}),
        "liquid_optical_depth_error": _edit_attrs(
            {"label": "Liquid optical depth $\\sigma_{ln}$ error"}
        ),
        "liquid_water_content_extinction_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of liquid water content and ext. coeff.",
            }
        ),
        "liquid_water_content_effective_radius_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of liquid water content and effective radius",
            }
        ),
        "aerosol_state_variable_count": _edit_attrs(
            {"label": "Number of state-vector elements associated with aerosol"}
        ),
        "aerosol_cost_function": _edit_attrs({"label": "Aerosol cost function contribution"}),
        "aerosol_prior_cost_function": _edit_attrs(
            {"label": "Aerosol prior constraints cost function contribution"}
        ),
        "aerosol_regularization_cost_function": _edit_attrs(
            {
                "label": "Aerosol regularization constraints cost function contribution",
            }
        ),
        "aerosol_degrees_of_freedom": _edit_attrs({"label": "Aerosol DoF"}),
        "aerosol_classification": _edit_attrs({"label": "Aerosol classification"}),
        "aerosol_median_volume_diameter": _edit_attrs({"label": "Aerosol median volume diameter"}),
        "aerosol_median_volume_diameter_error": _edit_attrs(
            {"label": "Aerosol median volume diameter $\\sigma_{ln}$ error"}
        ),
        "aerosol_median_volume_diameter_error_corr_scale": _edit_attrs(
            {"label": "Aerosol median volume diameter decorr. scale"}
        ),
        "aerosol_number_concentration": _edit_attrs({"label": "Aerosol num. conc."}),
        "aerosol_number_concentration_error": _edit_attrs(
            {"label": "Aerosol num. conc. $\\sigma_{ln}$ error"}
        ),
        "aerosol_number_concentration_error_corr_scale": _edit_attrs(
            {"label": "Aerosol num. conc. decorr. scale"}
        ),
        "aerosol_number_concentration_kernel_sum": _edit_attrs(
            {"label": "Row-sum of averaging kernel of aerosol num. conc."}
        ),
        "aerosol_number_concentration_kernel_corr_scale": _edit_attrs(
            {"label": "Aerosol num. conc. kernel decorr. scale"}
        ),
        "aerosol_mass_content": _edit_attrs({"label": "Aerosol mass content"}),
        "aerosol_mass_content_error": _edit_attrs(
            {"label": "Aerosol mass content $\\sigma_{ln}$ error"}
        ),
        "aerosol_mass_content_error_corr_scale": _edit_attrs(
            {"label": "Aerosol mass content decorr. scale"}
        ),
        "aerosol_extinction_error": _edit_attrs(
            {"label": "Aerosol geometric ext. coeff. $\\sigma_{ln}$ error"}
        ),
        "aerosol_extinction_error_corr_scale": _edit_attrs({"label": "Aerosol ext. decorr. scale"}),
        "aerosol_optical_depth": _edit_attrs({"label": "AOD"}),
        "aerosol_optical_depth_error": _edit_attrs({"label": "AOD $\\sigma_{ln}$ error"}),
        "aerosol_median_volume_diameter_number_concentration_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of aerosol median volume diameter and num. conc.",
            }
        ),
        "aerosol_median_volume_diameter_mass_content_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of aerosol median volume diameter and mass content",
            }
        ),
        "aerosol_median_volume_diameter_extinction_error_corr": _edit_attrs(
            {
                "label": "Error corr. between natural logs of aerosol median volume diameter and geometric ext. coeff.",
            }
        ),
        "CPR_observation_variable_count": _edit_attrs({"label": "CPR obs. var. count"}),
        "CPR_cost_function": _edit_attrs({"label": "CPR cost function contribution"}),
        "CPR_reflectivity_factor_forward": _edit_attrs(
            {"label": "Forward modelled reflectivity factor"}
        ),
        "CPR_reflectivity_factor": _edit_attrs({"label": "Reflectivity factor"}),
        "CPR_reflectivity_factor_assimilation_status": _edit_attrs(
            {"label": "Reflectivity factor assim. status"}
        ),
        "CPR_doppler_velocity_forward": _edit_attrs({"label": "Forward modelled doppler velocity"}),
        "CPR_doppler_velocity": _edit_attrs({"label": "Doppler velocity"}),
        "CPR_doppler_velocity_assimilation_status": _edit_attrs(
            {"label": "Doppler velocity assim. status"}
        ),
        "CPR_path_integrated_attenuation_forward": _edit_attrs(
            {"label": "Forward modelled path-integrated attenuation"}
        ),
        "CPR_path_integrated_attenuation": _edit_attrs({"label": "Path-integrated attenuation"}),
        "CPR_path_integrated_attenuation_assimilation_status": _edit_attrs(
            {"label": "Path-integrated attenuation assim. status"}
        ),
        "CPR_optical_depth_forward": _edit_attrs(
            {"label": "Forward modelled AOD at CPR wavelength"}
        ),
        "ATLID_observation_variable_count": _edit_attrs({"label": "ATLID obs. var. count"}),
        "ATLID_cost_function": _edit_attrs({"label": "ATLID cost function contribution"}),
        "ATLID_backscatter_mie_forward": _edit_attrs(
            {"label": "Forward modelled Mie apparent bsc. coeff."}
        ),
        "ATLID_backscatter_mie": _edit_attrs({"label": "Mie apparent bsc. coeff."}),
        "ATLID_backscatter_mie_assimilation_status": _edit_attrs(
            {"label": "Mie apparent bsc. coeff. assim. status"}
        ),
        "ATLID_backscatter_rayleigh_forward": _edit_attrs(
            {"label": "Forward modelled Rayleigh apparent bsc. coeff."}
        ),
        "ATLID_backscatter_rayleigh": _edit_attrs({"label": "Rayleigh apparent bsc. coeff."}),
        "ATLID_backscatter_rayleigh_assimilation_status": _edit_attrs(
            {"label": "Rayleigh apparent bsc. coeff. assim. status"}
        ),
        "ATLID_bscat_extinction_ratio": _edit_attrs({"label": "Bsc. to ext. coeff. ratio"}),
        "ATLID_optical_depth_forward": _edit_attrs(
            {"label": "Forward modelled AOD at ATLID wavelength"}
        ),
        "MSI_longwave_observation_variable_count": _edit_attrs(
            {"label": "MSI longwave obs. var. count"}
        ),
        "MSI_longwave_cost_function": _edit_attrs(
            {"label": "MSI longwave cost function contribution"}
        ),
        "MSI_longwave_wavelength": _edit_attrs({"label": "MSI_longwave channel wavelengths"}),
        "MSI_longwave_brightness_temperature_forward": _edit_attrs(
            {"label": "Forward modelled brightness temperature"}
        ),
        "MSI_longwave_brightness_temperature": _edit_attrs(
            {"label": "MSI longwave brightness temperature"}
        ),
        "MSI_longwave_brightness_temperature_assimilation_status": _edit_attrs(
            {"label": "MSI longwave brightness temperature assim. status"}
        ),
        "MSI_shortwave_observation_variable_count": _edit_attrs(
            {"label": "MSI shortwave obs. var. count"}
        ),
        "MSI_shortwave_cost_function": _edit_attrs(
            {"label": "MSI shortwave cost function contribution"}
        ),
        "MSI_shortwave_wavelength": _edit_attrs({"label": "MSI shortwave wavelengths"}),
        "MSI_shortwave_albedo_forward": _edit_attrs({"label": "Forward modelled albedo"}),
        "MSI_shortwave_albedo": _edit_attrs({"label": "MSI shortwave albedo"}),
        "MSI_shortwave_albedo_assimilation_status": _edit_attrs(
            {"label": "MSI shortwave albedo assim. status"}
        ),
    }


register(
    file_type=FileType.ACM_CAP_2B.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="elevation",
        tropopause_var="tropopause_height",
        land_flag_var="land_flag",
        geoid_offset_var="geoid_offset",
        generators={},
        optional_generators={},
        transforms={**_get_transforms_dict()},
        height_vars={
            "height",
            "elevation",
            "tropopause_height",
        },
    ),
)
