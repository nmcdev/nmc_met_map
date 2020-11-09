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
import pkg_resources
import nmc_met_map.product.diagnostic.elements.horizontal.SCMOC as draw_SCMOC

def T2m_zero_heatwaves(initTime=None, fhour=24, day_back=0,model='中央气象台中短期指导',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],data_source='MICAPS',
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

# prepare data
    if(data_source =='MICAPS'):    
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='T2m')]
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
                        fcst_level=0, fcst_ele='TEF2', units='K')
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

#- to solve the problem of labels on all the contours
    T_2m.attrs['model']=model
    T_2m.attrs['title']='2米温度'

    elements_graphics.draw_T_2m(
        T_2m=T_2m,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def T2m_mx24(initTime=None, fhour=24, day_back=0,model='中央气象台中短期指导',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],data_source='MICAPS',area=None,
    **kargws):

# prepare data
    if(data_source =='MICAPS'):    
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='Tmx_2m')]

            if(initTime != None):
                filename = utl.model_filename(initTime, fhour)
            else:
                filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

            Tmx_2m = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)

        except:
            try:
                data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='Tmx3_2m')]
            except:
                data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='T2m')]
            fhours = np.arange(fhour-21, fhour+1, 3)
            if(initTime is None):
                initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour)[0:8]
            filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
            T_2m = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames)

            Tmx_2m=T_2m.isel(time=[-1]).copy()
            Tmx_2m['data'].values[0,:,:]=np.max(T_2m['data'].values,axis=0)

    if(data_source =='CIMISS'): 
        # get filename
        fhours = np.arange(fhour-18, fhour+1, 3)
        if(initTime is None):
            initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)[0:8]
        try:
            # retrieve data from CMISS server        
            T_2m=CMISS_IO.cimiss_model_by_times('20'+initTime,valid_times=fhours,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='MX2T6'),
                        fcst_level=0, fcst_ele='MX2T6', units='K',allExists=False)
        except:
            T_2m=CMISS_IO.cimiss_model_by_times('20'+initTime,valid_times=fhours,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEF2'),
                        fcst_level=0, fcst_ele='TEF2', units='K',allExists=False)
            if T_2m is None:
                return
        T_2m['data'].values=T_2m['data'].values-273.15
        Tmx_2m=T_2m.isel(time=[-1]).copy()
        Tmx_2m['data'].values[0,:,:]=np.max(T_2m['data'].values,axis=0)

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
    mask1 = (Tmx_2m['lon'] > map_extent[0]-delt_x) & (Tmx_2m['lon'] < map_extent[1]+delt_x) & (Tmx_2m['lat'] > map_extent[2]-delt_y) & (Tmx_2m['lat'] < map_extent[3]+delt_y)
    Tmx_2m=Tmx_2m.where(mask1,drop=True)

#- to solve the problem of labels on all the contours
    Tmx2=xr.DataArray(np.squeeze(Tmx_2m['data'].values,axis=0),name='data',
                    coords={'time':('time',[Tmx_2m['time'].values[0]]),
                            'fhour':('time',[fhour]),
                            'lat':('lat',Tmx_2m['lat'].values),
                            'lon':('lon',Tmx_2m['lon'].values)
                            },
                    dims=('time','lat','lon'),
                    attrs={'model_name':'中央气象台中短期指导',
                           'var_name':'2米最高温度',
                           'vhours':24})

    draw_SCMOC.draw_TMP2(TMP2=Tmx2,map_extent=map_extent,**kargws)


def T2m_mn24(initTime=None, fhour=24, day_back=0,model='中央气象台中短期指导',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],data_source='MICAPS',
    south_China_sea=True,area =None,city=False,output_dir=None,
    Global=False):

# prepare data
    if(data_source =='MICAPS'):    
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='Tmn_2m')]

            if(initTime != None):
                filename = utl.model_filename(initTime, fhour)
            else:
                filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

            Tmn_2m = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)

        except:
            try:
                data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='Tmn3_2m')]
            except:
                data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='T2m')]
            fhours = np.arange(fhour-21, fhour+1, 3)
            if(initTime is None):
                initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour)[0:8]
            filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
            T_2m = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames)

            Tmn_2m=T_2m.isel(time=[-1]).copy()
            Tmn_2m['data'].values[0,:,:]=np.min(T_2m['data'].values,axis=0)

    if(data_source =='CIMISS'): 
        # get filename
        fhours = np.arange(fhour-18, fhour+1, 3)
        if(initTime is None):
            initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)[0:8]
        try:
            # retrieve data from CMISS server        
            T_2m=CMISS_IO.cimiss_model_by_times('20'+initTime,valid_times=fhours,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='MN2T6'),
                        fcst_level=0, fcst_ele='MN2T6', units='K',allExists=False)
        except:
            T_2m=CMISS_IO.cimiss_model_by_times('20'+initTime,valid_times=fhours,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEF2'),
                        fcst_level=0, fcst_ele='TEF2', units='K',allExists=False)
            if T_2m is None:
                return
        T_2m['data'].values=T_2m['data'].values-273.15
        Tmn_2m=T_2m.isel(time=[-1]).copy()
        Tmn_2m['data'].values[0,:,:]=np.min(T_2m['data'].values,axis=0)

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
    mask1 = (Tmn_2m['lon'] > map_extent[0]-delt_x) & (Tmn_2m['lon'] < map_extent[1]+delt_x) & (Tmn_2m['lat'] > map_extent[2]-delt_y) & (Tmn_2m['lat'] < map_extent[3]+delt_y)
    Tmn_2m=Tmn_2m.where(mask1,drop=True)

#- to solve the problem of labels on all the contours

    Tmn_2m.attrs['model']=model
    Tmn_2m.attrs['title']='2米最低温度'

    elements_graphics.draw_T_2m(
        T_2m=Tmn_2m,#T_type='T_mn',
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)                

def T2m_mean24(initTime=None, fhour=24, day_back=0,model='中央气象台中短期指导',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],data_source='MICAPS',
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

# prepare data
    if(data_source =='MICAPS'):    
        data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='T2m')]
        fhours = np.arange(fhour-21, fhour+1, 3)
        if(initTime is None):
            initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour)[0:8]
        filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
        T_2m = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames)

        Tmean_2m=T_2m.isel(time=[-1]).copy()
        Tmean_2m['data'].values[0,:,:]=np.mean(T_2m['data'].values,axis=0)

    if(data_source =='CIMISS'): 
        # get filename
        fhours = np.arange(fhour-18, fhour+1, 3)
        if(initTime is None):
            initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)[0:8]
        T_2m=CMISS_IO.cimiss_model_by_times('20'+initTime,valid_times=fhours,
                    data_code=utl.CMISS_data_code(data_source=model,var_name='TEF2'),
                    fcst_level=0, fcst_ele='TEF2', units='K',allExists=False)
        T_2m['data'].values=T_2m['data'].values-273.15
        Tmean_2m=T_2m.isel(time=[-1]).copy()
        Tmean_2m['data'].values[0,:,:]=np.min(T_2m['data'].values,axis=0)

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
    mask1 = (Tmean_2m['lon'] > map_extent[0]-delt_x) & (Tmean_2m['lon'] < map_extent[1]+delt_x) & (Tmean_2m['lat'] > map_extent[2]-delt_y) & (Tmean_2m['lat'] < map_extent[3]+delt_y)
    Tmean_2m=Tmean_2m.where(mask1,drop=True)

#- to solve the problem of labels on all the contours

    Tmean_2m.attrs['model']=model
    Tmean_2m.attrs['title']='2米平均温度'

    elements_graphics.draw_T_2m(
        T_2m=Tmean_2m,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)  

def T2m_mslp_uv10m(initTime=None, fhour=6, day_back=0,model='ECMWF',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],data_source='MICAPS',
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
        u10m = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        v10m = MICAPS_IO.get_model_grid(data_dir[2], filename=filename)
        t2m = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)

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
            t2m['data'].values=t2m['data'].values-273.15

            u10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU10'),
                        fcst_level=0, fcst_ele="WIU10", units='m/s')

            v10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV10'),
                        fcst_level=0, fcst_ele="WIV10", units='m/s')

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

def mslp_gust10m(initTime=None, fhour=6, day_back=0,t_gap=3,model='ECMWF',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],data_source='MICAPS',
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    # micaps data directory
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='10M_GUST_'+'%i'%t_gap+'H')]
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
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GUST10T'+'%i'%t_gap),
                        fcst_level=0, fcst_ele="GUST10T"+'%i'%t_gap, units='m/s')
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

    if(area != '全国'):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
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
    gust.attrs['t_gap']=t_gap
    mslp=mslp.where(mask2,drop=True)
    mslp.attrs['model']=model

    elements_graphics.draw_mslp_gust10m(
        gust=gust, mslp=mslp,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def mslp_gust10m_uv10m(initTime=None, fhour=6, day_back=0,t_gap=3,model='ECMWF',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],data_source='MICAPS',
    south_China_sea=True,area = '全国',city=False,output_dir=None,
    Global=False):

    # micaps data directory
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='10M_GUST_'+'%i'%t_gap+'H'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='u10m'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='v10m')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)

        # retrieve data from micaps server
        mslp = MICAPS_IO.get_model_grid(data_dir[0], filename=filename)
        gust = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        u10m = MICAPS_IO.get_model_grid(data_dir[2], filename=filename)
        v10m = MICAPS_IO.get_model_grid(data_dir[3], filename=filename)
    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            gust=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GUST10T'+'%i'%t_gap),
                        fcst_level=0, fcst_ele="GUST10T"+'%i'%t_gap, units='m/s')

            u10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU10'),
                        fcst_level=0, fcst_ele="WIU10", units='m/s')

            v10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV10'),
                        fcst_level=0, fcst_ele="WIV10", units='m/s')                        

            if(model == 'ECMWF'):
                mslp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='GSSP'),
                            fcst_level=0, fcst_ele="GSSP", units='Pa')
            else:
                mslp=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='SSP'),
                            fcst_level=0, fcst_ele="SSP", units='Pa')

            mslp['data']=mslp['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed') 
    # prepare data

    if(area != '全国'):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
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
    mask3 = (u10m['lon'] > map_extent[0]-delt_x) & (u10m['lon'] < map_extent[1]+delt_x) & (u10m['lat'] > map_extent[2]-delt_y) & (u10m['lat'] < map_extent[3]+delt_y)
    gust=gust.where(mask1,drop=True)
    gust.attrs['t_gap']=t_gap
    mslp=mslp.where(mask2,drop=True)
    mslp.attrs['model']=model
    u10m=u10m.where(mask3,drop=True)
    v10m=v10m.where(mask2,drop=True)
    uv10m=xr.merge([u10m.rename({'data': 'u10m'}),v10m.rename({'data': 'v10m'})])

    elements_graphics.draw_mslp_gust10m_uv10m(
        gust=gust, mslp=mslp,uv10m=uv10m,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)        

def low_level_wind(initTime=None, fhour=6, day_back=0,model='ECMWF',wind_level='100m',data_source='MICAPS',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
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

            v10m=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'+wind_level[0:-1]),
                        fcst_level=0, fcst_ele="WIV"+wind_level[0:-1], units='m*s-1')
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