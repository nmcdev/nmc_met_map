# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_map.lib.utility import model_filename
from nmc_met_map.lib.utility import get_map_area,Tmax_stastics,get_coord_AWX,obs_radar_filename
import nmc_met_map.lib.utility as utl
#import datetime
import xarray as xr
from nmc_met_map.lib.read_micaps_16 import read_micaps_16
import pkg_resources
from nmc_met_publish_map.source.lib.match_two_array import match_two_array
from scipy.interpolate import Rbf
from scipy.interpolate import griddata
import regionmask
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import pandas as pd
from datetime import datetime, timedelta
import math
from nmc_met_map.graphics import observation_graphics

def cumulative_precip_and_rain_days(endtime=None, cu_ndays=5, rn_ndays=7,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

# prepare data
    data_dir = [utl.Cassandra_dir(data_type='surface',data_source='CLDAS',var_name='RAIN24') ]

    # get filename
    cu_days = np.arange(0, cu_ndays)
    filenames_cu=[(datetime.strptime('20'+endtime,'%Y%m%d%H')-timedelta(days=int(icu_days))).strftime('%Y%m%d%H')[2:]+'.000'
            for icu_days in cu_days]

    rn_days = np.arange(0, rn_ndays)
    filenames_days=[(datetime.strptime('20'+endtime,'%Y%m%d%H')-timedelta(days=int(irn_days))).strftime('%Y%m%d%H')[2:]+'.000'
            for irn_days in rn_days]

    # retrieve data from micaps server
    cu_rain_all = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames_cu)
    
    cu_days_rain = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames_days)
    
    coords=MICAPS_IO.get_model_grid(data_dir[0], filename=filenames_days[0])

# set map extent
    if(area != '全国'):
        south_China_sea=False
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

    mask1 = (cu_rain_all['lon'] > map_extent[0]-delt_x) & (cu_rain_all['lon'] < map_extent[1]+delt_x) & (cu_rain_all['lat'] > map_extent[2]-delt_y) & (cu_rain_all['lat'] < map_extent[3]+delt_y)
    mask2 = (cu_days_rain['lon'] > map_extent[0]-delt_x) & (cu_days_rain['lon'] < map_extent[1]+delt_x) & (cu_days_rain['lat'] > map_extent[2]-delt_y) & (cu_days_rain['lat'] < map_extent[3]+delt_y)

    coords=coords.where(mask1,drop=True)
    cu_rain_all=cu_rain_all.where(mask1,drop=True)
    mask11=(cu_rain_all['data'] == 9999.)
    cu_rain_all['data'].values[mask11.values]=np.nan
    cu_days_rain=cu_days_rain.where(mask2,drop=True)
    mask22=(cu_days_rain['data'] == 9999.)
    cu_days_rain['data'].values[mask22.values]=0

    cu_rain= xr.DataArray([np.sum(cu_rain_all['data'].values,axis=0)],
                    coords=coords['data'].coords,
                    dims=coords['data'].dims)
    mask3=(cu_days_rain['data']>0)
    cu_days_rain['data'].values[mask3.values]=1
    days_rain=xr.DataArray([np.sum(cu_days_rain['data'].values,axis=0)],
                    coords=coords['data'].coords,
                    dims=coords['data'].dims)
    days_rain.attrs['rn_ndays']=rn_ndays
    cu_rain.attrs['cu_ndays']=cu_ndays
# draw
    observation_graphics.draw_cumulative_precip_and_rain_days(
        cu_rain=cu_rain, days_rain=days_rain,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)