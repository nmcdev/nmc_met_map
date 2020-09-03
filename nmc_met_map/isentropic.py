# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
from nmc_met_io.retrieve_micaps_server import get_model_grid,get_model_3D_grid
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CMISS_IO
from nmc_met_map.graphics import isentropic_graphics
import nmc_met_map.lib.utility as utl
import metpy.calc as mpcalc
from metpy.units import units
import xarray as xr

def isentropic_uv(initTime=None, fhour=6, day_back=0,model='ECMWF',data_source='MICAPS',
    isentlev=310,
    map_ratio=19/9,zoom_ratio=20,cntr_pnt=[102,34],
    levels=[1000, 950, 925, 900, 850, 800, 700,600,500,400,300,250,200,100],
    Global=False,
    south_China_sea=True,area = '全国',city=False,output_dir=None
     ):
    # micaps data directory
    if(data_source =='MICAPS'):    
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=''),
                        utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl='')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
            
        # retrieve data from micaps server
        rh=MICAPS_IO.get_model_3D_grid(directory=data_dir[0][0:-1],filename=filename,levels=levels, allExists=False)
        if rh is None:
            return

        u=MICAPS_IO.get_model_3D_grid(directory=data_dir[1][0:-1],filename=filename,levels=levels, allExists=False)
        if u is None:
            return

        v=MICAPS_IO.get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
        if v is None:
            return

        t=MICAPS_IO.get_model_3D_grid(directory=data_dir[3][0:-1],filename=filename,levels=levels, allExists=False)
        if t is None:
            return

    if(data_source =='CIMISS'): 
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CMISS server        
            rh=CMISS_IO.cimiss_model_3D_grid(init_time_str='20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='RHU'),
                        fcst_levels=levels, fcst_ele="RHU", units='%')
            if rh is None:
                return

            u=CMISS_IO.cimiss_model_3D_grid(init_time_str='20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        fcst_levels=levels, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CMISS_IO.cimiss_model_3D_grid(init_time_str='20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        fcst_levels=levels, fcst_ele="WIV", units='m/s')
            if v is None:
                return

            t=CMISS_IO.cimiss_model_3D_grid(init_time_str='20'+filename[0:8],valid_time=fhour,
                        data_code=utl.CMISS_data_code(data_source=model,var_name='TEM'),
                        fcst_levels=levels, fcst_ele="TEM", units='K')
            if t is None:
                return
            t['data'].values=t['data'].values-273.15
        except KeyError:
            raise ValueError('Can not find all data needed')

    lats = np.squeeze(rh['lat'].values)
    lons = np.squeeze(rh['lon'].values)

    pres = np.array(levels)*100 * units('Pa')
    tmp = t['data'].values.squeeze()*units('degC')
    uwnd = u['data'].values.squeeze()*units.meter/units.second
    vwnd = v['data'].values.squeeze()*units.meter/units.second
    relh = rh['data'].values.squeeze()*units.meter/units.percent

    isentlev = isentlev * units.kelvin

    isent_anal = mpcalc.isentropic_interpolation(isentlev, pres, tmp,
                                                 relh, uwnd, vwnd, axis=0,bottom_up_search=False)

    isentprs, isentrh, isentu, isentv = isent_anal

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

    idx_x1 = np.where((lons > map_extent[0]-delt_x) & 
        (lons < map_extent[1]+delt_x))
    idx_y1 = np.where((lats > map_extent[2]-delt_y) & 
        (lats < map_extent[3]+delt_y))

    mask1 = ((t['lon'] > map_extent[0]-delt_x) & 
            (t['lon'] < map_extent[1]+delt_x) & 
            (t['lat'] > map_extent[2]-delt_y) & 
            (t['lat'] < map_extent[3]+delt_y) &
            (t['level'] == t['level'].values[0]))
    isentrh1=t.where(mask1 ,drop=True)
    isentrh1['data'].values=[[np.array(isentrh)[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)]]]
    isentrh1.attrs['model']=model
    isentrh1=isentrh1.assign_coords(level=[np.array(isentlev)])

    isentu1=isentrh1.copy()
    isentu1['data'].values=[[np.array(isentu)[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)]]]

    isentv1=isentrh1.copy()
    isentv1['data'].values=[[np.array(isentv)[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)]]]

    isentuv1=xr.merge([isentu1.rename({'data': 'isentu'}),isentv1.rename({'data': 'isentv'})])

    isentprs1=isentrh1.copy()
    isentprs1['data'].values=[[np.array(isentprs)[0,idx_y1[0][0]:(idx_y1[0][-1]+1),idx_x1[0][0]:(idx_x1[0][-1]+1)]]]

    isentropic_graphics.draw_isentropic_uv(
        isentrh=isentrh1, isentuv=isentuv1, isentprs=isentprs1,
        map_extent=map_extent, regrid_shape=20,
        city=city,south_China_sea=south_China_sea,
        output_dir=output_dir,Global=Global
        )