# _*_ coding: utf-8 _*_

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from nmc_met_graphics.plot.china_map import add_china_map_2cartopy
import nmc_met_graphics.cmap.cm as cm_collected
from nmc_met_graphics.plot.util import add_model_title
import nmc_met_map.lib.utility as utl
from datetime import datetime, timedelta
import pandas as pd
import locale
import sys
from matplotlib.colors import BoundaryNorm,ListedColormap
import nmc_met_graphics.cmap.ctables as dk_ctables
from scipy.ndimage import gaussian_filter
import matplotlib.patheffects as mpatheffects

def draw_T_2m(T_2m=None,T_type='Tmx',
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

    # define return plots
    plots = {}
    if T_2m is not None:
        x, y = np.meshgrid(T_2m['lon'], T_2m['lat'])
        z=np.squeeze(T_2m['data'])
        cmap=dk_ctables.cm_temp()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['T_2m'] = ax.pcolormesh(
            x,y,z,
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.5, vmin=-45, vmax=45)

        z=gaussian_filter(z,5)
        plots['T_2m_zero'] = ax.contour(
            x, y, z, levels=[0], colors='#232B99',
            linewidths=2, transform=datacrs, zorder=2)
        cl_zero=plt.clabel(plots['T_2m_zero'], inline=1, fontsize=15, fmt='%i',colors='#232B99')
        for t in cl_zero:
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'),
                       mpatheffects.Normal()])

        plots['T_2m_35'] = ax.contour(
            x, y, z, levels=[35,37,40], colors=['#FF8F00','#FF6200','#FF0000'],
            linewidths=2, transform=datacrs, zorder=2)
        cl_35=plt.clabel(plots['T_2m_35'], inline=1, fontsize=15, fmt='%i',colors='#FF0000')
        for t in cl_35:
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'),
                       mpatheffects.Normal()])


    plt.title('['+T_2m.attrs['model']+']'+' '+T_2m.attrs['title'], 
        loc='left', fontsize=30)

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=4,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=4)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=4)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=4,alpha=0.5)

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=5)
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
    str(T_2m.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=T_2m.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(T_2m.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(T_2m != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['T_2m'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label(u'°C',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    #if(map_extent2[1]-map_extent2[0] < 25):
    #    small_city=True
    #if city:
    utl.add_city_and_number_on_map(ax,data=T_2m,map_extent=map_extent2,transform=datacrs,zorder=6,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'最低温度_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(T_2m.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200)
    if(output_dir == None):
        plt.show()

def draw_dT_2m(dT_2m=None,T_type='Tmx',
            map_extent=(50, 150, 0, 65),
            regrid_shape=20,
            add_china=True,city=True,south_China_sea=True,
            output_dir=None,Global=False):
# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

# set figure
    fig=plt.figure(figsize=(16,9))

    if(Global == True):
        plotcrs = ccrs.Robinson(central_longitude=115.)
    else:
        plotcrs = ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2., 
            central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])
 
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    datacrs = ccrs.PlateCarree()
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)

    # define return plots
    plots = {}
    if dT_2m is not None:
        x, y = np.meshgrid(dT_2m['lon'], dT_2m['lat'])
        z=np.squeeze(dT_2m['data'])
        cmap=utl.linearized_ncl_cmap('hotcold_18lev')
        plots['T_2m'] = ax.pcolormesh(
            x,y,z,
            cmap=cmap, zorder=1,transform=datacrs,alpha=1, vmin=-16, vmax=16)

        z=gaussian_filter(z,5)
        cmap=utl.linearized_ncl_cmap('BlRe')
        clevs=[-16,-12,-10,-8,-6,6,8,10,12,16]
        plots['T_2m_contour'] = ax.contour(
            x,y,z,levels=clevs,
            cmap=cmap, zorder=3,transform=datacrs,alpha=0.5, vmin=-16, vmax=16)
        clev_colors = []
        for iclev in clevs:
            per_color=utl.get_part_clev_and_cmap(cmap=cmap,clev_range=[-16,16],clev_slt=iclev)
            clev_colors.append(np.squeeze(per_color[:]))

        cl=plt.clabel(plots['T_2m_contour'], inline=1, fontsize=15, fmt='%i',colors=clev_colors)
        for t in cl:
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='#D9D9D9'),
                       mpatheffects.Normal()])
                       
        '''
        z=gaussian_filter(z,5)
        plots['T_2m_zero'] = ax.contour(
            x, y, z, levels=[0], colors='#232B99',
            linewidths=2, transform=datacrs, zorder=2)
        cl_zero=plt.clabel(plots['T_2m_zero'], inline=1, fontsize=15, fmt='%i',colors='#232B99')
        for t in cl_zero:
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'),
                       mpatheffects.Normal()])

        plots['T_2m_35'] = ax.contour(
            x, y, z, levels=[35,37,40], colors=['#FF8F00','#FF6200','#FF0000'],
            linewidths=2, transform=datacrs, zorder=2)
        cl_35=plt.clabel(plots['T_2m_35'], inline=1, fontsize=15, fmt='%i',colors='#FF0000')
        for t in cl_35:
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'),
                       mpatheffects.Normal()])
        '''

    plt.title('['+dT_2m.attrs['model']+']'+' '+dT_2m.attrs['title'], 
        loc='left', fontsize=30)

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=4,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=4)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=4)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=4,alpha=0.5)

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=5)
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
    str(dT_2m.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=dT_2m.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(dT_2m.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(dT_2m != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['T_2m'], cax=cax, orientation='horizontal',extend='both',
        ticks=[-16,-12,-10,-8,-6,-4,0,4,6,8,10,12,16])
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label(u'°C',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    #if(map_extent2[1]-map_extent2[0] < 25):
    #    small_city=True
    #if city:
    utl.add_city_and_number_on_map(ax,data=dT_2m,map_extent=map_extent2,transform=datacrs,zorder=6,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'最低温度_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(dT_2m.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200)
    if(output_dir == None):
        plt.show()
        #return(fig)       

def draw_T2m_mslp_uv10m(t2m=None, mslp=None, uv10m=None,
                    map_extent=(50, 150, 0, 65),
                    regrid_shape=20,
                    add_china=True,city=True,south_China_sea=True,
                    output_dir=None,Global=False):

# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

# draw figure
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
    if t2m is not None:
        x, y = np.meshgrid(t2m['lon'], t2m['lat'])
        z=np.squeeze(t2m['data'])
        cmap=dk_ctables.cm_high_temperature_nws()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['t2m'] = ax.pcolormesh(
            x, y, z, 
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)

    if uv10m is not None:
        x, y = np.meshgrid(uv10m['lon'].values, uv10m['lat'].values)
        u = np.squeeze(uv10m['u10m'].values) * 2.5
        v = np.squeeze(uv10m['v10m'].values) * 2.5
        plots['uv'] = ax.barbs(
            x, y, u, v, length=6, regrid_shape=regrid_shape,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.05),
            zorder=2,color ='white')

    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(900, 1100,2.5)
        z=gaussian_filter(np.squeeze(mslp['data']),5)
        plots['mslp'] = ax.contour(
            x, y, z, clevs_mslp, colors='black',
            linewidths=1, transform=datacrs, zorder=3)
        cl=ax.clabel(plots['mslp'], inline=1, fontsize=20, fmt='%.0f',colors='black')

#additional information
    plt.title('['+mslp.attrs['model']+'] '+
        '海平面气压, '+
        '10米风场, '+
        '2米 温度', 
        loc='left', fontsize=30)
    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=4,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=4)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=4)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=4,alpha=0.5)

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=5)
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
    str(mslp['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=mslp.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(mslp.coords['forecast_period'].values[0])+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(t2m != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['t2m'], cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('Temperature at 2m Above Ground ('+u'°C'+')',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=6,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'海平面气压_10米风场_2米温度_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(mslp.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()                           
    

def draw_mslp_gust10m(gust=None, mslp=None,
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

#draw data
    plots = {}
    if gust is not None:
        x, y = np.meshgrid(gust['lon'], gust['lat'])
        z=np.squeeze(gust['data'].values)
        cmap=dk_ctables.cm_wind_speed_nws()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        z[z<7.9]=np.nan
        plots['gust'] = ax.pcolormesh(
            x, y, z,
            cmap=cmap,vmin=7.9,vmax=65,
            zorder=1,transform=datacrs,alpha=0.5)

    # draw -hPa geopotential height
    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(900, 1100,2.5)
        z=gaussian_filter(np.squeeze(mslp['data']),5)
        plots['mslp'] = ax.contour(
            x, y, z, clevs_mslp, colors='black',
            linewidths=1, transform=datacrs, zorder=2)
        plt.clabel(plots['mslp'], inline=1, fontsize=15, fmt='%.0f',colors='black')

#additional information
    plt.title('['+mslp.attrs['model']+'] '+
        '海平面气压, '+
        '逐'+'%i'%gust.attrs['t_gap']+'小时最大阵风 ', 
        loc='left', fontsize=30)

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
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=4)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    #utl.add_cartopy_background(ax,name='RD')
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
    if(gust != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['gust'], cax=cax, orientation='horizontal',extend='max',
            ticks=[8.0,10.8,13.9,17.2,20.8,24.5,28.5,32.7,37,41.5,46.2,51.0,56.1,61.3])
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('风速 (m/s)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=5,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'海平面气压_逐6小时最大风速_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(mslp.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()                           

def draw_mslp_gust10m_uv10m(gust=None, mslp=None,uv10m=None,
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

#draw data
    plots = {}
    if gust is not None:
        x, y = np.meshgrid(gust['lon'], gust['lat'])
        z=np.squeeze(gust['data'].values)
        cmap=dk_ctables.cm_wind_speed_nws()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        z[z<7.9]=np.nan
        plots['gust'] = ax.pcolormesh(
            x, y, z,
            cmap=cmap,vmin=7.9,vmax=65,
            zorder=1,transform=datacrs,alpha=0.5)

    ax.quiver(x, y, np.squeeze(uv10m['u10m'].values), np.squeeze(uv10m['v10m'].values),
         transform=datacrs,regrid_shape=40,width=0.001)

    if mslp is not None:
        x, y = np.meshgrid(mslp['lon'], mslp['lat'])
        clevs_mslp = np.arange(900, 1100,2.5)
        z=gaussian_filter(np.squeeze(mslp['data']),5)
        plots['mslp'] = ax.contour(
            x, y, z, clevs_mslp, colors='black',
            linewidths=1, transform=datacrs, zorder=2,alpha=0.5)
        cl=plt.clabel(plots['mslp'], inline=1, fontsize=15, fmt='%.1f',colors='black')
        for t in cl:
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'),
                       mpatheffects.Normal()])

#additional information
    plt.title('['+mslp.attrs['model']+'] '+
        '海平面气压, '+
        '逐'+'%i'%gust.attrs['t_gap']+'小时10米最大阵风和10米平均风', 
        loc='left', fontsize=30)

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
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=4)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    #utl.add_cartopy_background(ax,name='RD')
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
    if(gust != None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['gust'], cax=cax, orientation='horizontal',extend='max',
            ticks=[8.0,10.8,13.9,17.2,20.8,24.5,28.5,32.7,37,41.5,46.2,51.0,56.1,61.3])
        cb.ax.tick_params(labelsize='x-large')                      
        cb.set_label('风速 (m/s)',size=20)

    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=5,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'海平面气压_逐6小时最大风速_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(mslp.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()                           

def draw_low_level_wind(uv=None,
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
    
    # define return plots
    plots = {}
    # draw mean sea level pressure
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        wsp=np.squeeze((uv['u'].values**2+uv['v'].values**2)**0.5)
        z=wsp

        cmap=dk_ctables.cm_wind_speed_nws()
        cmap.set_under(color=[0,0,0,0],alpha=0.0)
        plots['wsp'] = ax.pcolormesh(
            x, y, z, 
            cmap=cmap, zorder=1,transform=datacrs,alpha=0.5)

    # draw -hPa wind bards
    if uv is not None:
        x, y = np.meshgrid(uv['lon'], uv['lat'])
        u = np.squeeze(uv['u'].values)*2.5
        v = np.squeeze(uv['v'].values)*2.5

    x, y = np.meshgrid(uv['lon'], uv['lat'])
    lw = 5*wsp / wsp.max()
    plots['stream']=ax.streamplot(x, y, u, v, density=2, color='r', linewidth=lw,zorder=100, transform=datacrs)

    spd_rtio=0.03
    for i in range(0,len(uv['lon'])-1,10):
        for j in range(0,len(uv['lat'])-1,10):
            ax.arrow(x[j,i], y[j,i], u[j,i]*spd_rtio, v[j,i]*spd_rtio, color='black', zorder=100, transform=datacrs,width=0.05)

    plt.title('['+uv.attrs['model']+'] '+
    uv.attrs['level']+' 风场, 风速', 
        loc='left', fontsize=30)

    #adapt to the map ratio
    map_extent2=utl.adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)
    #adapt to the map ratio

    ax.add_feature(cfeature.OCEAN)
    utl.add_china_map_2cartopy_public(
        ax, name='coastline', edgecolor='gray', lw=0.8, zorder=2,alpha=0.5)
    if add_china:
        utl.add_china_map_2cartopy_public(
            ax, name='province', edgecolor='gray', lw=0.5, zorder=2)
        utl.add_china_map_2cartopy_public(
            ax, name='nation', edgecolor='black', lw=0.8, zorder=2)
        utl.add_china_map_2cartopy_public(
            ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=2,alpha=0.5)

    # grid lines
    gl = ax.gridlines(
        crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=3)
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
    str(uv.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initTime+timedelta(hours=uv.coords['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initTime.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(uv.coords['forecast_period'].values[0]))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add color bar
    if(wsp is not None):
        cax=plt.axes([l,b-0.04,w,.02])
        cb = plt.colorbar(plots['wsp'], cax=cax, orientation='horizontal',
                      extend='max',extendrect=False)
        cb.ax.tick_params(labelsize='x-large') 
        cb.set_label('(m/s)',size=20)
    # add south China sea
    if south_China_sea:
        utl.add_south_China_sea(pos=[l+w-0.091,b,.1,.2])

    small_city=False
    if(map_extent2[1]-map_extent2[0] < 25):
        small_city=True
    if city:
        utl.add_city_on_map(ax,map_extent=map_extent2,transform=datacrs,zorder=4,size=13,small_city=small_city)

    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'低层风_预报_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(uv.coords['forecast_period'].values[0])+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()