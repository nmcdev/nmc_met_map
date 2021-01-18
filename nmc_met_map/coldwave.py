# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import coldwave_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr
from scipy.ndimage import gaussian_filter
def tmp_evo(initTime=None,tmp_lev=850, t_gap=6,t_range=[6,36],model='ECMWF',
    data_source='MICAPS',map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    south_China_sea=True,area =None,**kwargs):

    fhours=np.arange(t_range[0],t_range[1],t_gap)
#prepare data
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=tmp_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PSFC')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime==None):
            initTime = MICAPS_IO.get_latest_initTime(data_dir[0])
        filenames = [initTime+'.'+str(fhour).zfill(3) for fhour in fhours]

        # retrieve data from micaps server
        tmp = MICAPS_IO.get_model_grids(data_dir[0], filenames=filenames)
        psfc = MICAPS_IO.get_model_grids(data_dir[1], filenames=filenames)
        
    if(data_source=='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, 0,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=0,fhour=0,UTC=True)
        try:
            tmp=CMISS_IO.cimiss_model_by_times('20'+filename[0:8],valid_times=fhours,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEM'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=tmp_lev, fcst_ele="TEM", units='K')
            tmp['data'].values=tmp['data'].values-273.15

            psfc=CMISS_IO.cimiss_model_by_times('20'+filename[0:8], valid_times=fhours,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                        fcst_level=0, fcst_ele="PRS", units='Pa')
            psfc['data']=psfc['data']/100.

        except KeyError:
            raise ValueError('Can not find all data needed')                
# set map extent
    if(area != None):
        south_China_sea=False

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)
    map_extent,delt_x,delt_y=utl.get_map_extent(cntr_pnt,zoom_ratio,map_ratio)
    tmp=utl.cut_xrdata(map_extent, tmp, delt_x=delt_x, delt_y=delt_y)
    tmp=tmp.rolling({'lon':3,'lat':3}).mean()
    psfc=utl.cut_xrdata(map_extent, psfc, delt_x=delt_x, delt_y=delt_y)
    tmp=utl.mask_terrian(tmp_lev,psfc,tmp)
    tmp.attrs['model']=model
    coldwave_graphics.draw_tmp_evo(tmp=tmp,map_extent=map_extent,south_China_sea=south_China_sea,**kwargs)