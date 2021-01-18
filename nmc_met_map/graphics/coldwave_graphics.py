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
import nmc_met_graphics.cmap.cm as dk_ctables2
import nmc_met_map.lib.gy_ctables as gy_ctables
import nmc_met_map.graphics2 as GF
import matplotlib.patches as mpatches
import os

def draw_tmp_evo(
        tmp=None,thr=-4,
        map_extent=(50, 150, 0, 65),
        add_china=True,city=True,south_China_sea=True,
        output_dir=None,Global=False):
# set font
    initTime = pd.to_datetime(tmp.coords['forecast_reference_time'].values).replace(tzinfo=None).to_pydatetime()
    fhour = int(tmp['forecast_period'].values[-1])
    fcstTime = initTime + timedelta(hours=fhour)
    title = '['+tmp.attrs['model']+'] '+str(int(tmp['level'].values[0]))+'hPa '+str(thr)+'℃等温线演变'
    forcast_info = '起报时间: {0:%Y}年{0:%m}月{0:%d}日{0:%H}时\n预报时间: {1:%Y}年{1:%m}月{1:%d}日{1:%H}时\n预报时效: {2}小时\nwww.nmc.cn'.format(initTime, fcstTime, fhour)

    fig, ax, map_extent = GF.pallete_set.Horizontal_Pallete((18, 9),map_extent=map_extent, title=title, forcast_info=forcast_info,info_zorder=1,plotcrs=None,
                                             add_china=add_china, add_city=city,south_China_sea=south_China_sea,title_fontsize=25)

    plots = {}
    label_handles=[]
    x, y = np.meshgrid(tmp['lon'], tmp['lat'])
    for itime in range(0,len(tmp['time'].values)):
        z=np.squeeze(tmp['data'].values[itime,:,:])
        initTime = pd.to_datetime(str(tmp.coords['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
        labels=(initTime+timedelta(hours=tmp.coords['forecast_period'].values[itime])).strftime("%m月%d日%H时")
        cmap=dk_ctables2.ncl_cmaps('BlueDarkRed18')
        per_color=utl.get_part_clev_and_cmap(cmap=cmap,clev_range=[0,len(tmp['time'].values)],clev_slt=itime)
        ax.contour(
            x,y,z, levels=[thr],
            colors=per_color, zorder=3,linewidths=2,linestyles='solid',
            transform=ccrs.PlateCarree(),alpha=1)
        label_handles.append(mpatches.Patch(color=per_color.reshape(4),alpha=1, label=labels))
    leg = ax.legend(handles=label_handles, loc=3,framealpha=1,fontsize=10)
    #additional information

    l, b, w, h = ax.get_position().bounds

    # show figure
    if(output_dir != None):
        plt.savefig(output_dir+'['+tmp.attrs['model']+'] '+str(int(tmp['level'].values[0]))+'hPa '+str(thr)+'℃等温线演变_'+
        '起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+
        '预报时效_'+str(int(tmp.coords['forecast_period'].values[0]))+'小时'+'.png', dpi=200,bbox_inches='tight')
        plt.close()
    
    if(output_dir == None):
        plt.show()                              