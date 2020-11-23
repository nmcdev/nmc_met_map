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
import nmc_met_map.product.diagnostic.elements.horizontal.SCMOC as draw_SCMOC

def dT2m_mx24(initTime=None, fhour=48,day_back=0,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],area=None,south_China_sea=True,
    **kargws):

    data_dir = [utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='Tmx_2m')]
    fhours1 = np.arange(fhour-24, fhour+1, 24)
    if(initTime is None):
        initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour)[0:8]
    filename1 = initTime+'.'+str(fhour).zfill(3)

    if(fhour >= 48):
        fhour2 = fhour-24
        filename2 = initTime+'.'+str(fhour2).zfill(3)
    if(fhour >=36 and fhour < 48):
        fhour2 = fhour-12
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=12)).strftime('%Y%m%d%H')[2:10]
        filename2=initTime2+'.'+str(fhour2).zfill(3)
    if(fhour >=24 and fhour < 36):
        fhour2 = fhour
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=24)).strftime('%Y%m%d%H')[2:10]
        filename2=initTime2+'.'+str(fhour2).zfill(3)
    if(fhour < 24):
        print('fhour should > 24')
        return

# prepare data
    T_2m1 = MICAPS_IO.get_model_grid(data_dir[0], filename=filename1)

    T_2m2 = MICAPS_IO.get_model_grid(data_dir[0], filename=filename2)

    dTmx_2m=T_2m1.copy()
    dTmx_2m['data'].values=T_2m1['data'].values-T_2m2['data'].values
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

#+ to solve the problem of labels on all the contours
    mask1 = (dTmx_2m['lon'] > map_extent[0]-delt_x) & (dTmx_2m['lon'] < map_extent[1]+delt_x) & (dTmx_2m['lat'] > map_extent[2]-delt_y) & (dTmx_2m['lat'] < map_extent[3]+delt_y)
    dTmx_2m=dTmx_2m.where(mask1,drop=True)

#- to solve the problem of labels on all the contours
    dTmx2=xr.DataArray(np.squeeze(dTmx_2m['data'].values,axis=0),name='data',
                    coords={'time':('time',[dTmx_2m['forecast_reference_time'].values]),
                            'fhour':('time',[fhour]),
                            'lat':('lat',dTmx_2m['lat'].values),
                            'lon':('lon',dTmx_2m['lon'].values)
                            },
                    dims=('time','lat','lon'),
                    attrs={'model_name':'中央气象台中短期指导',
                           'var_name':'2米最高温度24小时变温',
                           'vhours':24})

    draw_SCMOC.draw_dT2m(dTmx2,map_extent=map_extent,south_China_sea=south_China_sea,**kargws)

def dT2m_mn24(initTime=None, fhour=48,day_back=0,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],area=None,south_China_sea=True,
    **kargws):

    data_dir = [utl.Cassandra_dir(data_type='surface',data_source='中央气象台中短期指导',var_name='Tmn_2m')]
    fhours1 = np.arange(fhour-24, fhour+1, 24)
    if(initTime is None):
        initTime=utl.filename_day_back_model(day_back=day_back,fhour=fhour)[0:8]
    filename1 = initTime+'.'+str(fhour).zfill(3)

    if(fhour >= 48):
        fhour2 = fhour-24
        filename2 = initTime+'.'+str(fhour2).zfill(3)
    if(fhour >=36 and fhour < 48):
        fhour2 = fhour-12
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=12)).strftime('%Y%m%d%H')[2:10]
        filename2=initTime2+'.'+str(fhour2).zfill(3)
    if(fhour >=24 and fhour < 36):
        fhour2 = fhour
        initTime2=(datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=24)).strftime('%Y%m%d%H')[2:10]
        filename2=initTime2+'.'+str(fhour2).zfill(3)
    if(fhour < 24):
        print('fhour should > 24')
        return

# prepare data
    T_2m1 = MICAPS_IO.get_model_grid(data_dir[0], filename=filename1)

    T_2m2 = MICAPS_IO.get_model_grid(data_dir[0], filename=filename2)

    dTmx_2m=T_2m1.copy()
    dTmx_2m['data'].values=T_2m1['data'].values-T_2m2['data'].values
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

#+ to solve the problem of labels on all the contours
    mask1 = (dTmx_2m['lon'] > map_extent[0]-delt_x) & (dTmx_2m['lon'] < map_extent[1]+delt_x) & (dTmx_2m['lat'] > map_extent[2]-delt_y) & (dTmx_2m['lat'] < map_extent[3]+delt_y)
    dTmx_2m=dTmx_2m.where(mask1,drop=True)

#- to solve the problem of labels on all the contours
    dTmx2=xr.DataArray(np.squeeze(dTmx_2m['data'].values,axis=0),name='data',
                    coords={'time':('time',[dTmx_2m['forecast_reference_time'].values]),
                            'fhour':('time',[fhour]),
                            'lat':('lat',dTmx_2m['lat'].values),
                            'lon':('lon',dTmx_2m['lon'].values)
                            },
                    dims=('time','lat','lon'),
                    attrs={'model_name':'中央气象台中短期指导',
                           'var_name':'2米最低温度24小时变温',
                           'vhours':24})

    draw_SCMOC.draw_dT2m(dTmx2,map_extent=map_extent,south_China_sea=south_China_sea,**kargws)