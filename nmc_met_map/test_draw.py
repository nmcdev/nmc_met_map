import nmc_met_map.synoptic as draw_synoptic
import nmc_met_map.dynamic as draw_dynamic
import nmc_met_map.moisture as draw_moisture
import nmc_met_map.thermal as draw_thermal
import nmc_met_map.QPF as draw_QPF
import nmc_met_map.elements as draw_elements
import nmc_met_map.elements2 as draw_elements2
import nmc_met_map.sta2 as draw_sta2
import nmc_met_map.sta as draw_sta
import nmc_met_map.isentropic as draw_isentropic
import nmc_met_map.synthetical as draw_synthetical
import nmc_met_map.local_scale as draw_local_scale
import nmc_met_map.observation as draw_observation
import nmc_met_map.syn_ver as draw_synoptic_verification
import nmc_met_map.observation2 as draw_observation2
import nmc_met_map.graphics2.pallete_set as ps
from nmc_met_map.sta import sta_graphics
import numpy as np
import pandas as pd

import nmc_met_map.crossection as draw_crossection
import nmc_met_map.syn_ver.VS_ana as draw_syn_ver_ana

Tmean_2m=draw_elements.T2m_mean24(model='中央气象台智能网格',data_source ='MICAPS',city=True,return_data=True)

draw_elements.T2m_mn24(initTime='20111608',fhour=24,area='全国',map_ratio=10/9,
                        model='中央气象台智能网格',data_source ='MICAPS',city=True)

sta_all={'lon':[86.92528],
        'lat':[27.98805],
        'altitude':[8848],
        'ID':['A01'],
        'name':['珠峰']}

draw_sta2.MICAPS.ECMWF_ENSEMBLE.point_fcst_wsp_according_to_3D_field_box_line(
            t_gap=6,
            points=sta_all,
            extra_info={
                'output_head_name':' ',
                'output_tail_name':' ',
                'point_name':sta_all['name'][0],
                'drw_thr':False,
                'levels_for_interp':[850, 800, 700, 600, 500,400,300,250,200,150]}
                )

sta_fcs={'lon':[120],
    'lat':[36],
    'altitude':[8848],
    'name':['健美乡']}
draw_local_scale.wind_temp_rn_according_to_4D_data(data_source='MICAPS',fhour=3,
    sta_fcs=sta_fcs,zoom_ratio=0.1,map_ratio=4/3,model='ECMWF',draw_zd=True,
    bkgd_type='terrain')

draw_syn_ver_ana.compare_vs_ana.compare_gh_uv(fhour=72,city=True)

for ihour in [18,24,30,36]:
    draw_elements.mslp_gust10m_uv10m(model='ECMWF',city=False,area='全国',t_gap=6,fhour=ihour,map_ratio=12/9,
                            output_dir='L:/py_develop/test_output/20201107/')

draw_synoptic.gh_uv_mslp(model='GRAPES_GFS',city=False,area='全国',fhour=24,map_ratio=12/9,
                        output_dir='L:/py_develop/test_output/20201107/')

draw_elements.T2m_mn24(initTime='20110708',fhour=24,area='全国',map_ratio=10/9,
                        model='中央气象台智能网格',data_source ='MICAPS',city=True,
                        output_dir='L:/py_develop/test_output/20201107/')


draw_QPF.mslp_rain_snow(model='GRAPES_GFS',area='东北',fhour=36,atime=24,map_ratio=9/9,
        output_dir='L:/py_develop/test_output/20201107/')

for ihour in [18,24,30,36]:
    draw_elements.mslp_gust10m(model='ECMWF',t_gap=6,city=True,
        fhour=ihour,zoom_ratio=14,cntr_pnt=[115,42],map_ratio=9/9,south_China_sea=False,
        output_dir='L:/py_develop/test_output/20201107/')

draw_crossection.Time_Crossection_rh_uv_t()

draw_synoptic_verification.VS_OBS.MICAPS.ECMWF.point_fcst_uv_tmp_according_to_3D_field_vs_sounding(
        obs_ID='55664',
        initTime='20052208',fhour=12,day_back=0,
        output_dir='L:/Temp/',
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':' ',
            'drw_thr':True,
            'levels_for_interp':[1000, 950, 925, 900, 850, 800, 700, 600, 500,400,300,250,200,150]}
            )

draw_observation.IR_Sounding_GeopotentialHeight(Sounding_time='20110208',
    HGT_initTime='20110208',IR_time='20110208',fhour=12,zoom_ratio=20,map_ratio=4/3,
    south_China_sea=True,Channel='C009')

draw_QPF.cumulated_precip()

draw_sta.Station_Synthetical_Forecast_From_Cassandra()


sta_all={'lon':[86.92528],
        'lat':[27.98805],
        'altitude':[8848],
        'ID':['A01'],
        'name':['珠峰']}

draw_sta2.MICAPS.ECMWF_ENSEMBLE.point_fcst_rn_according_to_3D_field_box_line(
            t_range=[0,241],
            t_gap=6,
            points=sta_all,
            extra_info={
                'output_head_name':' ',
                'output_tail_name':' ',
                'point_name':' ',
                'drw_thr':True}
            )

draw_elements.T2m_mx24(fhour=24,
                        model='中央气象台中短期指导',
                        data_source ='MICAPS',
                        city=True,zoom_ratio=14,cntr_pnt=[115,42],map_ratio=9/9)

draw_elements2.MICAPS.GRAPES_GFS.dT2m_mx24(city=True,fhour=36,zoom_ratio=14,cntr_pnt=[115,42],map_ratio=9/9)
draw_elements2.MICAPS.GRAPES_GFS.dT2m_mn24(city=True,fhour=36,zoom_ratio=15,cntr_pnt=[115,42],map_ratio=12/9,)
draw_elements2.MICAPS.GRAPES_GFS.dT2m_mean24(city=True,area='全国',fhour=36,map_ratio=12/9)


draw_synoptic.gh_uv_wsp(model='GRAPES_GFS',fhour=18,map_ratio=12/9,zoom_ratio=10,gh_lev=500,uv_lev=700,area =None,cntr_pnt=[104,35])


draw_dynamic.fg_uv_tmp(model='GRAPES_GFS',fhour=24,city=True,cntr_pnt=[110,16],zoom_ratio=8,map_ratio=12/9,
                     fg_lev=925)

draw_elements2.MICAPS.SCMOC.dT2m_mx24(initTime='20102108',fhour=24,area='全国',city=True,map_ratio=12/9)

draw_crossection.Crosssection_Wind_Theta_e_absv(model='GRAPES_GFS',fhour=24,
                                               lw_ratio=[12,9],
                                                st_point=[28,107.0], ed_point=[33,120.0],
                                               levels=[1000, 950, 925, 900, 850, 800, 700,600,500])

draw_synoptic.PV_Div_uv(fhour=3,data_source='CIMISS',area='东北',city=True)

draw_moisture.gh_uv_spfh(model='ECMWF')

draw_sta2.MICAPS.SCMOC.point_uv_gust_tmp_rh_rn_fcst(
            t_range=[24,84],
            t_gap=3,
            points={'lon':[120], 'lat':[50]},
            initTime=None,day_back=0,
            extra_info={
                'output_head_name':' ',
                'output_tail_name':' ',
                'point_name':'test'}
                )

draw_sta.point_fcst(
        model='GRAPES_GFS',
        t_range=[0,84],
        initTime='20092220',
        t_gap=3
            )

sta_fcs={'lon':[120],
    'lat':[36],
    'altitude':[100],
    'name':['健美乡']}
draw_local_scale.wind_rh_according_to_4D_data(data_source='MICAPS',fhour=3,
    sta_fcs=sta_fcs,zoom_ratio=0.1,map_ratio=4/3,model='ECMWF',draw_zd=True,
    bkgd_type='terrain')

draw_sta.sta_SkewT()

draw_sta2.MICAPS.ECMWF_ENSEMBLE.point_fcst_tmp_according_to_3D_field_box_line(
            initTime='20092220',
            t_range=[0,241],
            t_gap=6,
            points=sta_all,
            extra_info={
                'output_head_name':' ',
                'output_tail_name':' ',
                'point_name':sta_all['name'][0],
                'drw_thr':False,
                'levels_for_interp':[700, 500,300,200]}
                )

draw_sta.point_fcst_according_to_3D_field_VS_zd_plot(initTime='20092308',
        model='ECMWF',t_range=[0,241],
        t_gap=6,
        points={'lon':[86.92528], 'lat':[27.98805],'altitude':[5209]},
        obs_ID=852020,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':'珠峰大本营',
            'drw_thr':False,
            'levels_for_interp':[850, 800, 700, 600, 500,400,300,250,200,150]}
            )

input_file='L:/Temp/test.h5'
test_file=pd.read_hdf(input_file)
sta_graphics.draw_AQI_points(test_file,output_dir='L:/Temp/',AQI_scatter_kwargs={'levels':np.arange(0,200)},pallete_kwargs={'add_background':False})

output_dir='L:/RoutineJob/20200827/'


draw_QPF.cumulated_precip_evo(output_dir='L:/新建文件夹/',
    initTime='20082508',t_range=[30,60],t_gap=6,map_ratio=9/14,
    zoom_ratio=15, cntr_pnt=[120,39],
    data_source='MICAPS')

for i in range(24,96,6):
    draw_QPF.cumulated_precip(output_dir='L:/新建文件夹/GRAPES/',
        initTime='20082520',t_range=[18,i+1],t_gap=6,map_ratio=16/14,
        zoom_ratio=6, cntr_pnt=[122,40.5],model='GRAPES_GFS',
        data_source='MICAPS')#加等值线、白边突显、固定4个时次

    draw_QPF.cumulated_precip(output_dir='L:/新建文件夹/EC/',
        initTime='20082520',t_range=[18,i+1],t_gap=6,map_ratio=16/14,
        zoom_ratio=6, cntr_pnt=[122,40.5],
        data_source='MICAPS')#加等值线、白边突显、固定4个时次


# draw_thermal.TMP850_extreme_uv()
draw_observation.CREF_Sounding_GeopotentialHeight(CREF_time='20082008',
    HGT_initTime='20081920',Sounding_time='20082008',fhour=12,zoom_ratio=20,map_ratio=4/3,area='全国')

draw_thermal.TMP850_anomaly_uv()

draw_synoptic.gh500_anomaly_uv()

draw_dynamic.gh_uv_VVEL(data_source='CIMISS',model='ECMWF',initTime='20081120',
                        fhour=24,map_ratio=12/9,gh_lev=700,uvw_lev=850)

draw_isentropic.isentropic_uv(initTime='20081220',fhour=0,map_ratio=12/9,area='华北',isentlev=360,city=True)

draw_crossection.Crosssection_Wind_Temp_RH(model='ECMWF',initTime='20081220',fhour=0,
                                               lw_ratio=[25,9],map_extent=[112,123,34,42],
                                                st_point=[41.5,116.6], ed_point=[36.8,117.0],
                                               levels=[1000, 950, 925, 900, 850, 800, 700])

draw_synoptic.PV_Div_uv(data_source='CIMISS',map_ratio=12/10)

draw_QPF.gh_rain(model='GRAPES_3KM',initTime='20081020',fhour=60,map_ratio=12/9)

draw_observation2.MICAPS.CLDAS.Tmx2m24(
    endtime='20072908', cu_ndays=7,area='全国',
    south_China_sea=True,city=True)

draw_crossection.Crosssection_Wind_Temp_RH(model='ECMWF',fhour=60,lw_ratio=[25,9],
    st_point=[43.5,111.5], ed_point=[33,125.0])


draw_observation2.MICAPS.CLDAS.cumulative_precip_and_rain_days(
    endtime='20072308', cu_ndays=7, rn_ndays=7,area='全国',
    south_China_sea=True,city=False)

draw_elements.mslp_gust10m_uv10m(model='ECMWF',area='全国',data_source='CIMISS',t_gap=6)
draw_synoptic.gh_uv_r6(initTime='20062620',model='ECMWF',data_source='CIMISS',fhour=12)

###############################+重新梳理'

draw_QPF.Rain_evo(initTime='20051908',data_source='CIMISS',t_range=[6,36],area='江南',fcs_lvl=13,t_gap=6,map_ratio=16/9)#加等值线、白边突显、固定4个时次

draw_elements.T2m_mslp_uv10m(model='ECMWF',data_source='CIMISS')

draw_elements.T2m_zero_heatwaves(model='ECMWF',data_source ='CIMISS',city=True)

draw_elements2.MICAPS.ECMWF.dT2m_mean24(city=True,fhour=60)
draw_elements2.MICAPS.ECMWF.dT2m_mn24(city=True,fhour=33)
draw_elements2.MICAPS.ECMWF.dT2m_mx24(city=True,fhour=60)
draw_crossection.Time_Crossection_rh_uv_theta_e(t_range=[0,108],levels=[1000,950,925,900,850,800,700,600,500])
draw_crossection.Crosssection_Wind_Theta_e_Qv(model='GRAPES_GFS',day_back=1,lw_ratio=[25,9],data_source='CIMISS')
draw_crossection.Time_Crossection_rh_uv_Temp(model='GRAPES_GFS',t_range=[0,84],levels=[1000,950,925,900,850,800,700,600,500],lw_ratio=[25,9],data_source='CIMISS')

draw_crossection.Crosssection_Wind_Theta_e_RH(model='GRAPES_GFS',data_source='CIMISS')
draw_synthetical.Miller_Composite_Chart(map_ratio=8/5)
draw_elements.low_level_wind(model='ECMWF',day_back=1,data_source='CIMISS')
draw_thermal.gh_uv_tmp(model='GRAPES_GFS',map_ratio=5/3,data_source='CIMISS')
draw_thermal.gh_uv_thetae(model='GRAPES_GFS',data_source='CIMISS',map_ratio=4/3)
draw_moisture.gh_uv_wvfl(model='GRAPES_GFS')
draw_moisture.gh_uv_rh(model='ECMWF',data_source='CIMISS',map_ratio=12/10)
draw_moisture.gh_uv_pwat(model='ECMWF',data_source='CIMISS',map_ratio=12/10)

###############################-重新梳理

draw_sta.point_fcst_according_to_3D_field(
        model='ECMWF',t_range=[0,240],
        output_dir='L:/py_develop/temperary_job/Olympic/V5/时序图/',
        points={'lon':[115.813611], 'lat':[40.558611],'altitude':[2194]},
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':'竞速1',
            'drw_thr':True,
            'levels_for_interp':[1000, 950, 925, 900, 850, 800, 700, 600, 500]}
            )

draw_sta.point_wind_time_fcst_according_to_3D_wind(
        model='GRAPES_GFS',t_range=[0,48],
        output_dir='L:/py_develop/temperary_job/Olympic/V5/时序图/',
        points={'lon':[115.813611], 'lat':[40.558611],'altitude':[2194]},
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':'竞速1',
            'drw_thr':True,
            'levels_for_interp':[1000, 950, 925, 900, 850, 800, 700, 600, 500]}
            )

draw_sta.point_uv_tmp_rh_rn_fcst(
        model='中央气象台中短期指导',
        t_range=[24,84],
        t_gap=3,
        points={'lon':[113.636912], 'lat':[35.74677]},
        initTime=None,day_back=0,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':'demo'}
            )
