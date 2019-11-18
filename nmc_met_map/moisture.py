# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid
from nmc_met_map.graphics import moisture_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc

def gh_uv_pwat(initial_time=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev='500',uv_lev='850',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                    utl.Cassandra_dir(data_type='surface',data_source=model,var_name='TCWV')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

    # retrieve data from micaps server
    gh = get_model_grid(data_dir[0], filename=filename)
    if gh is None:
        return
    
    u = get_model_grid(data_dir[1], filename=filename)
    if u is None:
        return
        
    v = get_model_grid(data_dir[2], filename=filename)
    if v is None:
        return
    pwat = get_model_grid(data_dir[3], filename=filename)
    
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

    idx_x2 = np.where((pwat.coords['lon'].values > map_extent[0]-delt_x) & 
        (pwat.coords['lon'].values < map_extent[1]+delt_x))
    idx_y2 = np.where((pwat.coords['lat'].values > map_extent[2]-delt_y) & 
        (pwat.coords['lat'].values < map_extent[3]+delt_y))
#- to solve the problem of labels on all the contours

    gh = {'lon': gh.coords['lon'].values[idx_x1],
             'lat': gh.coords['lat'].values[idx_y1],
             'data': gh['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':gh_lev,
             'model':model,
             'fhour':fhour,
             'init_time':init_time}
    uv = {'lon': u.coords['lon'].values[idx_x1],
             'lat': u.coords['lat'].values[idx_y1],
             'udata': u['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'vdata': v['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':uv_lev}
    pwat = {'lon': pwat.coords['lon'].values[idx_x2],
            'lat': pwat.coords['lat'].values[idx_y2],
             'data': pwat['data'].values[0,idx_y2[0][0]:(idx_y2[0][-1]+1),idx_x2[0][0]:(idx_x2[0][-1]+1)]}

    moisture_graphics.draw_gh_uv_pwat(
        pwat=pwat, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)


def gh_uv_rh(initial_time=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev='500',uv_lev='850',rh_lev='850',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl=rh_lev)]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

    # retrieve data from micaps server
    gh = get_model_grid(data_dir[0], filename=filename)
    if gh is None:
        return
    
    u = get_model_grid(data_dir[1], filename=filename)
    if u is None:
        return
        
    v = get_model_grid(data_dir[2], filename=filename)
    if v is None:
        return
    rh = get_model_grid(data_dir[3], filename=filename)
    if rh is None:
        return

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

    idx_x2 = np.where((rh.coords['lon'].values > map_extent[0]-delt_x) & 
        (rh.coords['lon'].values < map_extent[1]+delt_x))
    idx_y2 = np.where((rh.coords['lat'].values > map_extent[2]-delt_y) & 
        (rh.coords['lat'].values < map_extent[3]+delt_y))
#- to solve the problem of labels on all the contours

    gh = {'lon': gh.coords['lon'].values[idx_x1],
             'lat': gh.coords['lat'].values[idx_y1],
             'data': gh['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':gh_lev,
             'model':model,
             'fhour':fhour,
             'init_time':init_time}
    uv = {'lon': u.coords['lon'].values[idx_x1],
             'lat': u.coords['lat'].values[idx_y1],
             'udata': u['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'vdata': v['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':uv_lev}
    rh = {'lon': rh.coords['lon'].values[idx_x2],
            'lat': rh.coords['lat'].values[idx_y2],
             'data': rh['data'].values[0,0,idx_y2[0][0]:(idx_y2[0][-1]+1),idx_x2[0][0]:(idx_x2[0][-1]+1)],
             'lev':rh_lev}

    moisture_graphics.draw_gh_uv_rh(
        rh=rh, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)


def gh_uv_spfh(initial_time=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev='500',uv_lev='850',spfh_lev='850',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='SPFH',lvl=spfh_lev)]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

    # retrieve data from micaps server
    gh = get_model_grid(data_dir[0], filename=filename)
    if gh is None:
        return
    
    u = get_model_grid(data_dir[1], filename=filename)
    if u is None:
        return
        
    v = get_model_grid(data_dir[2], filename=filename)
    if v is None:
        return
    spfh = get_model_grid(data_dir[3], filename=filename)
    if spfh is None:
        return

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

    idx_x2 = np.where((spfh.coords['lon'].values > map_extent[0]-delt_x) & 
        (spfh.coords['lon'].values < map_extent[1]+delt_x))
    idx_y2 = np.where((spfh.coords['lat'].values > map_extent[2]-delt_y) & 
        (spfh.coords['lat'].values < map_extent[3]+delt_y))
#- to solve the problem of labels on all the contours

    gh = {'lon': gh.coords['lon'].values[idx_x1],
             'lat': gh.coords['lat'].values[idx_y1],
             'data': gh['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':gh_lev,
             'model':model,
             'fhour':fhour,
             'init_time':init_time}
    uv = {'lon': u.coords['lon'].values[idx_x1],
             'lat': u.coords['lat'].values[idx_y1],
             'udata': u['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'vdata': v['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':uv_lev}
    spfh = {'lon': spfh.coords['lon'].values[idx_x2],
            'lat': spfh.coords['lat'].values[idx_y2],
             'data': spfh['data'].values[0,0,idx_y2[0][0]:(idx_y2[0][-1]+1),idx_x2[0][0]:(idx_x2[0][-1]+1)],
             'lev':spfh_lev}

    moisture_graphics.draw_gh_uv_spfh(
        spfh=spfh, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def gh_uv_wvfl(initial_time=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev='500',uv_lev='850',wvfl_lev='850',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='WVFL',lvl=wvfl_lev)
                    ]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

    # retrieve data from micaps server
    gh = get_model_grid(data_dir[0], filename=filename)
    if gh is None:
        return
    
    u = get_model_grid(data_dir[1], filename=filename)
    if u is None:
        return
        
    v = get_model_grid(data_dir[2], filename=filename)
    if v is None:
        return
    wvfl = get_model_grid(data_dir[3], filename=filename)
    if wvfl is None:
        return

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

    idx_x2 = np.where((wvfl.coords['lon'].values > map_extent[0]-delt_x) & 
        (wvfl.coords['lon'].values < map_extent[1]+delt_x))
    idx_y2 = np.where((wvfl.coords['lat'].values > map_extent[2]-delt_y) & 
        (wvfl.coords['lat'].values < map_extent[3]+delt_y))
#- to solve the problem of labels on all the contours

    gh = {'lon': gh.coords['lon'].values[idx_x1],
             'lat': gh.coords['lat'].values[idx_y1],
             'data': gh['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':gh_lev,
             'model':model,
             'fhour':fhour,
             'init_time':init_time}
    uv = {'lon': u.coords['lon'].values[idx_x1],
             'lat': u.coords['lat'].values[idx_y1],
             'udata': u['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'vdata': v['data'].values[0,0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
             'lev':uv_lev}
    wvfl = {'lon': wvfl.coords['lon'].values[idx_x2],
            'lat': wvfl.coords['lat'].values[idx_y2],
             'data': wvfl['data'].values[0,0,idx_y2[0][0]:(idx_y2[0][-1]+1),idx_x2[0][0]:(idx_x2[0][-1]+1)],
             'lev':wvfl_lev}

    moisture_graphics.draw_gh_uv_wvfl(
        wvfl=wvfl, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)