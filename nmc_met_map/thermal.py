# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import thermal_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr
from scipy.ndimage import gaussian_filter

def gh_uv_thetae(initTime=None, fhour=6, day_back=0,model='GRAPES_GFS',
    gh_lev=500,uv_lev=850,th_lev=850,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False,**kwargs):

# prepare data
    if(data_source =='MICAPS'):    
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='THETAE',lvl=th_lev),
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
        thetae = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        if thetae is None:
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

            thetae=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PPT'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=th_lev, fcst_ele="PPT", units='K')
            if thetae is None:
                return                

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.

        except KeyError:
            raise ValueError('Can not find all data needed')                
# set map extent
    if(area != '全国'):
        south_China_sea=False

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
    thetae=utl.cut_xrdata(map_extent, thetae, delt_x=delt_x, delt_y=delt_y)

    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    thetae=utl.mask_terrian(th_lev,psfc,thetae)

    gh.attrs['model']=model
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

# draw
    thermal_graphics.draw_gh_uv_thetae(
        thetae=thetae, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def gh_uv_tmp(initTime=None, fhour=6, day_back=0,model='ECMWF',
    gh_lev=500,uv_lev=850,tmp_lev=850,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False,**kwargs):

#prepare data
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=tmp_lev),
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
        if tmp is None:
            return   
        psfc = MICAPS_IO.get_model_grid(data_dir[4], filename=filename)
        
    if(data_source=='CIMISS'):
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

            tmp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEM'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=tmp_lev, fcst_ele="TEM", units='K')
            if tmp is None:
                return   
            tmp['data'].values=tmp['data'].values-273.15

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.

        except KeyError:
            raise ValueError('Can not find all data needed')                
# set map extent
    if(area != '全国'):
        south_China_sea=False

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
    tmp=utl.cut_xrdata(map_extent, tmp, delt_x=delt_x, delt_y=delt_y)

    gh=utl.mask_terrian(gh_lev,psfc,gh)
    u=utl.mask_terrian(uv_lev,psfc,u)
    tmp=utl.mask_terrian(tmp_lev,psfc,tmp)

    gh.attrs['model']=model
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])

#draw
    thermal_graphics.draw_gh_uv_tmp(
        tmp=tmp, gh=gh, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)        


def TMP850_anomaly_uv(initTime=None, fhour=6, day_back=0,model='ECMWF',
    uv_lev=850,tmp_lev=850,
    map_ratio=13/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False,**kwargs):

#prepare data
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=tmp_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PSFC')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

        # retrieve data from micaps server
        u = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)
        if u is None:
            return
            
        v = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        if v is None:
            return
        tmp = MICAPS_IO.get_model_grid(data_dir[2], filename=filename)
        if tmp is None:
            return   

        psfc = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)

    if(data_source=='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
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

            tmp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEM'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=tmp_lev, fcst_ele="TEM", units='K')
            if tmp is None:
                return   
            tmp['data'].values=tmp['data'].values-273.15

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed')                
# set map extent
    tmp_anm=utl.get_var_anm(tmp+273.15,Var_name='t850')

    if(area != '全国'):
        south_China_sea=False

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=utl.get_map_extent(cntr_pnt,zoom_ratio,map_ratio)
    tmp['data'].values=gaussian_filter(tmp['data'].values,5)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    tmp=utl.mask_terrian(tmp_lev,psfc,tmp)
    tmp_anm=utl.mask_terrian(tmp_lev,psfc,tmp_anm)
#to solve the problem of labels on all the contours
    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    tmp=utl.cut_xrdata(map_extent,tmp,delt_x=delt_x,delt_y=delt_y)
    u=utl.cut_xrdata(map_extent,u,delt_x=delt_x,delt_y=delt_y)
    v=utl.cut_xrdata(map_extent,v,delt_x=delt_x,delt_y=delt_y)
    tmp_anm=utl.cut_xrdata(map_extent,tmp_anm,delt_x=delt_x,delt_y=delt_y)

    tmp.attrs['model']=model
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])
#draw
    thermal_graphics.draw_gh_uv_tmp_anm(
        tmp=tmp, tmp_anm=tmp_anm, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)        

def TMP850_extreme_uv(initTime=None, fhour=6, day_back=0,model='ECMWF',
    uv_lev=850,tmp_lev=850,
    map_ratio=13/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,data_source='MICAPS',
    Global=False,**kwargs):

#prepare data
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=tmp_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PSFC')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

        # retrieve data from micaps server
        u = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)
        if u is None:
            return
            
        v = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        if v is None:
            return
        tmp = MICAPS_IO.get_model_grid(data_dir[2], filename=filename)
        if tmp is None:
            return   

        psfc = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)

    if(data_source=='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
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

            tmp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEM'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=tmp_lev, fcst_ele="TEM", units='K')
            if tmp is None:
                return   
            tmp['data'].values=tmp['data'].values-273.15

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed')                
# set map extent
    tmp_extr=utl.get_var_extr(tmp+273.15,Var_name='t850')

    if(area != '全国'):
        south_China_sea=False

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=utl.get_map_extent(cntr_pnt,zoom_ratio,map_ratio)
    tmp['data'].values=gaussian_filter(tmp['data'].values,5)
    u=utl.mask_terrian(uv_lev,psfc,u)
    v=utl.mask_terrian(uv_lev,psfc,v)
    tmp=utl.mask_terrian(tmp_lev,psfc,tmp)
    tmp_extr=utl.mask_terrian(tmp_lev,psfc,tmp_extr)
#to solve the problem of labels on all the contours
    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    tmp=utl.cut_xrdata(map_extent,tmp,delt_x=delt_x,delt_y=delt_y)
    u=utl.cut_xrdata(map_extent,u,delt_x=delt_x,delt_y=delt_y)
    v=utl.cut_xrdata(map_extent,v,delt_x=delt_x,delt_y=delt_y)
    tmp_extr=utl.cut_xrdata(map_extent,tmp_extr,delt_x=delt_x,delt_y=delt_y)

    tmp.attrs['model']=model
    uv=xr.merge([u.rename({'data': 'u'}),v.rename({'data': 'v'})])
#draw
    thermal_graphics.draw_gh_uv_tmp_extr(
        tmp=tmp, tmp_extr=tmp_extr, uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)