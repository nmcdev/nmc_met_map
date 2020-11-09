import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math
import os
import xarray as xr
import metpy.calc as mpcalc
from metpy.units import units
from nmc_met_io.retrieve_micaps_server import get_model_points,get_model_3D_grid,get_latest_initTime,get_model_3D_grids,get_station_data,get_model_grids
import nmc_met_map.lib.utility as utl
from nmc_met_map.graphics import Ensemble_graphics
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, SkewT
from metpy.units import units
from scipy.stats import norm
from scipy.interpolate import LinearNDInterpolator

def point_fcst_tmp_according_to_3D_field_box_line(
        output_dir=None,
        t_range=[0,60],
        t_gap=3,
        points={'lon':[116.3833], 'lat':[39.9], 'altitude':[1351]},
        initTime=None,obs_ID=54511,day_back=0,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':' ',
            'drw_thr':True,
            'levels_for_interp':[1000, 925, 850, 700, 500,300,200]}
            ):

    try:
        dir_rqd=[utl.Cassandra_dir(data_type='high',data_source='ECMWF_ENSEMBLE',var_name='HGT_RAW',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source='ECMWF_ENSEMBLE',var_name='TMP_RAW',lvl='')]
                        #utl.Cassandra_dir(data_type='surface',data_source=model,var_name='RAIN'+str(t_gap).zfill(2)+'_RAW')]
    except KeyError:
        raise ValueError('Can not find all required directories needed')
    
    #-get all the directories needed
    if(initTime == None):
        initTime = get_latest_initTime(dir_rqd[0][0:-1]+'/850')
        #initTime=utl.filename_day_back_model(day_back=day_back,fhour=0)[0:8]

    directory=dir_rqd[0][0:-1]

    if(t_range[1] > 72):
        fhours = np.append(np.arange(t_range[0], 72, t_gap),np.arange(72,t_range[1],6))
    else:
        fhours = np.arange(t_range[0], t_range[1], t_gap)

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    HGT_4D=get_model_3D_grids(directory=directory,filenames=filenames,levels=extra_info['levels_for_interp'], allExists=False)
    directory=dir_rqd[0][0:-1]

    directory=dir_rqd[1][0:-1]
    TMP_4D=get_model_3D_grids(directory=directory,filenames=filenames,levels=extra_info['levels_for_interp'], allExists=False)
    
    #rn=utl.get_model_points_gy(dir_rqd[4], filenames, points,allExists=False)

    directory=dir_rqd[1][0:-1]
    coords_info_2D=utl.get_model_points_gy(directory+str(extra_info['levels_for_interp'][0])+'/',
                        points=points,filenames=filenames,allExists=False)

    delt_xy=HGT_4D['lon'].values[1]-HGT_4D['lon'].values[0]
    mask = (HGT_4D['lon']<(points['lon']+2*delt_xy))&(HGT_4D['lon']>(points['lon']-2*delt_xy))&(HGT_4D['lat']<(points['lat']+2*delt_xy))&(HGT_4D['lat']>(points['lat']-2*delt_xy))

    HGT_4D_sm=HGT_4D['data'].where(mask,drop=True)
    TMP_4D_sm=TMP_4D['data'].where(mask,drop=True)

    lon_md=np.squeeze(HGT_4D_sm['lon'].values)
    lat_md=np.squeeze(HGT_4D_sm['lat'].values)
    alt_md=np.squeeze(HGT_4D_sm.values*10).flatten()
    time_md=np.squeeze(HGT_4D_sm['forecast_period'].values)
    number_md=np.squeeze(HGT_4D_sm['number'].values)
    '''
    coords = np.zeros((len(time_md),len(number_md),len(extra_info['levels_for_interp']),len(lat_md),len(lon_md),5))
    coords[...,0]=time_md.reshape((len(time_md),1,1,1,1))
    coords[...,1]=number_md.reshape((1,len(number_md),1,1,1))
    coords[...,3] = lat_md.reshape((1,1,1,len(lat_md),1))
    coords[...,4] = lon_md.reshape((1,1,1,1,len(lon_md)))
    coords = coords.reshape((alt_md.size,5))
    coords[:,2]=alt_md

    interpolator_TMP = LinearNDInterpolator(coords,TMP_4D_sm.values.reshape((TMP_4D_sm.values.size)),rescale=True)
    
    coords2 = np.zeros((len(time_md),len(number_md),1,1,1,5))
    coords2[...,0]=time_md.reshape((len(time_md),1,1,1,1))
    coords2[...,1]=number_md.reshape(1,(len(number_md),1,1,1))
    coords2[...,2]=points['altitude'][0]
    coords2[...,3] = points['lat'][0]
    coords2[...,4] = points['lon'][0]
    coords2 = coords2.reshape((time_md.size,5))

    TMP_interped=np.squeeze(interpolator_TMP(coords2))
    '''
    TMP_interped=np.zeros((len(time_md),len(number_md)))

    for it in range(0,len(time_md)):
        for inum in range(0,len(number_md)):
            alt_md=np.squeeze(HGT_4D_sm.values[it,inum,:,:,:]*10).flatten()
            coords = np.zeros((len(extra_info['levels_for_interp']),len(lat_md),len(lon_md),3))
            coords[...,1] = lat_md.reshape((1,len(lat_md),1))
            coords[...,2] = lon_md.reshape((1,1,len(lon_md)))
            coords = coords.reshape((alt_md.size,3))
            coords[:,0]=alt_md
            interpolator_TMP = LinearNDInterpolator(coords,TMP_4D_sm.values[it,inum,:,:,:].reshape((TMP_4D_sm.values[it,inum,:,:,:].size)),rescale=True)

            coords2 = np.zeros((1,1,1,3))
            coords2[...,0]=points['altitude'][0]
            coords2[...,1] = points['lat'][0]
            coords2[...,2] = points['lon'][0]
            coords2 = coords2.reshape((1,3))

            TMP_interped[it,inum]=np.squeeze(interpolator_TMP(coords2))

    TMP_interped_xr=coords_info_2D.copy()
    TMP_interped_xr['data'].values[:,:,0,0]=TMP_interped
    TMP_interped_xr.attrs['model']='ECMWF_ENSEMBLE'

    Ensemble_graphics.box_line_temp(TMP=TMP_interped_xr,
        points=points,
        extra_info=extra_info,output_dir=output_dir)  

def point_fcst_wsp_according_to_3D_field_box_line(
        output_dir=None,
        t_range=[0,60],
        t_gap=3,
        points={'lon':[116.3833], 'lat':[39.9], 'altitude':[1351]},
        initTime=None,obs_ID=54511,day_back=0,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':' ',
            'drw_thr':True,
            'levels_for_interp':[1000, 925, 850, 700, 500,300,200]}
            ):

    try:
        dir_rqd=[utl.Cassandra_dir(data_type='high',data_source='ECMWF_ENSEMBLE',var_name='HGT_RAW',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source='ECMWF_ENSEMBLE',var_name='UGRD_RAW',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source='ECMWF_ENSEMBLE',var_name='VGRD_RAW',lvl='')]
                        #utl.Cassandra_dir(data_type='surface',data_source=model,var_name='RAIN'+str(t_gap).zfill(2)+'_RAW')]
    except KeyError:
        raise ValueError('Can not find all required directories needed')
    
    #-get all the directories needed
    if(initTime == None):
        initTime = get_latest_initTime(dir_rqd[0][0:-1]+'/850')
        #initTime=utl.filename_day_back_model(day_back=day_back,fhour=0)[0:8]

    directory=dir_rqd[0][0:-1]

    if(t_range[1] > 72):
        fhours = np.append(np.arange(t_range[0], 72, t_gap),np.arange(72,t_range[1],6))
    else:
        fhours = np.arange(t_range[0], t_range[1], t_gap)

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    HGT_4D=get_model_3D_grids(directory=directory,filenames=filenames,levels=extra_info['levels_for_interp'], allExists=False)
    directory=dir_rqd[0][0:-1]

    directory=dir_rqd[1][0:-1]
    UGRD_4D=get_model_3D_grids(directory=directory,filenames=filenames,levels=extra_info['levels_for_interp'], allExists=False)
    directory=dir_rqd[2][0:-1]
    VGRD_4D=get_model_3D_grids(directory=directory,filenames=filenames,levels=extra_info['levels_for_interp'], allExists=False)
    WSP_4D=UGRD_4D.copy()
    WSP_4D['data'].values=(UGRD_4D['data'].values**2+VGRD_4D['data'].values**2)**0.5
    
    #rn=utl.get_model_points_gy(dir_rqd[4], filenames, points,allExists=False)

    directory=dir_rqd[1][0:-1]
    coords_info_2D=utl.get_model_points_gy(directory+str(extra_info['levels_for_interp'][0])+'/',
                        points=points,filenames=filenames,allExists=False)

    delt_xy=HGT_4D['lon'].values[1]-HGT_4D['lon'].values[0]
    mask = (HGT_4D['lon']<(points['lon']+2*delt_xy))&(HGT_4D['lon']>(points['lon']-2*delt_xy))&(HGT_4D['lat']<(points['lat']+2*delt_xy))&(HGT_4D['lat']>(points['lat']-2*delt_xy))

    HGT_4D_sm=HGT_4D['data'].where(mask,drop=True)
    WSP_4D_sm=WSP_4D['data'].where(mask,drop=True)

    lon_md=np.squeeze(HGT_4D_sm['lon'].values)
    lat_md=np.squeeze(HGT_4D_sm['lat'].values)
    alt_md=np.squeeze(HGT_4D_sm.values*10).flatten()
    time_md=np.squeeze(HGT_4D_sm['forecast_period'].values)
    number_md=np.squeeze(HGT_4D_sm['number'].values)
    '''
    coords = np.zeros((len(time_md),len(number_md),len(extra_info['levels_for_interp']),len(lat_md),len(lon_md),5))
    coords[...,0]=time_md.reshape((len(time_md),1,1,1,1))
    coords[...,1]=number_md.reshape((1,len(number_md),1,1,1))
    coords[...,3] = lat_md.reshape((1,1,1,len(lat_md),1))
    coords[...,4] = lon_md.reshape((1,1,1,1,len(lon_md)))
    coords = coords.reshape((alt_md.size,5))
    coords[:,2]=alt_md

    interpolator_TMP = LinearNDInterpolator(coords,TMP_4D_sm.values.reshape((TMP_4D_sm.values.size)),rescale=True)
    
    coords2 = np.zeros((len(time_md),len(number_md),1,1,1,5))
    coords2[...,0]=time_md.reshape((len(time_md),1,1,1,1))
    coords2[...,1]=number_md.reshape(1,(len(number_md),1,1,1))
    coords2[...,2]=points['altitude'][0]
    coords2[...,3] = points['lat'][0]
    coords2[...,4] = points['lon'][0]
    coords2 = coords2.reshape((time_md.size,5))

    TMP_interped=np.squeeze(interpolator_TMP(coords2))
    '''
    WSP_interped=np.zeros((len(time_md),len(number_md)))

    for it in range(0,len(time_md)):
        for inum in range(0,len(number_md)):
            alt_md=np.squeeze(HGT_4D_sm.values[it,inum,:,:,:]*10).flatten()
            coords = np.zeros((len(extra_info['levels_for_interp']),len(lat_md),len(lon_md),3))
            coords[...,1] = lat_md.reshape((1,len(lat_md),1))
            coords[...,2] = lon_md.reshape((1,1,len(lon_md)))
            coords = coords.reshape((alt_md.size,3))
            coords[:,0]=alt_md
            interpolator_WSP = LinearNDInterpolator(coords,WSP_4D_sm.values[it,inum,:,:,:].reshape((WSP_4D_sm.values[it,inum,:,:,:].size)),rescale=True)

            coords2 = np.zeros((1,1,1,3))
            coords2[...,0]=points['altitude'][0]
            coords2[...,1] = points['lat'][0]
            coords2[...,2] = points['lon'][0]
            coords2 = coords2.reshape((1,3))

            WSP_interped[it,inum]=np.squeeze(interpolator_WSP(coords2))

    WSP_interped_xr=coords_info_2D.copy()
    WSP_interped_xr['data'].values[:,:,0,0]=WSP_interped
    WSP_interped_xr.attrs['model']='ECMWF_ENSEMBLE'

    Ensemble_graphics.box_line_wsp(wsp=WSP_interped_xr,
        points=points,
        extra_info=extra_info,output_dir=output_dir)          

def point_fcst_rn_according_to_3D_field_box_line(
        output_dir=None,
        t_range=[6,60],
        t_gap=6,
        points={'lon':[116.3833], 'lat':[39.9]},
        initTime=None,obs_ID=54511,
        extra_info={
            'output_head_name':' ',
            'output_tail_name':' ',
            'point_name':' ',
            'drw_thr':True}
            ):

    try:
        dir_rqd=utl.Cassandra_dir(data_type='surface',data_source='ECMWF_ENSEMBLE',var_name='RAIN'+str(t_gap).zfill(2)+'_RAW')
    except KeyError:
        raise ValueError('Can not find all required directories needed')
    
    #-get all the directories needed
    if(initTime == None):
        initTime = get_latest_initTime(dir_rqd)
        #initTime=utl.filename_day_back_model(day_back=day_back,fhour=0)[0:8]

    if(t_range[1] > 72):
        fhours = np.append(np.arange(t_range[0], 72, t_gap),np.arange(72,t_range[1],6))
    else:
        fhours = np.arange(t_range[0], t_range[1], t_gap)

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]

    rn=utl.get_model_points_gy(dir_rqd, filenames, points,allExists=False)
    rn.attrs['model']='ECMWF_ENSEMBLE'

    Ensemble_graphics.box_line_rn(rn=rn,
        points=points,
        extra_info=extra_info,output_dir=output_dir)          