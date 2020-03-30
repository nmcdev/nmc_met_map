# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import dynamic_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr

def gh_uv_VVEL(initTime=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev=500,uvw_lev=850,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source=='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uvw_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uvw_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VVEL',lvl=uvw_lev)]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

        # retrieve data from micaps server
        gh = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)
        if gh is None:
            return
        
        u = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        if u is None:
            return
            
        v = MICAPS_IO.get_model_grid(data_dir[2], filename=filename)
        if v is None:
            return
        w = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        
        init_time = gh.coords['forecast_reference_time'].values

    if(data_source =='CIMISS'):
        
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        
        # retrieve data from CMISS server 
        try:       
            gh=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GPH'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=gh_lev, fcst_ele="GPH", units='gpm')
            if gh is None:
                return
            gh['data'].values=gh['data'].values/10.

            u=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uvw_lev, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uvw_lev, fcst_ele="WIV", units='m/s')
            if v is None:
                return

            w=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='VVP'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uvw_lev, fcst_ele="VVP", units='Pa.s-1')
            if w is None:
                return
            w['data'].values=w['data'].values*100
        except KeyError:
            raise ValueError('Can not find all data needed')
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

    mask1 = (gh['lon'] > map_extent[0]-delt_x) & (gh['lon'] < map_extent[1]+delt_x) & (gh['lat'] > map_extent[2]-delt_y) & (gh['lat'] < map_extent[3]+delt_y)

    mask2 = (u['lon'] > map_extent[0]-delt_x) & (u['lon'] < map_extent[1]+delt_x) & (u['lat'] > map_extent[2]-delt_y) & (u['lat'] < map_extent[3]+delt_y)

    mask3 = (w['lon'] > map_extent[0]-delt_x) & (w['lon'] < map_extent[1]+delt_x) & (w['lat'] > map_extent[2]-delt_y) & (w['lat'] < map_extent[3]+delt_y)

    gh=gh.where(mask1,drop=True)
    gh.attrs['model']=model
    u=u.where(mask2,drop=True)
    v=v.where(mask2,drop=True)
    VVEL=w.where(mask3,drop=True)
    VVEL.attrs['units']='0.01Pa.s-1'
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])
#- to solve the problem of labels on all the contours

    dynamic_graphics.draw_gh_uv_VVEL(
        VVEL=VVEL, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)