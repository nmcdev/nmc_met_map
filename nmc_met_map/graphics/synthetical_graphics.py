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
import matplotlib.patches as mpatches
import matplotlib.lines as lines

def draw_Miller_Composite_Chart(fcst_info=None,
                    u_300=None,v_300=None,u_500=None,v_500=None,u_850=None,v_850=None,
                    pmsl_change=None,hgt_500_change=None,Td_dep_700=None,
                    Td_sfc=None,pmsl=None,lifted_index=None,vort_adv_500_smooth=None,
                    map_extent=(50, 150, 0, 65),
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

#draw data
    plots = {}

    lons=fcst_info['lon']
    lats=fcst_info['lat']
    cs1 = ax.contour(lons, lats, lifted_index, range(-8, -2, 2), transform=ccrs.PlateCarree(),
                    colors='red', linewidths=0.75, linestyles='solid', zorder=7)
    cs1.clabel(fontsize=10, inline=1, inline_spacing=7,
            fmt='%i', rightside_up=True, use_clabeltext=True)


    # Plot Surface pressure falls
    cs2 = ax.contour(lons, lats, pmsl_change.to('hPa'), range(-10, -1, 4),
                    transform=ccrs.PlateCarree(),
                    colors='k', linewidths=0.75, linestyles='dashed', zorder=6)
    cs2.clabel(fontsize=10, inline=1, inline_spacing=7,
            fmt='%i', rightside_up=True, use_clabeltext=True)

    # Plot 500-hPa height falls
    cs3 = ax.contour(lons, lats, hgt_500_change, range(-60, -29, 15),
                    transform=ccrs.PlateCarree(), colors='k', linewidths=0.75,
                    linestyles='solid', zorder=5)
    cs3.clabel(fontsize=10, inline=1, inline_spacing=7,
            fmt='%i', rightside_up=True, use_clabeltext=True)

    # Plot surface pressure
    ax.contourf(lons, lats, pmsl.to('hPa'), range(990, 1011, 20), alpha=0.5,
                transform=ccrs.PlateCarree(),
                colors='yellow', zorder=1)

    # Plot surface dewpoint
    ax.contourf(lons, lats, Td_sfc.to('degF'), range(65, 76, 10), alpha=0.4,
                transform=ccrs.PlateCarree(),
                colors=['green'], zorder=2)

    # Plot 700-hPa dewpoint depression
    ax.contourf(lons, lats, Td_dep_700, range(15, 46, 30), alpha=0.5, transform=ccrs.PlateCarree(),
                colors='tan', zorder=3)

    # Plot Vorticity Advection
    ax.contourf(lons, lats, vort_adv_500_smooth, range(5, 106, 100), alpha=0.5,
                transform=ccrs.PlateCarree(),
                colors='BlueViolet', zorder=4)

    # Define a skip to reduce the barb point density
    skip_300 = (slice(None,None, 12), slice(None,None, 12))
    skip_500 = (slice(None,None, 10), slice(None,None, 10))
    skip_850 = (slice(None,None, 8), slice(None,None, 8))
    x,y=np.meshgrid(fcst_info['lon'], fcst_info['lat'])
    # 300-hPa wind barbs
    jet300 = ax.barbs(x[skip_300], y[skip_300], u_300[skip_300].m, v_300[skip_300].m, length=6,
                    transform=ccrs.PlateCarree(),
                    color='green', zorder=10, label='300-hPa Jet Core Winds (m/s)')

    # 500-hPa wind barbs
    jet500 = ax.barbs(x[skip_500], y[skip_500], u_500[skip_500].m, v_500[skip_500].m, length=6,
                    transform=ccrs.PlateCarree(),
                    color='blue', zorder=9, label='500-hPa Jet Core Winds (m/s)')

    # 850-hPa wind barbs
    jet850 = ax.barbs(x[skip_850], y[skip_850], u_850[skip_850].m, v_850[skip_850].m, length=6,
                    transform=ccrs.PlateCarree(),
                    color='k', zorder=8, label='850-hPa Jet Core Winds (m/s)')

#additional information
    plt.title('['+fcst_info['model']+'] '+
    'Miller 综合分析图', 
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

    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=40)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    utl.add_cartopy_background(ax,name='RD')

    l, b, w, h = ax.get_position().bounds

    # Legend
    purple = mpatches.Patch(color='BlueViolet', label='Cyclonic Absolute Vorticity Advection')
    yellow = mpatches.Patch(color='yellow', label='Surface MSLP < 1010 hPa')
    green = mpatches.Patch(color='green', label='Surface Td > 65 F')
    tan = mpatches.Patch(color='tan', label='700 hPa Dewpoint Depression > 15 C')
    red_line = lines.Line2D([], [], color='red', label='Best Lifted Index (C)')
    dashed_black_line = lines.Line2D([], [], linestyle='dashed', color='k',
                                    label='12-hr Surface Pressure Falls (hPa)')
    black_line = lines.Line2D([], [], linestyle='solid', color='k',
                            label='12-hr 500-hPa Height Falls (m)')
    leg = plt.legend(handles=[jet300, jet500, jet850, dashed_black_line, black_line, red_line,
                            purple, tan, green, yellow], loc=3,
                    title='Composite Analysis Valid: ',
                    framealpha=1)
    leg.set_zorder(100)

    #forecast information
    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initTime = pd.to_datetime(
    str(fcst_info['forecast_reference_time'])).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=fcst_info['forecast_period'])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(fcst_info['forecast_period'])+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

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
        plt.savefig(output_dir+'Miller_综合图_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(fcst_info['forecast_period'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()