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
from scipy.ndimage import gaussian_filter

def gh_uv_VVEL(initTime=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev=500,uvw_lev=850,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS'):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source=='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uvw_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uvw_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VVEL',lvl=uvw_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PSFC')]
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
        
        psfc = MICAPS_IO.get_model_grid(data_dir[4], filename=filename)
        
        if(model == 'GRAPES_GFS'):
            data_dir2=utl.Cassandra_dir(data_type='high',data_source=model,var_name='SPFH',lvl=uvw_lev)
            data_dir3=utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=uvw_lev)
            SPFH = MICAPS_IO.get_model_grid(data_dir2, filename=filename)
            TMP = MICAPS_IO.get_model_grid(data_dir3, filename=filename)
            temp=mpcalc.vertical_velocity_pressure((w['data'].values/100)*units('m/s'),
                        (np.zeros_like(w['data'].values)+uvw_lev)*units.hPa,
                        TMP['data'].values*units.degC, mixing=SPFH['data'].values*units['g/kg']).magnitude*100.
            w['data'].values=temp
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

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed')
    # prepare data

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
    map_extent=utl.get_map_extent(cntr_pnt, zoom_ratio, map_ratio)

    w['data'].values=gaussian_filter(w['data'].values,5)



#+ to solve the problem of labels on all the contours


    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uvw_lev,psfc,u)
    v=utl.mask_terrian(uvw_lev,psfc,v)
    w=utl.mask_terrian(uvw_lev,psfc,w)

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    gh=utl.cut_xrdata(map_extent, gh, delt_x=delt_x, delt_y=delt_y)
    u=utl.cut_xrdata(map_extent, u, delt_x=delt_x, delt_y=delt_y)
    v=utl.cut_xrdata(map_extent, v, delt_x=delt_x, delt_y=delt_y)
    VVEL=utl.cut_xrdata(map_extent, w, delt_x=delt_x, delt_y=delt_y)

    gh.attrs['model']=model

    VVEL.attrs['units']='0.01Pa.s-1'
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])
#- to solve the problem of labels on all the contours
    dynamic_graphics.draw_gh_uv_VVEL(
        VVEL=VVEL, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir)

def fg_uv_tmp(initTime=None, fhour=6, day_back=0,model='ECMWF',
    fg_lev=500,
    map_ratio=16/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = None,city=False,output_dir=None,data_source='MICAPS',
    ):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source=='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=fg_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=fg_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=fg_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=fg_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PSFC')]
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
        tmp = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        
        psfc = MICAPS_IO.get_model_grid(data_dir[4], filename=filename)
        
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
                        fcst_level=fg_lev, fcst_ele="GPH", units='gpm')
            if gh is None:
                return
            gh['data'].values=gh['data'].values/10.

            u=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=fg_lev, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=fg_lev, fcst_ele="WIV", units='m/s')
            if v is None:
                return

            tmp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEM'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=fg_lev, fcst_ele="TEM", units='K')
            if tmp is None:
                return
            tmp['data'].values=tmp['data'].values-273.15

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed')

    #caluculate_fg
    pressure=fg_lev*units('hPa')
    theta = mpcalc.potential_temperature(pressure, tmp['data'].values.squeeze()*units('degC'))
    dx,dy=mpcalc.lat_lon_grid_deltas(tmp['lon'].values.squeeze(),tmp['lat'].values.squeeze())
    fg=mpcalc.frontogenesis(theta,u['data'].values.squeeze()*units('mps'),v['data'].values.squeeze()*units('mps'),dx,dy,dim_order='yx')

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
    map_extent=utl.get_map_extent(cntr_pnt, zoom_ratio, map_ratio)

#+ to solve the problem of labels on all the contours

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    fg_xr=u.copy()
    fg_xr['data'].values=fg.magnitude[np.newaxis,np.newaxis,:,:]
    fg_xr=utl.cut_xrdata(map_extent, fg_xr, delt_x=delt_x, delt_y=delt_y)
    u=utl.cut_xrdata(map_extent, u, delt_x=delt_x, delt_y=delt_y)
    v=utl.cut_xrdata(map_extent, v, delt_x=delt_x, delt_y=delt_y)
    tmp=utl.cut_xrdata(map_extent, tmp, delt_x=delt_x, delt_y=delt_y)

    fg_xr=utl.mask_terrian(fg_lev,psfc,fg_xr)
    u=utl.mask_terrian(fg_lev,psfc,u)
    v=utl.mask_terrian(fg_lev,psfc,v)
    tmp=utl.mask_terrian(fg_lev,psfc,tmp)

    fg_xr.attrs['model']=model
    fg_xr.attrs['units']='K*s${^{-1}}$ m${^{-1}}$'
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])
#- to solve the problem of labels on all the contours
    dynamic_graphics.draw_fg_uv_tmp(
        fg=fg_xr, tmp=tmp, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir)