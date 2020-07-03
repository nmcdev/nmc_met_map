import numpy as np
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import elements_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr
from datetime import datetime, timedelta
import pkg_resources

def dT2m_mx24(initTime=None, fhour=48, day_back=0,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    data_dir = [utl.Cassandra_dir(data_type='surface',data_source='ECMWF',var_name='Tmx3_2m')]
    fhours1 = np.arange(fhour-21, fhour+1, 3)
    if(initTime is None):
        initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour)[0:8]
    filenames1 = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours1]

    if(fhour >= 48):
        fhours2 = np.arange(fhour-21-24, fhour+1-24, 3)
        filenames2 = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour >=36 and fhour < 48):
        fhours2 = np.arange(fhour-21+12-24, fhour+1+12-24, 3)
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=12)).strftime('%Y%m%d%H')[2:10]
        filenames2=[initTime2+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour >=24 and fhour < 36):
        fhours2 = np.arange(fhour-21+24-24, fhour+1+24-24, 3)
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=24)).strftime('%Y%m%d%H')[2:10]
        filenames2=[initTime2+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour < 24):
        print('fhour should > 24')
        return

# prepare data
    T_2m1 = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames1)
    Tmx_2m1=T_2m1.isel(time=[-1]).copy()
    Tmx_2m1['data'].values[0,:,:]=np.max(T_2m1['data'].values,axis=0)

    T_2m2 = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames2)
    Tmx_2m2=T_2m2.isel(time=[-1]).copy()
    Tmx_2m2['data'].values[0,:,:]=np.max(T_2m2['data'].values,axis=0)

    dTmx_2m=Tmx_2m1.copy()
    dTmx_2m['data'].values=Tmx_2m1['data'].values-Tmx_2m2['data'].values
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
    mask1 = (dTmx_2m['lon'] > map_extent[0]-delt_x) & (dTmx_2m['lon'] < map_extent[1]+delt_x) & (dTmx_2m['lat'] > map_extent[2]-delt_y) & (dTmx_2m['lat'] < map_extent[3]+delt_y)
    dTmx_2m=dTmx_2m.where(mask1,drop=True)

#- to solve the problem of labels on all the contours

    dTmx_2m.attrs['model']='ECMWF'
    dTmx_2m.attrs['title']='2米最高温度24小时变温'

    elements_graphics.draw_dT_2m(
        dT_2m=dTmx_2m,T_type='dT2m_mx',
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)        

def dT2m_mn24(initTime=None, fhour=48, day_back=0,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    data_dir = [utl.Cassandra_dir(data_type='surface',data_source='ECMWF',var_name='Tmn3_2m')]
    fhours1 = np.arange(fhour-21, fhour+1, 3)
    if(initTime is None):
        initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour)[0:8]
    filenames1 = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours1]

    if(fhour >= 48):
        fhours2 = np.arange(fhour-21-24, fhour+1-24, 3)
        filenames2 = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour >=36 and fhour < 48):
        fhours2 = np.arange(fhour-21+12-24, fhour+1+12-24, 3)
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=12)).strftime('%Y%m%d%H')[2:10]
        filenames2=[initTime2+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour >=24 and fhour < 36):
        fhours2 = np.arange(fhour-21+24-24, fhour+1+24-24, 3)
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=24)).strftime('%Y%m%d%H')[2:10]
        filenames2=[initTime2+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour < 24):
        print('fhour should > 24')
        return
        
# prepare data
    T_2m1 = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames1)
    Tmn_2m1=T_2m1.isel(time=[-1]).copy()
    Tmn_2m1['data'].values[0,:,:]=np.min(T_2m1['data'].values,axis=0)

    T_2m2 = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames2)
    Tmn_2m2=T_2m2.isel(time=[-1]).copy()
    Tmn_2m2['data'].values[0,:,:]=np.min(T_2m2['data'].values,axis=0)

    dTmn_2m=Tmn_2m1.copy()
    dTmn_2m['data'].values=Tmn_2m1['data'].values-Tmn_2m2['data'].values
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
    mask1 = (dTmn_2m['lon'] > map_extent[0]-delt_x) & (dTmn_2m['lon'] < map_extent[1]+delt_x) & (dTmn_2m['lat'] > map_extent[2]-delt_y) & (dTmn_2m['lat'] < map_extent[3]+delt_y)
    dTmn_2m=dTmn_2m.where(mask1,drop=True)

#- to solve the problem of labels on all the contours

    dTmn_2m.attrs['model']='ECMWF'
    dTmn_2m.attrs['title']='2米最低温度24小时变温'

    elements_graphics.draw_dT_2m(
        dT_2m=dTmn_2m,T_type='dT2m_mn',
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def dT2m_mean24(initTime=None, fhour=48, day_back=0,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    data_dir = [utl.Cassandra_dir(data_type='surface',data_source='ECMWF',var_name='T2m')]
    fhours1 = np.arange(fhour-21, fhour+1, 3)
    if(initTime is None):
        initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour)[0:8]
    filenames1 = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours1]

    if(fhour >= 48):
        fhours2 = np.arange(fhour-21-24, fhour+1-24, 3)
        filenames2 = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour >=36 and fhour < 48):
        fhours2 = np.arange(fhour-21+12-24, fhour+1+12-24, 3)
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=12)).strftime('%Y%m%d%H')[2:10]
        filenames2=[initTime2+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour >=24 and fhour < 36):
        fhours2 = np.arange(fhour-21+24-24, fhour+1+24-24, 3)
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=24)).strftime('%Y%m%d%H')[2:10]
        filenames2=[initTime2+'.'+str(fhour).zfill(3) for fhour in fhours2]
    if(fhour < 24):
        print('fhour should > 24')
        return
        
# prepare data
    T_2m1 = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames1)
    Tmn_2m1=T_2m1.isel(time=[-1]).copy()
    Tmn_2m1['data'].values[0,:,:]=np.mean(T_2m1['data'].values,axis=0)

    T_2m2 = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames2)
    Tmn_2m2=T_2m2.isel(time=[-1]).copy()
    Tmn_2m2['data'].values[0,:,:]=np.mean(T_2m2['data'].values,axis=0)

    dTmn_2m=Tmn_2m1.copy()
    dTmn_2m['data'].values=Tmn_2m1['data'].values-Tmn_2m2['data'].values
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
    mask1 = (dTmn_2m['lon'] > map_extent[0]-delt_x) & (dTmn_2m['lon'] < map_extent[1]+delt_x) & (dTmn_2m['lat'] > map_extent[2]-delt_y) & (dTmn_2m['lat'] < map_extent[3]+delt_y)
    dTmn_2m=dTmn_2m.where(mask1,drop=True)

#- to solve the problem of labels on all the contours

    dTmn_2m.attrs['model']='ECMWF'
    dTmn_2m.attrs['title']='2米最低温度24小时变温'

    elements_graphics.draw_dT_2m(
        dT_2m=dTmn_2m,T_type='dT2m_meann',
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)