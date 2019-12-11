
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

def draw_Station_Synthetical_Forecast_From_Cassandra(
            t2m=None,Td2m=None,AT=None,u10m=None,v10m=None,u100m=None,v100m=None,
            gust10m=None,wsp10m=None,wsp100m=None,r03=None,TCDC=None,LCDC=None,
            draw_VIS=False,VIS=None,drw_thr=False,
            time_all=None,
            model=None,points=None,
            output_dir=None):

    #if(sys.platform[0:3] == 'win'):
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')       

    initial_time1=pd.to_datetime(str(t2m['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    initial_time2=pd.to_datetime(str(VIS['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()

    # draw figure
    fig=plt.figure(figsize=(12,16))
    # draw main figure
    #温度————————————————————————————————————————————————
    ax = plt.axes([0.05,0.83,.94,.15])
    utl.add_public_title_sta(title=model+'预报 ['+str(points['lon'][0])+','+str(points['lat'][0])+']',initial_time=initial_time1, fontsize=23)

    for ifhour in t2m['forecast_period'].values:
        if (ifhour == t2m['forecast_period'].values[0] ):
            t2m_t=(initial_time1
                +timedelta(hours=ifhour))
        else:
            t2m_t=np.append(t2m_t,
                            (initial_time1
                            +timedelta(hours=ifhour)))
    #开启自适应
    xaxis_intaval=mpl.dates.HourLocator(byhour=(8,20)) #单位是小时
    ax.xaxis.set_major_locator(xaxis_intaval)
    ax.set_xticklabels([' '])
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), -100,facecolor='#3D5AFE')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), -5,facecolor='#2979FF')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 0,facecolor='#00B0FF')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 5,facecolor='#00E5FF')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 13,facecolor='#1DE9B6')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 18,facecolor='#00E676')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 22,facecolor='#76FF03')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 28,facecolor='#C6FF00')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 33,facecolor='#FFEA00')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 35,facecolor='#FFC400')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 37,facecolor='#FF9100')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 40,facecolor='#FF3D00')
    ax.fill_between(t2m_t, np.squeeze(t2m['data']), 100,facecolor='#FFFFFF')
    ax.plot(t2m_t,np.squeeze(t2m['data']),label='2米温度')
    ax.plot(t2m_t, np.squeeze(Td2m), dashes=[6, 2],linewidth=4,label='2米露点温度')
    ax.plot(t2m_t, np.squeeze(AT), dashes=[6, 2],linewidth=3,c='#00796B',label='2米体感温度')
    ax.tick_params(length=10)
    ax.grid()
    ax.grid(axis='x',c='black')
    miloc = mpl.dates.HourLocator(byhour=(11,14,17,23,2,5)) #单位是小时
    ax.xaxis.set_minor_locator(miloc)
    ax.grid(axis='x', which='minor')
    plt.xlim(time_all[0],time_all[-1])
    plt.ylim(min([np.array(Td2m).min(),AT.values.min(),t2m['data'].values.min()]),
        max([np.array(Td2m).max(),AT.values.max(),t2m['data'].values.max()]))
    ax.legend(fontsize=10,loc='upper right')
    ax.set_ylabel('2米温度 体感温度\n'+'2米露点温度 ($^\circ$C)', fontsize=15)
    
                      
    #10米风——————————————————————————————————————
    ax = plt.axes([0.05,0.66,.94,.15])
    for ifhour in u10m['forecast_period'].values:
        if (ifhour == u10m['forecast_period'].values[0] ):
            uv10m_t=(initial_time1
                +timedelta(hours=ifhour))
        else:
            uv10m_t=np.append(uv10m_t,
                            (initial_time1
                            +timedelta(hours=ifhour)))

    for ifhour in u100m['forecast_period'].values:
        if (ifhour == u100m['forecast_period'].values[0] ):
            uv100m_t=(initial_time1
                +timedelta(hours=ifhour))
        else:
            uv100m_t=np.append(uv100m_t,
                            (initial_time1
                            +timedelta(hours=ifhour)))
            
    for ifhour in gust10m['forecast_period'].values:
        if (ifhour == gust10m['forecast_period'].values[0] ):
            gust10m_t=(initial_time1
                +timedelta(hours=ifhour))
        else:
            gust10m_t=np.append(gust10m_t,
                            (initial_time1
                            +timedelta(hours=ifhour)))

    ax.plot(uv10m_t, np.squeeze(wsp10m), c='#40C4FF',label='10米风',linewidth=3)
    ax.plot(uv100m_t,np.squeeze(wsp100m),c='#FF6F00',label='100米风',linewidth=3)
    ax.plot(gust10m_t,np.squeeze(gust10m['data']),c='#7C4DFF',label='10米阵风',linewidth=3)
    if(drw_thr == True):
        ax.plot([uv10m_t[0],uv10m_t[-1]],[5.5,5.5],c='#4CAE50',label='10米平均风一般影响',linewidth=1)
        ax.plot([uv10m_t[0],uv10m_t[-1]],[8,8],c='#FFEB3B',label='10米平均风较大影响',linewidth=1)
        ax.plot([uv10m_t[0],uv10m_t[-1]],[10.8,10.8],c='#F44336',label='10米平均风高影响',linewidth=1)

        ax.plot([gust10m_t[0],gust10m_t[-1]],[10.8,10.8],c='#4CAE50',label='10米阵风一般影响', dashes=[6, 2],linewidth=1)
        ax.plot([gust10m_t[0],gust10m_t[-1]],[13.9,13.9],c='#FFEB3B',label='10米阵风较大影响', dashes=[6, 2],linewidth=1)
        ax.plot([gust10m_t[0],gust10m_t[-1]],[17.2,17.2],c='#F44336',label='10米阵风高影响', dashes=[6, 2],linewidth=1)

    ax.barbs(uv10m_t[0:-1], wsp10m[0:-1], 
            np.squeeze(u10m['data'])[0:-1], np.squeeze(v10m['data'])[0:-1],
            fill_empty=True,color='gray',barb_increments={'half':2,'full':4,'flag':20})

    ax.barbs(uv100m_t[0:-1], wsp100m[0:-1], 
            np.squeeze(u100m['data'])[0:-1], np.squeeze(v100m['data'])[0:-1],
            fill_empty=True,color='gray',barb_increments={'half':2,'full':4,'flag':20})

    xaxis_intaval=mpl.dates.HourLocator(byhour=(8,20)) #单位是小时
    ax.xaxis.set_major_locator(xaxis_intaval)
    ax.set_xticklabels([' '])
    plt.xlim(time_all[0],time_all[-1])    
    # add legend
    ax.legend(fontsize=10,loc='upper right')
    ax.tick_params(length=10)    
    ax.grid()
    ax.grid(axis='x',c='black')
    miloc = mpl.dates.HourLocator(byhour=(11,14,17,23,2,5)) #单位是小时
    ax.xaxis.set_minor_locator(miloc)
    ax.grid(axis='x', which='minor')    
    ax.set_ylabel('10米风 100米 风\n'+'风速 (m/s)', fontsize=15)
    #降水——————————————————————————————————————
    # draw main figure
    ax = plt.axes([0.05,0.49,.94,.15])
    for ifhour in r03['forecast_period'].values:
        if (ifhour == r03['forecast_period'].values[0] ):
            r03_t=(initial_time1
                +timedelta(hours=ifhour))
        else:
            r03_t=np.append(r03_t,
                            (initial_time1
                            +timedelta(hours=ifhour)))
    #开启自适应
    xaxis_intaval=mpl.dates.HourLocator(byhour=(8,20)) #单位是小时
    ax.xaxis.set_major_locator(xaxis_intaval)
    ax.set_xticklabels([' '])
    ax.bar(r03_t,np.squeeze(r03['data']),width=0.12,color='#1E88E5')
    gap_hour_r03=int(r03['forecast_period'].values[1]-r03['forecast_period'].values[0])

    if(drw_thr == True):
        ax.plot([r03_t[0],r03_t[-1]],[1*gap_hour_r03,1*gap_hour_r03],c='#FFEB3B',label=str(gap_hour_r03)+'小时降水较大影响',linewidth=1)
        ax.plot([r03_t[0],r03_t[-1]],[10*gap_hour_r03,10*gap_hour_r03],c='#F44336',label=str(gap_hour_r03)+'小时降水高影响',linewidth=1)
        ax.legend(fontsize=10,loc='upper right')
    ax.tick_params(length=10)    
    ax.grid()
    ax.grid(axis='x',c='black')
    miloc = mpl.dates.HourLocator(byhour=(11,14,17,23,2,5)) #单位是小时
    ax.xaxis.set_minor_locator(miloc)
    ax.grid(axis='x', which='minor')    
    plt.xlim(time_all[0],time_all[-1])
    plt.ylim([np.squeeze(r03['data']).values.min(),np.squeeze(r03['data'].values.max())+2])
    ax.set_ylabel(str(gap_hour_r03)+'小时累积雨量 (mm)', fontsize=15)
    #总量云——————————————————————————————————————
    # draw main figure
    ax = plt.axes([0.05,0.32,.94,.15])
    for ifhour in TCDC['forecast_period'].values:
        if (ifhour == TCDC['forecast_period'].values[0] ):
            TCDC_t=(initial_time1
                +timedelta(hours=ifhour))
        else:
            TCDC_t=np.append(TCDC_t,
                            (initial_time1
                            +timedelta(hours=ifhour)))
    # draw main figure
    for ifhour in LCDC['forecast_period'].values:
        if (ifhour == LCDC['forecast_period'].values[0] ):
            LCDC_t=(initial_time1
                +timedelta(hours=ifhour))
        else:
            LCDC_t=np.append(LCDC_t,
                            (initial_time1
                            +timedelta(hours=ifhour)))

    #开启自适应
    xaxis_intaval=mpl.dates.HourLocator(byhour=(8,20)) #单位是小时
    ax.xaxis.set_major_locator(xaxis_intaval)
    ax.set_xticklabels([' '])

    ax.bar(TCDC_t,np.squeeze(TCDC['data']),width=0.20,color='#82B1FF',label='总云量')
    ax.bar(LCDC_t,np.squeeze(LCDC['data']),width=0.125,color='#2962FF',label='低云量')
    ax.tick_params(length=10)    
    ax.grid()
    ax.grid(axis='x',c='black')
    miloc = mpl.dates.HourLocator(byhour=(11,14,17,23,2,5)) #单位是小时
    ax.xaxis.set_minor_locator(miloc)
    ax.grid(axis='x', which='minor')    
    plt.xlim(time_all[0],time_all[-1])
    plt.ylim(0,100)
    ax.legend(fontsize=10,loc='upper right')
    ax.set_ylabel('云量 (%)', fontsize=15)

    if(draw_VIS==False):
        xstklbls = mpl.dates.DateFormatter('%m月%d日%H时')
        ax.xaxis.set_major_formatter(xstklbls)
        for label in ax.get_xticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment('center')
        
        #发布信息————————————————————————————————————————————————
        ax = plt.axes([0.05,0.08,.94,.05])
        ax.axis([0, 10, 0, 10])
        ax.axis('off')
        utl.add_logo_extra_in_axes(pos=[0.7,0.23,.05,.05],which='nmc', size='Xlarge')
        ax.text(7.5, 33,(initial_time1 - timedelta(hours=2)).strftime("%Y年%m月%d日%H时")+'发布',size=15)

    if(draw_VIS==True):
        #能见度——————————————————————————————————————
        # draw main figure
        ax = plt.axes([0.05,0.15,.94,.15])

        #VIS=pd.read_csv(dir_all['VIS_SC']+last_file[model])
        for ifhour in VIS['forecast_period'].values:
            if (ifhour == VIS['forecast_period'].values[0] ):
                VIS_t=(initial_time2
                    +timedelta(hours=ifhour))
            else:
                VIS_t=np.append(VIS_t,
                                (initial_time2
                                +timedelta(hours=ifhour)))

        #开启自适应
        xaxis_intaval=mpl.dates.HourLocator(byhour=(8,20)) #单位是小时
        ax.xaxis.set_major_locator(xaxis_intaval)

        ax.fill_between(VIS_t, np.squeeze(VIS['data']), -100,facecolor='#B3E5FC')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 1,facecolor='#81D4FA')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 3,facecolor='#4FC3F7')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 5,facecolor='#29B6F6')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 10,facecolor='#03A9F4')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 15,facecolor='#039BE5')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 20,facecolor='#0288D1')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 25,facecolor='#0277BD')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 30,facecolor='#01579B')
        ax.fill_between(VIS_t, np.squeeze(VIS['data']), 100,facecolor='#FFFFFF')

        ax.plot(VIS_t,np.squeeze(VIS['data']))
        if(drw_thr == True):
            ax.plot([VIS_t[0],VIS_t[-1]],[5,5],c='#4CAF50',label='能见度一般影响',linewidth=1)
            ax.plot([VIS_t[0],VIS_t[-1]],[3,3],c='#FFEB3B',label='能见度较大影响',linewidth=1)
            ax.plot([VIS_t[0],VIS_t[-1]],[1,1],c='#F44336',label='能见度高影响',linewidth=1)
            ax.legend(fontsize=10,loc='upper right')

        xstklbls = mpl.dates.DateFormatter('%m月%d日%H时')
        ax.xaxis.set_major_formatter(xstklbls)
        for label in ax.get_xticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment('center')
        ax.tick_params(length=10)
        ax.grid()
        ax.grid(axis='x',c='black')
        miloc = mpl.dates.HourLocator(byhour=(11,14,17,23,2,5)) #单位是小时
        ax.xaxis.set_minor_locator(miloc)
        ax.grid(axis='x', which='minor')    
        plt.xlim(time_all[0],time_all[-1])
        plt.ylim(0,25)
        ax.set_ylabel('能见度 （km）', fontsize=15)
            #发布信息————————————————————————————————————————————————
        ax = plt.axes([0.05,0.08,.94,.05])
        ax.axis([0, 10, 0, 10])
        ax.axis('off')
        utl.add_logo_extra_in_axes(pos=[0.7,0.06,.05,.05],which='nmc', size='Xlarge')
        ax.text(7.5, 0.1,
                (initial_time1 - timedelta(hours=2)).strftime("%Y年%m月%d日%H时")+'发布',size=15)

    #出图——————————————————————————————————————————————————————————
    if(output_dir != None ):
        plt.savefig(output_dir+model+'模式_'+
        initial_time1.strftime("%Y%m%d%H")+
        '00'+'.jpg', dpi=200,bbox_inches='tight')
    else:
        plt.show()


def draw_sta_skewT(p=None,T=None,Td=None,wind_speed=None,wind_dir=None,u=None,v=None,
    fcst_info=None,output_dir=None):
    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig, rotation=45)

    plt.rcParams['font.sans-serif'] = ['SimHei'] # 步骤一（替换sans-serif字体）
    plt.rcParams['axes.unicode_minus'] = False  # 步骤二（解决坐标轴负数的负号显示问题）

    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot.
    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p, u, v)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-40, 60)

    # Calculate LCL height and plot as black dot. Because `p`'s first value is
    # ~1000 mb and its last value is ~250 mb, the `0` index is selected for
    # `p`, `T`, and `Td` to lift the parcel from the surface. If `p` was inverted,
    # i.e. start from low value, 250 mb, to a high value, 1000 mb, the `-1` index
    # should be selected.
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')

    # Calculate full parcel profile and add to plot as black line
    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    skew.plot(p, prof, 'k', linewidth=2)

    # Shade areas of CAPE and CIN
    skew.shade_cin(p, T, prof)
    skew.shade_cape(p, T, prof)

    # An example of a slanted line at constant T -- in this case the 0
    # isotherm
    skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

    # Add the relevant special lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    #forecast information
    bax=plt.axes([0.12,0.88,.25,.07],facecolor='#FFFFFFCC')
    bax.axis('off')
    bax.axis([0, 10, 0, 10])

    initial_time = pd.to_datetime(
        str(fcst_info['forecast_reference_time'].values)).replace(tzinfo=None).to_pydatetime()
    if(sys.platform[0:3] == 'lin'):
        locale.setlocale(locale.LC_CTYPE, 'zh_CN')
    if(sys.platform[0:3] == 'win'):        
        locale.setlocale(locale.LC_CTYPE, 'chinese')
    plt.text(2.5, 7.5,'起报时间: '+initial_time.strftime("%Y年%m月%d日%H时"),size=11)
    plt.text(2.5, 5.0,'['+str(fcst_info.attrs['model'])+'] '+str(int(fcst_info['forecast_period'].values[0]))+'小时预报探空',size=11)
    plt.text(2.5, 2.5,'预报点: '+str(fcst_info.attrs['points']['lon'])+
        ', '+str(fcst_info.attrs['points']['lat']),size=11)
    plt.text(2.5, 0.5,'www.nmc.cn',size=11)
    utl.add_logo_extra_in_axes(pos=[0.1,0.88,.07,.07],which='nmc', size='Xlarge')

    # Show the plot
    if(output_dir != None ):
        plt.savefig(output_dir+'时间剖面产品_起报时间_'+
        str(fcst_info['forecast_reference_time'].values)[0:13]+
        '_预报时效_'+str(int(fcst_info.attrs['forecast_period'].values))
        +'.png', dpi=200,bbox_inches='tight')
    else:
        plt.show()