# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid,get_model_3D_grid
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.product.syn_ver import vs_ana
import nmc_met_map.lib.utility as utl
import metpy.calc as mpcalc
from metpy.units import units
import math as mth
import xarray as xr
import pkg_resources
import pandas as pd
from datetime import datetime, timedelta

def compare_gh_uv(anaTime=None, anamodel='GRAPES_GFS',
    fhour=24, model='ECMWF',data_source='MICAPS',
    gh_lev=500,uv_lev=850,area=None,
    map_ratio=14/9,zoom_ratio=20,cntr_pnt=[104,34],
    **products_kwargs):

    if(area != '全国'):
        south_China_sea=False

    # micaps data directory
    if(data_source =='MICAPS'):
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=gh_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=uv_lev),
                        utl.Cassandra_dir(data_type='surface',data_source=model,var_name='PSFC')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename

        if(anaTime == None):
            anaTime = MICAPS_IO.get_latest_initTime(data_dir[-1])
            iniTime= (datetime.strptime('20'+anaTime, '%Y%m%d%H')-timedelta(hours=fhour)).strftime("%Y%m%d%H")[2:10]

        if(anaTime != None):
            filename_ana = utl.model_filename(anaTime, 0)
            filename_fcst = utl.model_filename(iniTime, fhour)

        # retrieve data from micaps server
        gh_ana = MICAPS_IO.get_model_grid(data_dir[0], filename=filename_ana)
        u_ana = MICAPS_IO.get_model_grid(data_dir[1], filename=filename_ana)
        v_ana = MICAPS_IO.get_model_grid(data_dir[2], filename=filename_ana)
        mslp_ana = MICAPS_IO.get_model_grid(data_dir[3], filename=filename_ana)
        gh_fcst = MICAPS_IO.get_model_grid(data_dir[0], filename=filename_fcst)
        u_fcst = MICAPS_IO.get_model_grid(data_dir[1], filename=filename_fcst)
        v_fcst = MICAPS_IO.get_model_grid(data_dir[2], filename=filename_fcst)
        mslp_fcst = MICAPS_IO.get_model_grid(data_dir[3], filename=filename_fcst)

    if(data_source =='CIMISS'):

        # get filename
        if(anaTime != None):
            filename_ana = utl.model_filename(anaTime, 0,UTC=True)
            filename_fcst = utl.model_filename(iniTime, fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
            gh_ana=CMISS_IO.cimiss_model_by_time('20'+filename_ana[0:8],valid_time=0,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GPH'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=gh_lev, fcst_ele="GPH", units='gpm')
            gh_ana['data'].values=gh_ana['data'].values/10.
            gh_fcst=CMISS_IO.cimiss_model_by_time('20'+filename_fcst[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GPH'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=gh_lev, fcst_ele="GPH", units='gpm')
            gh_fcst['data'].values=gh_fcst['data'].values/10.

            u_ana=CMISS_IO.cimiss_model_by_time('20'+filename_ana[0:8],valid_time=0,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uv_lev, fcst_ele="WIU", units='m/s')
            u_fcst=CMISS_IO.cimiss_model_by_time('20'+filename_fcst[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uv_lev, fcst_ele="WIU", units='m/s')

            v_ana=CMISS_IO.cimiss_model_by_time('20'+filename_ana[0:8],valid_time=0,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uv_lev, fcst_ele="WIV", units='m/s')
            v_fcst=CMISS_IO.cimiss_model_by_time('20'+filename_fcst[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_level=uv_lev, fcst_ele="WIV", units='m/s')

            if(model == 'ECMWF'):
                mslp_ana=CMISS_IO.cimiss_model_by_time('20'+filename_ana[0:8], valid_time=0,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='GSSP'),
                            levattrs={'long_name':'Mean_sea_level', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="GSSP", units='Pa')
                mslp_fcst=CMISS_IO.cimiss_model_by_time('20'+filename_fcst[0:8], valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='GSSP'),
                            levattrs={'long_name':'Mean_sea_level', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="GSSP", units='Pa')
            else:
                mslp_ana=CMISS_IO.cimiss_model_by_time('20'+filename_ana[0:8],valid_time=0,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='SSP'),
                            levattrs={'long_name':'Mean_sea_level', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="SSP", units='Pa')
                mslp_fcst=CMISS_IO.cimiss_model_by_time('20'+filename_fcst[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='PRS'),
                            levattrs={'long_name':'Mean_sea_level', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="PRS", units='Pa')
            mslp_ana['data']=mslp_ana['data']/100.
            mslp_fcst['data']=mslp_fcst['data']/100.
        except KeyError:
            raise ValueError('Can not find all data needed')                
    # prepare data
    if(all([gh_ana,u_ana,v_ana,mslp_ana,gh_fcst,u_fcst,v_fcst,mslp_fcst]) is False):
        print('some data is not avaliable')
        return

    if(area != None):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    gh_ana=utl.cut_xrdata(map_extent,gh_ana)
    u_ana=utl.cut_xrdata(map_extent,u_ana)
    v_ana=utl.cut_xrdata(map_extent,v_ana)
    mslp_ana=utl.cut_xrdata(map_extent,mslp_ana)

    gh_fcst=utl.cut_xrdata(map_extent,gh_fcst)
    u_fcst=utl.cut_xrdata(map_extent,u_fcst)
    v_fcst=utl.cut_xrdata(map_extent,v_fcst)
    mslp_fcst=utl.cut_xrdata(map_extent,mslp_fcst)

    u_ana=utl.mask_terrian(uv_lev,mslp_ana,u_ana)
    v_ana=utl.mask_terrian(uv_lev,mslp_ana,v_ana)
    gh_ana=utl.mask_terrian(gh_lev,mslp_ana,gh_ana)
    u_fcst=utl.mask_terrian(uv_lev,mslp_fcst,u_fcst)
    v_fcst=utl.mask_terrian(uv_lev,mslp_fcst,v_fcst)
    gh_fcst=utl.mask_terrian(gh_lev,mslp_fcst,gh_fcst)

    uv_ana=xr.merge([u_ana.rename({'data': 'u'}),v_ana.rename({'data': 'v'})])
    uv_fcst=xr.merge([u_fcst.rename({'data': 'u'}),v_fcst.rename({'data': 'v'})])
    
    gh_ana.attrs={'model_name':model}
    u_ana.attrs={'model_name':model}
    v_ana.attrs={'model_name':model}
    gh_fcst.attrs={'model_name':model}
    u_fcst.attrs={'model_name':model}
    v_fcst.attrs={'model_name':model}

    vs_ana.draw_compare_gh_uv(
        gh_ana=gh_ana, uv_ana=uv_ana,gh_fcst=gh_fcst,uv_fcst=uv_fcst,
        map_extent=map_extent,**products_kwargs)