# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
import nmc_met_map.lib.utility as utl
import metpy.calc as mpcalc
from metpy.units import units
import xarray as xr

from datetime import datetime, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import metpy.calc

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as lines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
import numpy as np
import numpy.ma as ma
from scipy.ndimage import gaussian_filter
from nmc_met_map.graphics import synthetical_graphics

def Miller_Composite_Chart(initTime=None, fhour=24, day_back=0,model='GRAPES_GFS',
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],data_source='MICAPS',
    Global=False,
    south_China_sea=True,area = '全国',city=False,output_dir=None,**kwargs
     ):

    # micaps data directory
    if(data_source == 'MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl='700'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl='300'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl='300'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl='500'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl='500'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl='850'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl='850'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl='700'),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl='500'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='BLI'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='Td2m'),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PRMSL')
                        ]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
            filename2 = utl.model_filename(initTime, fhour-12)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
            filename2=utl.filename_day_back_model(day_back=day_back,fhour=fhour-12)
            
        # retrieve data from micaps server
        rh_700=MICAPS_IO.get_model_grid(directory=data_dir[0],filename=filename)
        if rh_700 is None:
            return

        u_300=MICAPS_IO.get_model_grid(directory=data_dir[1],filename=filename)
        if u_300 is None:
            return

        v_300=MICAPS_IO.get_model_grid(directory=data_dir[2],filename=filename)
        if v_300 is None:
            return

        u_500=MICAPS_IO.get_model_grid(directory=data_dir[3],filename=filename)
        if u_500 is None:
            return

        v_500=MICAPS_IO.get_model_grid(directory=data_dir[4],filename=filename)
        if v_500 is None:
            return

        u_850=MICAPS_IO.get_model_grid(directory=data_dir[5],filename=filename)
        if u_850 is None:
            return

        v_850=MICAPS_IO.get_model_grid(directory=data_dir[6],filename=filename)
        if v_850 is None:
            return

        t_700=MICAPS_IO.get_model_grid(directory=data_dir[7],filename=filename)
        if t_700 is None:
            return

        hgt_500=MICAPS_IO.get_model_grid(directory=data_dir[8],filename=filename)
        if hgt_500 is None:
            return     

        hgt_500_2=MICAPS_IO.get_model_grid(directory=data_dir[8],filename=filename2)
        if hgt_500_2 is None:
            return 

        BLI=MICAPS_IO.get_model_grid(directory=data_dir[9],filename=filename)
        if BLI is None:
            return

        Td2m=MICAPS_IO.get_model_grid(directory=data_dir[10],filename=filename)
        if Td2m is None:
            return

        PRMSL=MICAPS_IO.get_model_grid(directory=data_dir[11],filename=filename)
        if PRMSL is None:
            return

        PRMSL2=MICAPS_IO.get_model_grid(directory=data_dir[11],filename=filename2)
        if PRMSL2 is None:
            return

    if(data_source =='CIMISS'):

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
            filename2 = utl.model_filename(initTime, fhour-12,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
            filename2=utl.filename_day_back_model(day_back=day_back,fhour=fhour-12,UTC=True)
        try:
            # retrieve data from CIMISS server        
            rh_700=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='RHU'),
                        fcst_level=700, fcst_ele="RHU", units='%')
            if rh_700 is None:
                return

            hgt_500=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GPH'),
                        fcst_level=500, fcst_ele="GPH", units='gpm')
            if hgt_500 is None:
                return
            hgt_500['data'].values=hgt_500['data'].values/10.

            hgt_500_2=CMISS_IO.cimiss_model_by_time('20'+filename2[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GPH'),
                        fcst_level=500, fcst_ele="GPH", units='gpm')
            if hgt_500_2 is None:
                return
            hgt_500_2['data'].values=hgt_500_2['data'].values/10.            

            u_300=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        fcst_level=300, fcst_ele="WIU", units='m/s')
            if u_300 is None:
                return
                
            v_300=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        fcst_level=300, fcst_ele="WIV", units='m/s')
            if v_300 is None:
                return

            u_500=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        fcst_level=500, fcst_ele="WIU", units='m/s')
            if u_500 is None:
                return
                
            v_500=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        fcst_level=500, fcst_ele="WIV", units='m/s')
            if v_500 is None:
                return

            u_850=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        fcst_level=850, fcst_ele="WIU", units='m/s')
            if u_850 is None:
                return
                
            v_850=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        fcst_level=850, fcst_ele="WIV", units='m/s')
            if v_850 is None:
                return

            BLI=CMISS_IO.cimiss_model_by_time('20'+filename2[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PLI'),
                        fcst_level=0, fcst_ele="PLI", units='Pa')
            if BLI is None:
                return

            #1000hPa 露点温度代替2m露点温度
            Td2m=CMISS_IO.cimiss_model_by_time('20'+filename2[0:8], valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='DPT'),
                        fcst_level=1000, fcst_ele="DPT", units='Pa')
            if Td2m is None:
                return
            Td2m['data'].values=Td2m['data'].values-273.15

            if(model == 'ECMWF'):
                PRMSL=CMISS_IO.cimiss_model_by_time('20'+filename[0:8], valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='GSSP'),
                            fcst_level=0, fcst_ele="GSSP", units='Pa')
            else:
                PRMSL=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='SSP'),
                            fcst_level=0, fcst_ele="SSP", units='Pa')

            t_700=CMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEM'),
                        fcst_level=700, fcst_ele="TEM", units='K')
            if t_700 is None:
                return   
            t_700['data'].values=t_700['data'].values-273.15

            if PRMSL is None:
                return
            PRMSL['data']=PRMSL['data']/100.

            if(model == 'ECMWF'):
                PRMSL2=CMISS_IO.cimiss_model_by_time('20'+filename2[0:8], valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='GSSP'),
                            fcst_level=0, fcst_ele="GSSP", units='Pa')
            else:
                PRMSL2=CMISS_IO.cimiss_model_by_time('20'+filename2[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='SSP'),
                            fcst_level=0, fcst_ele="SSP", units='Pa')
            if PRMSL2 is None:
                return
            PRMSL2['data']=PRMSL2['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed') 

    lats = np.squeeze(rh_700['lat'].values)
    lons = np.squeeze(rh_700['lon'].values)
    x,y=np.meshgrid(rh_700['lon'], rh_700['lat'])

    tmp_700 = t_700['data'].values.squeeze()*units('degC')
    u_300 = (u_300['data'].values.squeeze()*units.meter/units.second).to('kt')
    v_300 = (v_300['data'].values.squeeze()*units.meter/units.second).to('kt')
    u_500 = (u_500['data'].values.squeeze()*units.meter/units.second).to('kt')
    v_500 = (v_500['data'].values.squeeze()*units.meter/units.second).to('kt')
    u_850 = (u_850['data'].values.squeeze()*units.meter/units.second).to('kt')
    v_850 = (v_850['data'].values.squeeze()*units.meter/units.second).to('kt')
    hgt_500 = (hgt_500['data'].values.squeeze())*10/9.8*units.meter
    rh_700 = rh_700['data'].values.squeeze()
    lifted_index = BLI['data'].values.squeeze()*units.kelvin
    Td_sfc = Td2m['data'].values.squeeze()*units('degC')
    dx,dy=mpcalc.lat_lon_grid_deltas(lons,lats)

    avor_500=mpcalc.absolute_vorticity(u_500,v_500,dx,dy,y*units.degree)
    pmsl=PRMSL['data'].values.squeeze()*units('hPa')

    hgt_500_2 = (hgt_500_2['data'].values.squeeze())*10/9.8*units.meter
    pmsl2=PRMSL2['data'].values.squeeze()*units('hPa')

    # 500 hPa CVA
    vort_adv_500 = mpcalc.advection(avor_500, [u_500.to('m/s'), v_500.to('m/s')],
                                    (dx, dy), dim_order='yx') * 1e9
    vort_adv_500_smooth = gaussian_filter(vort_adv_500, 4)

    wspd_300 = gaussian_filter(mpcalc.wind_speed(u_300, v_300), 5)
    wspd_500 = gaussian_filter(mpcalc.wind_speed(u_500, v_500), 5)
    wspd_850 = gaussian_filter(mpcalc.wind_speed(u_850, v_850), 5)

    Td_dep_700 = tmp_700 - mpcalc.dewpoint_rh(tmp_700, rh_700 / 100.)

    pmsl_change = pmsl - pmsl2
    hgt_500_change = hgt_500 - hgt_500_2

    mask_500 = ma.masked_less_equal(wspd_500, 0.66 * np.max(wspd_500)).mask
    u_500[mask_500] = np.nan
    v_500[mask_500] = np.nan

    # 300 hPa
    mask_300 = ma.masked_less_equal(wspd_300, 0.66 * np.max(wspd_300)).mask
    u_300[mask_300] = np.nan
    v_300[mask_300] = np.nan

    # 850 hPa
    mask_850 = ma.masked_less_equal(wspd_850, 0.66 * np.max(wspd_850)).mask
    u_850[mask_850] = np.nan
    v_850[mask_850] = np.nan

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

    fcst_info= {'lon':lons,'lat':lats,
                'forecast_period':fhour,
                'model':model,
                'forecast_reference_time': t_700.coords['forecast_reference_time'].values
                }

    synthetical_graphics.draw_Miller_Composite_Chart(fcst_info=fcst_info,
                    u_300=u_300,v_300=v_300,u_500=u_500,v_500=v_500,u_850=u_850,v_850=v_850,
                    pmsl_change=pmsl_change,hgt_500_change=hgt_500_change,Td_dep_700=Td_dep_700,
                    Td_sfc=Td_sfc,pmsl=pmsl,lifted_index=lifted_index,vort_adv_500_smooth=vort_adv_500_smooth,
                    map_extent=map_extent,
                    add_china=True,city=False,south_China_sea=True,
                    output_dir=None,Global=False)           
