# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid,get_model_3D_grid
from nmc_met_map.graphics import isentropic_graphics
import nmc_met_map.lib.utility as utl
import metpy.calc as mpcalc
from metpy.units import units
import xarray as xr

def isentropic_uv(initTime=None, fhour=6, day_back=0,model='ECMWF',
    isentlev=310,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    levels=[1000, 950, 925, 900, 850, 800, 700,600,500,400,300,250,200,100],
    Global=False,
    south_China_sea=True,area = '全国',city=False,output_dir=None
     ):
    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl='')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initTime != None):
        filename = utl.model_filename(initTime, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
        
    # retrieve data from micaps server
    rh=get_model_3D_grid(directory=data_dir[0][0:-1],filename=filename,levels=levels, allExists=False)
    if rh is None:
        return

    u=get_model_3D_grid(directory=data_dir[1][0:-1],filename=filename,levels=levels, allExists=False)
    if u is None:
        return

    v=get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
    if v is None:
        return

    t=get_model_3D_grid(directory=data_dir[3][0:-1],filename=filename,levels=levels, allExists=False)
    if t is None:
        return

    lats = np.squeeze(rh['lat'].values)
    lons = np.squeeze(rh['lon'].values)

    pres = np.array(levels)*100 * units('Pa')
    tmp = t['data'].values.squeeze()*units('degC')
    uwnd = u['data'].values.squeeze()*units.meter/units.second
    vwnd = v['data'].values.squeeze()*units.meter/units.second
    relh = rh['data'].values.squeeze()*units.meter/units.percent

    isentlev = isentlev * units.kelvin

    isent_anal = mpcalc.isentropic_interpolation(isentlev, pres, tmp,
                                                 relh, uwnd, vwnd, axis=0)

    isentprs, isentrh, isentu, isentv = isent_anal

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
    idx_x1 = np.where((lons > map_extent[0]-delt_x) & 
        (lons < map_extent[1]+delt_x))
    idx_y1 = np.where((lats > map_extent[2]-delt_y) & 
        (lats < map_extent[3]+delt_y))
    #- to solve the problem of labels on all the contours
    init_time = u.coords['forecast_reference_time'].values
    isentrh = {
        'lon': lons[idx_x1],
        'lat': lats[idx_y1],
        'data': np.array(isentrh)[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
        'lev':str(isentlev),
        'model':model,
        'fhour':fhour,
        'init_time':init_time}
    isentuv = {
        'lon': lons[idx_x1],
        'lat': lats[idx_y1],
        'isentu': np.array(isentu)[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
        'isentv': np.array(isentv)[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
        'lev':str(isentlev)}
    isentprs = {
        'lon': lons[idx_x1],
        'lat': lats[idx_y1],
        'data': np.array(isentprs)[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)],
        'lev':str(isentlev)}

    isentropic_graphics.draw_isentropic_uv(
        isentrh=isentrh, isentuv=isentuv, isentprs=isentprs,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global
        )