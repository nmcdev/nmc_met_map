import nmc_met_map.synoptic as draw_synoptic
import nmc_met_map.dynamic as draw_dynamic
import nmc_met_map.moisture as draw_moisture
import nmc_met_map.thermal as draw_thermal
import nmc_met_map.QPF as draw_QPF
import nmc_met_map.elements as draw_elements
import nmc_met_map.crossection as draw_crossection
import nmc_met_map.sta as draw_sta
import nmc_met_map.isentropic as draw_isentropic
import nmc_met_map.synthetical as draw_synthetical

draw_sta.Station_Synthetical_Forecast_From_Cassandra(model='中央台指导',points={'lon':[113.59], 'lat':[22.14]},t_range=[4,80],drw_thr=True)
draw_synoptic.gh_uv_r6(model='NCEP_GFS',area='华中')
draw_synthetical.Miller_Composite_Chart()
draw_isentropic.isentropic_uv()
draw_synoptic.PV_Div_uv()
draw_crossection.Crosssection_Wind_Theta_e_RH(model='GRAPES_GFS',day_back=1)
draw_crossection.Crosssection_Wind_Theta_e_absv(model='ECMWF',day_back=1)
draw_elements.low_level_wind(model='ECMWF',day_back=1)
draw_elements.mslp_gust10m(model='ECMWF',day_back=1)
draw_elements.T2m_mslp_uv10m(model='GRAPES_GFS',day_back=1)
draw_elements.T2m_all_type(model='中央台指导预报',day_back=1)
draw_QPF.mslp_rain_snow(model='GRAPES_GFS',day_back=1)
draw_QPF.gh_rain(model='GRAPES_GFS',day_back=1)
draw_thermal.gh_uv_tmp(model='GRAPES_GFS',day_back=1)
draw_thermal.gh_uv_thetae(model='GRAPES_GFS',day_back=1)
draw_moisture.gh_uv_wvfl(model='GRAPES_GFS',day_back=1)
draw_moisture.gh_uv_spfh(model='GRAPES_GFS',day_back=1)
draw_moisture.gh_uv_rh(model='NCEP_GFS')
draw_moisture.gh_uv_pwat(model='NCEP_GFS')
draw_dynamic.gh_uv_VVEL(model='NCEP_GFS')
draw_synoptic.gh_uv_r6(model='NCEP_GFS')
draw_synoptic.gh_uv_wsp(model='NCEP_GFS')
draw_synoptic.gh_uv_mslp(model='NCEP_GFS')
draw_sta.sta_SkewT()
draw_crossection.Time_Crossection_rh_uv_t()    
draw_crossection.Time_Crossection_rh_uv_theta_e()
draw_crossection.Crosssection_Wind_Theta_e_Qv(model='GRAPES_GFS',day_back=1)