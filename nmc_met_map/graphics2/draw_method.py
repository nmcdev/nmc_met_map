# -*- coding: utf-8 -*-
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
import nmc_met_map.lib.gy_ctables as gy_ctables
from datetime import datetime, timedelta
import pandas as pd
import locale
import sys
from matplotlib.colors import BoundaryNorm,ListedColormap
import nmc_met_graphics.cmap.ctables as dk_ctables
import nmc_met_graphics.cmap.cm as dk_ctables2
from scipy.ndimage import gaussian_filter
import matplotlib.patheffects as mpatheffects
import nmc_met_graphics.cmap.cpt as cpt
import matplotlib.colors as col

def gh_contour(ax,x,y,z,colors='black',
    levels=np.append(np.append(np.arange(0, 480, 4),np.append(np.arange(480, 580, 4), np.arange(580, 604, 4))), np.arange(604, 2000, 8)),
    alpha=0.8,linewidths=None,transform=ccrs.PlateCarree(),**kwargs):
    if(linewidths == None):
        linewidths=np.zeros_like(levels)+2
        linewidths[levels==588]=4
    img = ax.contour(x,y,z,levels=levels,linewidths=linewidths,
        colors=colors, transform=transform,alpha=alpha,**kwargs)
    plt.clabel(img, inline=1, fontsize=20, fmt='%i',colors=colors)
    return img

def Tmx_pcolormesh(ax, x, y, z,cmap=dk_ctables.cm_temp(),transform=ccrs.PlateCarree(),
                    vmin=-45, vmax=45,alpha=0.5, **kwargs):
    img = ax.pcolormesh(x,y,z,
        cmap=cmap, transform=transform,alpha=0.5, vmin=-45, vmax=45,**kwargs)
    
    return img

def Tmx_contour(ax,x,y,z,colors=['#FF8F00','#FF6200','#FF0000'],levels=[35,37,40],linewidths=2,transform=ccrs.PlateCarree(),**kwargs):
    
    img = ax.contour(x, y, z, levels=levels, colors=colors,linewidths=2,transform=transform,**kwargs)
    cl=plt.clabel(img, inline=1, fontsize=15, fmt='%i',colors=colors)

    if(cl is not None):
        for t in cl:
            t.set_path_effects([mpatheffects.Stroke(linewidth=3, foreground='white'),
                    mpatheffects.Normal()])
    return img

def dT2m_pcolormesh(ax,x,y,z,cmap=utl.linearized_ncl_cmap('hotcold_18lev'),vmin=-16, vmax=16,transform=ccrs.PlateCarree(),**kwargs):
    img = ax.pcolormesh(x,y,z,
        cmap=cmap,transform=transform, vmin=vmin, vmax=vmax,**kwargs)
    return img

def dT2m_contour(ax,x,y,z,cmap=utl.linearized_ncl_cmap('BlRe'),levels=[-16,-12,-10,-8,-6,6,8,10,12,16],vmin=-16, vmax=16,alpha=0.5,transform=ccrs.PlateCarree(),**kwargs):
    img = ax.contour(x,y,z,levels=levels,
        cmap=cmap, transform=transform,alpha=alpha, vmin=vmin, vmax=vmax,**kwargs)
    return img

def tmp_contour(ax,x,y,z,colors='black',levels=np.arange(4,48,4),alpha=0.8,transform=ccrs.PlateCarree(),**kwargs):
    img = ax.contour(x,y,z,colors=colors,levels=levels,transform=transform,alpha=alpha,**kwargs)
    cl=plt.clabel(img, inline=1, fontsize=15, fmt='%i',colors=colors)
    return img

def anm_pcolormesh(ax,x,y,z,cmap=dk_ctables2.ncl_cmaps('GHRSST_anomaly'),vmin=-50,vmax=50,alpha=0.8,transform=ccrs.PlateCarree(),**kwargs):
    img = ax.pcolormesh(x,y,z,
        cmap=cmap,transform=transform, vmin=vmin, vmax=vmax,**kwargs)
    return img

def AQI_scatter(ax,x,y,z,cmap=dk_ctables2.ncl_cmaps('hotcold_18lev'),vmin=0,vmax=100,alpha=0.8,transform=ccrs.PlateCarree(),levels=None,**kwargs):
    if(levels is not None):
        cmap,norm=cpt.generate_cmap_norm(levels,cm=cmap,extend='both')
        img = ax.scatter(x,y,c=z,cmap=cmap,transform=transform, norm=norm,alpha=alpha,**kwargs)
    else:
        img = ax.scatter(x,y,c=z,cmap=cmap,transform=transform, vmin=vmin, vmax=vmax,alpha=alpha,**kwargs)
    return img

def wind_barbs(ax,x,y,u,v,length=6, regrid_shape=20,
        transform=ccrs.PlateCarree(), fill_empty=False, sizes=dict(emptybarb=0.05),
        color ='black',**kwargs):

    img= ax.barbs(
        x, y, u * 2.5, v * 2.5, length=length, regrid_shape=regrid_shape,
        transform=transform, fill_empty=False, sizes=sizes,
        color =color)

    return img

def cu_rain_pcolormesh(ax,x,y,z,cmap=None,norm=None,atime=6,vmin=-50,vmax=50,alpha=0.8,transform=ccrs.PlateCarree(),**kwargs):
    if(cmap == None or norm == None):
        cmap,norm=dk_ctables.cm_precipitation_nws(atime=atime)
    z[z<0.1]=np.nan
    img = ax.pcolormesh(x,y,z,cmap=cmap, norm=norm,transform=transform,**kwargs)
    return img

def cu_rain_contourf(ax,x,y,z,cmap=None,levels=None,atime=6,vmin=-50,vmax=50,alpha=0.8,transform=ccrs.PlateCarree(),**kwargs):
    if(cmap == None):
        colors,levels=gy_ctables.cm_precipitation_nmc(atime=atime)
    z[z<0.1]=np.nan
    img = ax.contourf(x,y,z,colors=colors, levels=levels,transform=transform,extend='max',**kwargs)
    return img

def ulj_contourf(ax,x,y,z,cmap=utl.linearized_ncl_cmap('MPL_Oranges'),levels=np.arange(30,80,2),alpha=0.8,transform=ccrs.PlateCarree(),**kwargs):
    z[z<levels[0]]=np.nan
    img = ax.contourf(x,y,z,cmap=cmap, levels=levels,transform=transform,extend='max',alpha=alpha,**kwargs)
    return img

def wet_area_contourf(ax,x,y,z,cmap=utl.linearized_ncl_cmap('MPL_Blues'),levels=np.arange(50,80,2),vmin=50,vmax=80,alpha=0.8,transform=ccrs.PlateCarree(),**kwargs):
    z[z<levels[0]]=np.nan
    img = ax.contourf(x,y,z,cmap=cmap, levels=levels,transform=transform,extend='max',alpha=alpha,**kwargs)
    return img

def tadv_pcolormesh(ax,x,y,z,cmap=dk_ctables2.ncl_cmaps('cmp_b2r'),vmin=-50,vmax=50,alpha=0.8,transform=ccrs.PlateCarree(),**kwargs):
    img = ax.pcolormesh(x,y,z,
        cmap=cmap,transform=transform, vmin=vmin, vmax=vmax,**kwargs)
    return img

def rh_contourf(ax,x,y,z,cmap=None,levels=np.arange(30,80,2),alpha=0.8,transform=ccrs.PlateCarree(),**kwargs):
    if(cmap == None):
        cmap = col.LinearSegmentedColormap.from_list('own2',['#1E90FF','#94D8F6','#F1F1F1','#BFBFBF','#696969'])
    img = ax.contourf(x,y,z,levels=np.arange(0, 101, 0.5), cmap=cmap,extend='max',transform=transform,**kwargs)
    return img