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
import matplotlib.pyplot as plt
import matplotlib.patheffects as mpatheffects
from cartopy.io.shapereader import Reader
import locale
import cartopy.feature as cfeature
import sys
########
import re
import http.client
from datetime import datetime, timedelta
import pandas as pd
import math
import struct
from nmc_met_io.retrieve_micaps_server import get_model_grids
from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata
import matplotlib as mpl
import os.path
import cartopy.io.img_tiles as cimgt
import matplotlib.colors as colors
import nmc_met_graphics.cmap.cm as cm_collected
from scipy.interpolate import LinearNDInterpolator
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import Point as ShapelyPoint
from scipy.ndimage.filters import minimum_filter, maximum_filter
import xarray as xr


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
        fpath = "resources/logo/" + fname
    except KeyError:
        raise ValueError('Unknown logo size or selection')

    logo = plt.imread(pkg_resources.resource_filename(
        'nmc_met_map', fpath))
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
        fpath = "resources/logo/" + fname
    except KeyError:
        raise ValueError('Unknown logo size or selection')
    logo = plt.imread(pkg_resources.resource_filename(
        'nmc_met_map', fpath))

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
    # if(small_city):
    #     try:
    #         fname = 'small_city.000'
    #         fpath = "resources/" + fname
    #     except KeyError:
    #         raise ValueError('can not find the file small_city.000 in the resources')
    #     city = read_micaps_17(pkg_resources.resource_filename(
    #         'nmc_met_map', fpath))

    #     lon=city['lon'].values.astype(np.float)
    #     lat=city['lat'].values.astype(np.float)
    #     city_names=city['Name'].values

    #     for i in range(0,len(city_names)):
    #         if((lon[i] > map_extent[0]+dlon*0.05) and (lon[i] < map_extent[1]-dlon*0.05) and
    #         (lat[i] > map_extent[2]+dlat*0.05) and (lat[i] < map_extent[3]-dlat*0.05)):
    #                 #ax.text(lon[i],lat[i],city_names[i], family='SimHei-Bold',ha='right',va='top',size=size-4,color='w',zorder=zorder,**kwargs)
    #             ax.text(lon[i],lat[i],city_names[i], family='SimHei',ha='right',va='top',size=size-4,color='black',zorder=zorder,**kwargs)
    #         ax.scatter(lon[i], lat[i], c='black', s=25, alpha=0.5,zorder=zorder, **kwargs)
    #province city
    try:
        fname = 'city_province.000'
        fpath = "resources/" + fname
    except KeyError:
        raise ValueError('can not find the file city_province.000 in the resources')

    city = read_micaps_17(pkg_resources.resource_filename(
        'nmc_met_map', fpath))

    lon=city['lon'].values.astype(np.float)/100.
    lat=city['lat'].values.astype(np.float)/100.
    city_names=city['Name'].values

     # 步骤一（替换sans-serif字体） #得删除C:\Users\HeyGY\.matplotlib 然后重启vs，刷新该缓存目录获得新的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']     
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    for i in range(0,len(city_names)):
        if((lon[i] > map_extent[0]+dlon*0.05) and (lon[i] < map_extent[1]-dlon*0.05) and
        (lat[i] > map_extent[2]+dlat*0.05) and (lat[i] < map_extent[3]-dlat*0.05)):
            if((np.array(['香港','南京','石家庄','天津','济南','上海'])!=city_names[i]).all()):
                r = city_names[i]
                t=ax.text(lon[i],lat[i],city_names[i], family='SimHei',ha='right',va='top',size=size,zorder=zorder,**kwargs)
            else:
                t=ax.text(lon[i],lat[i],city_names[i], family='SimHei',ha='left',va='top',size=size,
                zorder=zorder,**kwargs)
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                       mpatheffects.Normal()])
            s=ax.scatter(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60., c='black', s=25, zorder=zorder,**kwargs)
            s.set_path_effects([mpatheffects.Stroke(linewidth=5, foreground='#D9D9D9'),
                       mpatheffects.Normal()])
    return

def add_city_and_number_on_map(ax,map_extent=[70,140,15,55],size=7,small_city=False,zorder=10,
     data=None,cmap=None,**kwargs):
    
    dlon=map_extent[1]-map_extent[0]
    dlat=map_extent[3]-map_extent[2]

    #small city
    if(small_city):
        try:
            fname = 'small_city.000'
            fpath = "resources/" + fname
        except KeyError:
            raise ValueError('can not find the file small_city.000 in the resources')
        city = read_micaps_17(pkg_resources.resource_filename(
            'nmc_met_map', fpath))

        lon=city['lon'].values.astype(np.float)
        lat=city['lat'].values.astype(np.float)
        city_names=city['Name'].values

        for i in range(0,len(city_names)):
            if((lon[i] > map_extent[0]+dlon*0.05) and (lon[i] < map_extent[1]-dlon*0.05) and
            (lat[i] > map_extent[2]+dlat*0.05) and (lat[i] < map_extent[3]-dlat*0.05)):
                    #ax.text(lon[i],lat[i],city_names[i], family='SimHei-Bold',ha='right',va='top',size=size-4,color='w',zorder=zorder,**kwargs)
                ax.text(lon[i],lat[i],city_names[i], family='SimHei',ha='right',va='top',size=size-4,color='black',zorder=zorder,**kwargs)
            ax.scatter(lon[i], lat[i], c='black', s=25, alpha=0.5,zorder=zorder, **kwargs)
    #province city
    try:
        fname = 'city_province.000'
        fpath = "resources/" + fname
    except KeyError:
        raise ValueError('can not find the file city_province.000 in the resources')

    city = read_micaps_17(pkg_resources.resource_filename(
        'nmc_met_map', fpath))

    lon=city['lon'].values.astype(np.float)/100.
    lat=city['lat'].values.astype(np.float)/100.
    city_names=city['Name'].values
    
    number_city=data.interp(lon=('points',lon),lat=('points',lat))

     # 步骤一（替换sans-serif字体） #得删除C:\Users\HeyGY\.matplotlib 然后重启vs，刷新该缓存目录获得新的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']     
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    for i in range(0,len(city_names)):
        if((lon[i] > map_extent[0]+dlon*0.05) and (lon[i] < map_extent[1]-dlon*0.05) and
        (lat[i] > map_extent[2]+dlat*0.05) and (lat[i] < map_extent[3]-dlat*0.05)):
            if((np.array(['香港','南京','石家庄','天津','济南','上海'])!=city_names[i]).all()):
                r = city_names[i]
                t=ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60.
                    ,city_names[i], family='SimHei',ha='right',va='top',size=size,zorder=zorder,**kwargs)
                num=ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60.
                    ,'%.1f'%np.squeeze(number_city['data'].values)[i],
                     family='SimHei',ha='right',va='bottom',size=size,zorder=zorder,**kwargs)
            else:
                t=ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60.
                    ,city_names[i], family='SimHei',ha='left',va='top',size=size,
                    zorder=zorder,**kwargs)
                num=ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60.
                    ,'%.1f'%np.squeeze(number_city['data'].values)[i],
                     family='SimHei',ha='left',va='bottom',size=size,zorder=zorder,**kwargs)
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                       mpatheffects.Normal()])
            num.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                       mpatheffects.Normal()])
            ax.scatter(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60., c='black', s=25, zorder=zorder,**kwargs)
    return


def add_city_values_on_map(ax,data,map_extent=[70,140,15,55],size=13,zorder=10,cmap=None,transform=ccrs.PlateCarree(),**kwargs):
    
    dlon=map_extent[1]-map_extent[0]
    dlat=map_extent[3]-map_extent[2]
    #province city
    try:
        fname = 'city_province.000'
        fpath = "resources/" + fname
    except KeyError:
        raise ValueError('can not find the file city_province.000 in the resources')

    city = read_micaps_17(pkg_resources.resource_filename(
        'nmc_met_map', fpath))

    lon=city['lon'].values.astype(np.float)/100.
    lat=city['lat'].values.astype(np.float)/100.
    city_names=city['Name'].values
    
    number_city=data.interp(lon=('points',lon),lat=('points',lat))

     # 步骤一（替换sans-serif字体） #得删除C:\Users\HeyGY\.matplotlib 然后重启vs，刷新该缓存目录获得新的字体
    plt.rcParams['font.sans-serif'] = ['SimHei']     
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    for i in range(0,len(city_names)):
        if((lon[i] > map_extent[0]+dlon*0.05) and (lon[i] < map_extent[1]-dlon*0.05) and
        (lat[i] > map_extent[2]+dlat*0.05) and (lat[i] < map_extent[3]-dlat*0.05)):
            if((np.array(['香港','南京','石家庄','天津','济南','上海'])!=city_names[i]).all()):
                r = city_names[i]
                num=ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60.
                    ,'%.1f'%np.squeeze(number_city.values)[i],
                     family='SimHei',ha='right',va='bottom',size=size,zorder=zorder,transform=transform,**kwargs)
            else:
                num=ax.text(int(lon[i])+100*(lon[i]-int(lon[i]))/60., int(lat[i])+100*(lat[i]-int(lat[i]))/60.
                    ,'%.1f'%np.squeeze(number_city.values)[i],
                     family='SimHei',ha='left',va='bottom',size=size,zorder=zorder,transform=transform,**kwargs)
            num.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                       mpatheffects.Normal()])
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
             'coastline':'ne_10m_coastline',
             'world':'world_line',
             'Yangtze_basin':'Yangtze_line',
             'MurrayDarling_basin':'MurrayDarling_complete',
             'MISSISSIPPI_basin':'MISSISSIPPI_line',
             'MEKONG_basin':'MEKONG_Line',
             'Amazonas_basin':'Amazonas_Line'}

    # get shape filename
    shpfile = pkg_resources.resource_filename(
        'nmc_met_map', "/resources/shapefile/" + names[name] + ".shp")

    # add map
    ax.add_geometries(
        Reader(shpfile).geometries(), ccrs.PlateCarree(),
        facecolor=facecolor, edgecolor=edgecolor, lw=lw, **kwargs)

def add_public_title(title, initTime,
                    fhour=0, fontsize=20, multilines=False,atime=24,
                    English=False):
    """
    Add the title information to the plot.
    :param title: str, the plot content information.
    :param initTime: model initial time.
    :param fhour: forecast hour.
    :param fontsize: font size.
    :param multilines: multilines for title.
    :param atime: accumulating time.
    :return: None.
    """
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if isinstance(initTime, np.datetime64):
        initTime = pd.to_datetime(
            str(initTime)).replace(tzinfo=None).to_pydatetime()

    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')


    if(English == False):
        start_time = initTime + timedelta(hours=fhour-atime)
        start_time_str=start_time.strftime("%Y年%m月%d日%H时")
        valid_time = initTime + timedelta(hours=fhour)
        valid_time_str=valid_time.strftime('%m月%d日%H时')
        time_str=start_time_str+'至'+valid_time_str
    else:
        start_time = initTime + timedelta(hours=fhour-atime)
        start_time_str=start_time.strftime("%Y/%m/%d/%H")
        valid_time = initTime + timedelta(hours=fhour)
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
    #ax.background_img(name='RD', resolution='high')
    add_cartopy_background(ax,name='RD')
    
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
    map_extent2=[]
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
    if(map_extent2 == []):
        return map_extent
    else:
        return map_extent2

def add_public_title_obs(title=None, initTime=None,valid_hour=0, fontsize=20, multilines=False,
                           shw_period=True):

    """
    Add the title information to the plot.
    :param title: str, the plot content information.
    :param initTime: model initial time.
    :param fhour: forecast hour.
    :param fontsize: font size.
    :param multilines: multilines for title.
    :param atime: accumulating time.
    :shw_period: whether show the obs period
    :return: None.
    """
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if isinstance(initTime, np.datetime64):
        initTime = pd.to_datetime(
            str(initTime)).replace(tzinfo=None).to_pydatetime()

    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')

    obs_time_str=initTime.strftime("%m月%d日%H时%M分")
    valid_time = initTime - timedelta(hours=valid_hour)
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
        '江淮':5,
        '华中':4,
        '西南':7,
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
        '江淮':[115,31],
        '华中':[112,30],
        '西南':[103,26.5],
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


def model_filename(initTime, fhour,UTC=False):

    if(UTC is False):
        if isinstance(initTime, datetime):
            return initTime.strftime('%y%m%d%H') + ".{:03d}".format(fhour)
        else:
            return initTime.strip() + ".{:03d}".format(fhour)
    else:
        if isinstance(initTime, datetime):
            return (initTime-timedelta(hours=8)).strftime('%y%m%d%H') + ".{:03d}".format(fhour)
        else:
            time_rel = (datetime.strptime('20'+initTime,'%Y%m%d%H')-timedelta(hours=8)).strftime('%y%m%d%H')
            return time_rel.strip() + ".{:03d}".format(fhour)

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

def filename_day_back_model(day_back=0,fhour=0,UTC=False):
    """
    get different initial time from models or observation time according the systime and day_back
    day_back: in, days to go back, days
    fhour: forecast hour for models, for observation, fhour = 0
    return: str, YYMMDDHH.HHH
    """
    hour=int(datetime.now().strftime('%H'))

    if(UTC is False):
        if(hour >= 14):
            initTime = (datetime.now()).strftime('%Y%m%d')+'08'
        elif(hour >= 2):    
            initTime = (datetime.now()-timedelta(hours=24)).strftime('%Y%m%d')+'20'
        else:
            initTime = (datetime.now()-timedelta(hours=24)).strftime('%Y%m%d')+'08'
    if(UTC is True):
        if(hour >= 14 or hour < 2):
            initTime = (datetime.now()).strftime('%Y%m%d')+'00'
        elif(hour >= 2):    
            initTime = (datetime.now()-timedelta(hours=24)).strftime('%Y%m%d')+'12'
        else:
            initTime = (datetime.now()-timedelta(hours=24)).strftime('%Y%m%d')+'00'
    #process day back
    initTime_dayback=datetime.strptime(initTime,'%Y%m%d%H')-timedelta(hours=day_back*24)
    filename=initTime_dayback.strftime('%Y%m%d%H')[2:10]+'.%03d'%fhour
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

def add_public_title_sta(title=None, initTime=None,fontsize=20,English=False):

    """
    Add the title information to the plot.
    :param title: str, the plot content information.
    :param initTime: model initial time.
    :param fhour: forecast hour.
    :param fontsize: font size.
    :param atime: accumulating time.
    :shw_period: whether show the obs period
    :return: None.
    """
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if isinstance(initTime, np.datetime64):
        initTime = pd.to_datetime(
            str(initTime)).replace(tzinfo=None).to_pydatetime()

    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')

    if(English == False):
        initTime_str=initTime.strftime("%Y年%m月%d日%H时")
        time_str='起报时间：'+initTime_str
    else:
        initTime_str=initTime.strftime("%Y%m%d%H")
        time_str='Initial Time：'+initTime_str

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
                    'TMP':'ECMWF_HR/TMP/'
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
                    'THETAE':'GRAPES_GFS/THETASE/',
                    'VVEL':'GRAPES_GFS/VVEL_GEOMETRIC/'
                    },
            'NCEP_GFS':{
                    'HGT':'NCEP_GFS_HR/HGT/',
                    'UGRD':'NCEP_GFS_HR/UGRD/',
                    'VGRD':'NCEP_GFS_HR/VGRD/',
                    'VVEL':'NCEP_GFS_HR/VVEL/',
                    'RH':'NCEP_GFS_HR/RH/',
                    'TMP':'NCEP_GFS_HR/TMP/',
                    },
            'ECMWF_ENSEMBLE':{
                    'UGRD_RAW':'ECMWF_ENSEMBLE/RAW/UGRD/',
                    'VGRD_RAW':'ECMWF_ENSEMBLE/RAW/VGRD/',
                    'HGT_RAW':'ECMWF_ENSEMBLE/RAW/HGT/',
                    'TMP_RAW':'ECMWF_ENSEMBLE/RAW/TMP/'
                    },
            'GRAPES_3KM':{
                    'HGT':'GRAPES_3KM/HGT/',
                    'UGRD':'GRAPES_3KM/UGRD/',
                    'VGRD':'GRAPES_3KM/VGRD/',
                    'IR':'GRAPES_3KM/INFRARED_BRIGHTNESS_TEMPERATURE/',
                    'RH':'GRAPES_3KM/RH/',
                    'SPFH':'GRAPES_3KM/SPFH/',
                    'TMP':'GRAPES_3KM/TMP/',
                    'WVFL':'GRAPES_3KM/WVFL/',
                    'THETAE':'GRAPES_3KM/THETASE/'
                    },
            'OBS':{            
                    'TLOGP':'UPPER_AIR/TLOGP/',
                    'PLOT':'UPPER_AIR/PLOT/',
                    'FY4AL1':'SATELLITE/FY4A/L1/CHINA/'
                    }
            }

    dir_mdl_sfc={
            'ECMWF':{
                    'u10m':'ECMWF_HR/UGRD_10M/',
                    'v10m':'ECMWF_HR/VGRD_10M/',
                    'u100m':'ECMWF_HR/UGRD_100M/',
                    'v100m':'ECMWF_HR/VGRD_100M/',
                    'wind10m':'ECMWF_HR/WIND_10M/',
                    'PRMSL':'ECMWF_HR/PRMSL/',
                    'RAIN24':'ECMWF_HR/RAIN24/',
                    'RAIN03':'ECMWF_HR/RAIN03/',                    
                    'RAIN06':'ECMWF_HR/RAIN06/',
                    'RAINC06':'ECMWF_HR/RAINC06/',
                    'SNOW03':'ECMWF_HR/SNOW03/',
                    'SNOW06':'ECMWF_HR/SNOW06/',
                    'SNOW24':'ECMWF_HR/SNOW24/',
                    'TCWV':'ECMWF_HR/TCWV/',
                    '10M_GUST_3H':'ECMWF_HR/10_METRE_WIND_GUST_IN_THE_LAST_3_HOURS/',
                    '10M_GUST_6H':'ECMWF_HR/10_METRE_WIND_GUST_IN_THE_LAST_6_HOURS/',
                    'LCDC':'ECMWF_HR/LCDC/',
                    'TCDC':'ECMWF_HR/TCDC/',
                    'T2m':'ECMWF_HR/TMP_2M/',
                    'Td2m':'ECMWF_HR/DPT_2M/',
                    'PSFC':'ECMWF_HR/PRES/SURFACE/',
                    'ORO':'ECMWF_HR/OROGRAPHY/',
                    'Tmx3_2m':'ECMWF_HR/MAXIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_3_HOURS/',
                    'Tmn3_2m':'ECMWF_HR/MINIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_3_HOURS/'
                    },
            'GRAPES_GFS':{
                    'u10m':'GRAPES_GFS/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'GRAPES_GFS/VGRD/10M_ABOVE_GROUND/',
                    'wind10m':'GRAPES_GFS/WIND/10M_ABOVE_GROUND/',
                    'PRMSL':'GRAPES_GFS/PRMSL/',
                    'RAIN24':'GRAPES_GFS/RAIN24/',
                    'RAIN03':'GRAPES_GFS/RAIN03/',                    
                    'RAIN06':'GRAPES_GFS/RAIN06/',
                    'RAINC06':'GRAPES_GFS/RAINC06/',
                    'SNOW03':'GRAPES_GFS/SNOW03/',
                    'SNOW06':'GRAPES_GFS/SNOW06/',
                    'SNOW24':'GRAPES_GFS/SNOW24/',
                    'TCWV':'GRAPES_GFS/PWAT/ENTIRE_ATMOSPHERE/',
                    'T2m':'GRAPES_GFS/TMP/2M_ABOVE_GROUND/',
                    'Tmx3_2m':'GRAPES_GFS/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'Tmn3_2m':'GRAPES_GFS/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'rh2m':'GRAPES_GFS/RH/2M_ABOVE_GROUND/',
                    'Td2m':'GRAPES_GFS/DPT/2M_ABOVE_GROUND/',
                    'BLI':'GRAPES_GFS/BLI/',
                    'PSFC':'GRAPES_GFS/PRES/SURFACE/',
                    'ORO':'GRAPES_GFS/HGT/SURFACE/'
                    },
            'NCEP_GFS':{
                    'u10m':'NCEP_GFS_HR/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'NCEP_GFS_HR/VGRD/10M_ABOVE_GROUND/',
                    'wind10m':'NCEP_GFS_HR/WIND/10M_ABOVE_GROUND/',
                    'PRMSL':'NCEP_GFS_HR/PRMSL/',
                    'RAIN24':'NCEP_GFS_HR/RAIN24/',
                    'RAIN03':'NCEP_GFS_HR/RAIN03/',
                    'RAIN06':'NCEP_GFS_HR/RAIN06/',
                    'RAINC06':'NCEP_GFS_HR/RAINC06/',
                    'TCWV':'NCEP_GFS_HR/PWAT/ENTIRE_ATMOSPHERE/',
                    'T2m':'NCEP_GFS_HR/TMP/2M_ABOVE_GROUND/',
                    'Tmx3_2m':'NCEP_GFS_HR/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'Tmn3_2m':'NCEP_GFS_HR/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'rh2m':'NCEP_GFS_HR/RH/2M_ABOVE_GROUND/',
                    'Td2m':'NCEP_GFS_HR/DPT/2M_ABOVE_GROUND/',
                    'BLI':'NCEP_GFS_HR/BLI/',
                    'PSFC':'NCEP_GFS_HR/PRES/SURFACE/',
                    'ORO':'NCEP_GFS_HR/HGT/SURFACE/'
                    },
            'GRAPES_3KM':{
                    'u10m':'GRAPES_3KM/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'GRAPES_3KM/VGRD/10M_ABOVE_GROUND/',
                    'wind10m':'GRAPES_3KM/WIND/10M_ABOVE_GROUND/',
                    'PRMSL':'GRAPES_3KM/PRMSL/',
                    'RAIN24':'GRAPES_3KM/RAIN24/',
                    'RAIN03':'GRAPES_3KM/RAIN03/',                    
                    'RAIN06':'GRAPES_3KM/RAIN06/',
                    'RAINC06':'GRAPES_3KM/RAINC06/',
                    'SNOW03':'GRAPES_3KM/SNOW03/',
                    'SNOW06':'GRAPES_3KM/SNOW06/',
                    'SNOW24':'GRAPES_3KM/SNOW024/',
                    'TCWV':'GRAPES_3KM/PWAT/ENTIRE_ATMOSPHERE/',
                    'T2m':'GRAPES_3KM/TMP/2M_ABOVE_GROUND/',
                    'Tmx3_2m':'GRAPES_3KM/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'Tmn3_2m':'GRAPES_3KM/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'rh2m':'GRAPES_3KM/RH/2M_ABOVE_GROUND/',
                    'Td2m':'GRAPES_3KM/DPT/2M_ABOVE_GROUND/',
                    'BLI':'GRAPES_3KM/BLI/',
                    'PSFC':'GRAPES_3KM/PRES/SURFACE/',
                    'ORO':'GRAPES_3KM/HGT/SURFACE/'
                    },
            'ECMWF_ENSEMBLE':{
                    'RAIN06_RAW':'ECMWF_ENSEMBLE/RAW/RAIN06/'
                    },
            'OBS':{
                'Tmx_2m':'SURFACE/TMP_MAX_24H_ALL_STATION/',
                'PLOT_ALL':'SURFACE/PLOT_ALL/',
                'RAIN06_ALL':'SURFACE/RAIN06_ALL_STATION/',
                'RAIN03_ALL':'SURFACE/RAIN06_ALL_STATION/',
                'PLOT_GLOBAL_3H':'SURFACE/PLOT_GLOBAL_3H/',
                'CREF':'RADARMOSAIC/CREF/',
                'PLOT_GUST':'SURFACE/MAX_WIND/'
                    },
            '中央气象台中短期指导':{
                    'u10m':'NWFD_SCMOC/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'NWFD_SCMOC/VGRD/10M_ABOVE_GROUND/',
                    'wind10m':'NWFD_SCMOC/WIND/10M_ABOVE_GROUND/',
                    'RAIN24':'NWFD_SCMOC/RAIN24/',
                    'RAIN06':'NWFD_SCMOC/RAIN06/',
                    'RAIN03':'NWFD_SCMOC/RAIN03/',
                    'Tmx_2m':'NWFD_SCMOC/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'Tmn_2m':'NWFD_SCMOC/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'T2m':'NWFD_SCMOC/TMP/2M_ABOVE_GROUND/',
                    'VIS':'NWFD_SCMOC/VIS/',
                    'rh2m':'NWFD_SCMOC/RH/2M_ABOVE_GROUND/'
                    },
            '中央气象台智能网格':{
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
                    'Tmx_2m':"CLDAS/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/",
                    'RAIN24':'CLDAS/RAIN24_TRI_DATA_SOURCE/'
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


def get_model_points_gy(directory, filenames, points, allExists=True,fill_null=False,Null_value=0):
    """
    Retrieve point time series from MICAPS cassandra service.
    
    Args:
        directory (string): the data directory on the service.
        filenames (list): the list of filenames.
        points (dict): dictionary, {'lon':[...], 'lat':[...]}.

    Examples:
    >>> directory = "NWFD_SCMOC/TMP/2M_ABOVE_GROUND"
    >>> fhours = np.arange(3, 75, 3)
    >>> filenames = ["19083008."+str(fhour).zfill(3) for fhour in fhours]
    >>> points = {'lon':[116.3833, 110.0], 'lat':[39.9, 32]}
    >>> data = get_model_points(dataDir, filenames, points)
    >>> allExists (boolean): all files should exist, or return None.
    """

    data = get_model_grids(directory, filenames, allExists=allExists)
    
    #if(fill_null is True):
    #    temp=np.array(data['data'].values)
    #    idx_null=np.where(temp == Null_value)
    #    #temp[idx_null]=np.nan
    #    temp2=gaussian_filter(temp,5)
    #    temp[idx_null]=temp2[idx_null]
    #    data['data'].values=temp

    if(fill_null is True):
        temp=np.array(data['data'].values)
        dims=np.shape(temp)
        grid_x=np.array(data['lon'].values)
        grid_y=np.array(data['lat'].values)
        x,y=np.meshgrid(data['lon'].values, data['lat'].values)
        idx_x=np.squeeze(np.where((grid_x > points['lon'][0]-6) & (grid_x < points['lon'][0]+6)))
        idx_y=np.squeeze(np.where((grid_y > points['lat'][0]-5) & (grid_y < points['lat'][0]+5)))
        x2,y2=np.meshgrid(grid_x[idx_x[0]:idx_x[-1]], grid_y[idx_y[0]:idx_y[-1]])
        nx2=len(idx_x)
        ny2=len(idx_y)
        x=x.reshape(dims[1]*dims[2])
        y=y.reshape(dims[1]*dims[2])
        nt=dims[0]
        for it in range(0,nt):
            temp2=np.squeeze(temp[it,:,:])
            temp2=temp2.reshape(dims[1]*dims[2])
            idx_ok=np.squeeze(np.where((temp2 != Null_value) & 
                (x < points['lon'][0]+6) & (x > points['lon'][0]-6) &
                (y < points['lat'][0]+5) & (y > points['lat'][0]-5)))

            n_ok=len(idx_ok)
            data_new=griddata(np.squeeze(np.dstack(([y[idx_ok],x[idx_ok]]))), temp2[idx_ok], (y2,x2))
            temp[it,idx_y[0]:idx_y[-1],idx_x[0]:idx_x[-1]]=data_new.reshape(1,ny2-1,nx2-1)

        data['data'].values=temp
        
    if data:
        return data.interp(lon=('points', points['lon']), lat=('points', points['lat']))
    else:
        return None

def gy_cm_rain_nws(atime=24, pos=None):
    """
    Rainfall color map.

    Keyword Arguments:
        atime {int} -- [description] (default: {24})
        pos {[type]} -- specify the color position (default: {None})
    """

    # set colors
    _colors = [
        [26, 35, 126], [48, 63, 159], [63, 81, 181],
        [21, 101, 192], [30, 136, 229], [30, 136, 229]
    ]
    
    _colors = np.array(_colors)/255.0
    if pos is None:
        if atime == 24:
            _pos = [0.1, 10, 25, 50, 100, 250, 800]
        elif atime == 6:
            _pos = [0.1, 4, 13, 25, 60, 120, 800]
        else:
            _pos = [0.01, 2, 7, 13, 30, 60, 800]
    else:
        _pos = pos
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='neither')
    return cmap, norm

def gy_cm_rain_nws2(atime=24, pos=None):
    """
    Rainfall color map.

    Keyword Arguments:
        atime {int} -- [description] (default: {24})
        pos {[type]} -- specify the color position (default: {None})
    """

    # set colors
    _colors = [
        [33, 150, 243], [33, 150, 243], [30, 136, 229],
        [25, 118, 210], [21, 101, 192], [13, 71, 161]
    ]
    
    _colors = np.array(_colors)/255.0
    if pos is None:
        if atime == 24:
            _pos = [0.1, 10, 25, 50, 100, 250, 800]
        elif atime == 6:
            _pos = [0.1, 4, 13, 25, 60, 120, 800]
        else:
            _pos = [0.01, 2, 7, 13, 30, 60, 800]
    else:
        _pos = pos
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='neither')
    return cmap, norm

def read_micaps_17(fname, limit=None):
    
    """
    Read Micaps 17 type file (general scatter point)
    此类数据主要用于读站点信息数据
    :param fname: micaps file name.
    :param limit: region limit, [min_lat, min_lon, max_lat, max_lon]
    :return: data, pandas type
    :Examples:
    >>> data = read_micaps_3('L:\py_develop\nmc_met_map\nmc_met_map\resource\sta2513.dat')
    """

    # check file exist
    if not os.path.isfile(fname):
        return None

    # read contents
    try:
        with open(fname, 'r') as f:
            #txt = f.read().decode('GBK').replace('\n', ' ').split()
            txt = f.read().replace('\n', ' ').split()
    except IOError as err:
        print("Micaps 17 file error: " + str(err))
        return None

    # head information
    head_info = txt[2]

    # date and time
    nsta = int(txt[3])

    # cut data
    txt = np.array(txt[4:])
    txt.shape = [nsta, 7]

    # initial data
    columns = list(['ID', 'lat', 'lon', 'alt','temp1','temp2','Name'])
    data = pd.DataFrame(txt, columns=columns)

    # cut the region
    if limit is not None:
        data = data[(limit[0] <= data['lat']) & (data['lat'] <= limit[2]) &
                    (limit[1] <= data['lon']) & (data['lon'] <= limit[3])]

    data['nstation']=nsta

    # check records
    if len(data) == 0:
        return None
    # return
    return data

def CMISS_data_code(
        data_source=None,var_name=None
    ):

    data_code={
            'ECMWF':{
                    'TEM':'NAFP_FOR_FTM_HIGH_EC_ANEA',
                    'GPH':'NAFP_FOR_FTM_HIGH_EC_ANEA',
                    'WIU':'NAFP_FOR_FTM_HIGH_EC_ANEA',
                    'WIV':'NAFP_FOR_FTM_HIGH_EC_ANEA',
                    'GSSP':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'RHU':'NAFP_FOR_FTM_HIGH_EC_ANEA',
                    'VVP':'NAFP_FOR_FTM_HIGH_EC_ANEA',
                    'TCWV':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'SHU':'NAFP_FOR_FTM_HIGH_EC_ANEA',
                    'WIU10':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'WIV10':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'WIU100':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'WIV100':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'TPE':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'TEF2':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'MN2T3':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'MX2T6':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'DPT':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'TTSP':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'GUST10T6':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'GUST10T3':'NAFP_FOR_FTM_HIGH_EC_GLB',
                    'PRS':'NAFP_FOR_FTM_HIGH_EC_GLB'
                    },
            'GRAPES_GFS':{
                    'TEM':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'GPH':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'WIU':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'WIV':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'SSP':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'TPE':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'RHU':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'MOFU':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'TIWV':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'SHU':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'PPT':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'WIU10':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'WIV10':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'TEF2':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'RHF2':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'PLI':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'DPT':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE',
                    'PRS':'NAFP_FOR_FTM_GRAPES_CFSV2_NEHE'
                    },
            'OBS':{            
                    'PLOT_sfc':'SURF_CHN_MUL_HOR'
                    }
            }

    return data_code[data_source][var_name]

def add_cartopy_background(ax,name='RD'):
    #http://earthpy.org/cartopy_backgroung.html
    #C:\ProgramData\Anaconda3\Lib\site-packages\cartopy\data\raster\natural_earth
    bg_dir=pkg_resources.resource_filename('nmc_met_map','resources/backgrounds/')
    os.environ["CARTOPY_USER_BACKGROUNDS"] = bg_dir
    ax.background_img(name=name, resolution='high')

class TDT_img(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'https://webst01.is.autonavi.com/appmaptile?x=%s&y=%s&z=%s&style=6'% (x, y, z)
        return url
class TDT_ter(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'http://mt2.google.cn/vt/lyrs=p&scale=2&hl=zh-CN&gl=cn&x=%s&y=%s&z=%s'% (x, y, z)
        return url
class TDT(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        url = 'http://wprd01.is.autonavi.com/appmaptile?x=%s&y=%s&z=%s&lang=zh_cn&size=1&scl=1&style=7'% (x, y, z)
        return url

def cal_background_zoom_ratio(zoom_ratio):
    x=zoom_ratio/0.0625
    zm = 0
    while (x >= 1):
        x = x / 2
        zm=zm+1
    return 14-zm

def get_part_clev_and_cmap(cmap=None,clev_range=[0,4],color_all=None,clev_slt=None):
    if color_all is not None:
        cmap=mpl.colors.LinearSegmentedColormap.from_list(" ", color_all)    
    color_slt=np.array(cmap((clev_slt-clev_range[0])/(clev_range[-1]-clev_range[0]))).reshape(1,4)
    return color_slt

def linearized_ncl_cmap(name):
    cmap1=cm_collected.ncl_cmaps(name)
    COLORS = []
    norm=np.linspace(0,1,cmap1.N-1)
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(cmap1.colors[i])))
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name, COLORS)
    return cmap

def sta_to_point_interpolation(points=None,sta=None,var_name=None):

    Ex1 = np.squeeze(sta[var_name].values)
    coords = np.zeros((sta['lon'].size,2))
    coords[...,0] = sta['lat'].values
    coords[...,1] = sta['lon'].values
    interpolator_sta = LinearNDInterpolator(coords,Ex1,rescale=True)
    coords2=np.zeros((np.size(points['lon']),2))
    coords2[:,0]=points['lat']
    coords2[:,1]=points['lon']
    point_interpolated=interpolator_sta(coords2)


    return point_interpolated

def find_nearest_sta(points=None,sta=None,var_name=None):

    Ex1 = np.squeeze(sta[var_name].values)
    coords = np.zeros((sta['lon'].size,2))
    coords[...,0] = sta['lat'].values
    coords[...,1] = sta['lon'].values
    interpolator_sta = LinearNDInterpolator(coords,Ex1,rescale=True)
    coords2=np.zeros((np.size(points['lon']),2))
    coords2[:,0]=points['lat']
    coords2[:,1]=points['lon']
    point_interpolated=interpolator_sta(coords2)


    return point_interpolated   


def cm_heavy_rain_nws(atime=24, pos=None):
    """
    Rainfall color map.

    Keyword Arguments:
        atime {int} -- [description] (default: {24})
        pos {[type]} -- specify the color position (default: {None})
    """

    # set colors
    _colors = [
        [135, 206, 250],
        [0, 0, 255], [255, 0, 255], [127, 0, 0]
    ]
    _colors = np.array(_colors)/255.0
    if pos is None:
        if atime == 24:
            _pos = [10, 25, 50, 100, 250]
        elif atime == 6:
            _pos = [13, 25, 60, 120, 800]
        else:
            _pos = [7, 13, 30, 60, 800]
    else:
        _pos = pos
    cmap, norm = mpl.colors.from_levels_and_colors(_pos, _colors, extend='neither')
    return cmap, norm


    #coding=utf-8
###################################################################################################################################
#####This module enables you to maskout the unneccessary data outside the interest region on a matplotlib-plotted output instance
####################in an effecient way,You can use this script for free     ########################################################
#####################################################################################################################################
#####USAGE: INPUT  include           'originfig':the matplotlib instance##
#                                    'ax': the Axes instance
#                                    'shapefile': the shape file used for generating a basemap A
#                                    'region':the name of a region of on the basemap A,outside the region the data is to be maskout
#           OUTPUT    is             'clip' :the the masked-out or clipped matplotlib instance.
import shapefile
from matplotlib.path import Path
from matplotlib.patches import PathPatch
def gy_shp2clip_China(originfig,ax,shpfile,lbs_originfig=None):
    
    sf = shapefile.Reader(shpfile,encoding='utf-8')
    vertices = []
    codes = []
    for shape_rec in sf.shapeRecords():
        if shape_rec.record[2] == 'China':  ####这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。
            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i+1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i+1] - prt[i] -2)
                codes += [Path.CLOSEPOLY]
    #codes = [Path.MOVETO] + [Path.LINETO]*2 + [Path.CLOSEPOLY]
    #vertices = [(120, 50), (120, 20), (70, 20), (70, 50)]
    clip = Path(vertices, codes)
    clip = PathPatch(clip, transform=ax.transData, facecolor='orange', lw=2,alpha=0.5)
    #clip=ax.add_patch(clip)
    for contour in originfig.collections:
        contour.set_clip_path(clip)

    if(lbs_originfig is not None):
        clip_map_shapely = ShapelyPolygon(vertices)
        for text_object in lbs_originfig:
            if not clip_map_shapely.contains(ShapelyPoint(text_object.get_position())):
                text_object.set_visible(False)

    return clip

def gy_shp2clip(originfig,ax,shpfile,lbs_originfig=None):
    
    sf = shapefile.Reader(shpfile,encoding='utf-8')
    vertices = []
    codes = []
    for shape_rec in sf.shapeRecords():
        pts = shape_rec.shape.points
        prt = list(shape_rec.shape.parts) + [len(pts)]
        for i in range(len(prt) - 1):
            for j in range(prt[i], prt[i+1]):
                vertices.append((pts[j][0], pts[j][1]))
            codes += [Path.MOVETO]
            codes += [Path.LINETO] * (prt[i+1] - prt[i] -2)
            codes += [Path.CLOSEPOLY]
    #codes = [Path.MOVETO] + [Path.LINETO]*2 + [Path.CLOSEPOLY]
    #vertices = [(120, 50), (120, 20), (70, 20), (70, 50)]
    clip = Path(vertices, codes)
    clip = PathPatch(clip, transform=ax.transData, facecolor='orange', lw=2,alpha=0.5)
    #clip=ax.add_patch(clip)
    # for contour in originfig.collections:
    #     contour.set_clip_path(clip)
    for contour in originfig.collections:
        contour.set_clip_path(clip)
        
    if(lbs_originfig is not None):
        clip_map_shapely = ShapelyPolygon(vertices)
        for text_object in lbs_originfig:
            if not clip_map_shapely.contains(ShapelyPoint(text_object.get_position())):
                text_object.set_visible(False)

    return clip

def gy_China_maskout(originfig,ax,lbs_originfig=None):
    shpfile = pkg_resources.resource_filename(
        'nmc_met_graphics', "resources/maps/country1.shp")
    clip=gy_shp2clip_China(originfig,ax,shpfile,lbs_originfig=lbs_originfig)
    return clip
    
def gy_continent_maskout(originfig,ax,lbs_originfig=None):
    shpfile = pkg_resources.resource_filename(
        'nmc_met_graphics', "resources/maps/country1.shp")
    clip=gy_shp2clip(originfig,ax,shpfile,lbs_originfig=lbs_originfig)
    return clip

def extrema(mat,mode='wrap',window=50):
        mn = minimum_filter(mat, size=window, mode=mode)
        mx = maximum_filter(mat, size=window, mode=mode)
        return np.nonzero(mat == mn), np.nonzero(mat == mx)

def get_map_regions():
    """
    Get the map region lon/lat limits.
    Returns:
        Dictionary: the region limits, 'name': [lonmin, lonmax, latmin, latmax]
    """
    map_region = {
        '中国': [70, 140, 8, 60], '中国陆地': [73, 136, 15, 56],
        '中国及周边': [50, 160, 0, 70], '华北': [103, 129, 30, 50],
        '东北': [103, 140, 32, 58], '华东': [107, 130, 20, 41],
        '华中': [100, 123, 22, 42], '华南': [100, 126, 12, 30],
        '西南': [90, 113, 18, 38], '西北': [89, 115, 27, 47],
        '新疆': [70, 101, 30, 52], '青藏': [68, 105, 18, 46]}
    return map_region

def mask_terrian(prs_lev,psfc,xr_input):
    psfc_new=psfc.interp(lon =xr_input['lon'].values, 
                        lat = xr_input['lat'].values, 
                        kwargs={"fill_value": "extrapolate"})
    idx_terrian=np.expand_dims((psfc_new['data'].values-prs_lev)<0,axis=0)
    if(idx_terrian.any()):
        xr_input['data'].values[idx_terrian]=np.nan
    return xr_input

def cut_xrdata(map_extent,xr_input,delt_x=0,delt_y=0):
            
    mask =  ((xr_input['lon'] > map_extent[0]-delt_x) & 
            (xr_input['lon'] < map_extent[1]+delt_x) & 
            (xr_input['lat'] > map_extent[2]-delt_y) & 
            (xr_input['lat'] < map_extent[3]+delt_y))
    xr_output=xr_input.where(mask,drop=True)
    return xr_output

def get_map_extent(cntr_pnt,zoom_ratio,map_ratio):
    map_extent=[0,0,0,0]
    map_extent[0]=cntr_pnt[0]-zoom_ratio*1*map_ratio
    map_extent[1]=cntr_pnt[0]+zoom_ratio*1*map_ratio
    map_extent[2]=cntr_pnt[1]-zoom_ratio*1
    map_extent[3]=cntr_pnt[1]+zoom_ratio*1
    return map_extent

def get_var_anm(input_var=None,Var_name='gh500'):
    clm_file_name={'gh500':'mean_hourly_from_1979_to_2020_gh500.nc',
                    't850':'mean_hourly_from_1979_to_2020_t850.nc',}
    clm_unit_change_ratio={'gh500':10*9.80665,
                    't850':1,}
    Var_name_ERA={'gh500':'z',
            't850':'t'}

    clm_file = pkg_resources.resource_filename(
        'nmc_met_map', "/resources/climate_data/"+clm_file_name[Var_name])
    clm_data=xr.open_dataset(clm_file).load()
    input_var_time=pd.to_datetime(input_var.time.values[0]-np.timedelta64(8,'h'))
    clm_data_slt=clm_data.sel(time=((clm_data.time.dt.month==input_var_time.month) &
            (clm_data.time.dt.day==input_var_time.day) & 
            (clm_data.time.dt.hour==input_var_time.hour)))
    clm_data_slt_regrided=clm_data_slt.interp(longitude=input_var['lon'].values, latitude=input_var['lat'].values)
    clm_data.close()
    var_anm=input_var.copy()
    var_anm['data'].values=var_anm['data'].values-clm_data_slt_regrided[Var_name_ERA[Var_name]].values[:,np.newaxis,:,:]/clm_unit_change_ratio[Var_name]
    return var_anm

def get_var_extr(input_var=None,Var_name='gh500'):
    clm_file_name={'gh500':'STD_hourly_from_1979_to_2020_gh500.nc',
                    't850':'STD_hourly_from_1979_to_2020_t850.nc',}
    clm_unit_change_ratio={'gh500':10*9.80665,
                    't850':1,}

    clm_file = pkg_resources.resource_filename(
        'nmc_met_map', "/resources/climate_data/"+clm_file_name[Var_name])
    clm_data=xr.open_dataset(clm_file).load()
    input_var_time=pd.to_datetime(input_var.time.values[0]-np.timedelta64(8,'h'))
    clm_data_slt=clm_data.sel(time=((clm_data.time.dt.month==input_var_time.month) &
            (clm_data.time.dt.day==input_var_time.dayofyear) & 
            (clm_data.time.dt.hour==input_var_time.hour)))
    clm_data_slt_regrided=clm_data_slt.interp(longitude=input_var['lon'].values, latitude=input_var['lat'].values)
    clm_data.close()
    var_extr=input_var.copy()
    var_extr['data'].values=var_extr['data'].values/(clm_data_slt_regrided[Var_name].values[:,np.newaxis,:,:]/clm_unit_change_ratio[Var_name])
    return var_extr

def map_extent_to_cntr_pnt_zoom_ratio_map_ratio(map_extent):
    #input: map_extent=[left,right,bottom,top]
    #example:cntr_pnt,zoom_ratio,map_ratio=map_extent_to_cntr_pnt_zoom_ratio_map_ratio([90,120,10,40])
    cntr_pnt=[(map_extent[0]+map_extent[1])/2,(map_extent[2]+map_extent[3])/2]
    zoom_ratio=map_extent[3]-cntr_pnt[1]
    map_ratio=(map_extent[1]-cntr_pnt[0])/zoom_ratio
    return cntr_pnt,zoom_ratio,map_ratio

def fitbox(fig, text, x0, x1, y0, y1, **kwargs):
    """Fit text into a NDC box."""
    figbox = fig.get_window_extent().transformed(
        fig.dpi_scale_trans.inverted())
    # need some slop for decimal comparison below
    px0 = x0 * fig.dpi * figbox.width - 0.15
    px1 = x1 * fig.dpi * figbox.width + 0.15
    py0 = y0 * fig.dpi * figbox.height - 0.15
    py1 = y1 * fig.dpi * figbox.height + 0.15
    # print("px0: %s px1: %s py0: %s py1: %s" % (px0, px1, py0, py1))
    xanchor = x0
    if kwargs.get('ha', '') == 'center':
        xanchor = x0 + (x1 - x0) / 2.
    yanchor = y0
    if kwargs.get('va', '') == 'center':
        yanchor = y0 + (y1 - y0) / 2.
    txt = fig.text(
        xanchor, yanchor, text,
        fontsize=50, ha=kwargs.get('ha', 'left'),
        va=kwargs.get('va', 'bottom'),
        color=kwargs.get('color', 'k')
    )
    for fs in range(50, 1, -2):
        txt.set_fontsize(fs)
        tbox = txt.get_window_extent(fig.canvas.get_renderer())
        # print("fs: %s tbox: %s" % (fs, str(tbox)))
        if (tbox.x0 >= px0 and tbox.x1 < px1 and tbox.y0 >= py0 and
                tbox.y1 <= py1):
            break
    return txt