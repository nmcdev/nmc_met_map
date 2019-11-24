# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid,get_model_3D_grid
import nmc_met_map.lib.utility as utl
import metpy.calc as mpcalc
from metpy.units import units
import xarray as xr

from datetime import datetime, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import metpy.calc
from netCDF4 import num2date

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as lines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
from netCDF4 import num2date
import numpy as np
import numpy.ma as ma
from scipy.ndimage import gaussian_filter
from nmc_met_map.graphics import synthetical_graphics

def Miller_Composite_Chart(initial_time=None, fhour=24, day_back=0,model='GRAPES_GFS',
    gh_lev='500',uv_lev='850',
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    Global=False,
    south_China_sea=True,area = '全国',city=False,output_dir=None
     ):

    # micaps data directory
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
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
        filename2 = utl.model_filename(initial_time, fhour-12)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
        filename2=utl.filename_day_back_model(day_back=day_back,fhour=fhour-12)
        
    # retrieve data from micaps server
    rh_700=get_model_grid(directory=data_dir[0],filename=filename)
    if rh_700 is None:
        return

    u_300=get_model_grid(directory=data_dir[1],filename=filename)
    if u_300 is None:
        return

    v_300=get_model_grid(directory=data_dir[2],filename=filename)
    if v_300 is None:
        return

    u_500=get_model_grid(directory=data_dir[3],filename=filename)
    if u_500 is None:
        return

    v_500=get_model_grid(directory=data_dir[4],filename=filename)
    if v_500 is None:
        return

    u_850=get_model_grid(directory=data_dir[5],filename=filename)
    if u_850 is None:
        return

    v_850=get_model_grid(directory=data_dir[6],filename=filename)
    if v_850 is None:
        return

    t_700=get_model_grid(directory=data_dir[7],filename=filename)
    if t_700 is None:
        return

    hgt_500=get_model_grid(directory=data_dir[8],filename=filename)
    if hgt_500 is None:
        return     

    hgt_500_2=get_model_grid(directory=data_dir[8],filename=filename2)
    if hgt_500_2 is None:
        return 

    BLI=get_model_grid(directory=data_dir[9],filename=filename)
    if BLI is None:
        return

    Td2m=get_model_grid(directory=data_dir[10],filename=filename)
    if Td2m is None:
        return

    PRMSL=get_model_grid(directory=data_dir[11],filename=filename)
    if PRMSL is None:
        return

    PRMSL2=get_model_grid(directory=data_dir[11],filename=filename2)
    if PRMSL2 is None:
        return

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

    #+ to solve the problem of labels on all the contours
    idx_x1 = np.where((lons > map_extent[0]-delt_x) & 
        (lons < map_extent[1]+delt_x))
    idx_y1 = np.where((lats > map_extent[2]-delt_y) & 
        (lats < map_extent[3]+delt_y))

    fcst_info= {'lon':lons,'lat':lats,
                'fhour':fhour,
                'model':model,
                'init_time': t_700.coords['forecast_reference_time'].values
                }

    synthetical_graphics.draw_Miller_Composite_Chart(fcst_info=fcst_info,
                    u_300=u_300,v_300=v_300,u_500=u_500,v_500=v_500,u_850=u_850,v_850=v_850,
                    pmsl_change=pmsl_change,hgt_500_change=hgt_500_change,Td_dep_700=Td_dep_700,
                    Td_sfc=Td_sfc,pmsl=pmsl,lifted_index=lifted_index,vort_adv_500_smooth=vort_adv_500_smooth,
                    map_extent=map_extent,
                    add_china=True,city=False,south_China_sea=True,
                    output_dir=None,Global=False)           
