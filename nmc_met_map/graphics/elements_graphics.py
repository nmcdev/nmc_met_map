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

def draw_T_2m(T_2m=None,
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
        
    plt.title('['+T_2m['model']+']'+' '+T_2m['title'], 
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
    if T_2m is not None:
        x, y = np.meshgrid(T_2m['lon'], T_2m['lat'])
        z=np.squeeze(T_2m['data'])
        cmap=dk_ctables.cm_temperature_nws()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['T_2m'] = ax.pcolormesh(
            x,y,z,
            cmap=cmap, zorder=100,transform=datacrs,alpha=0.5, vmin=-45, vmax=45)

        clevs_zero = 0
        z=gaussian_filter(z,5)
        plots['T_2m_zero'] = ax.contour(
            x, y, z, clevs_zero, colors='red',
            linewidths=2, transform=datacrs, zorder=110)

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=120)
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
    str(T_2m['init_time'])).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=T_2m['fhour'])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(T_2m['fhour'])+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(T_2m != None):
        cax=plt.axes([0.11,0.06,.86,.02])
        cb = plt.colorbar(plots['T_2m'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label(u'°C',size=20)

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
        plt.savefig(output_dir+'最低温度_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(T_2m['fhour'])+'小时'+'.png', dpi=200)
    if(output_dir == None):
        plt.show()

def draw_T2m_mslp_uv10m(t2m=None, mslp=None, uv10m=None,
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
        '10米风场, '+
        '2米 温度', 
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
    if t2m is not None:
        x, y = np.meshgrid(t2m['lon'], t2m['lat'])
        z=np.squeeze(t2m['data'])
        cmap=dk_ctables.cm_high_temperature_nws()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['t2m'] = ax.pcolormesh(
            x, y, z, 
            cmap=cmap, zorder=90,transform=datacrs,alpha=0.5)

    # draw -hPa wind bards
    if uv10m is not None:
        x, y = np.meshgrid(uv10m['lon'], uv10m['lat'])
        u = np.squeeze(uv10m['udata']) * 2.5
        v = np.squeeze(uv10m['vdata']) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=100,color ='white')

    # draw -hPa geopotential height
    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(900, 1100,2.5)
        z=gaussian_filter(np.squeeze(mslp['data']),5)
        plots['mslp'] = ax.contour(
            x, y, z, clevs_mslp, colors='black',
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
    if(t2m != None):
        cax=plt.axes([0.11,0.06,.86,.02])
        cb = plt.colorbar(plots['t2m'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Temperature at 2m Above Ground ('+u'°C'+')',size=20)

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
        plt.savefig(output_dir+'海平面气压_10米风场_2米温度_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(mslp['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()                           
    

def draw_mslp_gust10m(gust=None, mslp=None,
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
        '逐6小时最大阵风 ', 
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
    if gust is not None:
        x, y = np.meshgrid(gust['lon'], gust['lat'])
        z=np.squeeze(gust['data'])
        cmap=dk_ctables.cm_wind_speed_nws()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['gust'] = ax.pcolormesh(
            x, y, z, 
            cmap=cmap, zorder=90,transform=datacrs,alpha=0.5)

    # draw -hPa geopotential height
    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(900, 1100,2.5)
        z=gaussian_filter(np.squeeze(mslp['data']),5)
        plots['mslp'] = ax.contour(
            x, y, z, clevs_mslp, colors='black',
            linewidths=1, transform=datacrs, zorder=110)
        plt.clabel(plots['mslp'], inline=1, fontsize=15, fmt='%.0f',colors='black')

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
    if(gust != None):
        cax=plt.axes([0.11,0.06,.86,.02])
        cb = plt.colorbar(plots['gust'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('风速 (m/s)',size=20)

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
        plt.savefig(output_dir+'海平面气压_逐6小时最大风速_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(mslp['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()                           

def draw_low_level_wind(uv=None,wsp=None,
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
    
    plt.title('['+uv['model']+'] '+
    uv['lev']+' 风场, 风速', 
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

        cmap=dk_ctables.cm_wind_speed_nws()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['wsp'] = ax.pcolormesh(
            x, y, z, 
            cmap=cmap, zorder=90,transform=datacrs,alpha=0.5)


    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['udata']) * 2.5
        v = np.squeeze(uv['vdata']) * 2.5
        #plots['uv'] = ax.barbs(
        #    x, y, u, v, length=6, regrid_shape=regrid_shape,
        #    transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
        #    zorder=100)

    x, y = np.meshgrid(uv['lon'], uv['lat'])
    lw = 5*wsp['data'] / wsp['data'].max()
    plots['stream']=ax.streamplot(x, y, uv['udata'], uv['vdata'], density=2, color='r', linewidth=lw,zorder=100, transform=datacrs)

    spd_rtio=0.03
    for i in range(0,len(uv['lon'])-1,10):
        for j in range(0,len(uv['lat'])-1,10):
            ax.arrow(x[j,i], y[j,i], u[j,i]*spd_rtio, v[j,i]*spd_rtio, color='black', zorder=100, transform=datacrs,width=0.05)
            #ax.quiver(x[j,i], y[j,i], x[j,i]+u[j,i]*spd_rtio, y[j,i]+v[j,i]*spd_rtio, color='black', zorder=100, transform=datacrs)
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
    str(uv['init_time'])).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=uv['fhour'])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(uv['fhour'])+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(wsp != None):
        cax=plt.axes([0.11,0.06,.86,.02])
        cb = plt.colorbar(plots['wsp'], cax=cax, orientation='horizontal',
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
        plt.savefig(output_dir+'低层风_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(uv['fhour'])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()