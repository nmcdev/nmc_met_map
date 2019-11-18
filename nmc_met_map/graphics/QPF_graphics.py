# _*_ coding: utf-8 _*_

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from nmc_met_graphics.plot.china_map import add_china_map_2cartopy
from nmc_met_graphics.cmap.cm import guide_cmaps
from nmc_met_graphics.plot.util import add_model_title
import nmc_met_map.lib.utility as utl
from datetime import datetime, timedelta
import pandas as pd
import locale
import sys
from matplotlib.colors import BoundaryNorm,ListedColormap
import nmc_met_graphics.cmap.ctables as dk_ctables

def draw_gh_rain(gh=None, rain=None,atime=24,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None,Global=False):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    # draw figure
    plt.figure(figsize=(16,9))

    # set data projection
    if(Global == True):
        plotcrs = ccrs.Robinson(central_longitude=115.)
    else:
        plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
            central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    
    plt.title('['+gh['model']+'] '+
    gh['lev']+'hPa 位势高度场, '+
    str(atime)+'小时降水', 
        loc='left', fontsize=30)
        
    datacrs = ccrs.PlateCarree()

    #adapt to the map ratio
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)
    #adapt to the map ratio

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=105,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=105)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=105)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=105,alpha=0.5)

    # define return plots
    plots = {}
    # draw mean sea level pressure
    if rain is not None:
        x, y = np.meshgrid(rain['lon'], rain['lat'])
        z=np.squeeze(rain['data'])
        cmap,norm=dk_ctables.cm_qpf_nws(atime=atime)
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['rain'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=100,transform=datacrs,alpha=0.5)

    # draw -hPa geopotential height
    if gh is not None:
        x, y = np.meshgrid(gh['lon'], gh['lat'])
        clevs_gh = np.append(np.append(np.arange(0, 480, 4),np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8))
        plots['gh'] = ax.contour(
            x, y, np.squeeze(gh['data']), clevs_gh, colors='black',
            linewidths=2, transform=datacrs, zorder=110)
        plt.clabel(plots['gh'], inline=1, fontsize=20, fmt='%.0f',colors='black')

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=40)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    #http://earthpy.org/cartopy_backgroung.html
    #C:\ProgramData\Anaconda3\Lib\site-packages\cartopy\data\raster\natural_earth
    ax.background_img(name='RD', resolution='high')

    #forecast information
    bax=plt.axes([0.01,0.835,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initial_time = pd.to_datetime(
    str(gh['init_time'])).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=gh['fhour'])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(gh['fhour'])+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(rain != None):
        cax=plt.axes([0.11,0.06,.86,.02])
        cb = plt.colorbar(plots['rain'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label(str(atime)+'h precipitation (mm)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[0.85,0.13,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=110,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[-0.01,0.835,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'高度场_降水_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()

def draw_mslp_rain_snow(
        rain=None, snow=None,sleet=None,mslp=None,atime=None,
        map_extent=(50, 150, 0, 65),
        regrid_shape=20,
        add_china=True,city=True,south_China_sea=True,
        output_dir=None,Global=False):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    # draw figure
    plt.figure(figsize=(16,9))

    # set data projection
    if(Global == True):
        plotcrs = ccrs.Robinson(central_longitude=115.)
    else:
        plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
            central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    
    plt.title('['+mslp['model']+'] '+
    '海平面气压, '+
    str(atime)+'小时降水', 
        loc='left', fontsize=30)
        
    datacrs = ccrs.PlateCarree()

    #adapt to the map ratio
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)
    #adapt to the map ratio

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=105,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=105)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=105)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=105,alpha=0.5)

    # define return plots
    plots = {}
    # draw mean sea level pressure
    if rain is not None:
        x, y = np.meshgrid(rain['lon'], rain['lat'])
        z=np.squeeze(rain['data'])
        cmap,norm=dk_ctables.cm_rain_nws(atime=atime)
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['rain'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=100,transform=datacrs,alpha=0.5)
    

    if snow is not None:
        x, y = np.meshgrid(snow['lon'], snow['lat'])
        z=np.squeeze(snow['data'])
        cmap,norm=dk_ctables.cm_snow_nws(atime=atime)
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['snow'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=110,transform=datacrs,alpha=0.5)

    
    if sleet is not None:
        x, y = np.meshgrid(sleet['lon'], sleet['lat'])
        z=np.squeeze(sleet['data'])
        cmap,norm=dk_ctables.cm_sleet_nws(atime=atime)
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['sleet'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=110,transform=datacrs,alpha=0.5)
    

    # draw -hPa geopotential height
    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(900, 1100,2.5)
        plots['mslp'] = ax.contour(
            x, y, np.squeeze(mslp['data']), clevs_mslp, colors='black',
            linewidths=2, transform=datacrs, zorder=110)
        plt.clabel(plots['mslp'], inline=1, fontsize=20, fmt='%.0f',colors='black')

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=40)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    #http://earthpy.org/cartopy_backgroung.html
    #C:\ProgramData\Anaconda3\Lib\site-packages\cartopy\data\raster\natural_earth
    ax.background_img(name='RD', resolution='high')

    #forecast information
    bax=plt.axes([0.01,0.835,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initial_time = pd.to_datetime(
    str(mslp['init_time'])).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=mslp['fhour'])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(mslp['fhour'])+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(sleet != None):
        cax=plt.axes([0.01,0.06,.30,.02])
        cb = plt.colorbar(plots['sleet'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('雨夹雪 (mm)',size=20)

    if(snow != None):
        cax=plt.axes([0.33,0.06,.30,.02])
        cb = plt.colorbar(plots['snow'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('雪 (mm)',size=20)

    if(rain != None):
        cax=plt.axes([0.66,0.06,.30,.02])
        cb = plt.colorbar(plots['rain'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('雪 (mm)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[0.85,0.13,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=110,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[-0.01,0.835,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'海平面气压_降水_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(mslp['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()