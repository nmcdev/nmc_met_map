# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import nmc_met_map.lib.utility as utl
from datetime import datetime, timedelta
import pandas as pd
import locale
import sys
import nmc_met_graphics.cmap.ctables as dk_ctables

def draw_wind_rh_according_to_4D_data(sta_fcs_fcst=None,zd_fcst_obs=None,
                    fcst_info=None,
                    map_extent=(50, 150, 0, 65),bkgd_type='satellite',bkgd_level=None,
                    draw_zd=True,
                    output_dir=None):

# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
# set figure
    plt.figure(figsize=(16,9))

    plotcrs = ccrs.PlateCarree()
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    if(bkgd_type == 'satellite'):
        c_city_names='w'
        c_sta_fcst='w'
        c_tile_str='白色'
    else:
        c_city_names='black'
        c_sta_fcst='black'
        c_tile_str='黑色'

    datacrs = ccrs.PlateCarree()

    ax.set_extent(map_extent, crs=datacrs)

# draw data
    plots = {}

    if(bkgd_type=='satellite'):
        request = utl.TDT_img() #卫星图像
    if(bkgd_type=='terrain'):
        request = utl.TDT_ter() #卫星图像
    if(bkgd_type=='road'):
        request = utl.TDT() #卫星图像

    ax.add_image(request, bkgd_level)# level=10 缩放等级 

    #cmap=dk_ctables.cm_thetae()
    plots['t2m'] = ax.scatter(sta_fcs_fcst['lon'], sta_fcs_fcst['lat'], s=1400, c='white',alpha=1,zorder=120)
    cmap,norm=dk_ctables.cm_relative_humidity_nws()
    cmap.set_under(color=[0,0,0,0],alpha=0.0)
    plots['t2m'] = ax.scatter(sta_fcs_fcst['lon'], sta_fcs_fcst['lat'], s=1300, c=sta_fcs_fcst['RH'], vmin=0, vmax=100,
        cmap=cmap,alpha=1,zorder=120)
        
    for ista in range(0,len(sta_fcs_fcst['lon'])):
        city_names=sta_fcs_fcst['name'][ista]
        ax.text(sta_fcs_fcst['lon'][ista]-0.001,sta_fcs_fcst['lat'][ista],city_names+'  ', family='SimHei',ha='right',va='center',size=20,color=c_city_names,zorder=140)
        ax.text(sta_fcs_fcst['lon'][ista],sta_fcs_fcst['lat'][ista],'%i'%sta_fcs_fcst['RH'][ista], 
            family='SimHei',size=20,color='white',zorder=140,ha='center',va='center')
    plots['uv'] = ax.barbs(
        np.array(sta_fcs_fcst['lon'])-0.001, np.array(sta_fcs_fcst['lat']), sta_fcs_fcst['U'], sta_fcs_fcst['V'],barb_increments={'half':2,'full':4,'flag':20}, length=12, linewidth=6,
        transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.01),
        zorder=130,color ='white')

    plots['uv'] = ax.barbs(
        np.array(sta_fcs_fcst['lon'])-0.001, np.array(sta_fcs_fcst['lat']), sta_fcs_fcst['U'], sta_fcs_fcst['V'],
        barb_increments={'half':2,'full':4,'flag':20}, length=12, linewidth=3,
        transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.01),
        zorder=130,color ='black')

    if(draw_zd is True):
        plots['uv'] = ax.barbs(
            zd_fcst_obs['lon'],zd_fcst_obs['lat'], zd_fcst_obs['U'], zd_fcst_obs['V'],barb_increments={'half':2,'full':4,'flag':20}, length=7, linewidth=2,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.01),
            zorder=100,color =c_sta_fcst,alpha=0.7)

        if(zd_fcst_obs['obs_valid'] is True):
            plots['uv'] = ax.barbs(
            zd_fcst_obs['lon'],zd_fcst_obs['lat'], zd_fcst_obs['U_obs'], zd_fcst_obs['V_obs'],
            barb_increments={'half':2,'full':4,'flag':20}, length=8, linewidth=1.5,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.01),
            zorder=100,color ='red',alpha=0.7)

#additional information
    plt.title('基于EC模式降尺度预报 '+
    '10米风（红色实况，'+c_tile_str+'预报）, '+
    '相对湿度(圆形填色及数字)', 
        loc='left', fontsize=20)

    l, b, w, h = ax.get_position().bounds

    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initial_time = pd.to_datetime(
    str(fcst_info['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=fcst_info['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(fcst_info['forecast_period'].values))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add logo
    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # add color bar
    cax=plt.axes([0.25,0.06,.5,.02])
    cb = plt.colorbar(plots['t2m'], cax=cax, orientation='horizontal')
    cb.ax.tick_params(labelsize='x-large')                      
    cb.set_label('相对湿度 (%)',size=20)

# show figure
    if(output_dir != None):
        plt.savefig(output_dir+'BSEP_NMC_RFFC_ECMWF_EME_ASC_LNO_P9_'+
        initial_time.strftime("%Y%m%d%H")+
        '00'+str(int(fcst_info['forecast_period'].values[0])).zfill(3)+'03.jpg', dpi=200,bbox_inches='tight')
        plt.close()

    if(output_dir == None):
        plt.show()


def draw_wind_temp_according_to_4D_data(sta_fcs_fcst=None,zd_fcst_obs=None,
                    fcst_info=None,
                    map_extent=(50, 150, 0, 65),bkgd_type='satellite',bkgd_level=None,
                    draw_zd=True,
                    output_dir=None):

# set font
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
# set figure
    plt.figure(figsize=(16,9))

    plotcrs = ccrs.PlateCarree()
    ax = plt.axes([0.01,0.1,.98,.84], projection=plotcrs)
    if(bkgd_type == 'satellite'):
        c_city_names='black'
        c_sta_fcst='black'
        c_tile_str='白色'
    else:
        c_city_names='black'
        c_sta_fcst='black'
        c_tile_str='黑色'

    datacrs = ccrs.PlateCarree()

    ax.set_extent(map_extent, crs=datacrs)

# draw data
    plots = {}

    if(bkgd_type=='satellite'):
        request = utl.TDT_img() #卫星图像
    if(bkgd_type=='terrain'):
        request = utl.TDT_ter() #卫星图像
    if(bkgd_type=='road'):
        request = utl.TDT() #卫星图像

    ax.add_image(request, bkgd_level)# level=10 缩放等级 

    #cmap=dk_ctables.cm_thetae()
    plots['t2m'] = ax.scatter(sta_fcs_fcst['lon'], sta_fcs_fcst['lat'], s=1900, c='white',alpha=1,zorder=120)
    cmap=dk_ctables.cm_temp()
    cmap.set_under(color=[0,0,0,0],alpha=0.0)
    plots['t2m'] = ax.scatter(sta_fcs_fcst['lon'], sta_fcs_fcst['lat'], s=1700, c=sta_fcs_fcst['TMP'], vmin=-40, vmax=40,
        cmap=cmap,alpha=1,zorder=120)
        
    for ista in range(0,len(sta_fcs_fcst['lon'])):
        city_names=sta_fcs_fcst['name'][ista]
        ax.text(sta_fcs_fcst['lon'][ista]-0.001,sta_fcs_fcst['lat'][ista],city_names+'  ', family='SimHei',ha='right',va='center',size=24,color=c_city_names,zorder=140)
        ax.text(sta_fcs_fcst['lon'][ista],sta_fcs_fcst['lat'][ista],'%i'%sta_fcs_fcst['TMP'][ista], 
            family='SimHei',size=24,color='white',zorder=140,ha='center',va='center')
    plots['uv'] = ax.barbs(
        np.array(sta_fcs_fcst['lon'])-0.001, np.array(sta_fcs_fcst['lat']), sta_fcs_fcst['U'], sta_fcs_fcst['V'],barb_increments={'half':2,'full':4,'flag':20}, length=12, linewidth=6,
        transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.01),
        zorder=130,color ='white')

    plots['uv'] = ax.barbs(
        np.array(sta_fcs_fcst['lon'])-0.001, np.array(sta_fcs_fcst['lat']), sta_fcs_fcst['U'], sta_fcs_fcst['V'],
        barb_increments={'half':2,'full':4,'flag':20}, length=12, linewidth=3,
        transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.01),
        zorder=130,color ='black')

    if(draw_zd is True):
        plots['uv'] = ax.barbs(
            zd_fcst_obs['lon'],zd_fcst_obs['lat'], zd_fcst_obs['U'], zd_fcst_obs['V'],barb_increments={'half':2,'full':4,'flag':20}, length=10, linewidth=2.6,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.01),
            zorder=100,color =c_sta_fcst,alpha=1)

        if(zd_fcst_obs['obs_valid'] is True):
            plots['uv'] = ax.barbs(
            zd_fcst_obs['lon'],zd_fcst_obs['lat'], zd_fcst_obs['U_obs'], zd_fcst_obs['V_obs'],
            barb_increments={'half':2,'full':4,'flag':20}, length=10, linewidth=2,
            transform=datacrs, fill_empty=False, sizes=dict(emptybarb=0.01),
            zorder=100,color ='red',alpha=1)

#additional information
    plt.title('基于EC模式降尺度预报 '+
    '10米风（红色实况，'+c_tile_str+'预报）, '+
    '温度(圆形填色及数字)', 
        loc='left', fontsize=20)

    l, b, w, h = ax.get_position().bounds

    bax=plt.axes([l,b+h-0.1,.25,.1],facecolor='#FFFFFFCC')
    bax.set_yticks([])
    bax.set_xticks([])
    bax.axis([0, 10, 0, 10])

    initial_time = pd.to_datetime(
    str(fcst_info['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    fcst_time=initial_time+timedelta(hours=fcst_info['forecast_period'].values[0])
    #发布时间
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 5,'预报时间: '+fcst_time.strftime("%Y年%m月%d日%H时"),size=15)
    plt.text(2.5, 2.5,'预报时效: '+str(int(fcst_info['forecast_period'].values))+'小时',size=15)
    plt.text(2.5, 0.5,'www.nmc.cn',size=15)

    # add logo
    utl.add_logo_extra_in_axes(pos=[l-0.02,b+h-0.1,.1,.1],which='nmc', size='Xlarge')

    # add color bar
    cax=plt.axes([0.25,0.06,.5,.02])
    cb = plt.colorbar(plots['t2m'], cax=cax, orientation='horizontal')
    cb.ax.tick_params(labelsize='x-large')                      
    cb.set_label('温度 ($^\circ$C)',size=20)

# show figure
    if(output_dir != None):
        plt.savefig(output_dir+'BSEP_NMC_RFFC_ECMWF_EME_ASC_LNO_P9_'+
        initial_time.strftime("%Y%m%d%H")+
        '00'+str(int(fcst_info['forecast_period'].values[0])).zfill(3)+'03.jpg', dpi=200,bbox_inches='tight')
        plt.close()

    if(output_dir == None):
        plt.show()
