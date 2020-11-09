import nmc_met_map.sta as draw_sta

output_dir='L:/RoutineJob/20200109/'

extra_info={
    'output_head_name':'SEVP_NMC_NWPR_SMMEF_EME_A1708_LNO_P9_',
    'output_tail_name':'24006',
    'point_name':'A1708'}
draw_sta.Station_Synthetical_Forecast_From_Cassandra(
    model='中央台指导',
    points={'lon':[115.797778], 'lat':[40.541111]},
    t_range=[5,80],
    drw_thr=False,
    output_dir=output_dir,extra_info=extra_info
    ) 

extra_info={
    'output_head_name':'SEVP_NMC_NWPR_SMMEF_EME_A1701_LNO_P9_',
    'output_tail_name':'24006',
    'point_name':'A1701'}
draw_sta.Station_Synthetical_Forecast_From_Cassandra(
    model='中央台指导',
    points={'lon':[115.813611], 'lat':[40.558611]},
    t_range=[5,80],
    drw_thr=False,
    output_dir=output_dir,extra_info=extra_info
    )    

extra_info={
    'output_head_name':'SEVP_NMC_NWPR_SMMEF_ESNOW_A1701_LNO_P9_',
    'output_tail_name':'24006',
    'point_name':'A1701'}


draw_sta.Station_Snow_Synthetical_Forecast_From_Cassandra(
    model='中央台指导',
    points={'lon':[115.813611], 'lat':[40.558611]},
    t_range=[5,80],
    drw_thr=False,
    output_dir=output_dir,
    extra_info=extra_info
    )



extra_info={
    'output_head_name':'SEVP_NMC_NWPR_SMMEF_ESNOW_A1708_LNO_P9_',
    'output_tail_name':'24006',
    'point_name':'A1708'}

draw_sta.Station_Snow_Synthetical_Forecast_From_Cassandra(
    model='中央台指导',
    points={'lon':[115.797778], 'lat':[40.541111]},
    t_range=[5,80],
    drw_thr=False,
    output_dir=output_dir,
    extra_info=extra_info
    )


