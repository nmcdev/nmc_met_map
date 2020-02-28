# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid
from nmc_met_map.graphics import QPF_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr
import copy

def gh_rain(initial_time=None, fhour=24, day_back=0,model='ECMWF',
    gh_lev='500',atime=6,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                    utl.Cassandra_dir(data_type='surface',data_source=model,
                    var_name='RAIN'+ '%02d'%atime) ]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
        if(atime > 3):
            filename_gh=utl.model_filename(initial_time, int(fhour-atime/2))
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
        if(atime > 3):
            filename_gh=utl.filename_day_back_model(day_back=day_back,fhour=int(fhour-atime/2))

    # retrieve data from micaps server
    gh = get_model_grid(data_dir[0], filename=filename_gh)
    if gh is None:
        return
    
    rain = get_model_grid(data_dir[1], filename=filename)
    
    init_time = gh.coords['forecast_reference_time'].values


    # prepare data

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

#+ to solve the problem of labels on all the contours
    idx_x1 = np.where((gh.coords['lon'].values > map_extent[0]-delt_x) & 
        (gh.coords['lon'].values < map_extent[1]+delt_x))
    idx_y1 = np.where((gh.coords['lat'].values > map_extent[2]-delt_y) & 
        (gh.coords['lat'].values < map_extent[3]+delt_y))

    idx_x2 = np.where((rain.coords['lon'].values > map_extent[0]-delt_x) & 
        (rain.coords['lon'].values < map_extent[1]+delt_x))
    idx_y2 = np.where((rain.coords['lat'].values > map_extent[2]-delt_y) & 
        (rain.coords['lat'].values < map_extent[3]+delt_y))
#- to solve the problem of labels on all the contours

    gh = {'lon': gh.coords['lon'].values[idx_x1],
             'lat': gh.coords['lat'].values[idx_y1],
             'data': gh['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':gh_lev,
             'model':model,
             'fhour':fhour,
             'init_time':init_time}

    rain = {'lon': rain.coords['lon'].values[idx_x2],
            'lat': rain.coords['lat'].values[idx_y2],
             'data': copy.deepcopy(rain['data'].values[0,idx_y2[0][0]:(idx_y2[0][-1]+1),idx_x2[0][0]:(idx_x2[0][-1]+1)])
             }

    QPF_graphics.draw_gh_rain(
        rain=rain, gh=gh,atime=atime,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def mslp_rain_snow(initial_time=None, fhour=24, day_back=0,model='ECMWF',
    atime=6,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL'),
                    utl.Cassandra_dir(data_type='surface',data_source=model,var_name='RAIN'+ '%02d'%atime),
                    utl.Cassandra_dir(data_type='surface',data_source=model,var_name='SNOW'+ '%02d'%atime),]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
        if(atime > 3):
            filename_mslp=utl.model_filename(initial_time, int(fhour-atime/2))
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
        if(atime > 3):
            filename_mslp=utl.filename_day_back_model(day_back=day_back,fhour=int(fhour-atime/2))

    # retrieve data from micaps server
    mslp = get_model_grid(data_dir[0], filename=filename)
    if mslp is None:
        return
    
    rain = get_model_grid(data_dir[1], filename=filename)
    snow = get_model_grid(data_dir[2], filename=filename)
    init_time = mslp.coords['forecast_reference_time'].values


    # prepare data

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

#+ to solve the problem of labels on all the contours
    idx_x1 = np.where((mslp.coords['lon'].values > map_extent[0]-delt_x) & 
        (mslp.coords['lon'].values < map_extent[1]+delt_x))
    idx_y1 = np.where((mslp.coords['lat'].values > map_extent[2]-delt_y) & 
        (mslp.coords['lat'].values < map_extent[3]+delt_y))

    idx_x2 = np.where((rain.coords['lon'].values > map_extent[0]-delt_x) & 
        (rain.coords['lon'].values < map_extent[1]+delt_x))
    idx_y2 = np.where((rain.coords['lat'].values > map_extent[2]-delt_y) & 
        (rain.coords['lat'].values < map_extent[3]+delt_y))
#- to solve the problem of labels on all the contours
    rain_snow=xr.merge([rain.rename({'data': 'rain'}),snow.rename({'data': 'snow'})])

    mask1 = ((rain_snow['rain']-rain_snow['snow'])>0.1)&(rain_snow['snow']>0.1)
    sleet=rain_snow['rain'].where(mask1)

    mask2 = ((rain_snow['rain']-rain_snow['snow'])<0.1)&(rain_snow['snow']>0.1)
    snw=rain_snow['snow'].where(mask2)

    mask3 = (rain_snow['rain']>0.1)&(rain_snow['snow']<0.1)
    rn=rain_snow['rain'].where(mask3)

    mslp = {'lon': mslp.coords['lon'].values[idx_x1],
             'lat': mslp.coords['lat'].values[idx_y1],
             'data': mslp['data'].values[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'model':model,
             'fhour':fhour,
             'init_time':init_time}
    rain = {'lon': rn.coords['lon'].values[idx_x2],
            'lat': rn.coords['lat'].values[idx_y2],
             'data': rn.values[0,idx_y2[0][0]:(idx_y2[0][-1]+1),idx_x2[0][0]:(idx_x2[0][-1]+1)]}
    snow = {'lon': snw.coords['lon'].values[idx_x2],
            'lat': snw.coords['lat'].values[idx_y2],
             'data': snw.values[0,idx_y2[0][0]:(idx_y2[0][-1]+1),idx_x2[0][0]:(idx_x2[0][-1]+1)]}
    sleet={'lon': sleet.coords['lon'].values[idx_x2],
            'lat': sleet.coords['lat'].values[idx_y2],
             'data': sleet.values[0,idx_y2[0][0]:(idx_y2[0][-1]+1),idx_x2[0][0]:(idx_x2[0][-1]+1)]}

    QPF_graphics.draw_mslp_rain_snow(
        rain=rain, snow=snow,sleet=sleet,mslp=mslp,atime=atime,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)        
        