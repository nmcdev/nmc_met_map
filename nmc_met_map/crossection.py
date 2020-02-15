# _*_ coding: utf-8 _*_
import numpy as np
import xarray as xr
import metpy.calc as mpcalc
from metpy.interpolate import cross_section
from nmc_met_io.retrieve_micaps_server import get_model_3D_grid,get_model_grid,get_model_3D_grids,get_latest_initTime,get_model_points
from nmc_met_map.graphics import crossection_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import pandas as pd
import math
import os
import sys
from IPython import clear_output

def Crosssection_Wind_Theta_e_absv(
    initial_time=None, fhour=24,
    levels=[1000, 950, 925, 900, 850, 800, 700,600,500,400,300,200],
    day_back=0,model='ECMWF',
    output_dir=None,
    st_point = [20, 120.0],
    ed_point = [50, 130.0],
    map_extent=[70,140,15,55],
    h_pos=[0.125, 0.665, 0.25, 0.2] ):

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl='500')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
        
    # retrieve data from micaps server
    rh=get_model_3D_grid(directory=data_dir[0][0:-1],filename=filename,levels=levels, allExists=False)
    if rh is None:
        return
    rh = rh.metpy.parse_cf().squeeze()

    u=get_model_3D_grid(directory=data_dir[1][0:-1],filename=filename,levels=levels, allExists=False)
    if u is None:
        return
    u = u.metpy.parse_cf().squeeze()

    v=get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
    if v is None:
        return
    v = v.metpy.parse_cf().squeeze()

    v2=get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
    if v2 is None:
        return
    v2 = v2.metpy.parse_cf().squeeze()

    t=get_model_3D_grid(directory=data_dir[3][0:-1],filename=filename,levels=levels, allExists=False)
    if t is None:
        return
    t = t.metpy.parse_cf().squeeze()

    gh=get_model_grid(data_dir[4], filename=filename)
    if t is None:
        return

    resolution=u['lon'][1]-u['lon'][0]
    x,y=np.meshgrid(u['lon'], u['lat'])

    dx,dy=mpcalc.lat_lon_grid_deltas(u['lon'],u['lat'])
    for ilvl in levels:
        u2d=u.sel(level=ilvl)
        #u2d['data'].attrs['units']=units.meter/units.second
        v2d=v.sel(level=ilvl)
        #v2d['data'].attrs['units']=units.meter/units.second

        absv2d=mpcalc.absolute_vorticity(u2d['data'].values*units.meter/units.second,
                v2d['data'].values*units.meter/units.second,dx,dy,y*units.degree)
        
        if(ilvl == levels[0]):
            absv3d = v2
            absv3d['data'].loc[dict(level=ilvl)]=np.array(absv2d)
        else:
            absv3d['data'].loc[dict(level=ilvl)]=np.array(absv2d)
    absv3d['data'].attrs['units']=absv2d.units

    #rh=rh.rename(dict(lat='latitude',lon='longitude'))
    cross = cross_section(rh, st_point, ed_point)
    cross_rh=cross.set_coords(('lat', 'lon'))
    cross = cross_section(u, st_point, ed_point)
    cross_u=cross.set_coords(('lat', 'lon'))
    cross = cross_section(v, st_point, ed_point)
    cross_v=cross.set_coords(('lat', 'lon'))

    cross_u['data'].attrs['units']=units.meter/units.second
    cross_v['data'].attrs['units']=units.meter/units.second
    cross_u['t_wind'], cross_v['n_wind'] = mpcalc.cross_section_components(cross_u['data'],cross_v['data'])
    
    cross = cross_section(t, st_point, ed_point)
    cross_t=cross.set_coords(('lat', 'lon'))
    cross = cross_section(absv3d, st_point, ed_point)
    cross_absv3d=cross.set_coords(('lat', 'lon'))

    cross_Td = mpcalc.dewpoint_rh(cross_t['data'].values*units.celsius,
                cross_rh['data'].values* units.percent)

    rh,pressure = xr.broadcast(cross_rh['data'],cross_t['level'])

    Theta_e=mpcalc.equivalent_potential_temperature(pressure,
                                                cross_t['data'].values*units.celsius, 
                                                cross_Td)

    cross_Theta_e = xr.DataArray(np.array(Theta_e),
                        coords=cross_rh['data'].coords,
                        dims=cross_rh['data'].dims,
                        attrs={'units': Theta_e.units})

    crossection_graphics.draw_Crosssection_Wind_Theta_e_absv(
                    cross_absv3d=cross_absv3d, cross_Theta_e=cross_Theta_e, cross_u=cross_u,
                    cross_v=cross_v,gh=gh,
                    h_pos=h_pos,st_point=st_point,ed_point=ed_point,
                    levels=levels,map_extent=map_extent,
                    output_dir=output_dir)

def Crosssection_Wind_Theta_e_RH(
    initial_time=None, fhour=24,
    levels=[1000, 950, 925, 900, 850, 800, 700,600,500,400,300,200],
    day_back=0,model='ECMWF',
    output_dir=None,
    st_point = [20, 120.0],
    ed_point = [50, 130.0],
    map_extent=[70,140,15,55],
    h_pos=[0.125, 0.665, 0.25, 0.2] ):

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl='500')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
        
    # retrieve data from micaps server
    rh=get_model_3D_grid(directory=data_dir[0][0:-1],filename=filename,levels=levels, allExists=False)
    if rh is None:
        return
    rh = rh.metpy.parse_cf().squeeze()

    u=get_model_3D_grid(directory=data_dir[1][0:-1],filename=filename,levels=levels, allExists=False)
    if u is None:
        return
    u = u.metpy.parse_cf().squeeze()

    v=get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
    if v is None:
        return
    v = v.metpy.parse_cf().squeeze()

    v2=get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
    if v2 is None:
        return
    v2 = v2.metpy.parse_cf().squeeze()

    t=get_model_3D_grid(directory=data_dir[3][0:-1],filename=filename,levels=levels, allExists=False)
    if t is None:
        return
    t = t.metpy.parse_cf().squeeze()

    gh=get_model_grid(data_dir[4], filename=filename)
    if t is None:
        return

    resolution=u['lon'][1]-u['lon'][0]
    x,y=np.meshgrid(u['lon'], u['lat'])

    dx,dy=mpcalc.lat_lon_grid_deltas(u['lon'],u['lat'])
    for ilvl in levels:
        u2d=u.sel(level=ilvl)
        #u2d['data'].attrs['units']=units.meter/units.second
        v2d=v.sel(level=ilvl)
        #v2d['data'].attrs['units']=units.meter/units.second

        absv2d=mpcalc.absolute_vorticity(u2d['data'].values*units.meter/units.second,
                v2d['data'].values*units.meter/units.second,dx,dy,y*units.degree)
        
        if(ilvl == levels[0]):
            absv3d = v2
            absv3d['data'].loc[dict(level=ilvl)]=np.array(absv2d)
        else:
            absv3d['data'].loc[dict(level=ilvl)]=np.array(absv2d)
    absv3d['data'].attrs['units']=absv2d.units

    #rh=rh.rename(dict(lat='latitude',lon='longitude'))
    cross = cross_section(rh, st_point, ed_point)
    cross_rh=cross.set_coords(('lat', 'lon'))
    cross = cross_section(u, st_point, ed_point)
    cross_u=cross.set_coords(('lat', 'lon'))
    cross = cross_section(v, st_point, ed_point)
    cross_v=cross.set_coords(('lat', 'lon'))

    cross_u['data'].attrs['units']=units.meter/units.second
    cross_v['data'].attrs['units']=units.meter/units.second
    cross_u['t_wind'], cross_v['n_wind'] = mpcalc.cross_section_components(cross_u['data'],cross_v['data'])
    
    cross = cross_section(t, st_point, ed_point)
    cross_t=cross.set_coords(('lat', 'lon'))
    cross = cross_section(absv3d, st_point, ed_point)

    cross_Td = mpcalc.dewpoint_rh(cross_t['data'].values*units.celsius,
                cross_rh['data'].values* units.percent)

    rh,pressure = xr.broadcast(cross_rh['data'],cross_t['level'])

    Theta_e=mpcalc.equivalent_potential_temperature(pressure,
                                                cross_t['data'].values*units.celsius, 
                                                cross_Td)

    cross_Theta_e = xr.DataArray(np.array(Theta_e),
                        coords=cross_rh['data'].coords,
                        dims=cross_rh['data'].dims,
                        attrs={'units': Theta_e.units})

    crossection_graphics.draw_Crosssection_Wind_Theta_e_RH(
                    cross_rh=cross_rh, cross_Theta_e=cross_Theta_e, cross_u=cross_u,
                    cross_v=cross_v,gh=gh,
                    h_pos=h_pos,st_point=st_point,ed_point=ed_point,
                    levels=levels,map_extent=map_extent,
                    output_dir=output_dir)


def Crosssection_Wind_Theta_e_Qv(
    initial_time=None, fhour=24,
    levels=[1000, 950, 925, 900, 850, 800, 700,600,500,400,300,200],
    day_back=0,model='ECMWF',
    output_dir=None,
    st_point = [20, 120.0],
    ed_point = [50, 130.0],
    map_extent=[70,140,15,55],
    h_pos=[0.125, 0.665, 0.25, 0.2] ):

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl='500')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
        
    # retrieve data from micaps server
    rh=get_model_3D_grid(directory=data_dir[0][0:-1],filename=filename,levels=levels, allExists=False)
    if rh is None:
        return
    rh = rh.metpy.parse_cf().squeeze()

    u=get_model_3D_grid(directory=data_dir[1][0:-1],filename=filename,levels=levels, allExists=False)
    if u is None:
        return
    u = u.metpy.parse_cf().squeeze()

    v=get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
    if v is None:
        return
    v = v.metpy.parse_cf().squeeze()

    v2=get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
    if v2 is None:
        return
    v2 = v2.metpy.parse_cf().squeeze()

    t=get_model_3D_grid(directory=data_dir[3][0:-1],filename=filename,levels=levels, allExists=False)
    if t is None:
        return
    t = t.metpy.parse_cf().squeeze()

    gh=get_model_grid(data_dir[4], filename=filename)
    if t is None:
        return

    resolution=u['lon'][1]-u['lon'][0]
    x,y=np.meshgrid(u['lon'], u['lat'])

    dx,dy=mpcalc.lat_lon_grid_deltas(u['lon'],u['lat'])
    for ilvl in levels:
        u2d=u.sel(level=ilvl)
        #u2d['data'].attrs['units']=units.meter/units.second
        v2d=v.sel(level=ilvl)
        #v2d['data'].attrs['units']=units.meter/units.second

        absv2d=mpcalc.absolute_vorticity(u2d['data'].values*units.meter/units.second,
                v2d['data'].values*units.meter/units.second,dx,dy,y*units.degree)
        
        if(ilvl == levels[0]):
            absv3d = v2
            absv3d['data'].loc[dict(level=ilvl)]=np.array(absv2d)
        else:
            absv3d['data'].loc[dict(level=ilvl)]=np.array(absv2d)
    absv3d['data'].attrs['units']=absv2d.units

    #rh=rh.rename(dict(lat='latitude',lon='longitude'))
    cross = cross_section(rh, st_point, ed_point)
    cross_rh=cross.set_coords(('lat', 'lon'))
    cross = cross_section(u, st_point, ed_point)
    cross_u=cross.set_coords(('lat', 'lon'))
    cross = cross_section(v, st_point, ed_point)
    cross_v=cross.set_coords(('lat', 'lon'))

    cross_u['data'].attrs['units']=units.meter/units.second
    cross_v['data'].attrs['units']=units.meter/units.second
    cross_u['t_wind'], cross_v['n_wind'] = mpcalc.cross_section_components(cross_u['data'],cross_v['data'])
    
    cross = cross_section(t, st_point, ed_point)
    cross_t=cross.set_coords(('lat', 'lon'))
    cross = cross_section(absv3d, st_point, ed_point)

    cross_Td = mpcalc.dewpoint_rh(cross_t['data'].values*units.celsius,
                cross_rh['data'].values* units.percent)

    rh,pressure = xr.broadcast(cross_rh['data'],cross_t['level'])

    Qv = mpcalc.specific_humidity_from_dewpoint(cross_Td,
                pressure)

    cross_Qv = xr.DataArray(np.array(Qv)*1000.,
                    coords=cross_rh['data'].coords,
                    dims=cross_rh['data'].dims,
                    attrs={'units': units('g/kg')})

    Theta_e=mpcalc.equivalent_potential_temperature(pressure,
                                                cross_t['data'].values*units.celsius, 
                                                cross_Td)

    cross_Theta_e = xr.DataArray(np.array(Theta_e),
                        coords=cross_rh['data'].coords,
                        dims=cross_rh['data'].dims,
                        attrs={'units': Theta_e.units})

    crossection_graphics.draw_Crosssection_Wind_Theta_e_Qv(
                    cross_Qv=cross_Qv, cross_Theta_e=cross_Theta_e, cross_u=cross_u,
                    cross_v=cross_v,gh=gh,
                    h_pos=h_pos,st_point=st_point,ed_point=ed_point,
                    levels=levels,map_extent=map_extent,
                    output_dir=output_dir)

def Time_Crossection_rh_uv_t(initTime=None,model='ECMWF',points={'lon':[116.3833], 'lat':[39.9]},
    levels=[1000, 950, 925, 900, 850, 800, 700,600,500,400,300,200],
    t_gap=3,t_range=[0,48],output_dir=None):

    fhours = np.arange(t_range[0], t_range[1], t_gap)

    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl='')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # # 读数据
    if(initTime == None):
        initTime = get_latest_initTime(data_dir[0][0:-1]+"850")
    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    TMP_4D=get_model_3D_grids(directory=data_dir[0][0:-1],filenames=filenames,levels=levels, allExists=False)
    TMP_2D=TMP_4D.interp(lon=('points', points['lon']), lat=('points', points['lat']))

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    u_4D=get_model_3D_grids(directory=data_dir[1][0:-1],filenames=filenames,levels=levels, allExists=False)
    u_2D=u_4D.interp(lon=('points', points['lon']), lat=('points', points['lat']))

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    v_4D=get_model_3D_grids(directory=data_dir[2][0:-1],filenames=filenames,levels=levels, allExists=False)
    v_2D=v_4D.interp(lon=('points', points['lon']), lat=('points', points['lat']))

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    rh_4D=get_model_3D_grids(directory=data_dir[3][0:-1],filenames=filenames,levels=levels, allExists=False)
    rh_2D=rh_4D.interp(lon=('points', points['lon']), lat=('points', points['lat']))
    rh_2D.attrs['model']=model
    rh_2D.attrs['points']=points

    crossection_graphics.draw_Time_Crossection_rh_uv_t(
                    rh_2D=rh_2D, u_2D=u_2D, v_2D=v_2D,TMP_2D=TMP_2D,
                    output_dir=output_dir)


def Time_Crossection_rh_uv_theta_e(initTime=None,model='ECMWF',points={'lon':[116.3833], 'lat':[39.9]},
    levels=[1000, 950, 925, 900, 850, 800, 700,600,500,400,300,200],
    t_gap=3,t_range=[0,48],output_dir=None):
  
    fhours = np.arange(t_range[0], t_range[1], t_gap)

    # 读数据

    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl='')]
    except KeyError:
        raise ValueError('Can not find all directories needed')
    
    if(initTime==None):
        initTime = get_latest_initTime(data_dir[0][0:-1]+"850")
    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    TMP_4D=get_model_3D_grids(directory=data_dir[0][0:-1],filenames=filenames,levels=levels, allExists=False)
    TMP_2D=TMP_4D.interp(lon=('points', points['lon']), lat=('points', points['lat']))

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    u_4D=get_model_3D_grids(directory=data_dir[1][0:-1],filenames=filenames,levels=levels, allExists=False)
    u_2D=u_4D.interp(lon=('points', points['lon']), lat=('points', points['lat']))

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    v_4D=get_model_3D_grids(directory=data_dir[2][0:-1],filenames=filenames,levels=levels, allExists=False)
    v_2D=v_4D.interp(lon=('points', points['lon']), lat=('points', points['lat']))

    filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
    rh_4D=get_model_3D_grids(directory=data_dir[3][0:-1],filenames=filenames,levels=levels, allExists=False)
    rh_2D=rh_4D.interp(lon=('points', points['lon']), lat=('points', points['lat']))
    rh_2D.attrs['model']=model
    rh_2D.attrs['points']=points
    clear_output()
    Td_2D = mpcalc.dewpoint_rh(TMP_2D['data'].values*units.celsius,
                rh_2D['data'].values* units.percent)

    rh,pressure = xr.broadcast(rh_2D['data'],rh_2D['level'])

    Theta_e=mpcalc.equivalent_potential_temperature(pressure,
                                                TMP_2D['data'].values*units.celsius, 
                                                Td_2D)

    theta_e_2D = xr.DataArray(np.array(Theta_e),
                        coords=rh_2D['data'].coords,
                        dims=rh_2D['data'].dims,
                        attrs={'units': Theta_e.units})

    crossection_graphics.draw_Time_Crossection_rh_uv_theta_e(
                    rh_2D=rh_2D, u_2D=u_2D, v_2D=v_2D,theta_e_2D=theta_e_2D,
                    t_range=t_range,output_dir=output_dir)
