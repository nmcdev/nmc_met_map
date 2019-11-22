# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid
from nmc_met_map.graphics import elements_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr

def T2m_all_type(initial_time=None, fhour=24, day_back=0,model='SCMOC',Var_plot='Tmn_2m',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name=Var_plot)]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

    # retrieve data from micaps server
    T_2m = get_model_grid(data_dir[0], filename=filename)
    if T_2m is None:
        return
    init_time = T_2m.coords['forecast_reference_time'].values

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
    idx_x1 = np.where((T_2m.coords['lon'].values > map_extent[0]-delt_x) & 
        (T_2m.coords['lon'].values < map_extent[1]+delt_x))
    idx_y1 = np.where((T_2m.coords['lat'].values > map_extent[2]-delt_y) & 
        (T_2m.coords['lat'].values < map_extent[3]+delt_y))

    titles={
        'Tmn_2m':'过去24小时2米最低温度',
        'Tmx_2m':'过去24小时2米最高温度',
        'T2m':'2米温度'
        }
#- to solve the problem of labels on all the contours
    T_2m = {'lon': T_2m.coords['lon'].values[idx_x1],
             'lat': T_2m.coords['lat'].values[idx_y1],
             'data': T_2m['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'model':model,
             'fhour':fhour,
             'title':titles[Var_plot],
             'init_time':init_time}

    elements_graphics.draw_T_2m(
        T_2m=T_2m,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)
    
def T2m_mslp_uv10m(initial_time=None, fhour=6, day_back=0,model='ECMWF',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL'),
                    utl.Cassandra_dir(data_type='surface',data_source=model,var_name='u10m'),
                    utl.Cassandra_dir(data_type='surface',data_source=model,var_name='v10m'),
                    utl.Cassandra_dir(data_type='surface',data_source=model,var_name='T2m')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

    # retrieve data from micaps server
    mslp = get_model_grid(data_dir[0], filename=filename)
    if mslp is None:
        return
    
    u10m = get_model_grid(data_dir[1], filename=filename)
    if u10m is None:
        return
        
    v10m = get_model_grid(data_dir[2], filename=filename)
    if v10m is None:
        return
    t2m = get_model_grid(data_dir[3], filename=filename)
    if t2m is None:
        return   
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
    mask1 = (
            (mslp['lon']>(map_extent[0]-delt_x))&
            (mslp['lon']<(map_extent[1]+delt_x))&
            (mslp['lat']>(map_extent[2]-delt_y))&
            (mslp['lat']<(map_extent[3]+delt_y))
            )

    mask2 = (
            (mslp['lon']>(map_extent[0]-delt_x))&
            (mslp['lon']<(map_extent[1]+delt_x))
            )

    mask3 = (
            (mslp['lat']>(map_extent[2]-delt_y))&
            (mslp['lat']<(map_extent[3]+delt_y))
            )            
#- to solve the problem of labels on all the contours

    mslp = {'lon': mslp.coords['lon'].where(mask2, drop=True).values,
             'lat': mslp.coords['lat'].where(mask3, drop=True).values,
             'data': np.squeeze(mslp['data'].where(mask1, drop=True).values),
             'model':model,
             'fhour':fhour,
             'init_time':init_time}
    uv10m = {'lon': u10m.coords['lon'].where(mask2, drop=True).values,
             'lat': u10m.coords['lat'].where(mask3, drop=True).values,
             'udata': np.squeeze(u10m['data'].where(mask1, drop=True).values),
             'vdata': np.squeeze(v10m['data'].where(mask1, drop=True).values),
             }
    t2m = {'lon': t2m.coords['lon'].where(mask2, drop=True).values,
            'lat': t2m.coords['lat'].where(mask3, drop=True).values,
             'data': np.squeeze(t2m['data'].where(mask1, drop=True).values),
             }

    elements_graphics.draw_T2m_mslp_uv10m(
        t2m=t2m, mslp=mslp, uv10m=uv10m,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)        

def mslp_gust10m(initial_time=None, fhour=6, day_back=0,model='ECMWF',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL'),
                    utl.Cassandra_dir(data_type='surface',data_source=model,var_name='10M_GUST_6H')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

    # retrieve data from micaps server
    mslp = get_model_grid(data_dir[0], filename=filename)
    if mslp is None:
        return
    
    gust = get_model_grid(data_dir[1], filename=filename)
    if gust is None:
        return
        
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
    mask1 = (
            (mslp['lon']>(map_extent[0]-delt_x))&
            (mslp['lon']<(map_extent[1]+delt_x))&
            (mslp['lat']>(map_extent[2]-delt_y))&
            (mslp['lat']<(map_extent[3]+delt_y))
            )

    mask2 = (
            (mslp['lon']>(map_extent[0]-delt_x))&
            (mslp['lon']<(map_extent[1]+delt_x))
            )

    mask3 = (
            (mslp['lat']>(map_extent[2]-delt_y))&
            (mslp['lat']<(map_extent[3]+delt_y))
            )            
#- to solve the problem of labels on all the contours

    mslp = {'lon': mslp.coords['lon'].where(mask2, drop=True).values,
             'lat': mslp.coords['lat'].where(mask3, drop=True).values,
             'data': np.squeeze(mslp['data'].where(mask1, drop=True).values),
             'model':model,
             'fhour':fhour,
             'init_time':init_time}
    gust = {'lon': gust.coords['lon'].where(mask2, drop=True).values,
             'lat': gust.coords['lat'].where(mask3, drop=True).values,
             'data': np.squeeze(gust['data'].where(mask1, drop=True).values),
             }

    elements_graphics.draw_mslp_gust10m(
        gust=gust, mslp=mslp,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def low_level_wind(initial_time=None, fhour=6, day_back=0,model='ECMWF',wind_level='100m',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='u'+wind_level),
                    utl.Cassandra_dir(data_type='surface',data_source=model,var_name='v'+wind_level)]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

    # retrieve data from micaps server
    u10m = get_model_grid(data_dir[0], filename=filename)
    if u10m is None:
        return
    
    v10m = get_model_grid(data_dir[1], filename=filename)
    if v10m is None:
        return
        
    init_time = v10m.coords['forecast_reference_time'].values

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
    mask1 = (
            (u10m['lon']>(map_extent[0]-delt_x))&
            (u10m['lon']<(map_extent[1]+delt_x))&
            (u10m['lat']>(map_extent[2]-delt_y))&
            (u10m['lat']<(map_extent[3]+delt_y))
            )

    mask2 = (
            (u10m['lon']>(map_extent[0]-delt_x))&
            (u10m['lon']<(map_extent[1]+delt_x))
            )

    mask3 = (
            (u10m['lat']>(map_extent[2]-delt_y))&
            (u10m['lat']<(map_extent[3]+delt_y))
            )            
#- to solve the problem of labels on all the contours

    uv10m = {'lon': u10m.coords['lon'].where(mask2, drop=True).values,
             'lat': u10m.coords['lat'].where(mask3, drop=True).values,
             'lev': wind_level,
             'udata': np.squeeze(u10m['data'].where(mask1, drop=True).values),
             'vdata': np.squeeze(v10m['data'].where(mask1, drop=True).values),
             'model':model,
             'fhour':fhour,
             'init_time':init_time}

    wsp10m = {'lon': u10m.coords['lon'].where(mask2, drop=True).values,
            'lat': u10m.coords['lat'].where(mask3, drop=True).values,
             'data': ((uv10m['udata'])**2+ (uv10m['vdata'])**2)**0.5}


    elements_graphics.draw_low_level_wind(
        uv=uv10m,wsp=wsp10m,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)      