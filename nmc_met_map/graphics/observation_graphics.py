# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Map design before drawing
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
#import cartopy.io.img_tiles as cimgt
from matplotlib.patches import Patch
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from nmc_met_graphics.plot.china_map import add_china_map_2cartopy
from nmc_met_graphics.cmap.cm import guide_cmaps
from nmc_met_graphics.plot.util import add_logo, add_model_title
from nmc_met_map.lib.utility import add_logo_extra,add_city_on_map,add_china_map_2cartopy_public,add_public_title,add_south_China_sea,adjust_map_ratio,add_public_title_obs,add_logo_extra_in_axes,add_public_title_sta
from datetime import datetime, timedelta
import pandas as pd
import locale
import scipy.ndimage as ndimage
from matplotlib.colors import BoundaryNorm,ListedColormap
import sys
import nmc_met_graphics.cmap.ctables as dk_ctables
import nmc_met_graphics.cmap.wrf as wrf_ctables
import nmc_met_map.lib.utility as utl
from metpy.plots import add_metpy_logo, add_timestamp, colortables
import nmc_met_graphics.mask as dk_mask
import os
from scipy.ndimage import gaussian_filter

def OBS_Sounding_GeopotentialHeight(IR=None,Sounding=None,HGT=None,
        map_extent=None,city=True,south_China_sea=True,output_dir=None,
        Channel='C009'):

    #if(sys.platform[0:3] == 'win'):
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    # draw figure
    plt.figure(figsize=(16,9))

    plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
        central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
    
    # draw main figure
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    
    datacrs = ccrs.PlateCarree()
    
    map_extent2=adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)
    # plot map background
 
    ax.add_feature(cfeature.OCEAN)
    add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=2,alpha=0.5)
    add_china_map_2cartopy_public(
        ax, name='nation', edgecolor='black', lw=0.8, zorder=2)
    add_china_map_2cartopy_public(
        ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=2,alpha=0.5)

    # define return plots
    plots = {}

    # draw IR
    if IR is not None:
        x, y = np.meshgrid(IR['lon'], IR['lat'])

        z=np.squeeze(IR['image'])
        if(Channel == 'C009'):
            cmap=dk_ctables.cm_wv_enhancement()
            norm, cmap = colortables.get_with_range('WVCIMSS', 160, 300)            
            title_name='水汽图像'
            plots['IR'] = ax.pcolormesh(
                x, y, z, norm=norm,
                cmap=cmap, zorder=1,transform=datacrs)

        if(Channel == 'C012'):
            cmap=dk_ctables.cm_ir_enhancement1()
            title_name='红外(10.8微米)'
            plots['IR'] = ax.pcolormesh(
                x, y, z, vmin=105., vmax=335.0,
                cmap=cmap, zorder=1,transform=datacrs)

        plt.title('FY4A'+title_name+
            '观测'+' 探空观测 高度场',
            loc='left', fontsize=30)
        if(Sounding is not None):
            x = np.squeeze(Sounding['lon'].values)
            y = np.squeeze(Sounding['lat'].values)
            idx_vld=np.where((Sounding['Wind_angle'].values != np.nan) & 
                        (Sounding['Wind_speed'].values != np.nan))
            u,v=utl.wind2UV(Winddir=Sounding['Wind_angle'].values[idx_vld],Windsp=Sounding['Wind_speed'].values[idx_vld])
            idx_null=np.where((u > 100) | (v > 100))
            u[idx_null]=np.nan
            v[idx_null]=np.nan
            
            c_barb={'C009':'black',
                    'C012':'white'}

            plots['uv'] = ax.barbs(
                x, y, u, v,
                transform=datacrs, fill_empty=False, 
                sizes=dict(emptybarb=0.0),barb_increments={'half':2,'full':4,'flag':20},
                zorder=2,color=c_barb[Channel], alpha=0.7,lw=1.5, length=7)  

        # draw mean sea level pressure
        if(HGT is not None):
            x, y = np.meshgrid(HGT['lon'], HGT['lat'])
            clevs =np.append(np.arange(480, 584, 8), np.arange(580, 604, 4))
            plots_HGT = ax.contour(x, y, 
                ndimage.gaussian_filter(np.squeeze(HGT['data']), sigma=1, order=0), 
                levels=clevs, colors='black', alpha=1, zorder=3, 
                transform=datacrs,linewidths=3)
            ax.clabel(plots_HGT, inline=1, fontsize=20, fmt='%.0f')
            ax.contour(x, y,
                ndimage.gaussian_filter(np.squeeze(HGT['data']), sigma=1, order=0), 
                levels=[588], colors='black', alpha=1, zorder=3, 
                transform=datacrs,linewidths=6)            

    #if city:
    gl = ax.gridlines(
        crs=datacrs, linewidth=1, color='gray', alpha=0.5, linestyle='--', zorder=40)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    #utl.add_cartopy_background(ax,name='RD')
    l, b, w, h = ax.get_position().bounds

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    IR_time = pd.to_datetime(IR.coords['time'].values[0]).to_pydatetime()
    Sounding_time=Sounding['time'][0].to_pydatetime()
    HGT_initTime = pd.to_datetime(
    str(HGT.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    HGT_time=HGT_initTime+timedelta(hours=HGT.coords['forecast_period'].values[0])
    #logo
    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])        
    add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')
    bax.text(2.5,7.5,'卫星图像观测时间: '+IR_time.strftime("%Y年%m月%d日%H时"),size=12)
    bax.text(2.5,5,'探空观测时间: '+Sounding_time.strftime("%Y年%m月%d日%H时"),size=12)
    bax.text(2.5,2.5,'高度场时间: '+HGT_time.strftime("%Y年%m月%d日%H时"),size=12)
    bax.text(2.5, 0.5,'www.nmc.cn',size=12)
        
    initial_time = pd.to_datetime(
    str(IR['time'].values[0])).replace(tzinfo=None).to_pydatetime()
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    

    # add color bar
    cax=plt.axes([l,b-0.04,w,.02])
    cb = plt.colorbar(plots['IR'], cax=cax, orientation='horizontal',
                      extend='both',extendrect=False)
    cb.ax.tick_params(labelsize='x-large')                      
    cb.set_label('(K)',size=10)

    
    # add south China sea
    if south_China_sea:
        add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        add_city_on_map(ax,map_extent=map_extent2,
            transform=datacrs,zorder=2,size=16,small_city=small_city)
    
    # show figure
    
    if(output_dir != None ):
        plt.savefig(output_dir+'卫星'+
        #'_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '卫星观测时间_'+
        pd.to_datetime(IR['time'].values[0]).strftime("%Y年%m月%d日%H时")+'.png', dpi=300)

    if(output_dir == None ):
        plt.show()

def draw_cumulative_precip_and_rain_days(cu_rain=None, days_rain=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None,Global=False):
# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

# set figure
    plt.figure(figsize=(16,9))

    plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
        central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
    plotcrs=ccrs.PlateCarree()
    datacrs = ccrs.PlateCarree()

    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    map_extent2=map_extent
    #map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)

    # define return plots
    plots = {}
    # draw mean sea level pressure
    #if(os.path.exists('L:/Temp/mask.npy')):
    #    mask=np.load('L:/Temp/mask.npy')
    #else:
    #mask=dk_mask.grid_mask_china(cu_rain['lon'], cu_rain['lat'])
    #np.save('L:/Temp/mask',mask)


    # draw -hPa geopotential height
    if days_rain is not None:
        x, y = np.meshgrid(days_rain['lon'], days_rain['lat'])
        clevs_days = np.arange(4,np.nanmax(days_rain.values)+1)
        z = gaussian_filter(np.squeeze(days_rain.values),5)
        #z=z*mask
        z[z<0]=np.nan
        plots['days_rain'] = ax.contour(
            x, y, z, clevs_days, colors='black',
            linewidths=2, transform=datacrs, zorder=3)
        plt_lbs=plt.clabel(plots['days_rain'], inline=2, fontsize=20, fmt='%.0f',colors='black')
        clip_days=utl.gy_China_maskout(plots['days_rain'],ax,plt_lbs)
    if cu_rain is not None:
        x, y = np.meshgrid(cu_rain['lon'], cu_rain['lat'])
        z=np.squeeze(cu_rain.values)
        #cmap,norm=dk_ctables.cm_qpf_nws(atime=24)
        #cmap,norm=dk_ctables.cm_precipitation_nws(atime=24)
        #cmap,norm=dk_ctables.cm_rain_nws(atime=24)
        cmap,norm=utl.cm_heavy_rain_nws(atime=24)
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        #z=z*mask
        z[z<25]=np.nan
        plots['rain'] = ax.contourf(x,y,z,clevs=norm.boundaries,
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)
        #plots['rain'] = ax.pcolormesh(
        #    x,y,z, norm=norm,
        #    cmap=cmap, zorder=1,transform=datacrs,alpha=0.2)
        clip_rain=utl.gy_China_maskout(plots['rain'],ax)            

#additional information
    plt.title('过去'+str(int(days_rain.attrs['rn_ndays']))+'天降水日数, '+
    '过去'+str(int(cu_rain.attrs['cu_ndays']))+'天累积降水量', 
        loc='left', fontsize=30)
        
    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=3,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='black', lw=0.5, zorder=3)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=3)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=3,alpha=0.5)


    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=1)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    #utl.add_cartopy_background(ax,name='RD')

    l, b, w, h = ax.get_position().bounds

    #forecast information
    bax=plt.axes([l,b+h-0.05,.27,.05],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initTime = pd.to_datetime(
    str(days_rain.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=days_rain.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(1.5, 5.5,'观测截止时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(1.5, 0.5,'www.nmc.cn',size=18)

    # add color bar
    if(cu_rain is not None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['rain'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('累积降水量 (mm)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    #if(map_extent2[1]-map_extent2[0] < 25):
    #    small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=2,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.01,b+h-0.05,.06,.05],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'总降水_'+
        '观测时间_'+initTime.strftime("%Y年%m月%d日%H时")+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()
