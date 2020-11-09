import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math
import os
import xarray as xr
import metpy.calc as mpcalc
from metpy.units import units
from nmc_met_io.retrieve_micaps_server import get_model_points,get_model_3D_grid,get_latest_initTime,get_model_3D_grids,get_station_data,get_model_grids
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_map.lib.utility as utl
from nmc_met_map.graphics import sta_graphics
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, SkewT
from metpy.units import units
from scipy.stats import norm
from scipy.interpolate import LinearNDInterpolator

def point_fcst_uv_tmp_according_to_3D_field_vs_sounding(
        output_dir=None,
        obs_ID='55664',
        initTime=None,fhour=0,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':' ',
            'drw_thr':True,
            'levels_for_interp':[1000, 950, 925, 900, 850, 800, 700, 600, 500,400,300,250,200,150]}
            ):
            
    model='ECMWF'
    try:
        dir_rqd=[utl.Cassandra_dir(data_type='high',data_source='OBS',var_name='TLOGP',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl='')]
    except KeyError:
        raise ValueError('Can not find all required directories needed')
    
    if(initTime == None):
        initTime = get_latest_initTime(dir_rqd[1][0:-1]+'/850')
    
    filename_obs=(datetime.strptime('20'+initTime,'%Y%m%d%H')+timedelta(hours=fhour)).strftime('%Y%m%d%H%M%S')+'.000'
    obs_pfl_all=MICAPS_IO.get_tlogp(dir_rqd[0][0:-1], filename=filename_obs, cache=False)
    if(obs_pfl_all is None):
        return
    obs_pfl_raw=obs_pfl_all[obs_pfl_all.ID == obs_ID]
    obs_pfl=obs_pfl_raw.replace(9999.0, np.nan).dropna(how='any')
    obs_pfl=obs_pfl[obs_pfl.p >= 200.]

    directory=dir_rqd[1][0:-1]
    filename = initTime+'.'+str(fhour).zfill(3)
    HGT_4D=get_model_3D_grid(directory=directory,filename=filename,levels=extra_info['levels_for_interp'], allExists=False)
    directory=dir_rqd[2][0:-1]
    U_4D=get_model_3D_grid(directory=directory,filename=filename,levels=extra_info['levels_for_interp'], allExists=False)
    directory=dir_rqd[3][0:-1]
    V_4D=get_model_3D_grid(directory=directory,filename=filename,levels=extra_info['levels_for_interp'], allExists=False)

    directory=dir_rqd[4][0:-1]
    TMP_4D=get_model_3D_grid(directory=directory,filename=filename,levels=extra_info['levels_for_interp'], allExists=False)
    
    points={'lon':obs_pfl.lon.to_numpy(), 'lat':obs_pfl.lat.to_numpy(),'altitude':obs_pfl.h.to_numpy()*10}

    directory=dir_rqd[4][0:-1]

    delt_xy=HGT_4D['lon'].values[1]-HGT_4D['lon'].values[0]
    mask = (HGT_4D['lon']<(points['lon'][0]+2*delt_xy))&(HGT_4D['lon']>(points['lon'][0]-2*delt_xy))&(HGT_4D['lat']<(points['lat'][0]+2*delt_xy))&(HGT_4D['lat']>(points['lat'][0]-2*delt_xy))

    HGT_4D_sm=HGT_4D['data'].where(mask,drop=True)
    U_4D_sm=U_4D['data'].where(mask,drop=True)
    V_4D_sm=V_4D['data'].where(mask,drop=True)
    TMP_4D_sm=TMP_4D['data'].where(mask,drop=True)

    lon_md=np.squeeze(HGT_4D_sm['lon'].values)
    lat_md=np.squeeze(HGT_4D_sm['lat'].values)
    alt_md=np.squeeze(HGT_4D_sm.values*10).flatten()
    time_md=HGT_4D_sm['forecast_period'].values

    coords = np.zeros((len(extra_info['levels_for_interp']),len(lat_md),len(lon_md),3))
    coords[...,1] = lat_md.reshape((1,len(lat_md),1))
    coords[...,2] = lon_md.reshape((1,1,len(lon_md)))
    coords = coords.reshape((alt_md.size,3))
    coords[:,0]=alt_md

    interpolator_U = LinearNDInterpolator(coords,U_4D_sm.values.reshape((U_4D_sm.values.size)),rescale=True)
    interpolator_V = LinearNDInterpolator(coords,V_4D_sm.values.reshape((V_4D_sm.values.size)),rescale=True)
    interpolator_TMP = LinearNDInterpolator(coords,TMP_4D_sm.values.reshape((TMP_4D_sm.values.size)),rescale=True)

    coords2=np.zeros((np.size(points['lon']),3))
    coords2[:,0]=points['altitude']
    coords2[:,1]=points['lat']
    coords2[:,2]=points['lon']

    U_interped=np.squeeze(interpolator_U(coords2))
    V_interped=np.squeeze(interpolator_V(coords2))
    windsp_interped=(U_interped**2+V_interped**2)**0.5
    winddir10m_interped=mpcalc.wind_direction(U_interped* units('m/s'),V_interped* units('m/s'))
    TMP_interped=np.squeeze(interpolator_TMP(coords2))

    fcst_pfl=obs_pfl.copy()
    fcst_pfl.wind_angle=np.array(winddir10m_interped)
    fcst_pfl.wind_speed=np.array(windsp_interped)
    fcst_pfl.t=TMP_interped

    fcst_info= xr.DataArray(np.array(U_4D_sm.values),
                        coords=U_4D_sm.coords,
                        dims=U_4D_sm.dims,
                        attrs={'points': points,
                                'model': model})
                                
    sta_graphics.draw_sta_skewT_model_VS_obs(fcst_pfl=fcst_pfl,obs_pfl=obs_pfl,
            fcst_info=fcst_info,
            output_dir=output_dir)


