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
from scipy.ndimage import gaussian_filter
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
import os
import nmc_met_map.graphics2 as GF
# from celluloid import Camera

def draw_obs_cu_rain(rain=None,map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,add_background=True,
                    output_dir=None):

    initTime = pd.to_datetime(rain.attrs['obs_time']).replace(tzinfo=None).to_pydatetime()

    title = '[{}] 过去{}小时{}'.format(rain.attrs['model'],str(rain.attrs['atime']),rain.attrs['var_name'])

    forcast_info = '观测|分析时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\nwww.nmc.cn'.format(initTime)

    fig, ax, map_extent = GF.pallete_set.Horizontal_Pallete((18, 9),map_extent=map_extent, title=title, forcast_info=forcast_info,info_zorder=4,
                                             add_china=add_china, add_city=city, add_background=add_background, south_China_sea=south_China_sea)

    plots = {}
    # draw mean sea level pressure
    # plots['cu_rain']=GF.draw_method.cu_rain_pcolormesh(ax,rain['lon'].values,rain['lat'].values,rain['data'].values.squeeze(),zorder=1,alpha=0.8)
    plots['cu_rain']=GF.draw_method.cu_rain_contourf(ax,rain['lon'].values,rain['lat'].values,rain['data'].values.squeeze(),atime=int(rain.attrs['atime']),zorder=1,alpha=0.8)
    clip_rain=utl.gy_China_maskout(plots['cu_rain'],ax)
    # add color bar
    l, b, w, h = ax.get_position().bounds
    cax=plt.axes([l,b-0.04,w,.02])
    cb = plt.colorbar(plots['cu_rain'], cax=cax, orientation='horizontal')
    cb.ax.tick_params(labelsize='x-large')                      
    cb.set_label(str(int(rain.attrs['atime']))+'h accumulated precipitation (mm)',size=20)

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'累积降水_观测_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '累积时间_'+str(rain.attrs['atime'])+'小时'+'.png', 
        dpi=200,bbox_inches='tight')
        plt.close()
    
    if(output_dir == None):
        plt.show()

def draw_gh_rain(gh=None, rain=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None,Global=False):
# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

# set figure
    plt.figure(figsize=(16,9))

    if(Global == True):
        plotcrs = ccrs.Robinson(central_longitude=115.)
    else:
        plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
            central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    datacrs = ccrs.PlateCarree()

    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)

    # define return plots
    plots = {}
    # draw mean sea level pressure
    if rain is not None:
        x, y = np.meshgrid(rain['lon'], rain['lat'])
        z=np.squeeze(rain['data'].values)
        z[z<0.1]=np.nan
        cmap,norm=dk_ctables.cm_qpf_nws(atime=rain.attrs['atime'])
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['rain'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)

    # draw -hPa geopotential height
    if gh is not None:
        x, y = np.meshgrid(gh['lon'], gh['lat'])
        clevs_gh = np.append(np.append(np.arange(0, 480, 4),np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))), np.arange(604, 2000, 8))
        plots['gh'] = ax.contour(
            x, y, np.squeeze(gh['data'].values), clevs_gh, colors='black',
            linewidths=2, transform=datacrs, zorder=3)
        plt.clabel(plots['gh'], inline=2, fontsize=20, fmt='%.0f',colors='black')
#additional information
    plt.title('['+gh.attrs['model']+'] '+
                str(int(gh['level'].values[0]))+'hPa 位势高度场, '+
                str(int(rain.attrs['atime']))+'小时降水', 
                loc='left', fontsize=30)
        
    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=3,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=3)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=3)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=3,alpha=0.5)


    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=1)
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
    if(rain != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['rain'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label(str(int(rain.attrs['atime']))+'h precipitation (mm)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=2,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'高度场_降水_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(int(gh.coords['forecast_period'].values[0]))+'小时'+'.png', dpi=200,bbox_inches='tight')
        plt.close()
    
    if(output_dir == None):
        plt.show()

def draw_mslp_rain_snow(
        rain=None, snow=None,sleet=None,mslp=None,
        map_extent=(50, 150, 0, 65),
        regrid_shape=20,
        add_china=True,city=True,south_China_sea=True,
        output_dir=None,Global=False):
# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

# set figure
    plt.figure(figsize=(16,9))

    if(Global == True):
        plotcrs = ccrs.Robinson(central_longitude=115.)
    else:
        plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
            central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    
    datacrs = ccrs.PlateCarree()
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)

    plt.title('['+mslp.attrs['model']+'] '+
    '海平面气压, '+
    str(rain.attrs['atime'])+'小时降水', 
        loc='left', fontsize=30)

#draw data
    plots = {}
    if rain is not None:
        x, y = np.meshgrid(rain['lon'], rain['lat'])
        z=np.squeeze(rain.values)
        cmap,norm=dk_ctables.cm_rain_nws(atime=rain.attrs['atime'])
        #cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['rain'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=3,transform=datacrs,alpha=0.8)

    if snow is not None:
        x, y = np.meshgrid(snow['lon'], snow['lat'])
        z=np.squeeze(snow.values)
        cmap,norm=dk_ctables.cm_snow_nws(atime=rain.attrs['atime'])
        #cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['snow'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=3,transform=datacrs,alpha=0.8)
    
    if sleet is not None:
        x, y = np.meshgrid(sleet['lon'], sleet['lat'])
        z=np.squeeze(sleet.values)
        cmap,norm=dk_ctables.cm_sleet_nws(atime=rain.attrs['atime'])
        #cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['sleet'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=3,transform=datacrs,alpha=0.8)

    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(900, 1100,2.5)
        z=gaussian_filter(np.squeeze(mslp['data']), 5)
        plots['mslp'] = ax.contour(
            x, y, z, clevs_mslp, colors='black',
            linewidths=2, transform=datacrs, zorder=3)
        plt.clabel(plots['mslp'], inline=1, fontsize=20, fmt='%.0f',colors='black')
#additional information
    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=1,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=1)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=1)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=1,alpha=0.5)

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=1)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    # utl.add_cartopy_background(ax,name='RD')
    ax.add_feature(cfeature.LAND,color='#F5E19F')
    ax.add_feature(cfeature.OCEAN)
    
    l, b, w, h = ax.get_position().bounds

    #forecast information
    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initTime = pd.to_datetime(
    str(mslp.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=mslp.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(mslp.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(sleet is not None):
        cax=plt.axes([l-0.03,b-0.04,w/3,.02])
        cb = plt.colorbar(plots['sleet'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('雨夹雪 (mm)',size=20)

    if(snow is not None):
        # cax=plt.axes([l+0.32,b-0.04,w/4,.02])
        cax=plt.axes([l+w/3,b-0.04,w/3,.02])
        cb = plt.colorbar(plots['snow'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('雪 (mm)',size=20)

    if(rain is not None):
        # cax=plt.axes([l+0.65,b-0.04,w/4,.02])
        cax=plt.axes([l+w*2/3+0.03,b-0.04,w/3,.02])
        cb = plt.colorbar(plots['rain'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('雨 (mm)',size=20)

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
        plt.savefig(output_dir+'海平面气压_降水_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(int(mslp.coords['forecast_period'].values[0]))+'小时'+'.png',
         dpi=200,bbox_inches='tight')
        plt.close()
    
    if(output_dir == None):
        plt.show()


def draw_Rain_evo(
        rain=None,fcs_lvl=4,
        map_extent=(50, 150, 0, 65),
        regrid_shape=20,
        add_china=True,city=True,south_China_sea=True,
        output_dir=None,Global=False):
# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
# set figure
    plt.figure(figsize=(16,9))

    if(Global == True):
        plotcrs = ccrs.Robinson(central_longitude=115.)
    else:
        plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
            central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    
    datacrs = ccrs.PlateCarree()
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)

    plt.title('['+rain.attrs['model']+'] 预报逐'+
        str(rain.attrs['t_gap'])+'小时'+str(fcs_lvl)+'mm降水范围演变', 
        loc='left', fontsize=30)
#draw data
    plots = {}
    if rain is not None:
        x, y = np.meshgrid(rain['lon'], rain['lat'])
        for itime in range(0,len(rain['time'].values)):
            z=np.squeeze(rain['data'].values[itime,:,:])
            z[z<=0.1]=np.nan
            initTime = pd.to_datetime(str(rain.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
            labels=(initTime+timedelta(hours=rain.coords['forecast_period'].values[itime])).strftime("%m月%d日%H时")
            cmap=mpl.cm.jet
            per_color=utl.get_part_clev_and_cmap(cmap=cmap,clev_range=[0,len(rain['time'].values)],clev_slt=itime)
            ax.contourf(
                x,y,z, levels=[fcs_lvl,800],
                colors=per_color, zorder=3,transform=datacrs,
                alpha=0.2+itime*((1-0.2)/len(rain['time'].values)))
            if(itime == 0):
                label_handles = [mpatches.Patch(color=per_color.reshape(4),
                    alpha=0.2+itime*((1-0.2)/len(rain['time'].values)), label=labels)]
            else:
                label_handles.append(mpatches.Patch(color=per_color.reshape(4),alpha=0.2+itime*((1-0.2)/len(rain['time'].values)), label=labels))
        leg = plt.legend(handles=label_handles, loc=3,framealpha=1)
#additional information
    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=1,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=1)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=1)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=1,alpha=0.5)

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=1)
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
    str(rain.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=rain.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'起始时间: '+
        (initTime+timedelta(hours=rain.coords['forecast_period'].values[0])).strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'终止时间: '+
        (initTime+timedelta(hours=rain.coords['forecast_period'].values[1])).strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
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
        plt.savefig(output_dir+'海平面气压_降水_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(int(rain.coords['forecast_period'].values[0]))+'小时'+'.png', dpi=200,bbox_inches='tight')
        plt.close()
    
    if(output_dir == None):
        plt.show()        

def draw_cumulated_precip_evo(
        rain=None,
        map_extent=(50, 150, 0, 65),
        regrid_shape=20,
        add_china=True,city=True,south_China_sea=True,
        output_dir=None,Global=False):
# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

# set figure
    fig = plt.figure(figsize=(16,9))

    plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
        central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])

    datacrs = ccrs.PlateCarree()

    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)

    # define return plots
    plots = {}
    # draw mean sea level pressure
    if rain is not None:
        x, y = np.meshgrid(rain['lon'], rain['lat'])
        z=np.squeeze(rain['data'].values)
        z[z<0.1]=np.nan
        znan=np.zeros(shape=x.shape)
        znan[:]=np.nan
        cmap,norm=dk_ctables.cm_qpf_nws(atime=24)
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['rain'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)
#additional information
    plt.title('['+rain.attrs['model']+'] '+
    str(int(rain.coords['forecast_period'].values[0])-rain.attrs['t_gap'])+
        '至'+str(int(rain.coords['forecast_period'].values[-1]))+'时效累积降水预报',
        loc='left', fontsize=25)

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=3,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=3)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=3)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=3,alpha=0.5)

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=1)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    utl.add_cartopy_background(ax,name='RD')

    l, b, w, h = ax.get_position().bounds

    #forecast information


    initTime = pd.to_datetime(
    str(rain.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()

    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    # add color bar
    cax=plt.axes([l,b-0.04,w,.02])
    cb = plt.colorbar(plots['rain'], cax=cax, orientation='horizontal')
    cb.ax.tick_params(labelsize='x-large')                      
    cb.set_label('Precipitation (mm)',size=20)
    fcst_time=initTime+timedelta(hours=rain.coords['forecast_period'].values[0])
    bax=plt.axes([l,b+h-0.1,.25,.1])
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])   
    fcst_time1=initTime+timedelta(hours=rain.coords['forecast_period'].values[0]-6)
    bax.text(2.5, 7.5,'起始时间: '+fcst_time1.strftime("%Y年%m月%d日%H时"),size=15)
    bax.text(2.5, 0.5,'www.nmc.cn',size=15)
    valid_fhour=bax.text(2.5, 5,'截至时间: ',size=15)
    txt_fhour=bax.text(2.5, 2.5,'预报时效: ',size=15)
    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')
    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=2,size=13,small_city=small_city)

    def update(frame_number):
        fcst_time2=initTime+timedelta(hours=rain.coords['forecast_period'].values[frame_number])
        valid_fhour.set_text('截至时间: '+fcst_time2.strftime("%Y年%m月%d日%H时"))
        txt_fhour.set_text('预报时效: '+str(int(rain.coords['forecast_period'].values[frame_number]))+'小时')
        return ax.pcolormesh(
            x,y,np.squeeze(z[frame_number,:,:]), norm=norm,
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)
    nframes=rain['data'].shape[0]
    animation1 = FuncAnimation(fig, update, frames=nframes,interval=1000)
    # ffmpegpath = os.path.abspath(r"C:\Users\HEYGY\Desktop\ffmpeg-20200824-3477feb-win64-static\bin\ffmpeg.exe")
    # import matplotlib
    # matplotlib.rcParams["animation.ffmpeg_path"] = ffmpegpath
    # writer = animation.FFMpegWriter()
    # show figure
    plt.subplots_adjust(top=1, bottom=0, right=0.93, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    if(output_dir != None):
        animation1.save(output_dir+'累积降水演变_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(int(rain.coords['forecast_period'].values[-1]))+'小时_'+
        '['+rain.attrs['model']+'] '+'.gif',writer='pillow')

    if(output_dir == None):
        #animation.save('rain.gif', fps=75, writer='imagemagick')
        plt.show()
        #plt.draw()
        #plt.pause(0.1)


# def draw_cumulated_precip(
#         rain=None,
#         map_extent=(50, 150, 0, 65),
#         add_china=True,city=True,south_China_sea=True,
#         output_dir=None,Global=False):
# # set font
#     plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
#     plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

# # set figure
#     fig = plt.figure(figsize=(9,14))
#     # camera = Camera(fig)
#     nframe=rain['data'].shape[0]
#     plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
#         central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])

#     datacrs = ccrs.PlateCarree()

#     ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
#     map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)

#     # define return plots
#     plots = {}
#     # draw mean sea level pressure
#     if rain is not None:
#         x, y = np.meshgrid(rain['lon'], rain['lat'])
#         z=np.squeeze(rain['data'].values)
#         z[z<0.1]=np.nan
#         znan=np.zeros(shape=x.shape)
#         znan[:]=np.nan
#         cmap,norm=dk_ctables.cm_qpf_nws(atime=24)

#         cmap.set_under(color=[0,0,0,0],alpha=0.0)
#         plots['rain'] = ax.pcolormesh(
#             x,y,znan, norm=norm,
#             cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)
# #additional information
#     plt.title('['+rain.attrs['model']+'] '+
#     str(int(rain.coords['forecast_period'].values[0]))+'至'+str(int(rain.coords['forecast_period'].values[-1]))+'时效累积降水预报',
#         loc='left', fontsize=30)

#     ax.add_feature(cfeature.OCEAN)
#     utl.add_china_map_2cartopy_public(
#         ax, name='coastline', edgecolor='gray', lw=0.8, zorder=3,alpha=0.5)
#     if add_china:
#         utl.add_china_map_2cartopy_public(
#             ax, name='province', edgecolor='gray', lw=0.5, zorder=3)
#         utl.add_china_map_2cartopy_public(
#             ax, name='nation', edgecolor='black', lw=0.8, zorder=3)
#         utl.add_china_map_2cartopy_public(
#             ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=3,alpha=0.5)

#     # grid lines
#     gl = ax.gridlines(
#         crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=1)
#     gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
#     gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

#     utl.add_cartopy_background(ax,name='RD')

#     l, b, w, h = ax.get_position().bounds

#     #forecast information


#     initTime = pd.to_datetime(
#     str(rain.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()

#     #发布时间
#     if(sys.platform[0:3] == 'lin'):
#         locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
#     if(sys.platform[0:3] == 'win'):        
#         locale.setlocale(locale.LC_CTYPE, 'chinese')

#     # add color bar
#     cax=plt.axes([l,b-0.04,w,.02])
#     cb = plt.colorbar(plots['rain'], cax=cax, orientation='horizontal')
#     cb.ax.tick_params(labelsize='x-large')                      
#     cb.set_label('Precipitation (mm)',size=20)
#     fcst_time=initTime+timedelta(hours=rain.coords['forecast_period'].values[0])
#     bax=plt.axes([l,b+h-0.07,.45,.07])
#     bax.set_yticks([])
#     bax.set_xticks([])
#     bax.axis([0, 10, 0, 10])   
#     fcst_time1=initTime+timedelta(hours=rain.coords['forecast_period'].values[0]-6)
#     bax.text(2.5, 7.5,'起始时间: '+fcst_time1.strftime("%Y年%m月%d日%H时"),size=15)
#     bax.text(2.5, 0.5,'www.nmc.cn',size=15)
#     valid_fhour=bax.text(2.5, 5,'截至时间: ',size=15)
#     txt_fhour=bax.text(2.5, 2.5,'预报时效: ',size=15)
#     utl.add_logo_extra_in_axes(pos=[l-0.0,b+h-0.085,.1,.1],which='nmc', size='Xlarge')
#     # add south China sea
#     if south_China_sea:
#         utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

#     small_city=False
#     if(map_extent2[1]-map_extent2[0] < 25):
#         small_city=True
#     if city:
#         utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=2,size=13,small_city=small_city)

#     fcst_time2=initTime+timedelta(hours=rain.coords['forecast_period'].values[-1])
#     valid_fhour.set_text('截至时间: '+fcst_time2.strftime("%Y年%m月%d日%H时"))
#     txt_fhour.set_text('预报时效: '+str(int(rain.coords['forecast_period'].values[-1]))+'小时')
#     ax.pcolormesh(
#     x,y,np.squeeze(z[-1,:,:]), norm=norm,
#             cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)
    
#     # plt.draw()
#     if(output_dir is not None):
#         plt.savefig(output_dir+
#             '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
#             '预报时效_'+str(int(rain.coords['forecast_period'].values[-1]))+'小时_'+rain.attrs['model']+'.png', dpi=200,bbox_inches='tight')
#         plt.close()
#     else:
#         plt.show()

def draw_cumulated_precip(
        rain=None,
        map_extent=(50, 150, 0, 65),
        add_china=True,city=True,south_China_sea=True,add_background=True,
        output_dir=None,Global=False):
 
    initTime = pd.to_datetime(rain.attrs['initTime']).replace(tzinfo=None).to_pydatetime()
    fcstTime1 = initTime + timedelta(hours=int(rain.attrs['fhour1']-rain.attrs['t_gap']))
    fcstTime2 = initTime + timedelta(hours=int(rain.attrs['fhour2']))

    title = '[{}] {}到{}时效累积降水'.format(rain.attrs['model'],int(rain.attrs['fhour1']-rain.attrs['t_gap']),int(rain.attrs['fhour2']))
    
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n起始时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n终止时间: {2:%Y}年{2:%m}月{2:%d}日{2:%H}时\nwww.nmc.cn'.format(initTime, fcstTime1, fcstTime2)

    fig, ax, map_extent = GF.pallete_set.Horizontal_Pallete((18, 9),map_extent=map_extent, title=title, forcast_info=forcast_info,info_zorder=4,
                                            add_china=add_china, add_city=city, add_background=add_background, south_China_sea=south_China_sea)
    if rain is not None:
        x, y = np.meshgrid(rain['lon'], rain['lat'])
        z=np.squeeze(rain['data'].values)
        z[z<0.1]=np.nan
        cmap,norm=dk_ctables.cm_qpf_nws(atime=24)

        plots={}
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['rain'] = ax.pcolormesh(
            x,y,z, norm=norm,
            cmap=cmap, zorder=1,transform=ccrs.PlateCarree(),alpha=0.5)
 
    l, b, w, h = ax.get_position().bounds
    # add color bar
    cax=plt.axes([l,b-0.04,w,.02])
    cb = plt.colorbar(plots['rain'], cax=cax, orientation='horizontal')
    cb.ax.tick_params(labelsize='x-large')                      
    cb.set_label('Precipitation (mm)',size=20)

    if(output_dir is not None):
        plt.savefig(output_dir+
            '起报时间_{0:%Y}年{0:%m}月{0:%d}日{0:%H}时_起始时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时_终止时间_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时'.format(initTime, fcstTime1, fcstTime2)+'.png', dpi=200,bbox_inches='tight')
        plt.close()
    else:
        plt.show()