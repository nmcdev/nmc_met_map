import nmc_met_map.sta2 as draw_sta2
import nmc_met_map.sta as draw_sta

sta_all={'lon':[114.104],
       'lat':[22.550],
       'altitude':[1,1,1,1,1,1.5,1,1,1,1,1,1,1,1,1,1,1,1],
       'ID':['51463'],
       'name':['深圳']}

for ista in range(0,len(sta_all['name'])):
    draw_sta.point_fcst_ecgust(
            model='中央气象台中短期指导',
            output_dir='L:/RoutineJob/20201012/',
            t_range=[0,84],
            t_gap=3,
            points={'lon':[sta_all['lon'][ista]], 'lat':[sta_all['lat'][ista]]},
            initTime=None,day_back=0,
            extra_info={
                'output_head_name':' ',
                'output_tail_name':' ',
                'point_name':sta_all['name'][ista]}
                )

extra_info={
    'output_head_name':'SEVP_NMC_RFFC_SCMOC_EME_A01_LNO_P9_',
    'output_tail_name':'24003',
    'point_name':'纪念馆'}
    
draw_sta.Station_Synthetical_Forecast_From_Cassandra(
    model='中央气象台中短期指导',
    points={'lon':[116.225], 'lat':[39.8522]},
    t_range=[0,240],
    drw_thr=False,
    extra_info=extra_info
    )

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

draw_sta.point_fcst_according_to_3D_field_VS_zd_plot(initTime='20052408',
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

sta_all={'lon':[86.92528],
        'lat':[27.98805],
        'altitude':[8848],
        'ID':['A01'],
        'name':['珠峰']}

draw_sta2.MICAPS.ECMWF_ENSEMBLE.point_fcst_wsp_according_to_3D_field_box_line(
            initTime='20052120',
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

draw_sta2.MICAPS.ECMWF_ENSEMBLE.point_fcst_rn_according_to_3D_field_box_line(
            initTime='20052120',
            t_range=[0,241],
            t_gap=6,
            points=sta_all,
            extra_info={
                'output_head_name':' ',
                'output_tail_name':' ',
                'point_name':' ',
                'drw_thr':True}
            )

draw_sta2.MICAPS.ECMWF_ENSEMBLE.point_fcst_tmp_according_to_3D_field_box_line(
            initTime='20052120',
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

draw_sta.sta_SkewT()

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

draw_sta.point_fcst(
        model='中央台指导',
        output_dir='L:/py_develop/temperary_job/春节会商/',
        t_range=[0,36],
        t_gap=3,
        points={'lon':[126.567], 'lat':[45.933]},
        initTime='20011920',day_back=0,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':'哈尔滨'}
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