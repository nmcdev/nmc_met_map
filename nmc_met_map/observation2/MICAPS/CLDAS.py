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
from scipy.interpolate import Rbf
from scipy.interpolate import griddata
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CIMISS_IO
import pandas as pd
from datetime import datetime, timedelta
import math
from nmc_met_map.graphics import observation_graphics
from nmc_met_map.product.observation.horizontal.CLDAS import draw_TMP2
import cartopy.crs as ccrs
import nmc_met_map.graphics.QPF_graphics as QPF_graphics

def cumulative_precip_and_rain_days(endtime=None, cu_ndays=5, rn_ndays=7,
    map_ratio=19/11,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = None,city=False,output_dir=None,
    Global=False,**kwargs):

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
    if(area != None):
        if(area != None):
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

def cu_Tmx2(endtime, cu_ndays=1,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],area=None,
    **kargws):

# prepare data
    data_dir = [utl.Cassandra_dir(data_type='surface',data_source='CLDAS',var_name='Tmx_2m') ]

    # get filename
    cu_days = np.arange(0, cu_ndays)
    filenames_cu=[(datetime.strptime('20'+endtime,'%Y%m%d%H')-timedelta(days=int(icu_days))).strftime('%Y%m%d%H')[2:]+'.000'
            for icu_days in cu_days]

    # retrieve data from micaps server
    Tmx2m_all = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames_cu)
    
    coords=MICAPS_IO.get_model_grid(data_dir[0], filename=filenames_cu[0])

    # set map extent
    if(area != None):
        if(area != None):
            south_China_sea=False
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

    mask1 = ((Tmx2m_all['lon'] > map_extent[0]-delt_x) & 
            (Tmx2m_all['lon'] < map_extent[1]+delt_x) & 
            (Tmx2m_all['lat'] > map_extent[2]-delt_y) & 
            (Tmx2m_all['lat'] < map_extent[3]+delt_y))
    
    coords=coords.where(mask1,drop=True)
    Tmx2m_all=Tmx2m_all.where(mask1,drop=True)
    mask11=(Tmx2m_all['data'] == 9999.)
    Tmx2m_all['data'].values[mask11.values]=np.nan


    Tmx2= xr.DataArray(np.max(Tmx2m_all['data'].values,axis=0),name='data',
                    coords={'time':('time',[Tmx2m_all['time'].values[0]]),
                            'lat':('lat',Tmx2m_all['lat'].values),
                            'lon':('lon',Tmx2m_all['lon'].values)
                            },
                    dims=('time','lat','lon'),
                    attrs={'model_name':'CLDAS',
                           'var_name':'最高温度',
                           'vhours':cu_ndays*24})
# draw

    draw_TMP2(TMP2=Tmx2,map_extent=map_extent,**kargws)

def cu_Tmn2(endtime, cu_ndays=1,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],area=None,
    **kargws):

# prepare data
    data_dir = [utl.Cassandra_dir(data_type='surface',data_source='CLDAS',var_name='Tmn_2m') ]

    # get filename
    cu_days = np.arange(0, cu_ndays)
    filenames_cu=[(datetime.strptime('20'+endtime,'%Y%m%d%H')-timedelta(days=int(icu_days))).strftime('%Y%m%d%H')[2:]+'.000'
            for icu_days in cu_days]

    # retrieve data from micaps server
    Tmn2m_all = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames_cu)
    
    coords=MICAPS_IO.get_model_grid(data_dir[0], filename=filenames_cu[0])

    # set map extent
    if(area != None):
        if(area != None):
            south_China_sea=False
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

    mask1 = ((Tmn2m_all['lon'] > map_extent[0]-delt_x) & 
            (Tmn2m_all['lon'] < map_extent[1]+delt_x) & 
            (Tmn2m_all['lat'] > map_extent[2]-delt_y) & 
            (Tmn2m_all['lat'] < map_extent[3]+delt_y))
    
    coords=coords.where(mask1,drop=True)
    Tmn2m_all=Tmn2m_all.where(mask1,drop=True)
    mask11=(Tmn2m_all['data'] == 9999.)
    Tmn2m_all['data'].values[mask11.values]=np.nan


    Tmn2= xr.DataArray(np.max(Tmn2m_all['data'].values,axis=0),name='data',
                    coords={'time':('time',[Tmn2m_all['time'].values[0]]),
                            'lat':('lat',Tmn2m_all['lat'].values),
                            'lon':('lon',Tmn2m_all['lon'].values)
                            },
                    dims=('time','lat','lon'),
                    attrs={'model_name':'CLDAS',
                           'var_name':'最低温度',
                           'vhours':cu_ndays*24})
# draw

    draw_TMP2(TMP2=Tmn2,map_extent=map_extent,**kargws)

def cu_rain(initTime=None, atime=6,data_source='MICAPS',
            map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
            south_China_sea=True,area =None,city=False,output_dir=None,
            **kwargs):

# prepare data
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source='CLDAS',var_name='RAIN01')]
        except KeyError:
            raise ValueError('Can not find all directories needed')
        
        # get filename
        if(initTime == None):
            initTime=(datetime.now()-timedelta(hours=2)).strftime('%y%m%d%H')
        filenames=[]
        for ihour in range(0,atime):
            filenames.append((datetime.strptime(initTime,'%y%m%d%H')-timedelta(hours=ihour)).
                    strftime('%y%m%d%H')+'.000')

        # retrieve data from micaps server
        rain = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames)
        if rain is None:
            return

    if(data_source =='CIMISS'):
        # get filename
        if(initTime == None):
            initTime=(datetime.now()-timedelta(hours=2+8)).strftime('%y%m%d%H')
        filenames=[]
        for ihour in range(0,atime):
            filenames.append((datetime.strptime(initTime,'%y%m%d%H')-timedelta(hours=ihour)).
                    strftime('%Y%m%d%H')+'0000')
        try:
            # retrieve data from CIMISS server        
            rain=CIMISS_IO.cimiss_analysis_by_times(times_str=filenames,fcst_ele='PRE',
                            data_code=utl.CMISS_data_code(data_source='CLDAS',var_name='PRE'),
                            )
            if rain is None:
                return    
            rain=rain.rename({'PRE':'data'})
        except KeyError:
            raise ValueError('Can not find all data needed')

# set map extent
    if(area != None):
        south_China_sea=False

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent,delt_x,delt_y=utl.get_map_extent(cntr_pnt=cntr_pnt,zoom_ratio=zoom_ratio,map_ratio=map_ratio)
    rain=utl.cut_xrdata(map_extent, rain, delt_x=delt_x, delt_y=delt_y)
    rain['data'].values[rain['data'].values==9999.]=np.nan
    cu_rain=rain.sum('time')
    cu_rain.attrs['obs_time']=datetime.strptime(initTime,'%y%m%d%H')
    cu_rain.attrs['model']='CLDAS'
    cu_rain.attrs['atime']=atime
    cu_rain.attrs['var_name']='累积降水'
# draw
    QPF_graphics.draw_obs_cu_rain(
        rain=cu_rain,map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir)