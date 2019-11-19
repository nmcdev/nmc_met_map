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
    
def draw_Crosssection_Wind_Theta_e_absv(
                    cross_absv3d=None, cross_Theta_e=None, cross_u=None,cross_v=None,gh=None,
                    h_pos=None,st_point=None,ed_point=None,
                    levels=None,map_extent=(50, 150, 0, 65),
                    output_dir=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）



    initial_time = pd.to_datetime(
    str(cross_Theta_e['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=gh['forecast_period'].values[0])
    
    fig = plt.figure(1, figsize=(16., 9.))
    ax = plt.axes()
    absv_contour = ax.contourf(cross_absv3d['lon'], cross_absv3d['level'], cross_absv3d['data']*100000,
                            levels=range(-60, 60, 1), cmap=plt.cm.RdBu_r)
    absv_colorbar = fig.colorbar(absv_contour)

    # Plot potential temperature using contour, with some custom labeling
    Theta_e_contour = ax.contour(cross_Theta_e['lon'], cross_Theta_e['level'],cross_Theta_e.values,
                            levels=np.arange(250, 450, 5), colors='k', linewidths=2)

    Theta_e_contour.clabel(np.arange(250, 450, 5), fontsize=8, colors='k', inline=1,
                        inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    ax.barbs(cross_u['lon'][wind_slc_horz], cross_u['level'][wind_slc_vert],
            cross_u['t_wind'][wind_slc_vert, wind_slc_horz],    
            cross_v['n_wind'][wind_slc_vert, wind_slc_horz], color='k')
    # Adjust the y-axis to be logarithmic
    ax.set_yscale('symlog')
    ax.set_yticklabels(np.arange(levels[0], levels[-1], -100))
    ax.set_ylim(levels[0], levels[-1])
    ax.set_yticks(np.arange(levels[0], levels[-1], -100))

    # Define the CRS and inset axes
    data_crs = ccrs.PlateCarree()
    ax_inset = fig.add_axes(h_pos, projection=data_crs)
    ax_inset.set_extent(map_extent, crs=data_crs)
    # Plot geopotential height at 500 hPa using xarray's contour wrapper
    ax_inset.contour(gh['lon'], gh['lat'], np.squeeze(gh['data']),
                    levels=np.arange(500, 600, 4), cmap='inferno')
    # Plot the path of the cross section
    endpoints = data_crs.transform_points(ccrs.Geodetic(),
                                        *np.vstack([st_point, ed_point]).transpose()[::-1])
    ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
    ax_inset.plot(cross_u['lon'], cross_u['lat'], c='k', zorder=2)
    # Add geographic features
    ax_inset.coastlines()
    utl.add_china_map_2cartopy_public(
            ax_inset, name='province', edgecolor='black', lw=0.8, zorder=105)
    # Set the titles and axes labels
    ax_inset.set_title('')

    ax.set_title('相当位温, 绝对涡度, 水平风场', loc='right', fontsize=25)
    ax.set_ylabel('Pressure (hPa)')
    ax.set_xlabel('Longitude')
    absv_colorbar.set_label('Absolute Vorticity (dimensionless)')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    bax=fig.add_axes([0.10,0.88,.25,.07],facecolor='#FFFFFFCC')
    bax.axis('off')
    #bax.set_yticks([])
    #bax.set_xticks([])
    bax.axis([0, 10, 0, 10])        
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=11)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=11)
    plt.text(2.5, 2.5,'预报时效: '+str(int(gh['forecast_period'].values[0]))+'小时',size=11)
    plt.text(2.5, 0.5,'www.nmc.cn',size=11)

    utl.add_logo_extra_in_axes(pos=[0.1,0.88,.07,.07],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'相当位温_绝对涡度_水平风场_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(int(gh['forecast_period'].values[0]))+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show() 


def draw_Crosssection_Wind_Theta_e_RH(
                    cross_rh=None, cross_Theta_e=None, cross_u=None,cross_v=None,gh=None,
                    h_pos=None,st_point=None,ed_point=None,
                    levels=None,map_extent=(50, 150, 0, 65),
                    output_dir=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）



    initial_time = pd.to_datetime(
    str(cross_Theta_e['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=gh['forecast_period'].values[0])
    
    fig = plt.figure(1, figsize=(16., 9.))
    ax = plt.axes()
    rh_contour = ax.contourf(cross_rh['lon'], cross_rh['level'], cross_rh['data'],
                            levels=np.arange(0, 106, 5), cmap='YlGnBu')
    rh_colorbar = fig.colorbar(rh_contour)

    # Plot potential temperature using contour, with some custom labeling
    Theta_e_contour = ax.contour(cross_Theta_e['lon'], cross_Theta_e['level'],cross_Theta_e.values,
                            levels=np.arange(250, 450, 5), colors='k', linewidths=2)

    Theta_e_contour.clabel(np.arange(250, 450, 5), fontsize=8, colors='k', inline=1,
                        inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    ax.barbs(cross_u['lon'][wind_slc_horz], cross_u['level'][wind_slc_vert],
            cross_u['t_wind'][wind_slc_vert, wind_slc_horz],    
            cross_v['n_wind'][wind_slc_vert, wind_slc_horz], color='k')
    # Adjust the y-axis to be logarithmic
    ax.set_yscale('symlog')
    ax.set_yticklabels(np.arange(levels[0], levels[-1], -100))
    ax.set_ylim(levels[0], levels[-1])
    ax.set_yticks(np.arange(levels[0], levels[-1], -100))

    # Define the CRS and inset axes
    data_crs = ccrs.PlateCarree()
    ax_inset = fig.add_axes(h_pos, projection=data_crs)
    ax_inset.set_extent(map_extent, crs=data_crs)
    # Plot geopotential height at 500 hPa using xarray's contour wrapper
    ax_inset.contour(gh['lon'], gh['lat'], np.squeeze(gh['data']),
                    levels=np.arange(500, 600, 4), cmap='inferno')
    # Plot the path of the cross section
    endpoints = data_crs.transform_points(ccrs.Geodetic(),
                                        *np.vstack([st_point, ed_point]).transpose()[::-1])
    ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
    ax_inset.plot(cross_u['lon'], cross_u['lat'], c='k', zorder=2)
    # Add geographic features
    ax_inset.coastlines()
    utl.add_china_map_2cartopy_public(
            ax_inset, name='province', edgecolor='black', lw=0.8, zorder=105)
    # Set the titles and axes labels
    ax_inset.set_title('')

    ax.set_title('相当位温, 相对湿度, 水平风场', loc='right', fontsize=25)
    ax.set_ylabel('Pressure (hPa)')
    ax.set_xlabel('Longitude')
    rh_colorbar.set_label('Relative Humidity')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    bax=fig.add_axes([0.10,0.88,.25,.07],facecolor='#FFFFFFCC')
    bax.axis('off')
    #bax.set_yticks([])
    #bax.set_xticks([])
    bax.axis([0, 10, 0, 10])        
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=11)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=11)
    plt.text(2.5, 2.5,'预报时效: '+str(int(gh['forecast_period'].values[0]))+'小时',size=11)
    plt.text(2.5, 0.5,'www.nmc.cn',size=11)

    utl.add_logo_extra_in_axes(pos=[0.1,0.88,.07,.07],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'相当位温_相对湿度_水平风场_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(int(gh['forecast_period'].values[0]))+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()         

def draw_Crosssection_Wind_Theta_e_Qv(
                    cross_Qv=None, cross_Theta_e=None, cross_u=None,cross_v=None,gh=None,
                    h_pos=None,st_point=None,ed_point=None,
                    levels=None,map_extent=(50, 150, 0, 65),
                    output_dir=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）



    initial_time = pd.to_datetime(
    str(cross_Theta_e['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=gh['forecast_period'].values[0])
    
    fig = plt.figure(1, figsize=(16., 9.))
    ax = plt.axes()
    Qv_contour = ax.contourf(cross_Qv['lon'], cross_Qv['level'], cross_Qv['data'],
                            levels=np.arange(0, 20, 2), cmap='YlGnBu')
    Qv_colorbar = fig.colorbar(Qv_contour)

    # Plot potential temperature using contour, with some custom labeling
    Theta_e_contour = ax.contour(cross_Theta_e['lon'], cross_Theta_e['level'],cross_Theta_e.values,
                            levels=np.arange(250, 450, 5), colors='k', linewidths=2)

    Theta_e_contour.clabel(np.arange(250, 450, 5), fontsize=8, colors='k', inline=1,
                        inline_spacing=8, fmt='%i', rightside_up=True, use_clabeltext=True)

    wind_slc_vert = list(range(0, len(levels), 1))
    wind_slc_horz = slice(5, 100, 5)
    ax.barbs(cross_u['lon'][wind_slc_horz], cross_u['level'][wind_slc_vert],
            cross_u['t_wind'][wind_slc_vert, wind_slc_horz],    
            cross_v['n_wind'][wind_slc_vert, wind_slc_horz], color='k')
    # Adjust the y-axis to be logarithmic
    ax.set_yscale('symlog')
    ax.set_yticklabels(np.arange(levels[0], levels[-1], -100))
    ax.set_ylim(levels[0], levels[-1])
    ax.set_yticks(np.arange(levels[0], levels[-1], -100))

    # Define the CRS and inset axes
    data_crs = ccrs.PlateCarree()
    ax_inset = fig.add_axes(h_pos, projection=data_crs)
    ax_inset.set_extent(map_extent, crs=data_crs)
    # Plot geopotential height at 500 hPa using xarray's contour wrapper
    ax_inset.contour(gh['lon'], gh['lat'], np.squeeze(gh['data']),
                    levels=np.arange(500, 600, 4), cmap='inferno')
    # Plot the path of the cross section
    endpoints = data_crs.transform_points(ccrs.Geodetic(),
                                        *np.vstack([st_point, ed_point]).transpose()[::-1])
    ax_inset.scatter(endpoints[:, 0], endpoints[:, 1], c='k', zorder=2)
    ax_inset.plot(cross_u['lon'], cross_u['lat'], c='k', zorder=2)
    # Add geographic features
    ax_inset.coastlines()
    utl.add_china_map_2cartopy_public(
            ax_inset, name='province', edgecolor='black', lw=0.8, zorder=105)
    # Set the titles and axes labels
    ax_inset.set_title('')

    ax.set_title('相当位温, 绝对湿度, 水平风场', loc='right', fontsize=25)
    ax.set_ylabel('Pressure (hPa)')
    ax.set_xlabel('Longitude')
    Qv_colorbar.set_label('Specific Humidity')

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    bax=fig.add_axes([0.10,0.88,.25,.07],facecolor='#FFFFFFCC')
    bax.axis('off')
    #bax.set_yticks([])
    #bax.set_xticks([])
    bax.axis([0, 10, 0, 10])        
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=11)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=11)
    plt.text(2.5, 2.5,'预报时效: '+str(int(gh['forecast_period'].values[0]))+'小时',size=11)
    plt.text(2.5, 0.5,'www.nmc.cn',size=11)

    utl.add_logo_extra_in_axes(pos=[0.1,0.88,.07,.07],which='nmc', size='Xlarge')

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'相当位温_绝对湿度_水平风场_预报_'+
        '起报时间_'+initial_time.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(int(gh['forecast_period'].values[0]))+'小时'+'.png', dpi=200)
    
    if(output_dir == None):
        plt.show()                 