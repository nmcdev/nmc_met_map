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
import nmc_met_map.coldwave as draw_coldwave
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
from  datetime import datetime,timedelta
import nmc_met_map.lib.utility as utl
import nmc_met_io.retrieve_cmadaas as cmadaas_IO


draw_elements.T2m_mn24(initTime='21011208',fhour=290,area='全国',south_China_sea=True,
                        model='中央气象台智能网格延伸期预报',data_source ='MICAPS',city=True)
draw_QPF.gh_rain(atime=24)

test=cmadaas_IO.cmadass_get_model_latest_time(data_code="NAFP_ECMF_FTM_HIGH_ANEA_FOR", latestTime=24)
draw_thermal.gh_uv_tadv(initTime='20010808',data_source='CIMISS',uv_lev=500,model='GRAPES_GFS',fhour=42)
draw_moisture.gh_uv_wvfl(initTime='20010108',model='GRAPES_GFS',data_source='CIMISS')
sta_all={'lon':[86.92528],
        'lat':[27.98805],
        'altitude':[8848],
        'ID':['A01'],
        'name':['珠峰']}

draw_sta2.MICAPS.ECMWF_ENSEMBLE.point_fcst_tmp_according_to_3D_field_box_line(
            initTime='21010520',
            t_range=[0,36],
            t_gap=6,
            points=sta_all,
            extra_info={
                'output_head_name':' ',
                'output_tail_name':' ',
                'point_name':sta_all['name'][0],
                'drw_thr':False,
                'levels_for_interp':[700, 500,300,200]}
                )


draw_coldwave.tmp_evo(data_source='MICAPS',t_range=[6,72],thr=-4,area='江南')

draw_elements.T2m_mn24(initTime='20111608',fhour=24,area='全国',map_ratio=10/9,
                        model='中央气象台智能网格',data_source ='MICAPS',city=True)

draw_elements.mean24_rh2m_wind10m()
draw_elements.T2m_zero_heatwaves(model='中央气象台中短期指导',city=True)

draw_elements.mslp_gust10m_uv10m()

draw_dynamic.fg_uv_tmp(model='GRAPES_GFS',fhour=24,city=True,area='华北',fg_lev=500)

draw_crossection.Crosssection_Wind_Theta_e_mpv(model='GRAPES_GFS',fhour=60,lw_ratio=[16,9],
    st_point=[43.5,111.5], ed_point=[33,125.0],data_source='CIMISS')

output_dir='L:/RoutineJob/20201204/'

sta_all={'lon':[105.950349],
       'lat':[29.444548],
       'altitude':[1],
       'ID':['永川吊水洞煤矿'],
       'name':['永川吊水洞煤矿']}


for ista in range(0,len(sta_all['name'])):

    extra_info={
        'output_head_name':'SEVP_NMC_RFFC_SCMOC_EME_'+sta_all['ID'][ista]+'_LNO_P9_',
        'output_tail_name':'02403',
        'point_name':sta_all['name'][ista]}
    draw_sta.point_fcst(
            model='中央气象台滚动更新',
            output_dir=output_dir,
            t_range=[0,84],
            t_gap=1,
            points={'lon':[sta_all['lon'][ista]], 'lat':[sta_all['lat'][ista]]},
            initTime=None,
            extra_info=extra_info
                )

initTimes=[]
for ihour in range(0,168,6):
    initTimes.append((datetime(2020,7,4,8)+timedelta(hours=ihour)).strftime('%y%m%d%H'))

map_extent=[70,135,15,60]
cntr_pnt,zoom_ratio,map_ratio=utl.map_extent_to_cntr_pnt_zoom_ratio_map_ratio(map_extent)

draw_synoptic.periodmean_gh_uv_pwat_ulj(initTimes,model='GRAPES_GFS',fhours=[3],data_source='CIMISS',output_dir='./temp/',
                                        cntr_pnt=cntr_pnt,zoom_ratio=zoom_ratio,map_ratio=map_ratio)

draw_moisture.gh_uv_pwat(model='GRAPES_GFS',data_source='CIMISS',fhour=3,map_ratio=12/10)

draw_crossection.Crosssection_Wind_Temp_RH(model='ECMWF',fhour=60,lw_ratio=[16,9],
    st_point=[43.5,111.5], ed_point=[33,125.0])

draw_observation2.MICAPS.CLDAS.cu_rain(initTime='20112008',atime=96,area='东北',data_source ='CIMISS')

draw_elements.T2m_mean24(return_data=True)

draw_synoptic.gh500_anomaly_uv(initTime='20111708',fhour=0,cntr_pnt=[120,41],zoom_ratio=14,data_source='CIMISS')

draw_thermal.TMP850_anomaly_uv(initTime='20111708',fhour=0,cntr_pnt=[120,41],zoom_ratio=14,data_source='CIMISS')

draw_observation2.MICAPS.CLDAS.cu_rain(initTime='20111908',atime=72,cntr_pnt=[121.2,40],zoom_ratio=14)

draw_crossection.Crosssection_Wind_Theta_e_absv(model='GRAPES_GFS',fhour=24,
                                               lw_ratio=[12,9],
                                                st_point=[28,107.0], ed_point=[33,120.0],
                                               levels=[1000, 950, 925, 900, 850, 800, 700,600,500])

draw_dynamic.gh_uv_VVEL(model='GRAPES_GFS',fhour=3,initTime='20090308',area='东北',data_source='CIMISS')

draw_synoptic.gh_uv_wsp(model='GRAPES_GFS',initTime='20090314',fhour=0,area='东北',data_source='CIMISS')

draw_observation.IR_Sounding_GeopotentialHeight(Sounding_time='20111708',
    HGT_initTime='20111708',IR_time='20111708',fhour=12,zoom_ratio=20,map_ratio=4/3,
    south_China_sea=True,Channel='C009')

draw_QPF.cumulated_precip(initTime='20111708',t_range=[6,72],model='GRAPES_GFS')

draw_thermal.gh_uv_tmp(model='GRAPES_GFS')

draw_elements2.MICAPS.SCMOC.dT2m_mx24(fhour=24,output_dir='L:/py_develop/test_output/20201107/')

draw_crossection.Crosssection_Wind_Theta_e_div(initTime='20111708',fhour=36,st_point=[124.4,37.0],ed_point=[123,43])

draw_moisture.gh_uv_rh()

draw_observation.CREF_Sounding_GeopotentialHeight(CREF_time='20111808',
    HGT_initTime='20111720',Sounding_time='20111808',fhour=12,zoom_ratio=20,map_ratio=4/3,area='全国')



draw_dynamic.gh_uv_div(model='ECMWF',data_source='CIMISS',uv_lev=700)

draw_crossection.Crosssection_Wind_Theta_e_div(model='GRAPES_GFS',fhour=24,
                                               lw_ratio=[12,9],
                                                st_point=[28,107.0], ed_point=[33,120.0],
                                               levels=[1000, 950, 925, 900, 850, 800, 700,600,500])

draw_thermal.gh_uv_thetae(model='GRAPES_GFS',data_source='CIMISS',map_ratio=4/3)

draw_synoptic.gh_uv_r6(initTime='20062620',model='ECMWF',data_source='CIMISS',fhour=12)

draw_moisture.gh_uv_spfh(model='ECMWF')

draw_crossection.Crosssection_Wind_Theta_e_Qv(model='GRAPES_GFS',day_back=1,lw_ratio=[25,9],data_source='CIMISS')

draw_crossection.Crosssection_Wind_Theta_e_RH(model='GRAPES_GFS',data_source='CIMISS')

draw_crossection.Time_Crossection_rh_uv_theta_e(t_range=[0,108],points={'lon': [100.0],'lat': [39.9]},levels=[1000,950,925,900,850,800,700,600,500])

draw_crossection.Time_Crossection_rh_uv_Temp(model='GRAPES_GFS',points={'lon':[100], 'lat':[39.9]},t_range=[0,84],levels=[1000,950,925,900,850,800,700,600,500],lw_ratio=[16,9])

draw_crossection.Time_Crossection_rh_uv_t()

draw_synoptic.gh_uv_mslp(model='GRAPES_GFS',city=False,area='全国',fhour=24,map_ratio=12/9,
                        data_source='CIMISS')

draw_syn_ver_ana.compare_vs_ana.compare_gh_uv(fhour=72,city=True,data_source='CIMISS')

#-增加地形影响
Tmean_2m=draw_elements.T2m_mean24(model='中央气象台智能网格',data_source ='MICAPS',city=True,return_data=True)

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

for ihour in [18,24,30,36]:
    draw_elements.mslp_gust10m_uv10m(model='ECMWF',city=False,area='全国',t_gap=6,fhour=ihour,map_ratio=12/9,
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

draw_synoptic.PV_Div_uv(fhour=3,data_source='CIMISS',area='东北',city=True)

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

draw_isentropic.isentropic_uv(initTime='20081220',fhour=0,map_ratio=12/9,area='华北',isentlev=360,city=True)

draw_observation2.MICAPS.CLDAS.Tmx2m24(
    endtime='20072908', cu_ndays=7,area='全国',
    south_China_sea=True,city=True)

draw_observation2.MICAPS.CLDAS.cumulative_precip_and_rain_days(
    endtime='20072308', cu_ndays=7, rn_ndays=7,area='全国',
    south_China_sea=True,city=False)

draw_elements.mslp_gust10m_uv10m(model='ECMWF',area='全国',data_source='CIMISS',t_gap=6)

###############################+重新梳理'

draw_QPF.Rain_evo(initTime='20051908',data_source='CIMISS',t_range=[6,36],area='江南',fcs_lvl=13,t_gap=6,map_ratio=16/9)#加等值线、白边突显、固定4个时次

draw_elements.T2m_mslp_uv10m(model='ECMWF',data_source='CIMISS')

draw_elements2.MICAPS.ECMWF.dT2m_mean24(city=True,fhour=60)
draw_elements2.MICAPS.ECMWF.dT2m_mn24(city=True,fhour=33)
draw_elements2.MICAPS.ECMWF.dT2m_mx24(city=True,fhour=60)

draw_synthetical.Miller_Composite_Chart(map_ratio=8/5)
draw_elements.low_level_wind(model='ECMWF',day_back=1,data_source='CIMISS')
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
