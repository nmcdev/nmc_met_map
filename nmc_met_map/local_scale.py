# _*_ coding: utf-8 _*_

"""
Synoptic analysis or diagnostic maps for numeric weather model.
"""
import numpy as np
import nmc_met_io.retrieve_micaps_server as MICAPS_IO
import nmc_met_io.retrieve_cimiss_server as CIMISS_IO
from nmc_met_map.graphics import local_scale_graphics
import nmc_met_map.lib.utility as utl
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr
from scipy.interpolate import LinearNDInterpolator
from datetime import datetime, timedelta

def wind_rh_according_to_4D_data(initTime=None, fhour=6, day_back=0,
    model='ECMWF',
    sta_fcs={'lon':[101.82,101.32,101.84,102.23,102.2681],
        'lat':[28.35,27.91,28.32,27.82,27.8492],
        'altitude':[3600,3034.62,3240,1669,1941.5],
        'name':['健美乡','项脚乡','\n锦屏镇','\n马道镇','S9005  ']},
    draw_zd=True,
    levels=[1000, 950, 925, 900,850, 800, 700, 600, 500,400,300,250,200,150],
    map_ratio=14/9,zoom_ratio=1,
    south_China_sea=False,area = '全国',city=False,output_dir=None,
    bkgd_type='satellite',
    data_source='MICAPS',**kwargs):

    # micaps data directory
    if(area != '全国'):
        south_China_sea=False

    # prepare data
    if(area != '全国'):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    cntr_pnt=np.append(np.mean(sta_fcs['lon']),np.mean(sta_fcs['lat']))
    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    bkgd_level=utl.cal_background_zoom_ratio(zoom_ratio)
    # micaps data directory
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=''),
                                utl.Cassandra_dir(data_type='high',data_source=model,var_name='RH',lvl=''),
                                utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                                utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                                utl.Cassandra_dir(data_type='surface',data_source=model,var_name='u10m'),
                                utl.Cassandra_dir(data_type='surface',data_source=model,var_name='v10m'),
                                utl.Cassandra_dir(data_type='surface',data_source=model,var_name='Td2m'),
                                utl.Cassandra_dir(data_type='surface',data_source=model,var_name='T2m')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
            initTime=filename[0:8]
            
        # retrieve data from micaps server
        gh=MICAPS_IO.get_model_3D_grid(directory=data_dir[0][0:-1],filename=filename,levels=levels)
        if(gh is None):
            return
        gh['data'].values=gh['data'].values*10

        rh=MICAPS_IO.get_model_3D_grid(directory=data_dir[1][0:-1],filename=filename,levels=levels, allExists=False)
        if rh is None:
            return

        u=MICAPS_IO.get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
        if u is None:
            return

        v=MICAPS_IO.get_model_3D_grid(directory=data_dir[3][0:-1],filename=filename,levels=levels, allExists=False)
        if v is None:
            return

        u10m=MICAPS_IO.get_model_grid(directory=data_dir[4],filename=filename)
        if u10m is None:
            return

        v10m=MICAPS_IO.get_model_grid(directory=data_dir[5],filename=filename)
        if v10m is None:
            return

        td2m=MICAPS_IO.get_model_grid(directory=data_dir[6],filename=filename)
        if td2m is None:
            return

        t2m=MICAPS_IO.get_model_grid(directory=data_dir[7],filename=filename)
        if t2m is None:
            return

        if(draw_zd == True):
            validtime=(datetime.strptime('20'+initTime, '%Y%m%d%H')+timedelta(hours=fhour)).strftime("%Y%m%d%H")
            directory_obs=utl.Cassandra_dir(data_type='surface',data_source='OBS',var_name='PLOT_ALL')
            try:
                zd_sta=MICAPS_IO.get_station_data(filename=validtime+'0000.000',directory=directory_obs,dropna=True, cache=False)
                obs_valid=True
            except:
                zd_sta=MICAPS_IO.get_station_data(directory=directory_obs,dropna=True, cache=False)
                obs_valid=False

            zd_lon=zd_sta['lon'].values
            zd_lat=zd_sta['lat'].values
            zd_alt=zd_sta['Alt'].values
            zd_u,zd_v=mpcalc.wind_components(zd_sta['Wind_speed_2m_avg'].values* units('m/s'),
                    zd_sta['Wind_angle_2m_avg'].values*units.deg)

            idx_zd = np.where((zd_lon > map_extent[0]) & 
                (zd_lon < map_extent[1]) &
                (zd_lat > map_extent[2]) &
                (zd_lat < map_extent[3]) )
            
            zd_sm_lon=zd_lon[idx_zd[0]]
            zd_sm_lat=zd_lat[idx_zd[0]]
            zd_sm_alt=zd_alt[idx_zd[0]]
            zd_sm_u=zd_u[idx_zd[0]]
            zd_sm_v=zd_v[idx_zd[0]]

    if(data_source =='CIMISS'):
        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour,UTC=True)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour,UTC=True)
        try:
            # retrieve data from CIMISS server        

            gh=CIMISS_IO.cimiss_model_3D_grid(
                        data_code=utl.CMISS_data_code(data_source=model,var_name='GPH'),
                        init_time_str='20'+filename[0:8],valid_time=fhour,                        
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_levels=levels, fcst_ele="GPH", units='gpm')
            if gh is None:
                return

            rh=CIMISS_IO.cimiss_model_3D_grid(
                        data_code=utl.CMISS_data_code(data_source=model,var_name='RHU'),
                        init_time_str='20'+filename[0:8],valid_time=fhour,
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_levels=levels, fcst_ele="RHU", units='%')
            if rh is None:
                return

            u=CIMISS_IO.cimiss_model_3D_grid(
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIU'),
                        init_time_str='20'+filename[0:8],valid_time=fhour,
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_levels=levels, fcst_ele="WIU", units='m/s')
            if u is None:
                return
                
            v=CIMISS_IO.cimiss_model_3D_grid(
                        data_code=utl.CMISS_data_code(data_source=model,var_name='WIV'),
                        init_time_str='20'+filename[0:8],valid_time=fhour,
                        levattrs={'long_name':'pressure_level', 'units':'hPa', '_CoordinateAxisType':'-'},
                        fcst_levels=levels, fcst_ele="WIV", units='m/s')
            if v is None:
                return



            if(model == 'ECMWF'):
                td2m=CIMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='DPT'),
                            levattrs={'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="DPT", units='K')                
                if td2m is None:
                    return

                t2m=CIMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='TEF2'),
                            levattrs={'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="TEF2", units='K')                
                if t2m is None:
                    return

                v10m=CIMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='WIV10'),
                            levattrs={'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="WIV10", units='m/s')                
                if v10m is None:
                    return

                u10m=CIMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='WIU10'),
                            levattrs={'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=0, fcst_ele="WIU10", units='m/s')                
                if u10m is None:
                    return

            if(model == 'GRAPES_GFS'):
                rh2m=CIMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='RHF2'),
                            levattrs={'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=2, fcst_ele="RHF2", units='%')                
                if rh2m is None:
                    return

                v10m=CIMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='WIV10'),
                            levattrs={'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=10, fcst_ele="WIV10", units='m/s')                
                if v10m is None:
                    return

                u10m=CIMISS_IO.cimiss_model_by_time('20'+filename[0:8],valid_time=fhour,
                            data_code=utl.CMISS_data_code(data_source=model,var_name='WIU10'),
                            levattrs={'long_name':'height_above_ground', 'units':'m', '_CoordinateAxisType':'-'},
                            fcst_level=10, fcst_ele="WIU10", units='m/s')                
                if u10m is None:
                    return                    
        except KeyError:
            raise ValueError('Can not find all data needed')

        if(draw_zd == True):
            if(initTime == None):
                initTime1 = CIMISS_IO.cimiss_get_obs_latest_time(data_code="SURF_CHN_MUL_HOR")
                initTime = (datetime.strptime('20'+initTime1, '%Y%m%d%H')-timedelta(days=day_back)).strftime("%Y%m%d%H")[2:]

            validtime=(datetime.strptime('20'+initTime, '%Y%m%d%H')+timedelta(hours=fhour)).strftime("%Y%m%d%H")
            data_code=utl.CMISS_data_code(data_source='OBS',var_name='PLOT_sfc')
            zd_sta=CIMISS_IO.cimiss_obs_by_time(
                times=validtime+'0000',
                data_code=data_code,
                sta_levels="011,012,013,014",
                elements="Station_Id_C,Station_Id_d,lat,lon,Alti,TEM,WIN_D_Avg_2mi,WIN_S_Avg_2mi,RHU")
            obs_valid=True
            if(zd_sta is None):
                CIMISS_IO.cimiss_get_obs_latest_time(data_code=data_code, latestTime=6)
                zd_sta=CIMISS_IO.cimiss_obs_by_time(directory=directory_obs,dropna=True, cache=False)
                obs_valid=False

            zd_lon=zd_sta['lon'].values
            zd_lat=zd_sta['lat'].values
            zd_alt=zd_sta['Alti'].values
            zd_u,zd_v=mpcalc.wind_components(zd_sta['WIN_S_Avg_2mi'].values* units('m/s'),
                    zd_sta['WIN_D_Avg_2mi'].values*units.deg)

            idx_zd = np.where((zd_lon > map_extent[0]) & 
                (zd_lon < map_extent[1]) &
                (zd_lat > map_extent[2]) &
                (zd_lat < map_extent[3]) &
                (zd_sta['WIN_S_Avg_2mi'].values < 1000))
            
            zd_sm_lon=zd_lon[idx_zd[0]]
            zd_sm_lat=zd_lat[idx_zd[0]]
            zd_sm_alt=zd_alt[idx_zd[0]]
            zd_sm_u=zd_u[idx_zd[0]]
            zd_sm_v=zd_v[idx_zd[0]]

#maskout area
    delt_xy=rh['lon'].values[1]-rh['lon'].values[0]
    #+ to solve the problem of labels on all the contours
    mask1 = (rh['lon'] > map_extent[0]-delt_xy) & (rh['lon'] < map_extent[1]+delt_xy) & (rh['lat'] > map_extent[2]-delt_xy) & (rh['lat'] < map_extent[3]+delt_xy)
    mask2 = (u10m['lon'] > map_extent[0]-delt_xy) & (u10m['lon'] < map_extent[1]+delt_xy) & (u10m['lat'] > map_extent[2]-delt_xy) & (u10m['lat'] < map_extent[3]+delt_xy)
    #- to solve the problem of labels on all the contours
    rh=rh.where(mask1,drop=True)
    u=u.where(mask1,drop=True)
    v=v.where(mask1,drop=True)
    gh=gh.where(mask1,drop=True)
    u10m=u10m.where(mask2,drop=True)
    v10m=v10m.where(mask2,drop=True)
#prepare interpolator
    Ex1 = np.squeeze(u['data'].values).flatten()
    Ey1 = np.squeeze(v['data'].values).flatten()
    Ez1 = np.squeeze(rh['data'].values).flatten()
    z = (np.squeeze(gh['data'].values)).flatten()

    coords = np.zeros((np.size(levels),u['lat'].size,u['lon'].size,3))
    coords[...,1] = u['lat'].values.reshape((1,u['lat'].size,1))
    coords[...,2] = u['lon'].values.reshape((1,1,u['lon'].size))
    coords = coords.reshape((Ex1.size,3))
    coords[:,0]=z

    interpolator_U = LinearNDInterpolator(coords,Ex1,rescale=True)
    interpolator_V = LinearNDInterpolator(coords,Ey1,rescale=True)
    interpolator_RH = LinearNDInterpolator(coords,Ez1,rescale=True)

#process sta_fcs 10m wind
    coords2=np.zeros((np.size(sta_fcs['lon']),3))
    coords2[:,0]=sta_fcs['altitude']
    coords2[:,1]=sta_fcs['lat']
    coords2[:,2]=sta_fcs['lon']
    u_sta=interpolator_U(coords2)
    v_sta=interpolator_V(coords2)
    RH_sta=interpolator_RH(coords2)
    wsp_sta=(u_sta**2+v_sta**2)**0.5
    u10m_2D=u10m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))
    v10m_2D=v10m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))
    if(model=='GRAPES_GFS' and data_source=='CIMISS'):
        rh2m_2D=rh2m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))['data'].values
    else:
        td2m_2D=td2m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))
        t2m_2D=t2m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))
        if(data_source=='MICAPS'):
            rh2m_2D=mpcalc.relative_humidity_from_dewpoint(t2m_2D['data'].values*units('degC'),td2m_2D['data'].values*units('degC'))*100
        else:
            rh2m_2D=mpcalc.relative_humidity_from_dewpoint(t2m_2D['data'].values*units('kelvin'),td2m_2D['data'].values*units('kelvin'))*100
        
    wsp10m_2D=(u10m_2D['data'].values**2+v10m_2D['data'].values**2)**0.5
    winddir10m=mpcalc.wind_direction(u10m_2D['data'].values* units('m/s'),v10m_2D['data'].values* units('m/s'))
    if(np.isnan(wsp_sta).any()):
        if(wsp_sta.size == 1):
            wsp_sta[np.isnan(wsp_sta)]=np.squeeze(wsp10m_2D[np.isnan(wsp_sta)])
            RH_sta[np.isnan(RH_sta)]=np.squeeze(np.array(rh2m_2D)[np.isnan(RH_sta)])
        else:
            wsp_sta[np.isnan(wsp_sta)]=np.squeeze(wsp10m_2D)[np.isnan(wsp_sta)]
            RH_sta[np.isnan(RH_sta)]=np.squeeze(np.array(rh2m_2D))[np.isnan(RH_sta)]
    u_sta,v_sta=mpcalc.wind_components(wsp_sta* units('m/s'),winddir10m)
    
#process zd_sta 10m wind
    zd_fcst_obs=None
    if(draw_zd is True):
        coords3=np.zeros((np.size(zd_sm_alt),3))
        coords3[:,0]=zd_sm_alt
        coords3[:,1]=zd_sm_lat
        coords3[:,2]=zd_sm_lon
        u_sm_sta=interpolator_U(coords3)
        v_sm_sta=interpolator_V(coords3)
        wsp_sm_sta=(u_sm_sta**2+v_sm_sta**2)**0.5
        u10m_sm=u10m.interp(lon=('points', zd_sm_lon), lat=('points', zd_sm_lat))
        v10m_sm=v10m.interp(lon=('points', zd_sm_lon), lat=('points', zd_sm_lat))
        wsp10m_sta=np.squeeze((u10m_sm['data'].values**2+v10m_sm['data'].values**2)**0.5)
        winddir10m_sm=mpcalc.wind_direction(u10m_sm['data'].values* units('m/s'),v10m_sm['data'].values* units('m/s'))
        if(np.isnan(wsp_sm_sta).any()):
            wsp_sm_sta[np.isnan(wsp_sm_sta)]=wsp10m_sta[np.isnan(wsp_sm_sta)]
        u_sm_sta,v_sm_sta=mpcalc.wind_components(wsp_sm_sta* units('m/s'),winddir10m_sm)

        zd_fcst_obs={'lon':zd_sm_lon,
                    'lat':zd_sm_lat,
                    'altitude':zd_sm_alt,
                    'U':np.squeeze(np.array(u_sm_sta)),
                    'V':np.squeeze(np.array(v_sm_sta)),
                    'obs_valid':obs_valid,
                    'U_obs':np.squeeze(np.array(zd_sm_u)),
                    'V_obs':np.squeeze(np.array(zd_sm_v))}
#prepare for graphics
    sta_fcs_fcst={'lon':sta_fcs['lon'],
                'lat':sta_fcs['lat'],
                'altitude':sta_fcs['altitude'],
                'name':sta_fcs['name'],
                'RH':np.array(RH_sta),
                'U':np.squeeze(np.array(u_sta)),
                'V':np.squeeze(np.array(v_sta))}

    fcst_info=gh.coords

    local_scale_graphics.draw_wind_rh_according_to_4D_data(
            sta_fcs_fcst=sta_fcs_fcst,zd_fcst_obs=zd_fcst_obs,
            fcst_info=fcst_info,
            map_extent=map_extent,
            draw_zd=draw_zd,
            bkgd_type=bkgd_type,bkgd_level=bkgd_level,
            output_dir=output_dir)

def wind_temp_rn_according_to_4D_data(initTime=None, fhour=6, day_back=0,
    model='ECMWF',
    sta_fcs={'lon':[101.82,101.32,101.84,102.23,102.2681],
        'lat':[28.35,27.91,28.32,27.82,27.8492],
        'altitude':[3600,3034.62,3240,1669,1941.5],
        'name':['健美乡','项脚乡','\n锦屏镇','\n马道镇','S9005  ']},
    draw_zd=True,
    levels=[1000, 950, 925, 900,850, 800, 700, 600, 500,400,300,250,200,150],
    map_ratio=19/9,zoom_ratio=1,
    south_China_sea=False,area = '全国',city=False,output_dir=None,
    bkgd_type='satellite',
    data_source='MICAPS',**kwargs):

    # micaps data directory
    if(area != '全国'):
        south_China_sea=False

    # prepare data
    if(area != '全国'):
        cntr_pnt,zoom_ratio=utl.get_map_area(area_name=area)

    cntr_pnt=np.append(np.mean(sta_fcs['lon']),np.mean(sta_fcs['lat']))
    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1

    bkgd_level=utl.cal_background_zoom_ratio(zoom_ratio)
    # micaps data directory
    if(data_source =='MICAPS'):   
        try:
            data_dir = [utl.Cassandra_dir(data_type='high',data_source=model,var_name='HGT',lvl=''),
                                utl.Cassandra_dir(data_type='high',data_source=model,var_name='TMP',lvl=''),
                                utl.Cassandra_dir(data_type='high',data_source=model,var_name='UGRD',lvl=''),
                                utl.Cassandra_dir(data_type='high',data_source=model,var_name='VGRD',lvl=''),
                                utl.Cassandra_dir(data_type='surface',data_source=model,var_name='u10m'),
                                utl.Cassandra_dir(data_type='surface',data_source=model,var_name='v10m'),
                                utl.Cassandra_dir(data_type='surface',data_source=model,var_name='Td2m'),
                                utl.Cassandra_dir(data_type='surface',data_source=model,var_name='T2m')]
        except KeyError:
            raise ValueError('Can not find all directories needed')

        # get filename
        if(initTime != None):
            filename = utl.model_filename(initTime, fhour)
        else:
            filename=utl.filename_day_back_model(day_back=day_back,fhour=fhour)
            initTime=filename[0:8]
            
        # retrieve data from micaps server
        gh=MICAPS_IO.get_model_3D_grid(directory=data_dir[0][0:-1],filename=filename,levels=levels)
        if(gh is None):
            return
        gh['data'].values=gh['data'].values*10

        TMP=MICAPS_IO.get_model_3D_grid(directory=data_dir[1][0:-1],filename=filename,levels=levels, allExists=False)
        if TMP is None:
            return

        u=MICAPS_IO.get_model_3D_grid(directory=data_dir[2][0:-1],filename=filename,levels=levels, allExists=False)
        if u is None:
            return

        v=MICAPS_IO.get_model_3D_grid(directory=data_dir[3][0:-1],filename=filename,levels=levels, allExists=False)
        if v is None:
            return

        u10m=MICAPS_IO.get_model_grid(directory=data_dir[4],filename=filename)
        if u10m is None:
            return

        v10m=MICAPS_IO.get_model_grid(directory=data_dir[5],filename=filename)
        if v10m is None:
            return

        td2m=MICAPS_IO.get_model_grid(directory=data_dir[6],filename=filename)
        if td2m is None:
            return

        t2m=MICAPS_IO.get_model_grid(directory=data_dir[7],filename=filename)
        if t2m is None:
            return

        if(draw_zd == True):
            validtime=(datetime.strptime('20'+initTime, '%Y%m%d%H')+timedelta(hours=fhour)).strftime("%Y%m%d%H")
            directory_obs=utl.Cassandra_dir(data_type='surface',data_source='OBS',var_name='PLOT_ALL')
            try:
                zd_sta=MICAPS_IO.get_station_data(filename=validtime+'0000.000',directory=directory_obs,dropna=True, cache=False)
                obs_valid=True
            except:
                zd_sta=MICAPS_IO.get_station_data(directory=directory_obs,dropna=True, cache=False)
                obs_valid=False

            zd_lon=zd_sta['lon'].values
            zd_lat=zd_sta['lat'].values
            zd_alt=zd_sta['Alt'].values
            zd_u,zd_v=mpcalc.wind_components(zd_sta['Wind_speed_2m_avg'].values* units('m/s'),
                    zd_sta['Wind_angle_2m_avg'].values*units.deg)

            idx_zd = np.where((zd_lon > map_extent[0]) & 
                (zd_lon < map_extent[1]) &
                (zd_lat > map_extent[2]) &
                (zd_lat < map_extent[3]) )
            
            zd_sm_lon=zd_lon[idx_zd[0]]
            zd_sm_lat=zd_lat[idx_zd[0]]
            zd_sm_alt=zd_alt[idx_zd[0]]
            zd_sm_u=zd_u[idx_zd[0]]
            zd_sm_v=zd_v[idx_zd[0]]

#maskout area
    delt_xy=TMP['lon'].values[1]-TMP['lon'].values[0]
    #+ to solve the problem of labels on all the contours
    mask1 = (TMP['lon'] > map_extent[0]-delt_xy) & (TMP['lon'] < map_extent[1]+delt_xy) & (TMP['lat'] > map_extent[2]-delt_xy) & (TMP['lat'] < map_extent[3]+delt_xy)
    mask2 = (u10m['lon'] > map_extent[0]-delt_xy) & (u10m['lon'] < map_extent[1]+delt_xy) & (u10m['lat'] > map_extent[2]-delt_xy) & (u10m['lat'] < map_extent[3]+delt_xy)
    #- to solve the problem of labels on all the contours
    TMP=TMP.where(mask1,drop=True)
    u=u.where(mask1,drop=True)
    v=v.where(mask1,drop=True)
    gh=gh.where(mask1,drop=True)
    u10m=u10m.where(mask2,drop=True)
    v10m=v10m.where(mask2,drop=True)
#prepare interpolator
    Ex1 = np.squeeze(u['data'].values).flatten()
    Ey1 = np.squeeze(v['data'].values).flatten()
    Ez1 = np.squeeze(TMP['data'].values).flatten()
    z = (np.squeeze(gh['data'].values)).flatten()

    coords = np.zeros((np.size(levels),u['lat'].size,u['lon'].size,3))
    coords[...,1] = u['lat'].values.reshape((1,u['lat'].size,1))
    coords[...,2] = u['lon'].values.reshape((1,1,u['lon'].size))
    coords = coords.reshape((Ex1.size,3))
    coords[:,0]=z

    interpolator_U = LinearNDInterpolator(coords,Ex1,rescale=True)
    interpolator_V = LinearNDInterpolator(coords,Ey1,rescale=True)
    interpolator_TMP = LinearNDInterpolator(coords,Ez1,rescale=True)

#process sta_fcs 10m wind
    coords2=np.zeros((np.size(sta_fcs['lon']),3))
    coords2[:,0]=sta_fcs['altitude']
    coords2[:,1]=sta_fcs['lat']
    coords2[:,2]=sta_fcs['lon']
    u_sta=interpolator_U(coords2)
    v_sta=interpolator_V(coords2)
    TMP_sta=interpolator_TMP(coords2)
    wsp_sta=(u_sta**2+v_sta**2)**0.5
    u10m_2D=u10m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))
    v10m_2D=v10m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))
    td2m_2D=td2m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))
    t2m_2D=t2m.interp(lon=('points', sta_fcs['lon']), lat=('points', sta_fcs['lat']))
        
    wsp10m_2D=(u10m_2D['data'].values**2+v10m_2D['data'].values**2)**0.5
    winddir10m=mpcalc.wind_direction(u10m_2D['data'].values* units('m/s'),v10m_2D['data'].values* units('m/s'))
    if(np.isnan(wsp_sta).any()):
        if(wsp_sta.size == 1):
            wsp_sta[np.isnan(wsp_sta)]=np.squeeze(wsp10m_2D[np.isnan(wsp_sta)])
            TMP_sta[np.isnan(TMP_sta)]=np.squeeze(np.array(t2m_2D)[np.isnan(TMP_sta)])
        else:
            wsp_sta[np.isnan(wsp_sta)]=np.squeeze(wsp10m_2D)[np.isnan(wsp_sta)]
            TMP_sta[np.isnan(TMP_sta)]=np.squeeze(np.array(t2m_2D))[np.isnan(TMP_sta)]
    u_sta,v_sta=mpcalc.wind_components(wsp_sta* units('m/s'),winddir10m)
    
#process zd_sta 10m wind
    zd_fcst_obs=None
    if(draw_zd is True):
        coords3=np.zeros((np.size(zd_sm_alt),3))
        coords3[:,0]=zd_sm_alt
        coords3[:,1]=zd_sm_lat
        coords3[:,2]=zd_sm_lon
        u_sm_sta=interpolator_U(coords3)
        v_sm_sta=interpolator_V(coords3)
        wsp_sm_sta=(u_sm_sta**2+v_sm_sta**2)**0.5
        u10m_sm=u10m.interp(lon=('points', zd_sm_lon), lat=('points', zd_sm_lat))
        v10m_sm=v10m.interp(lon=('points', zd_sm_lon), lat=('points', zd_sm_lat))
        wsp10m_sta=np.squeeze((u10m_sm['data'].values**2+v10m_sm['data'].values**2)**0.5)
        winddir10m_sm=mpcalc.wind_direction(u10m_sm['data'].values* units('m/s'),v10m_sm['data'].values* units('m/s'))
        if(np.isnan(wsp_sm_sta).any()):
            wsp_sm_sta[np.isnan(wsp_sm_sta)]=wsp10m_sta[np.isnan(wsp_sm_sta)]
        
        for ista in range(0,len(wsp10m_sta)):
            if(wsp10m_sta[ista] > wsp_sm_sta[ista]):
                wsp_sm_sta[ista]=wsp10m_sta[ista]

        u_sm_sta,v_sm_sta=mpcalc.wind_components(wsp_sm_sta* units('m/s'),winddir10m_sm)

        zd_fcst_obs={'lon':zd_sm_lon,
                    'lat':zd_sm_lat,
                    'altitude':zd_sm_alt,
                    'U':np.squeeze(np.array(u_sm_sta)),
                    'V':np.squeeze(np.array(v_sm_sta)),
                    'obs_valid':obs_valid,
                    'U_obs':np.squeeze(np.array(zd_sm_u)),
                    'V_obs':np.squeeze(np.array(zd_sm_v))}
#prepare for graphics
    sta_fcs_fcst={'lon':sta_fcs['lon'],
                'lat':sta_fcs['lat'],
                'altitude':sta_fcs['altitude'],
                'name':sta_fcs['name'],
                'TMP':np.array(TMP_sta),
                'U':np.squeeze(np.array(u_sta)),
                'V':np.squeeze(np.array(v_sta))}

    fcst_info=gh.coords

    local_scale_graphics.draw_wind_temp_according_to_4D_data(
            sta_fcs_fcst=sta_fcs_fcst,zd_fcst_obs=zd_fcst_obs,
            fcst_info=fcst_info,
            map_extent=map_extent,
            draw_zd=draw_zd,
            bkgd_type=bkgd_type,bkgd_level=bkgd_level,
            output_dir=output_dir)