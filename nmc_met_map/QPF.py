# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import QPF_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
from datetime import datetime, timedelta
import xarray as xr
from scipy.ndimage import gaussian_filter
import copy

def gh_rain(initTime=None, fhour=24, day_back=0,model='ECMWF',
    gh_lev=500,atime=6,data_source='MICAPS',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area =None,city=False,output_dir=None,
    Global=False,**kwargs):

# prepare data
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=str(gh_lev)),
                        utl.Cassandra_dir(data_type='surface',data_source=model,
                        var_name='RAIN'+ '%02d'%atime),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PSFC')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
            if(atime > 3):
                filename_gh=utl.model_filename(initTime, int(fhour-atime/2))
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
            if(atime > 3):
                filename_gh=utl.filename_day_back_model(day_back=day_back,fhour=int(fhour-atime/2))

        # retrieve data from micaps server
        gh = MICAPS_IO.get_model_grid(data_dir[0], filename=filename_gh)
        if gh is None:
            return
        
        rain = MICAPS_IO.get_model_grid(data_dir[1], filename=filename)
        if rain is None:
            return

        psfc = MICAPS_IO.get_model_grid(data_dir[2], filename=filename)

    if(data_source =='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
            if(atime > 3):
                filename_gh=utl.model_filename(initTime,fhour=int(fhour-atime/2),UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
            if(atime > 3):
                filename_gh=utl.filename_day_back_model(day_back=day_back,fhour=int(fhour-atime/2),UTC=True)
        try:
            # retrieve data from CIMISS server        
            gh=CMISS_IO.cimiss_model_by_time('20'+filename_gh[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GPH'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=gh_lev, fcst_ele="GPH", units='gpm')
            if gh is None:
                return
            gh['data'].values=gh['data'].values/10.

            TPE1=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
            if TPE1 is None:
                return    

            TPE2=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour-atime,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
            if TPE2 is None:
                return 

            psfc=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed')
        rain=TPE1.copy(deep=True)
        rain['data'].values=TPE1['data'].values-TPE2['data'].values

# set map extent
    if(area != None):
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
    rain=utl.cut_xrdata(map_extent, rain, delt_x=delt_x, delt_y=delt_y)

    gh=utl.mask_terrian(gh_lev,psfc,gh)

    gh.attrs['model']=model
    gh.attrs['lev']=gh_lev
    rain.attrs['atime']=atime

# draw
    QPF_graphics.draw_gh_rain(
        rain=rain, gh=gh,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def mslp_rain_snow(initTime=None, fhour=24, day_back=0,model='ECMWF',
    atime=6,data_source='MICAPS',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area =None,city=False,output_dir=None,
    Global=False,**kwargs):
    '''
    issues:
    1. CIMISS 上上没有上没有GRAPES-GFS的降雪，所以当data_source='CIMISS',model='GRAPES_GFS'无法出图
    '''

# prepare data
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='RAIN'+ '%02d'%atime),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='SNOW'+ '%02d'%atime),]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
            if(atime > 3):
                filename_mslp=utl.model_filename(initTime, int(fhour-atime/2))
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
            if(atime > 3):
                filename_mslp=utl.filename_day_back_model(day_back=day_back,fhour=int(fhour-atime/2))

        # retrieve data from micaps server
        mslp = get_model_grid(data_dir[0], filename=filename)
        if mslp is None:
            return
        rain = get_model_grid(data_dir[1], filename=filename)
        if rain is None:
            return        
        snow = get_model_grid(data_dir[2], filename=filename)
        if snow is None:
            return        

    if(data_source =='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
            if(atime > 3):
                filename_gh=utl.filename_day_back_model(initTime,fhour=int(fhour-atime/2),UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
            if(atime > 3):
                filename_gh=utl.filename_day_back_model(day_back=day_back,fhour=int(fhour-atime/2),UTC=True)
        try:
            # retrieve data from CIMISS server        
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

            TPE1=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
            if TPE1 is None:
                return    

            TPE2=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour-atime,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
            if TPE2 is None:
                return 

            TTSP1=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TTSP'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TTSP", units='kg*m^-2')
            if TTSP1 is None:
                return    

            TTSP2=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour-atime,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TTSP'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TTSP", units='kg*m^-2')
            if TTSP2 is None:
                return 
        except KeyError:
            raise ValueError('Can not find all data needed')
        rain=TPE1.copy(deep=True)
        rain['data'].values=(TPE1['data'].values-TPE2['data'].values)*1000

        snow=TTSP1.copy(deep=True)
        snow['data'].values=(TTSP1['data'].values-TTSP2['data'].values)*1000

# set map extent
    if(area != None):
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

    mask1 = (mslp['lon'] > map_extent[0]-delt_x) & (mslp['lon'] < map_extent[1]+delt_x) & (mslp['lat'] > map_extent[2]-delt_y) & (mslp['lat'] < map_extent[3]+delt_y)

    mask2 = (rain['lon'] > map_extent[0]-delt_x) & (rain['lon'] < map_extent[1]+delt_x) & (rain['lat'] > map_extent[2]-delt_y) & (rain['lat'] < map_extent[3]+delt_y)

    mslp=mslp.where(mask1,drop=True)
    mslp.attrs['model']=model
    rain=rain.where(mask2,drop=True)
    snow=snow.where(mask2,drop=True)
    snow.attrs['atime']=atime

    rain_snow=xr.merge([rain.rename({'data': 'rain'}),snow.rename({'data': 'snow'})])

    mask1 = ((rain_snow['rain']-rain_snow['snow'])>0.1)&(rain_snow['snow']>0.1)
    sleet=rain_snow['rain'].where(mask1)

    mask2 = ((rain_snow['rain']-rain_snow['snow'])<0.1)&(rain_snow['snow']>0.1)
    snw=rain_snow['snow'].where(mask2)

    mask3 = (rain_snow['rain']>0.1)&(rain_snow['snow']<0.1)
    rn=rain_snow['rain'].where(mask3)
    rn.attrs['atime']=atime
# draw
    QPF_graphics.draw_mslp_rain_snow(
        rain=rn, snow=snw,sleet=sleet,mslp=mslp,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)        

def Rain_evo(initTime=None, t_gap=6,t_range=[6,36], fcs_lvl=4,day_back=0,model='ECMWF',
    data_source='MICAPS',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area =None,city=False,output_dir=None,
    Global=False,**kwargs):

    fhours = np.arange(t_range[0], t_range[1]+1, t_gap)
# prepare data
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='RAIN'+ '%02d'%t_gap)]
        except KeyError:
            raise ValueError('Can not find all directories needed')
        if(initTime==None):
            initTime = MICAPS_IO.get_latest_initTime(data_dir[0])
        filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
        # retrieve data from micaps server
        rain = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames)

    if(data_source =='CIMISS'):
        if(initTime != None):
            filename = utl.model_filename(initTime, 0,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=0,fhour=0,UTC=True)
        try:
            TPE1=CMISS_IO.cimiss_model_by_times('20'+filename[0:8],valid_times=fhours,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')

            TPE2=CMISS_IO.cimiss_model_by_times('20'+filename[0:8],valid_times=fhours-t_gap,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
        except KeyError:
            raise ValueError('Can not find all data needed')
        rain=TPE1.copy(deep=True)
        rain['data'].values=(TPE1['data'].values-TPE2['data'].values)*1000


# set map extent
    if(area != None):
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
    mask1 = (rain['lon'] > map_extent[0]-delt_x) & (rain['lon'] < map_extent[1]+delt_x) & (rain['lat'] > map_extent[2]-delt_y) & (rain['lat'] < map_extent[3]+delt_y)
    rain=rain.where(mask1,drop=True)
    rain.attrs['model']=model
    rain.attrs['t_gap']=t_gap
# draw
    QPF_graphics.draw_Rain_evo(
        rain=rain,fcs_lvl=fcs_lvl,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)

def cumulated_precip_evo(initTime=None, t_gap=6,t_range=[6,36],day_back=0,model='ECMWF',
    data_source='MICAPS',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area = None,city=False,output_dir=None,
    Global=False,**kwargs):
    fhours = np.arange(t_range[0], t_range[1]+1, t_gap)
# prepare data
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='RAIN'+ '%02d'%t_gap)]
        except KeyError:
            raise ValueError('Can not find all directories needed')
        if(initTime==None):
            initTime = MICAPS_IO.get_latest_initTime(data_dir[0])
        filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
        # retrieve data from micaps server
        rain = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames)
        rain2=rain.copy(deep=True)
        for itime in range(1,len(rain['forecast_period'].values)):
            rain2['data'].values[itime,:,:]=np.sum(rain['data'].values[0:itime+1,:,:],axis=0)


    if(data_source =='CIMISS'):
        if(initTime != None):
            filename = utl.model_filename(initTime, 0,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=0,fhour=0,UTC=True)
        try:
            TPE1=CMISS_IO.cimiss_model_by_times('20'+filename[0:8],valid_times=fhours,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        levattrs={'long_name':'Height above Ground', 'units':'m', '_CoordinateAxisType':'-'},
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
        except KeyError:
            raise ValueError('Can not find all data needed')
        rain=TPE1.copy(deep=True)
        rain['data'].values=(TPE1['data'].values)


# set map extent
    if(area != None):
        south_China_sea=False

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
    else:
        map_extent=[0,0,0,0]
        map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
        map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
        map_extent[2]=cntr_pnt[1]-zoom_ratio*1
        map_extent[3]=cntr_pnt[1]+zoom_ratio*1
        
    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    mask1 = (rain['lon'] > map_extent[0]-delt_x) & (rain['lon'] < map_extent[1]+delt_x) & (rain['lat'] > map_extent[2]-delt_y) & (rain['lat'] < map_extent[3]+delt_y)
    rain2=rain2.where(mask1,drop=True)
    rain2.attrs['model']=model
    rain2.attrs['t_gap']=t_gap
# draw
    QPF_graphics.draw_cumulated_precip_evo(
        rain=rain2,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)                

def cumulated_precip(initTime=None, t_gap=6,t_range=[6,36],day_back=0,model='ECMWF',
    data_source='MICAPS',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area = None,city=False,output_dir=None,
    Global=False,**kwargs):
    fhours = np.arange(t_range[0], t_range[1]+1, t_gap)
# prepare data
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='surface',data_source=model,var_name='RAIN'+ '%02d'%t_gap)]
        except KeyError:
            raise ValueError('Can not find all directories needed')
        if(initTime==None):
            initTime = MICAPS_IO.get_latest_initTime(data_dir[0])
        filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]
        # retrieve data from micaps server
        rain = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames)
        rain2=rain.sum('time')

    if(data_source =='CIMISS'):
        if(initTime != None):
            filename = utl.model_filename(initTime, 0,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=0,fhour=0,UTC=True)
        try:
            TPE1=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhours[0],
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
            if TPE1 is None:
                return    

            TPE2=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhours[-1],
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TPE'),
                        fcst_level=0, fcst_ele="TPE", units='kg*m^-2')
            if TPE2 is None:
                return    

        except KeyError:
            raise ValueError('Can not find all data needed')
        rain=TPE1.copy(deep=True)
        rain['data'].values=(TPE2['data'].values-TPE1['data'].values)
        rain2=rain.sum('time')
# set map extent
    if(area != None):
        south_China_sea=False

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
    else:
        map_extent=[0,0,0,0]
        map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
        map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
        map_extent[2]=cntr_pnt[1]-zoom_ratio*1
        map_extent[3]=cntr_pnt[1]+zoom_ratio*1
    delt_x=(map_extent[1]-map_extent[0])*0.2
    delt_y=(map_extent[3]-map_extent[2])*0.1
    rain=utl.cut_xrdata(map_extent=map_extent,xr_input=rain,delt_y=delt_y,delt_x=delt_x)
    rain2.attrs['model']=model
    rain2.attrs['t_gap']=t_gap
    rain2.attrs['initTime']=datetime.strptime(initTime,'%y%m%d%H')
    rain2.attrs['fhour1']=fhours[0]
    rain2.attrs['fhour2']=fhours[-1]
# draw
    QPF_graphics.draw_cumulated_precip(
        rain=rain2,
        map_extent=map_extent,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global)                