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
import matplotlib.patheffects as path_effects

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
    
    plt.title('['+gh.attrs['model']+'] '+
    str(int(gh['level'].values[0]))+'hPa 位势高度场, '+
    str(int(uv['level'].values[0]))+'hPa 风场, 海平面气压场', 
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
    if mslp is not None:   
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(960, 1065, 5)
        cmap = guide_cmaps(26)
        plots['mslp'] = ax.contourf(
            x, y, np.squeeze(mslp['data']), clevs_mslp,
            cmap=cmap, alpha=0.8, zorder=1, transform=datacrs)
        #+画高低压中心
        res = mslp['lon'].values[1] - mslp['lon'].values[0]
        nwindow = int(9.5 / res)
        mslp_hl = np.ma.masked_invalid(mslp['data'].values).squeeze()
        local_min, local_max = utl.extrema(mslp_hl, mode='wrap', window=nwindow)
        #Get location of extrema on grid
        xmin, xmax, ymin, ymax = map_extent2
        lons2d, lats2d = x,y
        transformed = datacrs.transform_points(datacrs, lons2d, lats2d)
        x = transformed[..., 0]
        y = transformed[..., 1]
        xlows = x[local_min]; xhighs = x[local_max]
        ylows = y[local_min]; yhighs = y[local_max]
        lowvals = mslp_hl[local_min]; highvals = mslp_hl[local_max]
        yoffset = 0.022*(ymax-ymin)
        dmin = yoffset
        #Plot low pressures
        xyplotted = []
        for x,y,p in zip(xlows, ylows, lowvals):
            if x < xmax-yoffset and x > xmin+yoffset and y < ymax-yoffset and y > ymin+yoffset:
                dist = [np.sqrt((x-x0)**2+(y-y0)**2) for x0,y0 in xyplotted]
                if not dist or min(dist) > dmin: #,fontweight='bold'
                    a = ax.text(x,y,'L',fontsize=28,
                            ha='center',va='center',color='r',fontweight='normal', transform=datacrs)
                    b = ax.text(x,y-yoffset,repr(int(p)),fontsize=14,
                            ha='center',va='top',color='r',fontweight='normal', transform=datacrs)
                    a.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'),
                        path_effects.SimpleLineShadow(),path_effects.Normal()])
                    b.set_path_effects([path_effects.Stroke(linewidth=1.0, foreground='black'),
                        path_effects.SimpleLineShadow(),path_effects.Normal()])
                    xyplotted.append((x,y))
                    
        #Plot high pressures
        xyplotted = []
        for x,y,p in zip(xhighs, yhighs, highvals):
            if x < xmax-yoffset and x > xmin+yoffset and y < ymax-yoffset and y > ymin+yoffset:
                dist = [np.sqrt((x-x0)**2+(y-y0)**2) for x0,y0 in xyplotted]
                if not dist or min(dist) > dmin:
                    a = ax.text(x,y,'H',fontsize=28,
                            ha='center',va='center',color='b',fontweight='normal', transform=datacrs)
                    b = ax.text(x,y-yoffset,repr(int(p)),fontsize=14,
                            ha='center',va='top',color='b',fontweight='normal', transform=datacrs)
                    a.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'),
                        path_effects.SimpleLineShadow(),path_effects.Normal()])
                    b.set_path_effects([path_effects.Stroke(linewidth=1.0, foreground='black'),
                        path_effects.SimpleLineShadow(),path_effects.Normal()])
                    xyplotted.append((x,y))
        #-画高低压中心


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
        linewidths_gh = np.zeros(clevs_gh.shape)+2
        idx_588=np.where(clevs_gh == 588)
        linewidths_gh[idx_588[0]]=4
        plots['gh'] = ax.contour(
            x, y, np.squeeze(gh['data']), clevs_gh, colors='purple',
            linewidths=linewidths_gh, transform=datacrs, zorder=3)
        ax.clabel(plots['gh'], inline=1, fontsize=20, fmt='%.0f',colors='black')

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=4)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    utl.add_cartopy_background(ax,name='RD')
    #forecast information
    l, b, w, h = ax.get_position().bounds

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
    cax=plt.axes([l,b-0.04,w,.02])
    cb = plt.colorbar(plots['mslp'], cax=cax, orientation='horizontal',
                      ticks=clevs_mslp[:-1],
                      extend='max',extendrect=False)
    cb.ax.tick_params(labelsize='x-large')                      
    cb.set_label('Mean sea level pressure (hPa)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=6,size=15,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')
    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'最高温度_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200,bbox_inches='tight')
    
    if(output_dir == None):
        plt.show()

def draw_gh_uv_wsp(gh=None, uv=None, wsp=None,
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
    
    plt.title('['+gh.attrs['model']+'] '+
    str(int(gh['level'].values[0]))+'hPa 位势高度场, '+
    str(int(uv['level'].values[0]))+'hPa 风场, 风速', 
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
    if wsp is not None:
        x, y = np.meshgrid(wsp['lon'], wsp['lat'])
        z=np.squeeze(wsp.values)
        clevs_wsp = [12, 15, 18,21, 24, 27,30]
        colors = ["#FFF59D", "#FFEE58", "#FFCA28", "#FFC107","#FF9800", "#FB8C00",'#E64A19','#BF360C'] # #RRGGBBAA
        cmap=ListedColormap(colors, 'wsp')
        idx_nan=np.where(z < clevs_wsp[0])
        z[idx_nan]=np.nan
        cmap.set_under(color=[1,1,1,0],alpha=0.0)
        norm = BoundaryNorm(clevs_wsp, ncolors=cmap.N, clip=False)

        plots['wsp'] = ax.pcolormesh(
            x, y, z, norm=norm,
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)

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
    if(wsp is not None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['wsp'], cax=cax, orientation='horizontal',
                      ticks=clevs_wsp[:],
                      extend='max',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Wind Speed (m/s)',size=20)

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
        plt.savefig(output_dir+'高度场_风_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200,bbox_inches='tight')
    
    if(output_dir == None):
        plt.show()

def draw_gh_anomaly_uv(gh=None, uv=None, gh_anm=None,
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
    
    plt.title('['+gh.attrs['model']+'] '+
    str(int(gh['level'].values[0]))+'hPa 位势高度场和异常, '+
    str(int(uv['level'].values[0]))+'hPa 风场', 
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
    if gh_anm is not None:
        x, y = np.meshgrid(gh_anm['lon'], gh_anm['lat'])
        z=np.squeeze(gh_anm['data'].values)
        cmap=dk_ctables2.ncl_cmaps('GHRSST_anomaly')
        plots['gh_anm'] = ax.pcolormesh(
            x, y, z, vmin=-50,vmax=50,
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.7)

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
    if(gh_anm is not None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['gh_anm'], cax=cax, orientation='horizontal',
                      ticks=np.arange(-50,51,5),
                      extend='both',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('gpm',size=20)

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
        plt.savefig(output_dir+'高度场_风_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200,bbox_inches='tight')
    
    if(output_dir == None):
        plt.show()
        

def draw_gh_uv_r6(gh=None, uv=None, r6=None,
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
    
    plt.title('['+gh.attrs['model']+'] '+
    str(int(gh['level'].values[0]))+'hPa 位势高度场, '+
    str(int(uv['level'].values[0]))+'hPa 风场, 6小时降水', 
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
    if r6 is not None:
        x, y = np.meshgrid(r6['lon'], r6['lat'])
        clevs_r6 = [0.1, 4, 13, 25, 60, 120]
        plots['r6'] = ax.contourf(
            x, y, np.squeeze(r6['data'].values), clevs_r6,
            colors=["#88F492", "#00A929", "#2AB8FF", "#1202FC", "#FF04F4", "#850C3E"],
            alpha=0.8, zorder=1, transform=datacrs,extend='max',extendrect=False)

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
    if(r6 != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['r6'], cax=cax, orientation='horizontal',
                      ticks=clevs_r6[:],
                      extend='max',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('6h precipitation (mm)',size=20)

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
        plt.savefig(output_dir+'高度场_风场_降水_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(gh.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200,bbox_inches='tight')
    
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
    
    plt.title('['+pv.attrs['model']+'] '+
    str(int(pv['level']))+'hPa 位涡扰动, 风场, 散度', 
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
    if div is not None:

        x, y = np.meshgrid(div['lon'], div['lat'])
        z=np.squeeze(div['data'])
        clevs_div = np.arange(-15, 16, 1)
        # plots['div'] = ax.contourf(
        #     x, y, z*1e5,clevs_div,cmap=plt.cm.PuOr,
        #     transform=datacrs,alpha=0.5, zorder=1,extend='both')

        cmap=dk_ctables2.ncl_cmaps('hotcolr_19lev')
        plots['div'] = ax.contourf(
            x, y, z*1e5,
            levels=clevs_div[:],
            vmin=-15,vmax=15,cmap=cmap,
            transform=datacrs,alpha=0.5, zorder=1,extend='both')

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['u'].values) * 2.5
        v = np.squeeze(uv['v'].values) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=2)

    # draw -hPa geopotential height
    if pv is not None:
        x, y = np.meshgrid(pv['lon'], pv['lat'])
        clevs_pv = np.arange(4, 25, 1)
        plots['pv'] = ax.contour(
            x, y, np.squeeze(pv['data'])*1e6, clevs_pv, colors='black',
            linewidths=2, transform=datacrs, zorder=3)
        plt.clabel(plots['pv'], inline=1, fontsize=20, fmt='%.0f',colors='black')

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=4)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    utl.add_cartopy_background(ax,name='RD')

    l, b, w, h = ax.get_position().bounds
    #forecast information
    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initTime = pd.to_datetime(
    str(pv['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=pv['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(pv.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(div != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['div'], cax=cax, orientation='horizontal',
                       ticks=clevs_div[:],
                      extend='both',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Divergence ($10^5$ s$^{-1}$)',size=20)

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
        plt.savefig(output_dir+'位涡_风场_散度_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(pv.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200,bbox_inches='tight')
    
    if(output_dir == None):
        plt.show()              