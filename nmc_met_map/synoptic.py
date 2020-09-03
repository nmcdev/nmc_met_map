# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid,get_model_3D_grid
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import synoptic_graphics
import nmc_met_map.lib.utility as utl
import metpy.calc as mpcalc
from metpy.units import units
import math as mth
import xarray as xr
import pkg_resources
import pandas as pd
def gh500_anomaly_uv(initTime=None, fhour=240, day_back=0,model='ECMWF',
    gh_lev=500,uv_lev=500,
    map_ratio=13/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source =='MICAPS'):    
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
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

        psfc = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)

    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
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
                        fcst_level=uv_lev, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uv_lev, fcst_ele="WIV", units='m/s')
            if v is None:
                return

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed') 

    # prepare data
    gh_anm=utl.get_var_anm(gh)
    
    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=utl.get_map_extent(cntr_pnt,zoom_ratio,map_ratio)
    
    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    gh_anm=utl.mask_terrian(gh_lev,psfc,gh_anm)
    #+ to solve the problem of labels on all the contours
    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    gh=utl.cut_xrdata(map_extent,gh,delt_x=delt_x,delt_y=delt_y)
    u=utl.cut_xrdata(map_extent,u,delt_x=delt_x,delt_y=delt_y)
    v=utl.cut_xrdata(map_extent,v,delt_x=delt_x,delt_y=delt_y)
    gh_anm=utl.cut_xrdata(map_extent,gh_anm,delt_x=delt_x,delt_y=delt_y)
    #- to solve the problem of labels on all the contours
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])
    
    gh.attrs['model']=model
    synoptic_graphics.draw_gh_anomaly_uv(
        gh_anm=gh_anm, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global) 

def gh_uv_mslp(initTime=None, fhour=0, day_back=0,model='ECMWF',
    gh_lev=500,uv_lev=850,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename

        if(initTime == None):
            initTime = MICAPS_IO.get_latest_initTime(data_dir[-1])

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
        mslp = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        if mslp is None:
            return

    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
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
                        fcst_level=uv_lev, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uv_lev, fcst_ele="WIV", units='m/s')
            if v is None:
                return

            if(model == 'ECMWF'):
                mslp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='GSSP'),
                            levattrs={'long_name':'Mean_sea_level', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="GSSP", units='Pa')
            else:
                mslp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='SSP'),
                            levattrs={'long_name':'Mean_sea_level', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="SSP", units='Pa')
            if mslp is None:
                return
            mslp['data']=mslp['data']/100.
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

    mask3 = (mslp['lon'] > map_extent[0]-delt_x) & (mslp['lon'] < map_extent[1]+delt_x) & (mslp['lat'] > map_extent[2]-delt_y) & (mslp['lat'] < map_extent[3]+delt_y)
#- to solve the problem of labels on all the contours
    gh=gh.where(mask1,drop=True)
    gh.attrs['model']=model

    u=u.where(mask2,drop=True)
    v=v.where(mask2,drop=True)
    mslp=mslp.where(mask3,drop=True)

    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

    synoptic_graphics.draw_gh_uv_mslp(
        mslp=mslp, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def gh_uv_wsp(initTime=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev=500,uv_lev=850,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source =='MICAPS'):    
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
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

        psfc = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)

    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
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
                        fcst_level=uv_lev, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uv_lev, fcst_ele="WIV", units='m/s')
            if v is None:
                return

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed')                      
    # prepare data
    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=utl.get_map_extent(cntr_pnt,zoom_ratio,map_ratio)
    
    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    #+ to solve the problem of labels on all the contours
    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    gh=utl.cut_xrdata(map_extent,gh,delt_x=delt_x,delt_y=delt_y)
    u=utl.cut_xrdata(map_extent,u,delt_x=delt_x,delt_y=delt_y)
    v=utl.cut_xrdata(map_extent,v,delt_x=delt_x,delt_y=delt_y)
    #- to solve the problem of labels on all the contours
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

    wsp=(u['data']**2+v['data']**2)**0.5
    gh.attrs['model']=model
    synoptic_graphics.draw_gh_uv_wsp(
        wsp=wsp, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global) 

def gh_uv_r6(initTime=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev=500,uv_lev=850,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source =='MICAPS'):       
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='RAIN06')]
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
        r6 = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        if r6 is None:
            return

    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
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
                        fcst_level=uv_lev, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uv_lev, fcst_ele="WIV", units='m/s')
            if v is None:
                return        

            TPE1=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
            if TPE1 is None:
                return    

            TPE2=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour-6,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
            if TPE2 is None:
                return                
        except KeyError:
            raise ValueError('Can not find all data needed')      

        r6=TPE1.copy(deep=True)
        r6['data'].values=TPE1['data'].values*1000-TPE2['data'].values*1000

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

    mask3 = (r6['lon'] > map_extent[0]-delt_x) & (r6['lon'] < map_extent[1]+delt_x) & (r6['lat'] > map_extent[2]-delt_y) & (r6['lat'] < map_extent[3]+delt_y)

#- to solve the problem of labels on all the contours
    gh=gh.where(mask1,drop=True)
    gh.attrs['model']=model

    u=u.where(mask2,drop=True)
    v=v.where(mask2,drop=True)
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

    r6=r6.where(mask3,drop=True)

    synoptic_graphics.draw_gh_uv_r6(
        r6=r6, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)


def PV_Div_uv(initTime=None, fhour=6, day_back=0,model='ECMWF',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    levels=[1000, 950, 925, 900, 850, 800, 700,600,500,400,300,250,200,100],lvl_ana=250,
    Global=False,
    south_China_sea=True,area =None,city=False,output_dir=None,data_source='MICAPS'
     ):

    # micaps data directory
    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source =='MICAPS'):   
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
        rh=MICAPS_IO.get_model_3D_grid(directory=data_dir[0][0:-1],filename=filename,levels=levels, allExists=False)
        if rh is None:
            return

        u=MICAPS_IO.get_model_3D_grid(directory=data_dir[1][0:-1],filename=filename,levels=levels, allExists=False)
        if u is None:
            return

        v=MICAPS_IO.get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
        if v is None:
            return

        t=MICAPS_IO.get_model_3D_grid(directory=data_dir[3][0:-1],filename=filename,levels=levels, allExists=False)
        if t is None:
            return

    if(data_source =='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
            rh=CMISS_IO.cimiss_model_3D_grid(
                        data_code=utl.CMISS_data_code(data_source=model,var_name='RHU'),
                        init_time_str='20'+filename[0:8],valid_time=fhour,
                        fcst_levels=levels, fcst_ele="RHU", units='%')
            if rh is None:
                return

            u=CMISS_IO.cimiss_model_3D_grid(
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        init_time_str='20'+filename[0:8],valid_time=fhour,
                        fcst_levels=levels, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_3D_grid(
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        init_time_str='20'+filename[0:8],valid_time=fhour,
                        fcst_levels=levels, fcst_ele="WIV", units='m/s')
            if v is None:
                return        

            t=CMISS_IO.cimiss_model_3D_grid(
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEM'),
                        init_time_str='20'+filename[0:8],valid_time=fhour,
                        fcst_levels=levels, fcst_ele="TEM", units='K')
            if t is None:
                return            
            t['data'].values=t['data'].values-273.15
            t['data'].attrs['units']='C'
        except KeyError:
            raise ValueError('Can not find all data needed')

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
    mask1 = (rh['lon'] > map_extent[0]-delt_x) & (rh['lon'] < map_extent[1]+delt_x) & (rh['lat'] > map_extent[2]-delt_y) & (rh['lat'] < map_extent[3]+delt_y)

    mask2 = (u['lon'] > map_extent[0]-delt_x) & (u['lon'] < map_extent[1]+delt_x) & (u['lat'] > map_extent[2]-delt_y) & (u['lat'] < map_extent[3]+delt_y)

    mask3 = (t['lon'] > map_extent[0]-delt_x) & (t['lon'] < map_extent[1]+delt_x) & (t['lat'] > map_extent[2]-delt_y) & (t['lat'] < map_extent[3]+delt_y)
    #- to solve the problem of labels on all the contours
    rh=rh.where(mask1,drop=True)
    u=u.where(mask2,drop=True)
    v=v.where(mask2,drop=True)
    t=t.where(mask3,drop=True)
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

    lats = np.squeeze(rh['lat'].values)
    lons = np.squeeze(rh['lon'].values)

    pres = np.array(levels)*100 * units('Pa')
    tmpk = mpcalc.smooth_n_point((t['data'].values.squeeze()+273.15), 9, 2)*units('kelvin')
    thta = mpcalc.potential_temperature(pres[:, None, None], tmpk)

    uwnd = mpcalc.smooth_n_point(u['data'].values.squeeze(), 9, 2)*units.meter/units.second
    vwnd = mpcalc.smooth_n_point(v['data'].values.squeeze(), 9, 2)*units.meter/units.second

    dx, dy = mpcalc.lat_lon_grid_deltas(lons, lats)

    # Comput the PV on all isobaric surfaces
    pv_raw = mpcalc.potential_vorticity_baroclinic(thta, pres[:, None, None], uwnd, vwnd,
                                            dx[None, :, :], dy[None, :, :],
                                            lats[None, :, None] * units('degrees'))
    div_raw = mpcalc.divergence(uwnd, vwnd, dx[None, :, :], dy[None, :, :], dim_order='yx')

    # prepare data
    idx_z1 = list(pres.m).index(((lvl_ana * units('hPa')).to(pres.units)).m)

    pv=rh.copy(deep=True)
    pv['data'].values=np.array(pv_raw).reshape(np.append(1,np.array(pv_raw).shape))
    pv['data'].attrs['units']=str(pv_raw.units)
    pv.attrs['model']=model
    pv=pv.where(pv['level'] == lvl_ana,drop=True )

    div=u.copy(deep=True)
    div['data'].values=np.array(div_raw).reshape(np.append(1,np.array(div_raw).shape))
    div['data'].attrs['units']=str(div_raw.units)
    div=div.where(div['level'] == lvl_ana,drop=True )

    uv=uv.where(uv['level'] == lvl_ana,drop=True )

    synoptic_graphics.draw_PV_Div_uv(
        pv=pv, uv=uv, div=div,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)
