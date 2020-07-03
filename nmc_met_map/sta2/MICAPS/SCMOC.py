import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math
import os
import xarray as xr
import metpy.calc as mpcalc
from metpy.units import units
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_map.lib.utility as utl
from nmc_met_map.graphics import sta_graphics
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, SkewT
from metpy.units import units
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
from scipy.stats import genextreme as gev


def point_uv_gust_tmp_rh_rn_fcst(
        output_dir=None,
        t_range=[0,60],
        t_gap=3,
        points={'lon':[116.3833], 'lat':[39.9], 'altitude':[1351]},
        initTime=None,day_back=0,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':' '}
            ):

    #+get all the directories needed
    try:
        dir_rqd=[utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='T2m'),
                        utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='u10m'),
                        utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='v10m'),
                        utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='rh2m'),
                        utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='RAIN'+str(t_gap).zfill(2)),
                        utl.Cassandra_dir(data_type='surface',data_source='OBS',var_name='PLOT_GUST')]
    except KeyError:
        raise ValueError('Can not find all required directories needed')

    #-get all the directories needed
    if(initTime == None):
        initTime = MICAPS_IO.get_latest_initTime(dir_rqd[0])
        #initTime=utl.filename_day_back_model(day_back=day_back,fhour=0)[0:8]

    gust_sta=MICAPS_IO.get_station_data(directory=dir_rqd[5],dropna=True, cache=False)
    datetime_sta=pd.to_datetime(str(gust_sta.time[0])).replace(tzinfo=None).to_pydatetime()
    datetime_model_initTime=datetime.strptime('20'+initTime,'%Y%m%d%H')


    u10_his_md = []
    v10_his_md = []
    wsp_his_sta_point= []

    model_filenames_his=None
    for iinit in range(0,240,12):
        for ifhour in range(0, 87, 3):
            for iobs in range(0,168,1):
                initTime_his=datetime_model_initTime-timedelta(hours=iinit)
                validTime_his=initTime_his+timedelta(hours=ifhour)
                staTime_his=datetime_sta-timedelta(hours=iobs)
                if(staTime_his==validTime_his):
                    model_filename_his=initTime_his.strftime('%Y%m%d%H')[2:10]+'.'+str(ifhour).zfill(3)
                    sta_filename_his=validTime_his.strftime('%Y%m%d%H')+'0000.000'
                    data_md1 = MICAPS_IO.get_model_grid(dir_rqd[1], filename=model_filename_his)
                    if(data_md1 is None):
                        continue
                    data_md2 = MICAPS_IO.get_model_grid(dir_rqd[1], filename=model_filename_his)
                    if(data_md2 is None):
                        continue
                    data_sta = MICAPS_IO.get_station_data(directory=dir_rqd[5],filename=sta_filename_his,dropna=True, cache=True)
                    if(data_sta is None):
                        continue
                    u10_his_md.append(data_md1)
                    v10_his_md.append(data_md2)
                    wsp_his_sta_interp=utl.sta_to_point_interpolation(points=points,sta=data_sta,var_name='Gust_speed')
                    wsp_his_sta_point.append(wsp_his_sta_interp[:])

    u10_his_md=xr.concat(u10_his_md, dim='time')
    v10_his_md=xr.concat(v10_his_md, dim='time')
    wsp_his_md=(u10_his_md**2+v10_his_md**2)**0.5
    wsp_his_md_point=wsp_his_md.interp(lon=('points', points['lon']), lat=('points', points['lat']))

    model = LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)
    x=np.squeeze(wsp_his_md_point['data'].values).reshape(-1, 1)
    y=np.squeeze(wsp_his_sta_point).reshape(-1, 1)
    model.fit(x, y) 
    if(model.coef_ < 0.2):
        f2=np.polyfit(np.squeeze(x),np.squeeze(y), 2)
        model2=np.poly1d(f2)

    fhours = np.arange(t_range[0], t_range[1], t_gap)
    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    t2m=utl.get_model_points_gy(dir_rqd[0], filenames, points,allExists=False)
    u10m=utl.get_model_points_gy(dir_rqd[1], filenames, points,allExists=False)
    v10m=utl.get_model_points_gy(dir_rqd[2], filenames, points,allExists=False)
    rh=utl.get_model_points_gy(dir_rqd[3], filenames, points,allExists=False)
    rn=utl.get_model_points_gy(dir_rqd[4], filenames, points,allExists=False)

    gust10m_predict=u10m.copy()
    if(model.coef_ > 0.2):
        gust10m_predict['data'].values=np.squeeze(model.predict(np.squeeze((u10m['data'].values**2+v10m['data'].values**2)**0.5).reshape(-1,1))).reshape(-1,1,1)
    else:
        gust10m_predict['data'].values=np.squeeze(model2(np.squeeze((u10m['data'].values**2+v10m['data'].values**2)**0.5))).reshape(-1,1,1)

    sta_graphics.draw_point_uv_tmp_rh_rn_gust_fcst(t2m=t2m,u10m=u10m,v10m=v10m,rh=rh,rn=rn,gust=gust10m_predict,
        model='中央气象台中短期指导',
        output_dir=output_dir,
        points=points,
        extra_info=extra_info
            )

def point_uv_ecgust_tmp_rh_rn_fcst(
        output_dir=None,
        t_range=[0,60],
        t_gap=3,
        points={'lon':[116.3833], 'lat':[39.9], 'altitude':[1351]},
        initTime=None,day_back=0,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':' '}
            ):

    #+get all the directories needed
    try:
        dir_rqd=[utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='T2m'),
                        utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='u10m'),
                        utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='v10m'),
                        utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='rh2m'),
                        utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='RAIN'+str(t_gap).zfill(2)),
                        utl.Cassandra_dir(data_type='surface',data_source='ECMWF',var_name='10M_GUST_3H')]
    except KeyError:
        raise ValueError('Can not find all required directories needed')

    #-get all the directories needed
    if(initTime == None):
        initTime = MICAPS_IO.get_latest_initTime(dir_rqd[0])
        initTime2 = MICAPS_IO.get_latest_initTime(dir_rqd[-1])
        #initTime=utl.filename_day_back_model(day_back=day_back,fhour=0)[0:8]

    fhours = np.arange(t_range[0], t_range[1], t_gap)
    fhours2 = np.arange(t_range[0], t_range[1]+12, t_gap)
    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    filenames2 = [initTime2+'.'+str(fhour).zfill(3) for fhour in fhours2]
    t2m=utl.get_model_points_gy(dir_rqd[0], filenames, points,allExists=False)
    u10m=utl.get_model_points_gy(dir_rqd[1], filenames, points,allExists=False)
    v10m=utl.get_model_points_gy(dir_rqd[2], filenames, points,allExists=False)
    rh=utl.get_model_points_gy(dir_rqd[3], filenames, points,allExists=False)
    rn=utl.get_model_points_gy(dir_rqd[4], filenames, points,allExists=False)
    gust=utl.get_model_points_gy(dir_rqd[5], filenames2, points,allExists=False)

    sta_graphics.draw_point_uv_tmp_rh_rn_gust_fcst(t2m=t2m,u10m=u10m,v10m=v10m,rh=rh,rn=rn,gust=gust,
        model='中央气象台中短期指导',
        output_dir=output_dir,
        points=points,
        extra_info=extra_info
            )