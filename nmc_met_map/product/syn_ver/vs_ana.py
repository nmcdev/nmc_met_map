# _*_ coding: utf-8 _*_

# Copyright (c) 2019 NMC Developers.
# Distributed under the terms of the GPL V3 License.

"""
Map design before drawing
"""

import numpy as np
import matplotlib.pyplot as plt
from nmc_met_map.lib.utility import add_city_on_map
from datetime import datetime, timedelta
import pandas as pd
import nmc_met_map.lib.utility as utl
import os
from scipy.ndimage import gaussian_filter
import nmc_met_map.graphics2 as GF

def draw_compare_gh_uv(gh_ana=None, uv_ana=None,
                        gh_fcst=None, uv_fcst=None,
                        map_extent=[50, 150, 0, 65],
                        regrid_shape=25,
                        add_china=True,city=True,south_China_sea=True,add_background=True,
                        output_dir=None):
                        
    initTime = pd.to_datetime(gh_fcst.coords['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    fhour = int(gh_fcst['forecast_period'].values[0])
    fcstTime = initTime + timedelta(hours=fhour)

    title = '[{}] {}高度场和{}风场预报检验'.format(
        gh_fcst.attrs['model_name'],str(int(gh_fcst['level'].values[0]))+'hPa',
        str(int(uv_fcst['level'].values[0]))+'hPa')
    
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n分析时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(initTime, fcstTime, fhour)

    fig, ax, map_extent = GF.pallete_set.Horizontal_Pallete((18, 9),map_extent=map_extent, 
                        title=title, forcast_info=forcast_info,info_zorder=4,
                        add_china=add_china, add_city=city, add_background=add_background,
                        south_China_sea=south_China_sea)

    contour_gh_ana=GF.draw_method.gh_contour(ax, gh_ana['lon'].values, gh_ana['lat'].values, np.squeeze(gh_ana['data'].values),zorder=1)
    contour_gh_fcst=GF.draw_method.gh_contour(ax, gh_fcst['lon'].values, gh_fcst['lat'].values, np.squeeze(gh_fcst['data'].values),zorder=2,colors='blue')
    handles=[contour_gh_ana.collections[0],contour_gh_fcst.collections[0]]
    labels=['分析场','预报场']
    ax.legend(handles ,labels,fontsize=20,loc='lower left')
    barb_uv_ana=GF.draw_method.wind_barbs(ax,
                uv_ana['lon'].values,uv_ana['lat'].values,
                uv_ana['u'].values.squeeze(),uv_ana['v'].values.squeeze(),zorder=3,regrid_shape=regrid_shape)
    barb_uv_fcst=GF.draw_method.wind_barbs(ax,
                uv_fcst['lon'].values,uv_fcst['lat'].values,
                uv_fcst['u'].values.squeeze(),uv_fcst['v'].values.squeeze().squeeze(),zorder=4,regrid_shape=regrid_shape,color='blue')
    # if(city is True):
    #     utl.add_city_on_map(ax,map_extent=map_extent,zorder=5)

    l, b, w, h = ax.get_position().bounds
    if output_dir:
        png_name = '{0:}位势高度_{1:}风场_检验_{2:%Y}年{2:%m}月{2:%d}日{2:%H}时分析'.format(str(int(gh_ana['levels'].values[0])),
            initTime)+'{}小时时效最高温度'.format(str(gh_fcst['data'].attrs['']))
        plt.savefig(output_dir+png_name, idpi=300, bbox_inches='tight')
    else:
        plt.show()
