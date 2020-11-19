import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import nmc_met_map.lib.utility as utl
from datetime import datetime, timedelta
import pandas as pd
import locale
import sys
import metpy.calc as mpcalc
from metpy.plots import  SkewT
import os
from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes
from matplotlib.ticker import MultipleLocator
import math
from metpy.units import units

def box_line_temp(TMP=None,
        output_dir=None,
        points=None,
        extra_info=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')       

    initTime=pd.to_datetime(str(TMP['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()

    # draw figure
    fig=plt.figure(figsize=(16,4.5))
    # draw main figure    
    #10米风——————————————————————————————————————
    ax = plt.axes([0.1,0.28,.8,.62])
    utl.add_public_title_sta(title=TMP.attrs['model']+'预报 '+extra_info['point_name']+' ['+str(points['lon'][0])+','+str(points['lat'][0])+']',initTime=initTime, fontsize=21)
    for ifhour in TMP['forecast_period'].values:
        if (ifhour == TMP['forecast_period'].values[0] ):
            if(ifhour % 12 == 0):
                uv_t=(initTime
                    +timedelta(hours=ifhour)).strftime('%m月%d日%H时')
            else:
                uv_t=' '
        else:
            if(ifhour % 12 == 0):
                uv_t=np.append(uv_t,
                            (initTime
                            +timedelta(hours=ifhour)).strftime('%m月%d日%H时'))
            else:
                uv_t=np.append(uv_t,' ')

    labels = uv_t
    ax.boxplot(np.transpose(np.squeeze(TMP['data'].values)),
         labels=labels,meanline=True,showmeans=True, showfliers=False,whis=(0,100))

    ax.set_ylim(math.floor(TMP['data'].values.min()/2)*2,
        math.ceil(TMP['data'].values.max()/2)*2)
    #plt.xlim(uv_t[0],uv_t[-1])    
    # add legend
    #ax.legend(fontsize=15,loc='upper right')
    ax.tick_params(length=7)   
    ax.tick_params(axis='y',labelsize=100)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment('center')
    ax.tick_params(axis='y',labelsize=15)
    ax.tick_params(axis='x',labelsize=10)
    miloc = mpl.dates.HourLocator(byhour=(8,11,14,17,20,23,2,5)) #单位是小时
    ax.xaxis.set_minor_locator(miloc)
    yminorLocator   = MultipleLocator(1) #将此y轴次刻度标签设置为1的倍数
    ax.yaxis.set_minor_locator(yminorLocator)
    ymajorLocator   = MultipleLocator(2) #将此y轴次刻度标签设置为1的倍数
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.grid(axis='x', ls='--')    
    for label in ax.get_yticklabels():
        label.set_fontsize(15)
    #ax.axis['left'].major_ticklabels.set_fontsize(15)
    ax.set_ylabel('温度 ($^\circ$C)', fontsize=15)

    utl.add_logo_extra_in_axes(pos=[0.87,0.00,.1,.1],which='nmc', size='Xlarge')

    #出图——————————————————————————————————————————————————————————
    if(output_dir != None ):
        isExists=os.path.exists(output_dir)
        if not isExists:
            os.makedirs(output_dir)

        output_dir2=output_dir+TMP.attrs['model']+'_起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+'/'
        if(os.path.exists(output_dir2) == False):
            os.makedirs(output_dir2)

        plt.savefig(output_dir2+TMP.attrs['model']+'_'+extra_info['point_name']+'_'+extra_info['output_head_name']+
        initTime.strftime("%Y%m%d%H")+
        '00'+extra_info['output_tail_name']+'_温度_箱线图'+'.jpg', dpi=200,bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def box_line_rn(rn=None,
        output_dir=None,
        points=None,
        extra_info=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')       

    initTime=pd.to_datetime(str(rn['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()

    # draw figure
    fig=plt.figure(figsize=(16,4.5))
    # draw main figure    
    #10米风——————————————————————————————————————
    ax = plt.axes([0.1,0.28,.8,.62])
    utl.add_public_title_sta(title=rn.attrs['model']+'预报 '+extra_info['point_name']+' ['+str(points['lon'][0])+','+str(points['lat'][0])+']',initTime=initTime, fontsize=21)
    for ifhour in rn['forecast_period'].values:
        if (ifhour == rn['forecast_period'].values[0] ):
            if(ifhour % 12 == 0):
                uv_t=(initTime
                    +timedelta(hours=ifhour)).strftime('%m月%d日%H时')
            else:
                uv_t=' '
        else:
            if(ifhour % 12 == 0):
                uv_t=np.append(uv_t,
                            (initTime
                            +timedelta(hours=ifhour)).strftime('%m月%d日%H时'))
            else:
                uv_t=np.append(uv_t,' ')

    labels = uv_t
    ax.boxplot(np.transpose(np.squeeze(rn['data'].values)), 
        labels=labels,meanline=True,showmeans=True, showfliers=False,whis=(0,100))

    ax.set_ylim(0,math.ceil(rn['data'].values.max()/2)*2)
    #plt.xlim(uv_t[0],uv_t[-1])    
    # add legend
    #ax.legend(fontsize=15,loc='upper right')
    ax.tick_params(length=7)   
    ax.tick_params(axis='y',labelsize=100)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment('center')
    ax.tick_params(axis='y',labelsize=15)
    ax.tick_params(axis='x',labelsize=10)
    miloc = mpl.dates.HourLocator(byhour=(8,11,14,17,20,23,2,5)) #单位是小时
    ax.xaxis.set_minor_locator(miloc)
    yminorLocator   = MultipleLocator(1) #将此y轴次刻度标签设置为1的倍数
    ax.yaxis.set_minor_locator(yminorLocator)
    ymajorLocator   = MultipleLocator(2) #将此y轴次刻度标签设置为1的倍数
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.grid(axis='x', ls='--')    
    for label in ax.get_yticklabels():
        label.set_fontsize(15)
    #ax.axis['left'].major_ticklabels.set_fontsize(15)
    t_gap=rn['forecast_period'].values[1]-rn['forecast_period'].values[0]
    ax.set_ylabel('%i'%t_gap+'小时降水 (mm)', fontsize=15)

    utl.add_logo_extra_in_axes(pos=[0.87,0.00,.1,.1],which='nmc', size='Xlarge')

    #出图——————————————————————————————————————————————————————————
    if(output_dir != None ):
        isExists=os.path.exists(output_dir)
        if not isExists:
            os.makedirs(output_dir)

        output_dir2=output_dir+rn.attrs['model']+'_起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+'/'
        if(os.path.exists(output_dir2) == False):
            os.makedirs(output_dir2)

        plt.savefig(output_dir2+rn.attrs['model']+'_'+extra_info['point_name']+'_'+extra_info['output_head_name']+
        initTime.strftime("%Y%m%d%H")+
        '00'+extra_info['output_tail_name']+'_降水_箱线图'+'.jpg', dpi=200,bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def box_line_wsp(wsp=None,
        output_dir=None,
        points=None,
        extra_info=None):

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN.utf8')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')       

    initTime=pd.to_datetime(str(wsp['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()

    # draw figure
    fig=plt.figure(figsize=(16,4.5))
    # draw main figure    
    #10米风——————————————————————————————————————
    ax = plt.axes([0.1,0.28,.8,.62])
    utl.add_public_title_sta(title=wsp.attrs['model']+'预报 '+extra_info['point_name']+' ['+str(points['lon'][0])+','+str(points['lat'][0])+']',initTime=initTime, fontsize=21)
    for ifhour in wsp['forecast_period'].values:
        if (ifhour == wsp['forecast_period'].values[0] ):
            if(ifhour % 12 == 0):
                uv_t=(initTime
                    +timedelta(hours=ifhour)).strftime('%m月%d日%H时')
            else:
                uv_t=' '
        else:
            if(ifhour % 12 == 0):
                uv_t=np.append(uv_t,
                            (initTime
                            +timedelta(hours=ifhour)).strftime('%m月%d日%H时'))
            else:
                uv_t=np.append(uv_t,' ')

    labels = uv_t
    ax.boxplot(np.transpose(np.squeeze(wsp['data'].values)), 
        labels=labels,meanline=True,showmeans=True, showfliers=False,whis=(0,100))

    warning=np.zeros(len(uv_t))+20.
    warning_t=np.arange(0,len(uv_t))+1
    ax.plot(warning_t,warning,c='red',label=' ',linewidth=1)
    ax.set_ylim(0,math.ceil(wsp['data'].values.max()/2)*2)
    #plt.xlim(uv_t[0],uv_t[-1])    
    # add legend
    #ax.legend(fontsize=15,loc='upper right')
    ax.tick_params(length=7)   
    ax.tick_params(axis='y',labelsize=100)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment('center')
    ax.tick_params(axis='y',labelsize=15)
    ax.tick_params(axis='x',labelsize=10)
    miloc = mpl.dates.HourLocator(byhour=(8,11,14,17,20,23,2,5)) #单位是小时
    ax.xaxis.set_minor_locator(miloc)
    yminorLocator   = MultipleLocator(1) #将此y轴次刻度标签设置为1的倍数
    ax.yaxis.set_minor_locator(yminorLocator)
    ymajorLocator   = MultipleLocator(2) #将此y轴次刻度标签设置为1的倍数
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.grid(axis='x', ls='--')    
    for label in ax.get_yticklabels():
        label.set_fontsize(15)
    #ax.axis['left'].major_ticklabels.set_fontsize(15)
    t_gap=wsp['forecast_period'].values[1]-wsp['forecast_period'].values[0]
    ax.set_ylabel('风速 (m s$^-$$^1$)', fontsize=15)

    utl.add_logo_extra_in_axes(pos=[0.87,0.00,.1,.1],which='nmc', size='Xlarge')

    #出图——————————————————————————————————————————————————————————
    if(output_dir != None ):
        isExists=os.path.exists(output_dir)
        if not isExists:
            os.makedirs(output_dir)

        output_dir2=output_dir+wsp.attrs['model']+'_起报时间_'+initTime.strftime("%Y年%m月%d日%H时")+'/'
        if(os.path.exists(output_dir2) == False):
            os.makedirs(output_dir2)

        plt.savefig(output_dir2+wsp.attrs['model']+'_'+extra_info['point_name']+'_'+extra_info['output_head_name']+
        initTime.strftime("%Y%m%d%H")+
        '00'+extra_info['output_tail_name']+'_风速_箱线图'+'.jpg', dpi=200,bbox_inches='tight')
        plt.close()
    else:
        plt.show()
