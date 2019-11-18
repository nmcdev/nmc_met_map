# _*_ coding: utf-8 _*_
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import metpy.calc as mpcalc
from metpy.interpolate import cross_section
import cf2cdm
import cfgrib
from nmc_met_map.lib.utility import add_china_map_2cartopy_public

from nmc_met_io.retrieve_micaps_server import get_model_grid
from nmc_met_map.graphics import elements_graphics
import nmc_met_map.lib.utility as utl

def Crosssection_Wind_Theta_e_absv(
    initial_time=None, fhour=24, day_back=0,model='ECMWF',
    output_dir=None,
    st_point = [20, 120.0],
    ed_point = [50, 130.0],
    map_extent=[90,135,20,50],
    h_pos=[0.125, 0.665, 0.25, 0.2] ):

    # micaps data directory
    try:
        data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH'),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD'),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD'),
                    utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP')]
    except KeyError:
        raise ValueError('Can not find all directories needed')

    # get filename
    if(initial_time != None):
        filename = utl.model_filename(initial_time, fhour)
    else:
        filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
        
    # retrieve data from micaps server
    T_2m = get_model_grid(data_dir[0], filename=filename)
    if T_2m is None:
        return
    init_time = T_2m.coords['forecast_reference_time'].values        

