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
import nmc_met_graphics.cmap.cm as dk_ctables2
from scipy.ndimage import gaussian_filter

def draw_gh_uv_div(gh=None, uv=None, div=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=30,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    # draw figure
    plt.figure(figsize=(16,9))

    # set data projection
    plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
        central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    
    plt.title('['+gh.attrs['model']+'] '+
    str(int(gh['level'].values[0]))+'hPa 位势高度场, '+
    str(int(uv['level'].values[0]))+'hPa 风场和水平散度', 
        loc='left', fontsize=25)
        
    datacrs = ccrs.PlateCarree()

    #adapt to the map ratio
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)
    #adapt to the map ratio

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=5,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=5)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=5)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=5,alpha=0.5)

    # define return plots
    plots = {}
    # draw mean sea level pressure
    if div is not None:
        x, y = np.meshgrid(div['lon'], div['lat'])
        
        z=np.squeeze(div['data'].values*1e5)

        cmap=dk_ctables2.ncl_cmaps('GMT_haxby')
        plots['div'] = ax.pcolormesh(
            x, y,z,cmap=cmap,vmax=10,vmin=-10,
            zorder=1, transform=datacrs,alpha=0.5)

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['u']) * 2.5
        v = np.squeeze(uv['v']) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u.values, v.values, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=2)

    # draw -hPa geopotential height
    if gh is not None:
        x, y = np.meshgrid(gh['lon'], gh['lat'])
        clevs_gh = np.append(np.append(np.arange(0, 480, 4),np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8))
        plots['gh'] = ax.contour(
            x, y, np.squeeze(gh['data']), clevs_gh, colors='black',
            linewidths=2, transform=datacrs, zorder=3)
        plt.clabel(plots['gh'], inline=1, fontsize=20, fmt='%.0f',colors='black')

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=4)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    utl.add_cartopy_background(ax,name='RD')
    
    #forecast information
    l, b, w, h = ax.get_position().bounds

    #forecast information
    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initTime = pd.to_datetime(
    str(gh.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=gh.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(gh.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(div != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['div'], cax=cax, orientation='horizontal',
                      extend='max',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Horizontal Divergence (10$^{-5}$ s$^{-1}$)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=110,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'高度场_风场_垂直气压速度_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200,bbox_inches='tight')
        plt.close()
    
    if(output_dir == None):
        plt.show()      


def draw_gh_uv_VVEL(gh=None, uv=None, VVEL=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    # draw figure
    plt.figure(figsize=(16,9))

    # set data projection
    plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
        central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    
    plt.title('['+gh.attrs['model']+'] '+
    str(int(gh['level'].values[0]))+'hPa 位势高度场, '+
    str(int(uv['level'].values[0]))+'hPa 风场和垂直气压速度', 
        loc='left', fontsize=30)
        
    datacrs = ccrs.PlateCarree()

    #adapt to the map ratio
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)
    #adapt to the map ratio

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=5,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=5)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=5)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=5,alpha=0.5)

    # define return plots
    plots = {}
    # draw mean sea level pressure
    if VVEL is not None:
        x, y = np.meshgrid(VVEL['lon'], VVEL['lat'])
        clevs_VVEL = [0.1, 4, 13, 25, 60, 120]

        clevs_VVEL=[
            -30, -20, -10, -5, -2.5, -1, -0.5,
            0.5, 1, 2.5, 5, 10, 20, 30]

        z=np.squeeze(VVEL['data']/10.)

        cmap,norm=dk_ctables.cm_vertical_velocity_nws(pos=clevs_VVEL)
        #cmap.set_under(color=[0,0,0,0],alpha=0.0)

        plots['VVEL'] = ax.pcolormesh(
            x, y,z, norm=norm,
            cmap=cmap,zorder=1, transform=datacrs,alpha=0.5)

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['u']) * 2.5
        v = np.squeeze(uv['v']) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u.values, v.values, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=2)

    # draw -hPa geopotential height
    if gh is not None:
        x, y = np.meshgrid(gh['lon'], gh['lat'])
        clevs_gh = np.append(np.append(np.arange(0, 480, 4),np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8))
        plots['gh'] = ax.contour(
            x, y, np.squeeze(gh['data']), clevs_gh, colors='black',
            linewidths=2, transform=datacrs, zorder=3)
        plt.clabel(plots['gh'], inline=1, fontsize=20, fmt='%.0f',colors='black')

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=4)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    utl.add_cartopy_background(ax,name='RD')
    
    #forecast information
    l, b, w, h = ax.get_position().bounds

    #forecast information
    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initTime = pd.to_datetime(
    str(gh.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=gh.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(gh.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(VVEL != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['VVEL'], cax=cax, orientation='horizontal',
                      ticks=clevs_VVEL[:],
                      extend='max',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Vertical Velocity (0.1Pa/s)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=110,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'高度场_风场_垂直气压速度_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200,bbox_inches='tight')
        plt.close()
    
    if(output_dir == None):
        plt.show()      

def draw_fg_uv_tmp(fg=None, tmp=None, uv=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    # draw figure
    plt.figure(figsize=(16,9))

    # set data projection
    plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
        central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    
    plt.title('['+fg.attrs['model']+'] '+
        str(int(fg['level'].values[0]))+'hPa 锋生函数, '+
        '风场和温度', 
        loc='left', fontsize=30)
        
    datacrs = ccrs.PlateCarree()

    #adapt to the map ratio
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)
    #adapt to the map ratio

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=5,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=5)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=5)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=5,alpha=0.5)

    # define return plots
    plots = {}
    # draw mean sea level pressure
    if fg is not None:
        x, y = np.meshgrid(fg['lon'], fg['lat'])
        z=np.squeeze(fg['data']*10**9)
        cmap=dk_ctables2.ncl_cmaps('hotcolr_19lev')

        plots['fg'] = ax.pcolormesh(
            x,y,z, vmin=-4,vmax=4,
            cmap=cmap,zorder=1, transform=datacrs,alpha=0.5)

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['u']) * 2.5
        v = np.squeeze(uv['v']) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u.values, v.values, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=2)

    # draw -hPa geopotential height
    if tmp is not None:
        x, y = np.meshgrid(tmp['lon'], tmp['lat'])
        clevs_tmp = np.arange(-60,60,4)
        plots['tmp'] = ax.contour(
            x, y, np.squeeze(tmp['data']), clevs_tmp, colors='red',
            linewidths=2, transform=datacrs, zorder=3)
        plt.clabel(plots['tmp'], inline=1, fontsize=20, fmt='%.0f',colors='red')

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=4)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    utl.add_cartopy_background(ax,name='RD')
    
    #forecast information
    l, b, w, h = ax.get_position().bounds

    #forecast information
    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initTime = pd.to_datetime(
    str(fg.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=fg.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(fg.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(fg != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['fg'], cax=cax, orientation='horizontal',
                      extend='both',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Front Genesis Function (1${0^{-8}}$'+fg.attrs['units']+')',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=110,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'锋生函数_风场_温度速度_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(fg.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200,bbox_inches='tight')
        plt.close()
    
    if(output_dir == None):
        plt.show()      