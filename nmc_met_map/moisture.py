# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import moisture_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr

def gh_uv_pwat(initTime=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev=500,uv_lev=850,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area =None,city=False,output_dir=None,data_source='MICAPS',
    Global=False,**kwargs):

    if(area != None):
        south_China_sea=False

    # micaps data directory
    if(data_source =='MICAPS'):       
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='TCWV'),
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
        pwat = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        if pwat is None:
            return
        psfc = MICAPS_IO.get_model_grid(data_dir[4], filename=filename)
         
    if(data_source =='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CIMISS server        
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
                pwat=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='TCWV'),
                            levattrs={'long_name':'Height_above_Ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="TCWV", units='kg m-2')
            else:
                pwat=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='TIWV'),
                            levattrs={'long_name':'Height_above_Ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="TIWV", units='kg m-2')
            if pwat is None:
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

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

    gh=utl.cut_xrdata(map_extent, gh, delt_x=delt_x, delt_y=delt_y)
    u=utl.cut_xrdata(map_extent, u, delt_x=delt_x, delt_y=delt_y)
    v=utl.cut_xrdata(map_extent, v, delt_x=delt_x, delt_y=delt_y)
    pwat=utl.cut_xrdata(map_extent, pwat, delt_x=delt_x, delt_y=delt_y)

    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    
    gh.attrs['model']=model

    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

    moisture_graphics.draw_gh_uv_pwat(
        pwat=pwat, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)


def gh_uv_rh(initTime=None, fhour=6, day_back=0,model='GRAPES_GFS',
    gh_lev=500,uv_lev=850,rh_lev=850,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area =None,city=False,output_dir=None,data_source='MICAPS',
    Global=False,**kwargs):

    if(area != None):
        south_China_sea=False
    if(data_source =='MICAPS'):
        # micaps data directory
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl=rh_lev),
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
        rh = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        if rh is None:
            return
        psfc = MICAPS_IO.get_model_grid(data_dir[4], filename=filename)

    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CIMISS server        
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

            rh=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='RHU'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=rh_lev, fcst_ele="RHU", units='%')
            if rh is None:
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

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

    gh=utl.cut_xrdata(map_extent, gh, delt_x=delt_x, delt_y=delt_y)
    u=utl.cut_xrdata(map_extent, u, delt_x=delt_x, delt_y=delt_y)
    v=utl.cut_xrdata(map_extent, v, delt_x=delt_x, delt_y=delt_y)
    rh=utl.cut_xrdata(map_extent, rh, delt_x=delt_x, delt_y=delt_y)

    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    rh=utl.mask_terrian(rh_lev,psfc,rh)

    gh.attrs['model']=model

    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

    moisture_graphics.draw_gh_uv_rh(
        rh=rh, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)


def gh_uv_spfh(initTime=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev=500,uv_lev=850,spfh_lev=850,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area =None,city=False,output_dir=None,data_source='MICAPS',
    Global=False,**kwargs):

    if(area != None):
        south_China_sea=False

    if(data_source=='MICAPS'):
        # micaps data directory
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='SPFH',lvl=spfh_lev),
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
        spfh = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        if spfh is None:
            return

        psfc = MICAPS_IO.get_model_grid(data_dir[4], filename=filename)


    if(data_source == 'CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CIMISS server        
            gh=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GPH'),
                        fcst_level=gh_lev, fcst_ele="GPH", units='gpm')
            if gh is None:
                return
            gh['data'].values=gh['data'].values/10.

            u=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        fcst_level=uv_lev, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        fcst_level=uv_lev, fcst_ele="WIV", units='m/s')
            if v is None:
                return

            spfh=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='SHU'),
                        fcst_level=spfh_lev, fcst_ele="SHU", units='kg.kg-1')
            if spfh is None:
                return
            spfh['data'].values=spfh['data'].values*1000

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.
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

    mask3 = (spfh['lon'] > map_extent[0]-delt_x) & (spfh['lon'] < map_extent[1]+delt_x) & (spfh['lat'] > map_extent[2]-delt_y) & (spfh['lat'] < map_extent[3]+delt_y)

    gh=utl.cut_xrdata(map_extent,gh,delt_x=delt_x,delt_y=delt_y)
    u=utl.cut_xrdata(map_extent, u, delt_x=delt_x, delt_y=delt_y)
    v=utl.cut_xrdata(map_extent, v, delt_x=delt_x, delt_y=delt_y)
    spfh=utl.cut_xrdata(map_extent, spfh, delt_x=delt_x, delt_y=delt_y)

    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    spfh=utl.mask_terrian(spfh_lev,psfc,spfh)
#- to solve the problem of labels on all the contours
    gh=gh.where(mask1,drop=True)
    gh.attrs['model']=model
    u=u.where(mask2,drop=True)
    v=v.where(mask2,drop=True)
    spfh=spfh.where(mask3,drop=True)

    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

    moisture_graphics.draw_gh_uv_spfh(
        spfh=spfh, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def gh_uv_wvfl(initTime=None, fhour=6, day_back=0,model='GRAPES_GFS',
    gh_lev=500,uv_lev=850,wvfl_lev=850,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area = None,city=False,output_dir=None,data_source='MICAPS',
    Global=False,**kwargs):

    if(area != None):
        south_China_sea=False

    # micaps data directory
    if(data_source =='MICAPS'):        
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='WVFL',lvl=wvfl_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PSFC')
                        ]
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
        wvfl = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        if wvfl is None:
            return
        psfc = MICAPS_IO.get_model_grid(data_dir[4], filename=filename)
        
    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CIMISS server        
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

            wvfl=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='MOFU'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=wvfl_lev, fcst_ele="MOFU", units='10^-1*g/cm*hPa*s')
            wvfl['data'].values=wvfl['data'].values*10.
            if wvfl is None:
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

    map_extent,delt_x,delt_y=utl.get_map_extent(cntr_pnt=cntr_pnt,zoom_ratio=zoom_ratio,map_ratio=map_ratio)

    gh=utl.cut_xrdata(map_extent, gh, delt_x=delt_x, delt_y=delt_y)
    u=utl.cut_xrdata(map_extent, u, delt_x=delt_x, delt_y=delt_y)
    v=utl.cut_xrdata(map_extent, v, delt_x=delt_x, delt_y=delt_y)
    wvfl=utl.cut_xrdata(map_extent, wvfl, delt_x=delt_x, delt_y=delt_y)

    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    wvfl=utl.mask_terrian(wvfl_lev,psfc,wvfl)

    gh.attrs['model']=model
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

    moisture_graphics.draw_gh_uv_wvfl(
        wvfl=wvfl, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)