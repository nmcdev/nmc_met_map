# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

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

def draw_gh_uv_mslp(gh=None, uv=None, mslp=None,
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
    uv['lev']+'hPa 风场, 海平面气压场', 
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
    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(960, 1065, 5)
        cmap = guide_cmaps(26)
        plots['mslp'] = ax.contourf(
            x, y, np.squeeze(mslp['data']), clevs_mslp,
            cmap=cmap, alpha=0.8, zorder=10, transform=datacrs)

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['udata']) * 2.5
        v = np.squeeze(uv['vdata']) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=20)

    # draw -hPa geopotential height
    if gh is not None:
        x, y = np.meshgrid(gh['lon'], gh['lat'])
        clevs_gh = np.append(np.append(np.arange(0, 480, 4),np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8))
        plots['gh'] = ax.contour(
            x, y, np.squeeze(gh['data']), clevs_gh, colors='purple',
            linewidths=2, transform=datacrs, zorder=30)
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
    cax=plt.axes([0.11,0.06,.86,.02])
    cb = plt.colorbar(plots['mslp'], cax=cax, orientation='horizontal',
                      ticks=clevs_mslp[:-1],
                      extend='max',extendrect=False)
    cb.ax.tick_params(labelsize='x-large')                      
    cb.set_label('Mean sea level pressure (hPa)',size=20)

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
        plt.savefig(output_dir+'最高温度_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()

def draw_gh_uv_wsp(gh=None, uv=None, wsp=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None,Global=False):
    """
    Draw -hPa geopotential height contours, -hPa wind barbs
    and mean sea level pressure filled contours.
    :param gh: -hPa gh, dictionary:
                  necessary, {'lon': 1D array, 'lat': 1D array,
                              'data': 2D array}
                  optional, {'clevs': 1D array}
    :param uv: -hPa u-component and v-component wind, dictionary:
                  necessary, {'lon': 1D array, 'lat': 1D array,
                              'udata': 2D array, 'vdata': 2D array}
    :param wsp: wsp, dictionary:
                 necessary, {'lon': 1D array, 'lat': 1D array,
                             'data': 2D array}
                 optional, {'clevs': 1D array}
    :param map_extent: [lonmin, lonmax, latmin, latmax],
                       longitude and latitude range.
    :param add_china: add china map or not.
    :param regrid_shape: control the wind barbs density.
    :return: plots dictionary.

    :Examples:
    """

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
    uv['lev']+'hPa 风场, 风速', 
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
    if wsp is not None:
        x, y = np.meshgrid(wsp['lon'], wsp['lat'])
        z=np.squeeze(wsp['data'])

        clevs_wsp = [12, 15, 18,21, 24, 27,30]
        colors = ["#FFF59D", "#FFEE58", "#FFCA28", "#FFC107","#FF9800", "#FB8C00",'#E64A19','#BF360C'] # #RRGGBBAA
        cmap=ListedColormap(colors, 'wsp')
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        norm = BoundaryNorm(clevs_wsp, ncolors=cmap.N, clip=False)

        plots['wsp'] = ax.pcolormesh(
            x, y, z, norm=norm,
            cmap=cmap, zorder=100,transform=datacrs,alpha=0.5)

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['udata']) * 2.5
        v = np.squeeze(uv['vdata']) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=20)

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
    if(wsp != None):
        cax=plt.axes([0.11,0.06,.86,.02])
        cb = plt.colorbar(plots['wsp'], cax=cax, orientation='horizontal',
                      ticks=clevs_wsp[:],
                      extend='max',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('(m/s)',size=20)

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
        plt.savefig(output_dir+'高度场_风_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()

def draw_gh_uv_r6(gh=None, uv=None, r6=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None,Global=False):
    """
    Draw -hPa geopotential height contours, -hPa wind barbs
    and mean sea level pressure filled contours.
    :param gh: -hPa gh, dictionary:
                  necessary, {'lon': 1D array, 'lat': 1D array,
                              'data': 2D array}
                  optional, {'clevs': 1D array}
    :param uv: -hPa u-component and v-component wind, dictionary:
                  necessary, {'lon': 1D array, 'lat': 1D array,
                              'udata': 2D array, 'vdata': 2D array}
    :param r6: r6, dictionary:
                 necessary, {'lon': 1D array, 'lat': 1D array,
                             'data': 2D array}
                 optional, {'clevs': 1D array}
    :param map_extent: [lonmin, lonmax, latmin, latmax],
                       longitude and latitude range.
    :param add_china: add china map or not.
    :param regrid_shape: control the wind barbs density.
    :return: plots dictionary.

    :Examples:
    """

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
    uv['lev']+'hPa 风场, 6小时降水', 
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
    if r6 is not None:
        x, y = np.meshgrid(r6['lon'], r6['lat'])
        clevs_r6 = [0.1, 4, 13, 25, 60, 120]
        plots['r6'] = ax.contourf(
            x, y, np.squeeze(r6['data']), clevs_r6,
            colors=["#88F492", "#00A929", "#2AB8FF", "#1202FC", "#FF04F4", "#850C3E"],
            alpha=0.8, zorder=10, transform=datacrs,extend='max',extendrect=False)

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['udata']) * 2.5
        v = np.squeeze(uv['vdata']) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=20)

    # draw -hPa geopotential height
    if gh is not None:
        x, y = np.meshgrid(gh['lon'], gh['lat'])
        clevs_gh = np.append(np.append(np.arange(0, 480, 4),np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8))
        plots['gh'] = ax.contour(
            x, y, np.squeeze(gh['data']), clevs_gh, colors='black',
            linewidths=2, transform=datacrs, zorder=30)
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
    if(r6 != None):
        cax=plt.axes([0.11,0.06,.86,.02])
        cb = plt.colorbar(plots['r6'], cax=cax, orientation='horizontal',
                      ticks=clevs_r6[:],
                      extend='max',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('6h precipitation (mm)',size=20)

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
        plt.savefig(output_dir+'高度场_风场_降水_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()      


def draw_PV_Div_uv(pv=None, uv=None, div=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=False,south_China_sea=True,
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
    
    plt.title('['+pv['model']+'] '+
    pv['lev']+'hPa 位涡扰动, 风场, 散度', 
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
    if div is not None:

        x, y = np.meshgrid(div['lon'], div['lat'])
        z=np.squeeze(div['data'])
        clevs_div = np.arange(-15, 16, 1)
        plots['div'] = ax.contourf(
            x, y, z*1e5,clevs_div,cmap=plt.cm.PuOr,
            transform=datacrs,alpha=0.5,extend='both')

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['udata']) * 2.5
        v = np.squeeze(uv['vdata']) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=20)

    # draw -hPa geopotential height
    if pv is not None:
        x, y = np.meshgrid(pv['lon'], pv['lat'])
        clevs_pv = np.arange(0, 25, 1)
        plots['pv'] = ax.contour(
            x, y, np.squeeze(pv['data'])*1e6, clevs_pv, colors='black',
            linewidths=2, transform=datacrs, zorder=30)
        plt.clabel(plots['pv'], inline=1, fontsize=20, fmt='%.0f',colors='black')

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
    str(pv['init_time'])).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=pv['fhour'])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(pv['fhour'])+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(div != None):
        cax=plt.axes([0.11,0.06,.86,.02])
        cb = plt.colorbar(plots['div'], cax=cax, orientation='horizontal',
                      ticks=clevs_div[:],
                      extend='both',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Divergence ($10^5$ s$^{-1}$)',size=20)

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
        plt.savefig(output_dir+'位涡_风场_散度_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(pv['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()              