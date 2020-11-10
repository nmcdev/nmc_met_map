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
import nmc_met_graphics.cmap.cm as dk_ctables2
import nmc_met_graphics.cmap.wrf as wrf_ctables
import nmc_met_map.lib.utility as utl
import nmc_met_graphics.mask as dk_mask
import os
from scipy.ndimage import gaussian_filter
import matplotlib.patheffects as path_effects
import cartopy.io.img_tiles as cimg
from matplotlib.font_manager import FontProperties
import matplotlib.patches as mpatches

def Horizontal_Pallete(figsize=(16, 9), plotcrs=ccrs.PlateCarree(), datacrs=ccrs.PlateCarree(),map_extent=(60, 145, 15, 55), title='', forcast_info='',
                       add_china=True, add_city=False, add_background=True, south_China_sea=True,info_zorder=10):
    
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):
        locale.setlocale(locale.LC_CTYPE, 'chinese')

    fig = plt.figure(figsize=figsize)
    if(plotcrs is None):
        plotcrs =ccrs.AlbersEqualArea(central_latitude=(map_extent[2]+map_extent[3])/2.,
                central_longitude=(map_extent[0]+map_extent[1])/2., standard_parallels=[30., 60.])

    ax = plt.axes([0.01, 0.1, .98, .84], projection=plotcrs)
    #ax.set_extent(map_extent, crs=crs)
    map_extent=adjust_map_ratio(ax,map_extent=map_extent,datacrs=datacrs)
    plt.title(title, loc='left', fontsize=30)
    # add grid lines
    gl = ax.gridlines(crs=datacrs, linewidth=2, color='gray', alpha=0.5, linestyle='--', zorder=info_zorder)
    gl.xlocator = mpl.ticker.FixedLocator(np.arange(0, 360, 15))
    gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90, 15))

    if add_china:
        utl.add_china_map_2cartopy_public(ax, name='coastline', edgecolor='gray', lw=0.8, zorder=info_zorder, alpha=0.5)
        utl.add_china_map_2cartopy_public(ax, name='province', edgecolor='gray', lw=0.5, zorder=info_zorder)
        utl.add_china_map_2cartopy_public(ax, name='nation', edgecolor='black', lw=0.8, zorder=info_zorder)
        utl.add_china_map_2cartopy_public(ax, name='river', edgecolor='#74b9ff', lw=0.8, zorder=info_zorder, alpha=0.5)

    if add_city:
        small_city = False
        if(map_extent[1] - map_extent[0] < 25):
            small_city = True
        utl.add_city_on_map(ax, map_extent=map_extent,size=12, transform=datacrs, zorder=info_zorder+1,small_city=small_city)

    if add_background:
        ax.add_feature(cfeature.OCEAN)
        utl.add_cartopy_background(ax, name='RD')

    if add_south_China_sea:
        l, b, w, h = ax.get_position().bounds
        utl.add_south_China_sea(pos=[l + w - 0.0875, b, .1, .2])

    if forcast_info:
        l, b, w, h = ax.get_position().bounds
        bax = plt.axes([l, b + h - 0.1, .25, .1], facecolor='#FFFFFFCC')
        bax.set_yticks([])
        bax.set_xticks([])
        bax.axis([0, 10, 0, 10])
        bax.text(2.2, 9.8, forcast_info, size=15, va='top', ha='left',)

    l, b, w, h = ax.get_position().bounds
    utl.add_logo_extra_in_axes(pos=[l - 0.022, b + h - 0.1, .1, .1], which='nmc', size='Xlarge')

    return fig, ax, map_extent