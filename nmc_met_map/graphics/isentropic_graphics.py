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
from scipy.ndimage import gaussian_filter

def draw_isentropic_uv(isentrh=None, isentuv=None, isentprs=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=False,south_China_sea=True,
                    output_dir=None,Global=False):

# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

# set figure
    plt.figure(figsize=(16,9))

    # set data projection
    if(Global == True):
        plotcrs = ccrs.Robinson(central_longitude=115.)
    else:
        plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
            central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
    
    datacrs = ccrs.PlateCarree()
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)


#draw data
    plots = {}
    if isentrh is not None:
        x, y = np.meshgrid(isentrh['lon'], isentrh['lat'])
        z=np.squeeze(isentrh['data'])
        clevs_rh= range(10, 106, 5)
        plots['isentrh'] = ax.contourf(
            x, y, z,clevs_rh,cmap=plt.cm.gist_earth_r,
            transform=datacrs,alpha=0.5,extend='both')

    # draw -hPa wind bards
    if isentuv is not None:
        x, y = np.meshgrid(isentuv['lon'], isentuv['lat'])
        u = np.squeeze(isentuv['isentu'].values) * 2.5
        v = np.squeeze(isentuv['isentv'].values) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=20)

    # draw -hPa geopotential height
    if isentprs is not None:
        x, y = np.meshgrid(isentprs['lon'], isentprs['lat'])
        clevs_isentprs =  np.arange(0, 1000, 25)
        z=gaussian_filter(np.squeeze(isentprs['data']),5)
        plots['isentprs'] = ax.contour(
            x, y, z , clevs_isentprs, colors='black',
            linewidths=2, transform=datacrs, zorder=30)
        plt.clabel(plots['isentprs'], inline=1, fontsize=20, fmt='%.0f',colors='black')
#additional information
    plt.title('['+isentrh.attrs['model']+'] '+
    str(isentrh['level'].values[0])+'K 等熵面  风场 相对湿度 气压', 
        loc='left', fontsize=30)

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

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=40)
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
    str(isentrh.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=isentrh.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(isentrh.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(isentrh != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['isentrh'], cax=cax, orientation='horizontal',
                      ticks=clevs_rh[:],
                      extend='both',extendrect=False)
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Relative Humidity (%)',size=20)

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
        plt.savefig(output_dir+isentrh['lev']+'等熵面分析_相对湿度_风场_气压_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(isentrh.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()              