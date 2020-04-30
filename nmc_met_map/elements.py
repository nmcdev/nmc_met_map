# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import elements_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr

def T2m_all_type(initTime=None, fhour=24, day_back=0,model='中央气象台中短期指导',Var_plot='Tmn_2m',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],data_source='MICAPS',
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

# prepare data
    if(data_source =='MICAPS'):    
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name=Var_plot)]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

        T_2m = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)
        if T_2m is None:
            return

    if(data_source =='CIMISS'): 
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
            T_2m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEF2'),
                        levattrs={'long_name':'Mean_sea_level', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TEF2", units='K')
            if T_2m is None:
                return
            T_2m['data'].values=T_2m['data'].values-273.15

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

#+ to solve the problem of labels on all the contours
    mask1 = (T_2m['lon'] > map_extent[0]-delt_x) & (T_2m['lon'] < map_extent[1]+delt_x) & (T_2m['lat'] > map_extent[2]-delt_y) & (T_2m['lat'] < map_extent[3]+delt_y)
    T_2m=T_2m.where(mask1,drop=True)

    titles={
        'Tmn_2m':'过去24小时2米最低温度',
        'Tmx_2m':'过去24小时2米最高温度',
        'T2m':'2米温度'
        }
#- to solve the problem of labels on all the contours
    T_2m.attrs['model']=model
    T_2m.attrs['title']=titles[Var_plot]

    elements_graphics.draw_T_2m(
        T_2m=T_2m,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)
    
def T2m_mslp_uv10m(initTime=None, fhour=6, day_back=0,model='ECMWF',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],data_source='MICAPS',
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

# prepare data
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='u10m'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='v10m'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='T2m')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

        # retrieve data from micaps server
        mslp = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)
        if mslp is None:
            return
        
        u10m = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        if u10m is None:
            return
            
        v10m = MICAPS_IO.get_model_grid(data_dir[2], filename=filename)
        if v10m is None:
            return
        t2m = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
        if t2m is None:
            return   

    if(data_source =='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
            t2m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEF2'),
                        fcst_level=0, fcst_ele="TEF2", units='K')
            if t2m is None:
                return
            t2m['data'].values=t2m['data'].values-273.15

            u10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU10'),
                        fcst_level=0, fcst_ele="WIU10", units='m/s')
            if u10m is None:
                return

            v10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV10'),
                        fcst_level=0, fcst_ele="WIV10", units='m/s')
            if v10m is None:
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

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
    if(area != '全国'):
        south_China_sea=False

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

#+ to solve the problem of labels on all the contours
    mask1 = (t2m['lon'] > map_extent[0]-delt_x) & (t2m['lon'] < map_extent[1]+delt_x) & (t2m['lat'] > map_extent[2]-delt_y) & (t2m['lat'] < map_extent[3]+delt_y)
    mask2 = (u10m['lon'] > map_extent[0]-delt_x) & (u10m['lon'] < map_extent[1]+delt_x) & (u10m['lat'] > map_extent[2]-delt_y) & (u10m['lat'] < map_extent[3]+delt_y)
    mask3 = (mslp['lon'] > map_extent[0]-delt_x) & (mslp['lon'] < map_extent[1]+delt_x) & (mslp['lat'] > map_extent[2]-delt_y) & (mslp['lat'] < map_extent[3]+delt_y)

    t2m=t2m.where(mask1,drop=True)
    t2m.attrs['model']=model
    u10m=u10m.where(mask2,drop=True)
    v10m=v10m.where(mask2,drop=True)
    uv10m=xr.merge([u10m.rename({'data': 'u10m'}),v10m.rename({'data': 'v10m'})])
    mslp=mslp.where(mask3,drop=True)
    mslp.attrs['model']=model

# draw
    elements_graphics.draw_T2m_mslp_uv10m(
        t2m=t2m, mslp=mslp, uv10m=uv10m,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)        

def mslp_gust10m(initTime=None, fhour=6, day_back=0,model='ECMWF',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],data_source='MICAPS',
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    # micaps data directory
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='10M_GUST_6H')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

        # retrieve data from micaps server
        mslp = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)
        if mslp is None:
            return
        
        gust = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        if gust is None:
            return

    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            gust=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GUST10T6'),
                        fcst_level=0, fcst_ele="GUST10T6", units='m/s')
            if gust is None:
                return

            if(model == 'ECMWF'):
                mslp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='GSSP'),
                            fcst_level=0, fcst_ele="GSSP", units='Pa')
            else:
                mslp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='SSP'),
                            fcst_level=0, fcst_ele="SSP", units='Pa')
            if mslp is None:
                return
            mslp['data']=mslp['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed') 
    # prepare data

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    if(area != '全国'):
        south_China_sea=False

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

#+ to solve the problem of labels on all the contours
    mask1 = (gust['lon'] > map_extent[0]-delt_x) & (gust['lon'] < map_extent[1]+delt_x) & (gust['lat'] > map_extent[2]-delt_y) & (gust['lat'] < map_extent[3]+delt_y)
    mask2 = (mslp['lon'] > map_extent[0]-delt_x) & (mslp['lon'] < map_extent[1]+delt_x) & (mslp['lat'] > map_extent[2]-delt_y) & (mslp['lat'] < map_extent[3]+delt_y)
   
    gust=gust.where(mask1,drop=True)
    mslp=mslp.where(mask2,drop=True)
    mslp.attrs['model']=model

    elements_graphics.draw_mslp_gust10m(
        gust=gust, mslp=mslp,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def low_level_wind(initTime=None, fhour=6, day_back=0,model='ECMWF',wind_level='100m',data_source='MICAPS',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    # micaps data directory
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='u'+wind_level),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='v'+wind_level)]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

        # retrieve data from micaps server
        u10m = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)
        if u10m is None:
            return
        
        v10m = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        if v10m is None:
            return
            
        init_time = v10m.coords['forecast_reference_time'].values

        # prepare data

        if(area != None):
            cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
        if(area != '全国'):
            south_China_sea=False
    if(data_source =='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
            u10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'+wind_level[0:-1]),
                        fcst_level=0, fcst_ele="WIU"+wind_level[0:-1], units='m*s-1')
            if u10m is None:
                return

            v10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'+wind_level[0:-1]),
                        fcst_level=0, fcst_ele="WIV"+wind_level[0:-1], units='m*s-1')
            if v10m is None:
                return
        except KeyError:
            raise ValueError('Can not find all data needed') 

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1

#+ to solve the problem of labels on all the contours
    mask1 = (v10m['lon'] > map_extent[0]-delt_x) & (v10m['lon'] < map_extent[1]+delt_x) & (v10m['lat'] > map_extent[2]-delt_y) & (v10m['lat'] < map_extent[3]+delt_y)

    u10m=u10m.where(mask1,drop=True)
    v10m=v10m.where(mask1,drop=True)
    uv=xr.merge([u10m.rename({'data': 'u'}),v10m.rename({'data': 'v'})])
    uv.attrs['model']=model
    uv.attrs['level']=wind_level

    elements_graphics.draw_low_level_wind(
        uv=uv,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)      