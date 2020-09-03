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
from nmc_met_io.retrieve_micaps_server import get_model_grid,get_fy_awx,get_station_data,get_radar_mosaic
import pandas as pd
from datetime import datetime, timedelta
import math
from nmc_met_map.graphics import observation_graphics

def IR_Sounding_GeopotentialHeight(Plot_IR=True,Plot_Sounding=True, Plot_HGT=True,
    IR_time=None,Sounding_time=None, HGT_initTime=None,fhour=24, model='ECMWF',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],city=False,Channel='C009',
    south_China_sea=True,area = '全国',output_dir=None,data_source='MICAPS'):

    Sounding=None
    HGT=None
    IR=None
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source='OBS',var_name='FY4AL1',lvl=Channel),
                        utl.Cassandra_dir(data_type='high',data_source='OBS',var_name='PLOT',lvl='500'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl='500')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        if(Plot_IR is True):
            if(IR_time != None):
                filename_IR=Channel+'_20'+IR_time+'0000_FY4A.AWX'
                IR = get_fy_awx(data_dir[0], filename=filename_IR)
            else:
                IR = get_fy_awx(data_dir[0])

        if(Plot_Sounding is True):
            if(Sounding_time != None):
                filename_Sounding = '20'+Sounding_time+'0000.000'
                Sounding = get_station_data(data_dir[1], filename=filename_Sounding)
            else:
                Sounding = get_station_data(data_dir[1])
            

        if(Plot_HGT is True):
            if(HGT_initTime != None):
                filename = model_filename(HGT_initTime, fhour)
                HGT = get_model_grid(data_dir[2], filename=filename)
            else:
                HGT = get_model_grid(data_dir[2])

    if(area != '全国'):
        cntr_pnt,zoom_ratio=get_map_area(area_name=area)
        south_China_sea=False

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1                       
    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    if(Plot_HGT is True):
        mask1 = (HGT['lon'] > map_extent[0]-delt_x) & (HGT['lon'] < map_extent[1]+delt_x) & (HGT['lat'] > map_extent[2]-delt_y) & (HGT['lat'] < map_extent[3]+delt_y)
        HGT=HGT.where(mask1,drop=True)
    if(output_dir != None):
        output_dir=output_dir+area+'_'

    observation_graphics.OBS_Sounding_GeopotentialHeight(IR=IR,Sounding=Sounding,HGT=HGT,
        map_extent=map_extent,city=city,south_China_sea=south_China_sea,output_dir=output_dir,
        Channel=Channel)

def CREF_Sounding_GeopotentialHeight(Plot_CREF=True,Plot_Sounding=True, Plot_HGT=True,
    CREF_time=None,Sounding_time=None, HGT_initTime=None,fhour=24, model='ECMWF',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],city=False,Channel='C009',
    south_China_sea=True,area = '全国',output_dir=None,data_source='MICAPS'):

    Sounding=None
    HGT=None
    IR=None
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source='OBS',var_name='CREF'),
                        utl.Cassandra_dir(data_type='high',data_source='OBS',var_name='PLOT',lvl='500'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl='500')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        if(Plot_CREF is True):
            if(CREF_time != None):
                filename_CREF='ACHN.CREF000.20'+CREF_time[0:6]+'.'+CREF_time[6:8]+'0000.LATLON'
                CREF = get_radar_mosaic(data_dir[0], filename=filename_CREF)
            else:
                CREF = get_CREF_mosaic(data_dir[0])

        if(Plot_Sounding is True):
            if(Sounding_time != None):
                filename_Sounding = '20'+Sounding_time+'0000.000'
                Sounding = get_station_data(data_dir[1], filename=filename_Sounding)
            else:
                Sounding = get_station_data(data_dir[1])
            

        if(Plot_HGT is True):
            if(HGT_initTime != None):
                filename = model_filename(HGT_initTime, fhour)
                HGT = get_model_grid(data_dir[2], filename=filename)
            else:
                HGT = get_model_grid(data_dir[2])

    if(area != '全国'):
        cntr_pnt,zoom_ratio=get_map_area(area_name=area)
        south_China_sea=False

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1                       
    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    if(Plot_HGT is True):
        mask1 = (HGT['lon'] > map_extent[0]-delt_x) & (HGT['lon'] < map_extent[1]+delt_x) & (HGT['lat'] > map_extent[2]-delt_y) & (HGT['lat'] < map_extent[3]+delt_y)
        HGT=HGT.where(mask1,drop=True)
    if(output_dir != None):
        output_dir=output_dir+area+'_'

    observation_graphics.OBS_CREF_Sounding_GeopotentialHeight(CREF=CREF,Sounding=Sounding,HGT=HGT,
        map_extent=map_extent,city=city,south_China_sea=south_China_sea,output_dir=output_dir)