# _*_ coding: utf-8 _*_

"""
  Some utility funcations.
"""

import itertools
import string
import pkg_resources
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
import matplotlib.patheffects as mpatheffects
import matplotlib.ticker as mticker
from nmc_met_publish_map.source.lib.read_micaps_17 import read_micaps_17
from cartopy.io.shapereader import Reader
import locale
import cartopy.feature as cfeature
import sys
########
import re
import http.client
from datetime import datetime, timedelta
import numpy as np
import xarray as xr
import pandas as pd
from nmc_met_io import DataBlock_pb2
from nmc_met_io.config import _get_config_from_rcfile
import math
import struct

def obs_radar_filename(time='none', product_name='CREF'):
    """
        Construct obsed radar file name.

    Arguments:
        time {string or datetime object} -- model initial time,
            like '20190514143600' or datetime(2019, 5, 14, 8, 14, 36, 00).
        fhour {int} -- model forecast hours.
    """

    if isinstance(time, datetime):
        timestr=time.strftime('%y%m%d%H%M%S')
        return 'ACHN.'+product_name+'000.'+timestr[0:8] + '.'+timestr[8:14]+'.LATLON'
    else:
        return 'ACHN.'+product_name+'000.'+time[0:8] + '.'+time[8:14]+'.LATLON'

def add_obs_title(title, obs_time, fontsize=20, multilines=False, atime=0):
    """
    Add the title information to the plot.
    :param obs_time: obsed time.
    :param title: str, the plot content information.
    :param fontsize: font size.
    :param multilines: multilines for title.
    :return: None.
    """
    if isinstance(obs_time, np.datetime64):
        obs_time = pd.to_datetime(
            str(obs_time)).replace(tzinfo=None).to_pydatetime()
    obs_time = obs_time.strftime("Observed at %Y/%m/%dT%H:%M")
    if multilines:
        title = title + '\n' + obs_time
        plt.title(title, loc='left', fontsize=fontsize)
    else:
        time_str = obs_time
        plt.title(title, loc='left', fontsize=fontsize)
        plt.title(time_str, loc='right', fontsize=fontsize-2)

def add_logo_extra(fig, x=10, y=10, zorder=100,
             which='nmc', size='medium', **kwargs):
    """
    :param fig: `matplotlib.figure`, The `figure` instance used for plotting
    :param x: x position padding in pixels
    :param y: y position padding in pixels
    :param zorder: The zorder of the logo
    :param which: Which logo to plot 'nmc', 'cmc'
    :param size: Size of logo to be used. Can be:
                 'small' for 40 px square
                 'medium' for 75 px square
                 'large' for 150 px square.
    :param kwargs:
    :return: `matplotlib.image.FigureImage`
             The `matplotlib.image.FigureImage` instance created.
    """
    fname_suffix = {
        'small': '_small.png', 'medium': '_medium.png',
        'large': '_large.png','Xlarge': '_Xlarge.png'}
    fname_prefix = {'nmc': 'nmc', 'cma': 'cma','wmo': 'wmo'}
    try:
        fname = fname_prefix[which] + fname_suffix[size]
        fpath = "resource/logo/" + fname
    except KeyError:
        raise ValueError('Unknown logo size or selection')

    logo = plt.imread(pkg_resources.resource_filename(
        'nmc_met_publish_map', fpath))
    return fig.figimage(logo, x, y, zorder=zorder, **kwargs)

def add_logo_extra_in_axes(pos=[0.1,0.1,.2,.4],
             which='nmc', size='medium', **kwargs):
    """
    :axes_pos:[left,bottom,increase_left,increase_right]
    :param which: Which logo to plot 'nmc', 'cmc'
    :param size: Size of logo to be used. Can be:
                 'small' for 40 px square
                 'medium' for 75 px square
                 'large' for 150 px square.
    :param kwargs:
    """
    fname_suffix = {
        'small': '_small.png', 'medium': '_medium.png',
        'large': '_large.png','Xlarge': '_Xlarge.png'}
    fname_prefix = {'nmc': 'nmc', 'cma': 'cma','wmo': 'wmo'}
    try:
        fname = fname_prefix[which] + fname_suffix[size]
        fpath = "resource/logo/" + fname
    except KeyError:
        raise ValueError('Unknown logo size or selection')

    logo = plt.imread(pkg_resources.resource_filename(
        'nmc_met_publish_map', fpath))

    ax = plt.axes(pos)
    ax.imshow(logo,alpha=0.6)
    ax.axis('off')

def add_city_on_map(ax,map_extent=[70,140,15,55],size=7,small_city=False,zorder=10, **kwargs):
    """
    :param ax: `matplotlib.figure`, The `figure` instance used for plotting
    :param x: x position padding in pixels
    :param kwargs:
    :return: `matplotlib.image.FigureImage`
             The `matplotlib.image.FigureImage` instance created.
    """
    dlon=map_extent[1]-map_extent[0]
    dlat=map_extent[3]-map_extent[2]

    #small city
    if(small_city):
        try:
            fname = 'small_city.000'
            fpath = "resource/" + fname
        except KeyError:
            raise ValueError('can not find the file small_city.000 in the resources')
        city = read_micaps_17(pkg_resources.resource_filename(
            'nmc_met_publish_map', fpath))

        lon=city['lon'].values.astype(np.float)
        lat=city['lat'].values.astype(np.float)
        city_names=city['Name'].values

        for i in range(0,len(city_names)):
            if((lon[i] > map_extent[0]+dlon*0.05) and (lon[i] < map_extent[1]-dlon*0.05) and
            (lat[i] > map_extent[2]+dlat*0.05) and (lat[i] < map_extent[3]-dlat*0.05)):
                    ax.text(lon[i],lat[i],city_names[i], family='SimHei-Bold',ha='right',va='top',size=size-4,color='w',zorder=zorder,**kwargs)
                    ax.text(lon[i],lat[i],city_names[i], family='SimHei',ha='right',va='top',size=size-4,color='black',zorder=zorder,**kwargs)
            ax.scatter(lon[i], lat[i], c='black', s=4, alpha=0.5,zorder=zorder, **kwargs)
#province city
    try:
        fname = 'city_province.000'
        fpath = "resource/" + fname
    except KeyError:
        raise ValueError('can not find the file city_province.000 in the resources')

    city = read_micaps_17(pkg_resources.resource_filename(
        'nmc_met_publish_map', fpath))

    lon=city['lon'].values.astype(np.float)/100.
    lat=city['lat'].values.astype(np.float)/100.
    city_names=city['Name'].values

     # 步骤一（替换sans-serif字体） #得删除C:\Users\HeyGY\.matplotlib 然后重启vs，刷新该缓存目录获得新的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']     
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    for i in range(0,len(city_names)):
        if((lon[i] > map_extent[0]+dlon*0.05) and (lon[i] < map_extent[1]-dlon*0.05) and
        (lat[i] > map_extent[2]+dlat*0.05) and (lat[i] < map_extent[3]-dlat*0.05)):
            if(city_names[i] != '香港' and city_names[i] != '南京' and city_names[i] != '石家庄' and  city_names[i] != '天津'):
                ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60.,int(lat[i])+100*(lat[i]-int(lat[i]))/60.,city_names[i], family='SimHei-Bold',ha='right',va='top',size=size,color='w',zorder=zorder,**kwargs)
                ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60.,int(lat[i])+100*(lat[i]-int(lat[i]))/60.,city_names[i], family='SimHei',ha='right',va='top',size=size,zorder=zorder,**kwargs)
            else:
                ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60.,int(lat[i])+100*(lat[i]-int(lat[i]))/60.,city_names[i], family='SimHei-Bold', ha='left',va='top',size=size,color='w', zorder=zorder,**kwargs)
                ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60.,int(lat[i])+100*(lat[i]-int(lat[i]))/60.,city_names[i], family='SimHei',ha='left',va='top',size=size, zorder=zorder,**kwargs)
            ax.scatter(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60., c='black', s=5, alpha=0.5, zorder=zorder,**kwargs)
    return

def add_china_map_2cartopy_public(ax, name='province', facecolor='none',
                           edgecolor='c', lw=2, **kwargs):
    """
    Draw china boundary on cartopy map.
    :param ax: matplotlib axes instance.
    :param name: map name.
    :param facecolor: fill color, default is none.
    :param edgecolor: edge color.
    :param lw: line width.
    :return: None
    """

    # map name
    names = {'nation': "NationalBorder", 'province': "Province",
             'county': "County", 'river': "hyd1_4l",
             'river_high': "hyd2_4l",
             'coastline':'ne_10m_coastline'}

    # get shape filename
    shpfile = pkg_resources.resource_filename(
        'nmc_met_publish_map', "/resource/shapefile/" + names[name] + ".shp")

    # add map
    ax.add_geometries(
        Reader(shpfile).geometries(), ccrs.PlateCarree(),
        facecolor=facecolor, edgecolor=edgecolor, lw=lw, **kwargs)

def add_public_title(title, initial_time,
                    fhour=0, fontsize=20, multilines=False,atime=24,
                    English=False):
    """
    Add the title information to the plot.
    :param title: str, the plot content information.
    :param initial_time: model initial time.
    :param fhour: forecast hour.
    :param fontsize: font size.
    :param multilines: multilines for title.
    :param atime: accumulating time.
    :return: None.
    """
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if isinstance(initial_time, np.datetime64):
        initial_time = pd.to_datetime(
            str(initial_time)).replace(tzinfo=None).to_pydatetime()

    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')


    if(English == False):
        start_time = initial_time + timedelta(hours=fhour-atime)
        start_time_str=start_time.strftime("%Y年%m月%d日%H时")
        valid_time = initial_time + timedelta(hours=fhour)
        valid_time_str=valid_time.strftime('%m月%d日%H时')
        time_str=start_time_str+'至'+valid_time_str
    else:
        start_time = initial_time + timedelta(hours=fhour-atime)
        start_time_str=start_time.strftime("%Y/%m/%d/%H")
        valid_time = initial_time + timedelta(hours=fhour)
        valid_time_str=valid_time.strftime('%m/%d/%H')
        time_str=start_time_str+' to '+valid_time_str


    plt.title(title, loc='left', fontsize=fontsize)
    plt.title(time_str, loc='right', fontsize=fontsize-6)

def add_south_China_sea(map_extent=[107,120,2,20],pos=[0.1,0.1,.2,.4], **kwargs):

    # draw main figure
    plotcrs = ccrs.PlateCarree(
    central_longitude=100.)
    ax = plt.axes(pos, projection=plotcrs)
    datacrs = ccrs.PlateCarree()
    ax.set_extent(map_extent, crs=datacrs)
    ax.add_feature(cfeature.OCEAN)
    ax.coastlines('50m', edgecolor='black', linewidth=0.5, zorder=50)
    add_china_map_2cartopy_public(
        ax, name='nation', edgecolor='black', lw=0.8, zorder=40)
    ax.background_img(name='RD', resolution='high')

def adjust_map_ratio(ax,map_extent=None,datacrs=None):
    '''
    adjust the map_ratio in the projection of AlbersEqualArea in different area
    :ax = Axes required
    :map_extent=map_extent required
    :datacrs data projection reqired
    :return none
    '''
    map_ratio=(map_extent[1]-map_extent[0])/(map_extent[3]-map_extent[2])
    ax.set_extent(map_extent, crs=datacrs)
    d_y=map_extent[3]-map_extent[2]
    for i in range(0,10000):
        map_ratio_real=(ax.get_extent()[1]-ax.get_extent()[0])/2./((ax.get_extent()[3]-ax.get_extent()[2])/2.)
        if(abs(map_ratio_real-map_ratio) < 0.001):
           break
        if(i == 0):
            if(map_ratio_real-map_ratio > 0):   
                d_y=d_y+d_y*0.001
            if(map_ratio_real-map_ratio <= 0):   
                d_y=d_y-d_y*0.001
            bottom=(map_extent[2]+map_extent[3])/2-d_y/2
            top=(map_extent[2]+map_extent[3])/2+d_y/2
            map_extent2=[map_extent[0],map_extent[1],bottom,top]
        if(i > 0):
            d_y=map_extent2[3]-map_extent2[2]
            if(map_ratio_real-map_ratio > 0):   
                d_y=d_y+d_y*0.001
            if(map_ratio_real-map_ratio <= 0):   
                d_y=d_y-d_y*0.001
            bottom=(map_extent2[2]+map_extent2[3])/2-d_y/2
            top=(map_extent2[2]+map_extent2[3])/2+d_y/2
            map_extent2=[map_extent2[0],map_extent2[1],bottom,top]
        ax.set_extent(map_extent2, crs=datacrs)
    return map_extent2

def add_public_title_obs(title=None, initial_time=None,valid_hour=0, fontsize=20, multilines=False,
                           shw_period=True):

    """
    Add the title information to the plot.
    :param title: str, the plot content information.
    :param initial_time: model initial time.
    :param fhour: forecast hour.
    :param fontsize: font size.
    :param multilines: multilines for title.
    :param atime: accumulating time.
    :shw_period: whether show the obs period
    :return: None.
    """
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if isinstance(initial_time, np.datetime64):
        initial_time = pd.to_datetime(
            str(initial_time)).replace(tzinfo=None).to_pydatetime()

    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')

    obs_time_str=initial_time.strftime("%m月%d日%H时%M分")
    valid_time = initial_time - timedelta(hours=valid_hour)
    valid_time_str=valid_time.strftime('%Y年%m月%d日%H时%M分')

    if(shw_period == False):
        time_str=obs_time_str
    else:    
        time_str=valid_time_str+'至'+obs_time_str

    plt.title(title, loc='left', fontsize=fontsize)
    plt.title(time_str, loc='right', fontsize=fontsize-6)

def get_map_area(area_name):

    """
    Add the title information to the plot.
    :param area_name ,in 
    :param zoom_ratio
    :param cntr_pnt
    :return: None.
    """
    zoom_ratio = {
        '全国':20,
        '华北':5,
        '东北':11,
        '华南':5,
        '西北':6,
        '江南':5,
        '西欧':15,
        '欧洲':25,
        '北美':30,
        '南美':27,
        '南亚':11,
        '东南亚':12,
        '中亚':13,
        '东北亚':20,
        '北非':18,
        '南非':18,
        '澳洲':20}
    cntr_pnt = {
        '全国':[102,34],
        '华北':[116,38],
        '东北':[123.5,45],
        '华南':[110.5,22],
        '西北':[90,43],
        '江南':[112,27.6],
        '西欧':[5,45],
        '欧洲':[14,48],
        '北美':[263,45],
        '南美':[300,-15],
        '南亚':[80,16],
        '东南亚':[110,4],
        '中亚':[55,40],
        '东北亚':[135,40],
        '北非':[13,15],
        '南非':[27,-12],
        '澳洲':[140,-28]}

    cntr_pnt_back=cntr_pnt[area_name]
    zoom_ratio_back=zoom_ratio[area_name]

    return cntr_pnt_back,zoom_ratio_back


def Tmax_stastics(Tmax):

    """
    Add the title information to the plot.
    :param Tmax ,in ,pandas
    """
    #####列明与数据对齐
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    #####列明与数据对齐

    Tmax3=Tmax.drop(['Alt','Grade','610','time'],axis=1)
    Tmax3.rename(columns={'Temp_24h_max':'最高温度','ID':'站号','lon':'经度','lat':'纬度'}, inplace = True)

    print('全国最高温度: '+ '%.2f' % (Tmax3['最高温度'].max())+
        ' 站号: '+ '%i' % (Tmax3['站号'][Tmax3['最高温度'].idxmax()])+
        ' 经度: '+ '%.2f' % (Tmax3['经度'][Tmax3['最高温度'].idxmax()])+
        ' 纬度: '+ '%.2f' % (Tmax3['纬度'][Tmax3['最高温度'].idxmax()]))
    print('高于35摄氏度站点数: '+ str(Tmax3.loc[Tmax3['最高温度'] > 35].count()['站号']))
    print('高于37摄氏度站点数: '+str(Tmax3.loc[Tmax3['最高温度'] > 37].count()['站号']))
    print('高于40摄氏度站点数: '+str(Tmax3.loc[Tmax3['最高温度'] > 40].count()['站号']))
    print(' ')
    print('最高温度排全国前十的站点:')
    print(Tmax3.sort_values(by='最高温度',ascending=False).head(10))

def get_coord_AWX(data_in=None):
    """
    return coordnates of the satellite read from cassandra by get_fy_awx
    :param data_in ,in 
    :lon,lat ,out
    :time, out, datetime
    :return lon,lat,time
    """
    if(data_in[0][0]['flagOfProjection'] == 4):
        nlon=data_in[1].shape[0]
        nlat=data_in[1].shape[1]
        res_x=(data_in[0][0]['longitudeOfEast']-data_in[0][0]['longitudeOfWest'])/(nlon-1)/100.
        res_y=(data_in[0][0]['latitudeOfNorth']-data_in[0][0]['latitudeOfSouth'])/(nlat-1)/100.
        lon=np.arange(nlon)*res_x+data_in[0][0]['longitudeOfWest']/100
        lat=np.arange(nlat)*res_y+data_in[0][0]['latitudeOfSouth']/100

        time=datetime((data_in[0][0]['year']),
            data_in[0][0]['month'],
            data_in[0][0]['day'],
            data_in[0][0]['hour'],
            data_in[0][0]['minute'])


    return lon,lat,time


def model_filename(initial_time, fhour):
    """
        Construct model file name.

    Arguments:
        initial_time {string or datetime object} -- model initial time,
            like 18042008' or datetime(2018, 4, 20, 8).
        fhour {int} -- model forecast hours.
    """

    if isinstance(initial_time, datetime):
        return initial_time.strftime('%y%m%d%H') + ".{:03d}".format(fhour)
    else:
        return initial_time.strip() + ".{:03d}".format(fhour)


def filename_day_back(day_back=0,fhour=0):
    """
    get different initial time from models or observation time according the systime and day_back
    day_back: in, days to go back, days
    fhour: forecast hour for models, for observation, fhour = 0
    return: str, YYMMDDHH.HHH
    """
    hour=int(datetime.now().strftime('%H'))

    if(hour >= 22):
        filename = (datetime.now()-timedelta(hours=day_back*24)).strftime('%Y%m%d')[2:8]+'20.'+'%03d' % fhour
    elif(hour >= 10):    
        filename = (datetime.now()-timedelta(hours=day_back*24)).strftime('%Y%m%d')[2:8]+'08.'+'%03d' % fhour
    else:
        filename = (datetime.now()-timedelta(hours=24)-timedelta(hours=day_back*24)).strftime('%Y%m%d')[2:8]+'20.'+'%03d' % fhour
            
    return filename

def filename_day_back_model(day_back=0,fhour=0):
    """
    get different initial time from models or observation time according the systime and day_back
    day_back: in, days to go back, days
    fhour: forecast hour for models, for observation, fhour = 0
    return: str, YYMMDDHH.HHH
    """
    hour=int(datetime.now().strftime('%H'))

    if(hour >= 14 or hour < 2):
        filename = (datetime.now()-timedelta(hours=day_back*24)).strftime('%Y%m%d')[2:8]+'08.'+'%03d' % fhour
    elif(hour >= 2):    
        filename = (datetime.now()-timedelta(hours=24)-timedelta(hours=day_back*24)).strftime('%Y%m%d')[2:8]+'20.'+'%03d' % fhour
    return filename    

def wind2UV(Winddir=None,Windsp=None):
    """
    Winddir, in, Wind direction
    Windsp, in, Wind speed
    U,V, out, U V wind
    """

    U=np.empty(len(Winddir))
    V=np.empty(len(Winddir))


    idx_msk1=np.where(((Winddir >= 0) & (Winddir < 90)) | 
        ((Winddir >= 270) & (Winddir < 360)))
    V[idx_msk1]=-1*Windsp[idx_msk1]*abs(np.cos(np.radians(Winddir[idx_msk1])))

    idx_msk2=np.where(((Winddir >= 90) & (Winddir < 270)))
    V[idx_msk2]=Windsp[idx_msk2]*abs(np.cos(Winddir[idx_msk2]))

    idx_msk3=np.where(((Winddir >= 0) & (Winddir < 180)))
    U[idx_msk3]=-1*Windsp[idx_msk3]*abs(np.sin(np.radians(Winddir[idx_msk3])))

    idx_msk4=np.where(((Winddir >= 180) & (Winddir < 360)))
    U[idx_msk4]=Windsp[idx_msk4]*abs(np.sin(np.radians(Winddir[idx_msk4])))

    return U,V

def add_public_title_sta(title=None, initial_time=None,fontsize=20,English=False):

    """
    Add the title information to the plot.
    :param title: str, the plot content information.
    :param initial_time: model initial time.
    :param fhour: forecast hour.
    :param fontsize: font size.
    :param atime: accumulating time.
    :shw_period: whether show the obs period
    :return: None.
    """
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if isinstance(initial_time, np.datetime64):
        initial_time = pd.to_datetime(
            str(initial_time)).replace(tzinfo=None).to_pydatetime()

    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')

    if(English == False):
        initial_time_str=initial_time.strftime("%Y年%m月%d日%H时")
        time_str='起报时间：'+initial_time_str
    else:
        initial_time_str=initial_time.strftime("%Y%m%d%H")
        time_str='Initial Time：'+initial_time_str

    plt.title(title, loc='left', fontsize=fontsize)
    plt.title(time_str, loc='right', fontsize=fontsize-6)

def Cassandra_dir(data_type=None,data_source=None,var_name=None,lvl=None
    ):

    dir_mdl_high={
            'ECMWF':{
                    'HGT':'ECMWF_HR/HGT/',
                    'UGRD':'ECMWF_HR/UGRD/',
                    'VGRD':'ECMWF_HR/VGRD/',
                    'IR':'ECMWF_HR/MET_10/',
                    'VVEL':'ECMWF_HR/VVEL/',
                    'RH':'ECMWF_HR/RH/',
                    'SPFH':'ECMWF_HR/SPFH/',
                    'TMP':'ECMWF_HR/TMP/',
                    },
            'GRAPES_GFS':{
                    'HGT':'GRAPES_GFS/HGT/',
                    'UGRD':'GRAPES_GFS/UGRD/',
                    'VGRD':'GRAPES_GFS/VGRD/',
                    'IR':'GRAPES_GFS/INFRARED_BRIGHTNESS_TEMPERATURE/',
                    'RH':'GRAPES_GFS/RH/',
                    'SPFH':'GRAPES_GFS/SPFH/',
                    'TMP':'GRAPES_GFS/TMP/',
                    'WVFL':'GRAPES_GFS/WVFL/',
                    'THETAE':'GRAPES_GFS/THETASE/'
                    },
            'NCEP_GFS':{
                    'HGT':'NCEP_GFS/HGT/',
                    'UGRD':'NCEP_GFS/UGRD/',
                    'VGRD':'NCEP_GFS/VGRD/',
                    'VVEL':'NCEP_GFS/VVEL/',
                    'RH':'NCEP_GFS/RH/',
                    'TMP':'NCEP_GFS/TMP/',
                    },
            'OBS':{            
                    'PLOT':'UPPER_AIR/PLOT/'
                    }
            }

    dir_mdl_sfc={
            'ECMWF':{
                    'u10m':'ECMWF_HR/UGRD_10M/',
                    'v10m':'ECMWF_HR/VGRD_10M/',
                    'u100m':'ECMWF_HR/UGRD_100M/',
                    'v100m':'ECMWF_HR/VGRD_100M/',                    
                    'PRMSL':'ECMWF_HR/PRMSL/',
                    'RAIN24':'ECMWF_HR/RAIN24/',
                    'RAIN03':'ECMWF_HR/RAIN03/',                    
                    'RAIN06':'ECMWF_HR/RAIN06/',
                    'RAINC06':'ECMWF_HR/RAINC06/',
                    'SNOW03':'ECMWF_HR/SNOW03/',
                    'SNOW06':'ECMWF_HR/SNOW06/',
                    'SNOW24':'ECMWF_HR/SNOW024/',
                    'TCWV':'ECMWF_HR/TCWV/',
                    '10M_GUST_3H':'ECMWF_HR/10_METRE_WIND_GUST_IN_THE_LAST_3_HOURS/',
                    '10M_GUST_6H':'ECMWF_HR/10_METRE_WIND_GUST_IN_THE_LAST_6_HOURS/',
                    'LCDC':'ECMWF_HR/LCDC/',
                    'TCDC':'ECMWF_HR/TCDC/',
                    'T2m':'ECMWF_HR/TMP_2M/',
                    'Td2m':'ECMWF_HR/DPT_2M/'
                    },
            'GRAPES_GFS':{
                    'u10m':'GRAPES_GFS/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'GRAPES_GFS/VGRD/10M_ABOVE_GROUND/',
                    'PRMSL':'GRAPES_GFS/PRMSL/',
                    'RAIN24':'GRAPES_GFS/RAIN24/',
                    'RAIN03':'GRAPES_GFS/RAIN03/',                    
                    'RAIN06':'GRAPES_GFS/RAIN06/',
                    'RAINC06':'GRAPES_GFS/RAINC06/',
                    'SNOW03':'GRAPES_GFS/SNOW03/',
                    'SNOW06':'GRAPES_GFS/SNOW06/',
                    'SNOW24':'GRAPES_GFS/SNOW024/',
                    'TCWV':'GRAPES_GFS/PWAT/ENTIRE_ATMOSPHERE/',
                    'T2m':'GRAPES_GFS/TMP/2M_ABOVE_GROUND/',
                    'rh2m':'GRAPES_GFS/RH/2M_ABOVE_GROUND/',
                    'Td2m':'GRAPES_GFS/DPT/2M_ABOVE_GROUND/',
                    'BLI':'GRAPES_GFS/BLI/'
                    },
            'NCEP_GFS':{
                    'u10m':'NCEP_GFS/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'NCEP_GFS/VGRD/10M_ABOVE_GROUND/',
                    'PRMSL':'NCEP_GFS/PRMSL/',
                    'RAIN24':'NCEP_GFS/RAIN24/',
                    'RAIN03':'NCEP_GFS/RAIN03/',
                    'RAIN06':'NCEP_GFS/RAIN06/',
                    'RAINC06':'NCEP_GFS/RAINC06/',
                    'TCWV':'NCEP_GFS/PWAT/ENTIRE_ATMOSPHERE/',
                    'T2m':'NCEP_GFS/TMP/2M_ABOVE_GROUND/',
                    'rh2m':'NCEP_GFS/RH/2M_ABOVE_GROUND/',
                    'Td2m':'NCEP_GFS/DPT/2M_ABOVE_GROUND/',
                    'BLI':'NCEP_GFS/BLI/'
                    },

            'OBS':{
                'Tmx_2m':'SURFACE/TMP_MAX_24H_ALL_STATION/',
                'PLOT_GLOBAL_3H':'SURFACE/PLOT_GLOBAL_3H/',
                'CREF':'RADARMOSAIC/CREF/'
                    },

            '中央台指导预报':{
                    'u10m':'NWFD_SCMOC/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'NWFD_SCMOC/VGRD/10M_ABOVE_GROUND/',
                    'RAIN24':'NWFD_SCMOC/RAIN24/',
                    'RAIN06':'NWFD_SCMOC/RAIN06/',
                    'RAIN03':'NWFD_SCMOC/RAIN03/',
                    'Tmx_2m':'NWFD_SCMOC/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'Tmn_2m':'NWFD_SCMOC/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'T2m':'NWFD_SCMOC/TMP/2M_ABOVE_GROUND/',
                    'VIS':'NWFD_SCMOC/VIS_SURFACE/',
                    'rh2m':'NWFD_SCMOC/RH/2M_ABOVE_GROUND/'
                    },
            '国省反馈预报':{
                    'u10m':'NWFD_SMERGE/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'NWFD_SMERGE/VGRD/10M_ABOVE_GROUND/',
                    'RAIN24':'NWFD_SMERGE/RAIN24/',
                    'RAIN06':'NWFD_SMERGE/RAIN06/',
                    'RAIN03':'NWFD_SMERGE/RAIN03/',
                    'Tmx_2m':'NWFD_SMERGE/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'Tmn_2m':'NWFD_SMERGE/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'T2m':'NWFD_SMERGE/TMP/2M_ABOVE_GROUND/',  
                    'rh2m':'NWFD_SMERGE/RH/2M_ABOVE_GROUND/'               
                    },
            'CLDAS':{
                    'Tmx_2m':"CLDAS/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/"  
                    } 
            }
    if(data_type== 'high'):
        dir_full=dir_mdl_high[data_source][var_name]+str(lvl)+'/'

    if(data_type== 'surface'):
        dir_full=dir_mdl_sfc[data_source][var_name]

    return dir_full


def load_array(file):
    """
    从二进制文件中加载二维数组并返回
    :param file:
    :return:
    """
    f = open(file, 'rb')
    c = f.read()
    # c = zlib.decompress(c)
    data = struct.unpack(('%df' % (len(c) / 4)), c)
    return data

"""
读取国外城市报
:param file:
:return:
"""

from itertools import islice

MISSING_VALUE = '9999.00'

class SCMOC(object):

    def __init__(self, file, site_ids=None, ec_eo=False):
        self.data = {}
       # print('load file %s' % file)
        try:
            with open(file, encoding='utf-8', errors='ignore') as f:
                for site_num_line in islice(f, 4, 5):
                    self.site_num = int(site_num_line.strip())
                for line in f:
                    #print(line)
                    line_item = line.split()
                    if len(line_item) == 8:
                        if site_ids and line_item[0] not in site_ids:
                            site_id = None
                            continue
                        site_id = line_item[0]
                        self.data.update({site_id: {}})
                        self.data[site_id].update({line_item[0]: line_item[1:]})
                    if len(line_item) == 22:
                        if site_id:
                            if line_item[1] == '0.00':
                                line_item[1] = MISSING_VALUE
                            if ec_eo:
                                for index, item in enumerate(line_item[1:]):
                                    if item == '999.90':
                                        line_item[index + 1] = MISSING_VALUE
                            self.data[site_id].update({line_item[0]: line_item[1:]})
        except FileNotFoundError:
            print('----%s not exists!!!' % file)


if __name__ == '__main__':
    s = SCMOC(r'D:\forecast_glb\data\sta\N_SEVP_NMC_RFFC_SFER_EME_AGLB_L88_P9_20190728120014412.txt')
    data = s.data
    print(data)

