import nmc_met_map.synoptic as draw_synoptic
import nmc_met_map.dynamic as draw_dynamic
import nmc_met_map.moisture as draw_moisture
import nmc_met_map.thermal as draw_thermal
import nmc_met_map.QPF as draw_QPF
import nmc_met_map.elements as draw_elements
import nmc_met_map.elements2 as draw_elements2
import nmc_met_map.sta2 as draw_sta2
import nmc_met_map.sta as draw_sta
import nmc_met_map.lib.utility as utl
import nmc_met_map.isentropic as draw_isentropic
import nmc_met_map.synthetical as draw_synthetical
import nmc_met_map.local_scale as draw_local_scale
import nmc_met_map.observation as draw_observation
import nmc_met_map.syn_ver as draw_synoptic_verification
import nmc_met_map.observation2 as draw_observation2
import nmc_met_map.crossection as draw_crossection
import multiprocessing as mp
from multiprocessing import Manager
import os
import time as timer
import copy
import matplotlib.pyplot as plt
import datetime
import shutil
import numpy as np

def compare(func=None,initTime=None,fhour=24,output_dir='./temp/',
            models=['ECMWF','GRAPES_GFS','NCEP_GFS','GRAPES_3KM'],tab_size=(30,18),show='tab',
            func_other_args={},max_workers=6,keep_temp=False):

    systime=datetime.datetime.now()
    temp_path='./temp/'+systime.strftime('%M%S%f')+'/'
    isExists=os.path.exists(temp_path)
    if not isExists:
        os.makedirs(temp_path)

    pool = mp.Pool(processes=max_workers)

    for idx,imodel in enumerate(models):
        func_args = copy.deepcopy(func_other_args)
        func_args['initTime'] = initTime.strftime('%Y%m%d%H')[2:10]
        func_args['fhour'] = fhour
        func_args['model'] = imodel
        func_args['map_ratio'] = 14/9
        func_args['output_dir']=temp_path+str(idx)+'_'+imodel
        pool.apply_async(func,kwds=func_args)
        timer.sleep(1)
    pool.close()
    pool.join()

    pic_all=os.listdir(temp_path)
    if len(pic_all) == 0:
        shutil.rmtree(temp_path)
        return
    # png_name = 'compare_{}.png'.format(func.__name__)
    # utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name)
    pic_all=sorted(pic_all,key=lambda i:int(i.split('_')[0]))
    if(show == 'tab'):
        png_name = 'compare_{}.png'.format(func.__name__)
        utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name,keep_temp=keep_temp)
    if(show == 'animation'):
        gif_name = 'compare_{}.gif'.format(func.__name__)
        utl.save_animation(temp_path=temp_path,pic_all=pic_all,output_dir=output_dir,gif_name=gif_name,keep_temp=keep_temp)


def stability(target_time=None, latest_init_time=None, ninit=4, init_interval=12, model='GRAPES_GFS',
                     func=None, func_other_args={}, max_workers=6,show='tab',
                     output_dir='./temp/', tab_size=(30, 18),keep_temp=False):
    
    systime=datetime.datetime.now()
    temp_path='./temp/'+systime.strftime('%M%S%f')+'/'
    isExists=os.path.exists(temp_path)
    if not isExists:
        os.makedirs(temp_path)
    if(target_time != None):
        target_time=datetime.datetime.strptime(target_time,'%y%m%d%H')
    if(latest_init_time != None):
        latest_init_time=datetime.datetime.strptime(latest_init_time,'%y%m%d%H')

    if latest_init_time is None:
        # 获得最近的一次模式起报时间
        latest_init_time = utl.get_latest_init_time_model()
    else:
        latest_init_time = datetime.datetime(latest_init_time.year, latest_init_time.month, latest_init_time.day, latest_init_time.hour)

    # 如果target_time为空，则取latest_init_time+36
    if target_time is None:
        target_time = latest_init_time + datetime.timedelta(hours=36) 
    target_time = datetime.datetime(target_time.year, target_time.month, target_time.day, target_time.hour)
    if target_time < latest_init_time:
        print('target_time({:%Y%m%d%H}) < latest_init_time({:%Y%m%d%H})'.format(target_time, latest_init_time))
        return

    initTime = latest_init_time
    fhour = int((target_time - latest_init_time).total_seconds() / 60 / 60)

    pool = mp.Pool(processes=max_workers)

    for i in range(ninit):
        func_args = copy.deepcopy(func_other_args)
        func_args['initTime'] = (initTime - datetime.timedelta(hours=init_interval * i)).strftime('%Y%m%d%H')[2:10]
        func_args['fhour'] = fhour + init_interval * i
        func_args['model'] = model
        func_args['map_ratio'] = 14/9
        func_args['lw_ratio'] = [14,9]
        func_args['output_dir']=temp_path+str(i)+'_'+model
        if func_args['fhour'] < 0:
            continue
        pool.apply_async(func,kwds=func_args)
        timer.sleep(1)
    pool.close()
    pool.join()

    pic_all=os.listdir(temp_path)
    if len(pic_all) == 0:
        shutil.rmtree(temp_path)
        return
    # png_name = 'stability_{}.png'.format(func.__name__)
    # utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name)

    pic_all=sorted(pic_all,key=lambda i:int(i.split('_')[0]))
    if(show == 'tab'):
        png_name = 'stability_{}.png'.format(func.__name__)
        utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name,keep_temp=keep_temp)
    if(show == 'animation'):
        gif_name = 'stability_{}.gif'.format(func.__name__)
        utl.save_animation(temp_path=temp_path,pic_all=pic_all,output_dir=output_dir,gif_name=gif_name,keep_temp=keep_temp)


def vercompare(anl_time=None, ninit=4, init_interval=12, model='GRAPES_GFS',
                     func=None, func_other_args={}, max_workers=6,show='tab',
                     output_dir='./temp/', tab_size=(30, 18),keep_temp=False
                     ):
    if(anl_time != None):
        anl_time=datetime.datetime.strptime(anl_time,'%y%m%d%H')
    systime=datetime.datetime.now()
    temp_path='./temp/'+systime.strftime('%M%S%f')+'/'
    isExists=os.path.exists(temp_path)
    if not isExists:
        os.makedirs(temp_path)
    initTime = None
    fhour = None
    if anl_time is None:
        # 获得最近的一次000时效预报数据
        initTime = utl.get_latest_init_time_model()
        fhour = 0
    else:
        # fhour固定为0，此时对于如ecwmf只有anl_time=08/20时才会找得到
        initTime = datetime.datetime(anl_time.year, anl_time.month, anl_time.day, anl_time.hour)
        fhour = 0

    pool = mp.Pool(processes=max_workers)

    for i in range(ninit):
        func_args = copy.deepcopy(func_other_args)
        func_args['initTime'] = (initTime - datetime.timedelta(hours=init_interval * i)).strftime('%Y%m%d%H')[2:10]
        func_args['fhour'] = fhour + init_interval * i
        func_args['model'] = model
        func_args['map_ratio'] = 14/9
        func_args['lw_ratio'] = [14,9]
        func_args['output_dir']=temp_path+str(i)+'_'+model
        if func_args['fhour'] < 0:
            continue
        pool.apply_async(func,kwds=func_args)
        timer.sleep(1)
    pool.close()
    pool.join()

    pic_all=os.listdir(temp_path)
    if len(pic_all) == 0:
        shutil.rmtree(temp_path)
        return
    # png_name = 'vercompare_{}.png'.format(func.__name__)
    # utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name)
    pic_all=sorted(pic_all,key=lambda i:int(i.split('_')[0]))
    if(show == 'tab'):
        png_name = 'vercompare_{}.png'.format(func.__name__)
        utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name,keep_temp=keep_temp)
    if(show == 'animation'):
        gif_name = 'vercompare_{}.gif'.format(func.__name__)
        utl.save_animation(temp_path=temp_path,pic_all=pic_all,output_dir=output_dir,gif_name=gif_name,keep_temp=keep_temp)

def evolution(initTime=None, fhours=[12, 18, 24, 30, 36], model='GRAPES_GFS',
                   func=None, func_other_args={}, max_workers=6,show='tab',
                   output_dir='./temp/', tab_size=(30, 18),keep_temp=False): 

    systime=datetime.datetime.now()
    temp_path='./temp/'+systime.strftime('%M%S%f')+'/'
    isExists=os.path.exists(temp_path)
    if not isExists:
        os.makedirs(temp_path)

    pool = mp.Pool(processes=max_workers)

    for idx,ifhour in enumerate(fhours):
        func_args = copy.deepcopy(func_other_args)
        func_args['initTime'] = initTime
        func_args['fhour'] = ifhour
        func_args['model'] = model
        func_args['map_ratio'] = 14/9
        func_args['lw_ratio'] = [14,9]
        func_args['output_dir']=temp_path+str(idx)+'_'+model
        pool.apply_async(func,kwds=func_args)
        timer.sleep(1)
    pool.close()
    pool.join()

    pic_all=os.listdir(temp_path)
    if len(pic_all) == 0:
        shutil.rmtree(temp_path)
        return

    pic_all=sorted(pic_all,key=lambda i:int(i.split('_')[0]))
    if(show == 'tab'):
        png_name = 'evolution_{}.png'.format(func.__name__)
        utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name,keep_temp=keep_temp)
    if(show == 'animation'):
        gif_name = 'evolution_{}.gif'.format(func.__name__)
        utl.save_animation(temp_path=temp_path,pic_all=pic_all,output_dir=output_dir,gif_name=gif_name,keep_temp=keep_temp)

def structure3D(func=None,levs=[{'uv_lev':925},{'uv_lev':850},{'uv_lev':700},{'uv_lev':500}],
                initTime=None,fhour=24,model='GRAPES_GFS', func_other_args={}, max_workers=6,show='tab',
                   output_dir='./temp/', tab_size=(30, 18),keep_temp=False): 

    systime=datetime.datetime.now()
    temp_path='./temp/'+systime.strftime('%M%S%f')+'/'
    isExists=os.path.exists(temp_path)
    if not isExists:
        os.makedirs(temp_path)

    pool = mp.Pool(processes=max_workers)

    for idx,ilev in enumerate(levs):
        func_args = copy.deepcopy(func_other_args)
        func_args = {**func_args,**ilev}
        func_args['initTime'] = initTime
        func_args['fhour'] = fhour
        func_args['model'] = model
        func_args['map_ratio'] = 14/9
        func_args['lw_ratio'] = [14,9]
        func_args['output_dir']=temp_path+str(idx)+'_'+model
        pool.apply_async(func,kwds=func_args)
        timer.sleep(1)
    pool.close()
    pool.join()

    pic_all=os.listdir(temp_path)
    if len(pic_all) == 0:
        shutil.rmtree(temp_path)
        return

    pic_all=sorted(pic_all,key=lambda i:int(i.split('_')[0]))
    if(show == 'tab'):
        png_name = 'structure3D_{}.png'.format(func.__name__)
        utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name,keep_temp=keep_temp)
    if(show == 'animation'):
        gif_name = 'structure3D_{}.gif'.format(func.__name__)
        utl.save_animation(temp_path=temp_path,pic_all=pic_all,output_dir=output_dir,gif_name=gif_name,keep_temp=keep_temp)

def evolution_ana(initTime=[], fhour=0,atime=6, data_source='CIMISS', model='GRAPES_GFS',
                   func=None, func_other_args={}, max_workers=6,show='tab',
                   output_dir='./temp/', tab_size=(30, 18),keep_temp=False): 

    systime=datetime.datetime.now()
    temp_path='./temp/'+systime.strftime('%M%S%f')+'/'
    isExists=os.path.exists(temp_path)
    if not isExists:
        os.makedirs(temp_path)

    pool = mp.Pool(processes=max_workers)
    for idx,iinit in enumerate(initTime):
        func_args = copy.deepcopy(func_other_args)
        func_args['initTime'] = iinit
        func_args['fhour'] = fhour
        func_args['atime'] = atime
        func_args['model'] = model
        func_args['data_source'] = data_source
        func_args['map_ratio'] = 14/9
        func_args['lw_ratio'] = [14,9]
        func_args['output_dir']=temp_path+str(idx)+'_'+model
        x=pool.apply_async(func,kwds=func_args)
        #x.get() # for debug
        timer.sleep(1)
    pool.close()
    pool.join()

    pic_all=os.listdir(temp_path)
    if len(pic_all) == 0:
        shutil.rmtree(temp_path)
        return

    pic_all=sorted(pic_all,key=lambda i:int(i.split('_')[0]))
    if(show == 'tab'):
        png_name = 'evolution_ana_{}.png'.format(func.__name__)
        utl.save_tab(temp_path=temp_path,pic_all=pic_all,tab_size=tab_size,output_dir=output_dir,png_name=png_name,keep_temp=keep_temp)
    if(show == 'animation'):
        gif_name = 'evolution_ana_{}.gif'.format(func.__name__)
        utl.save_animation(temp_path=temp_path,pic_all=pic_all,output_dir=output_dir,gif_name=gif_name,keep_temp=keep_temp)

if __name__ == '__main__':

    func=draw_elements.T2m_zero_heatwaves
    evolution(func=func,initTime='21010708',fhours=list(np.arange(0,84,3)),show='animation',model='中央气象台中短期指导',func_other_args={'city':True},keep_temp=True,max_workers=6)

    func=draw_elements.T2m_mn24
    evolution(func=func,initTime='20122908',fhours=list(np.arange(0,84,3)),show='tab',model='中央气象台中短期指导',func_other_args={'city':True},keep_temp=True)

    #剖面时间
    time_cross=['20111808','20111814','20111820','20111902','20111908','20111914','20111920']
    #第一个剖面位置
    ed_point1=[37.0,124.4]
    st_point1=[44,122]
    #第二个剖面位置
    ed_point2=[47.1,134.3]
    st_point2=[38,120.888]
    model_name='GRAPES_GFS'
    func_other_args1={'ed_point':ed_point1,'st_point':st_point1,'map_extent':[120,140,35,50],'levels':[1000,975,950, 925, 900, 850, 800, 750,700,600,500],'data_source':'CIMISS'}
    func_other_args2={'ed_point':ed_point2,'st_point':st_point2,'map_extent':[120,140,35,50],'levels':[1000,975,950, 925, 900, 850, 800, 750,700,600,500],'data_source':'CIMISS'}
    func=draw_crossection.Crosssection_Wind_Theta_e_Qv
    evolution_ana(func=func,model=model_name,initTime=time_cross,fhour=0,keep_temp=True,max_workers=6,func_other_args=func_other_args2,show='animation')

    func=draw_moisture.gh_uv_rh
    evolution_ana(func=func,initTime=['20111808','20111814','20111820','20111902'],fhour=0)

    func=draw_thermal.TMP850_anomaly_uv
    evolution(func=func,initTime='20111708',fhours=[18,24,30,36])

    func=draw_moisture.gh_uv_rh
    structure3D(func=func,initTime='20111820')
    func=draw_synthetical.Miller_Composite_Chart
    evolution(func=func,initTime='20111708',fhours=[18,24,30,36])

    func=draw_QPF.gh_rain
    stability(func=func,target_time='20111720',latest_init_time='20111620',func_other_args={'data_source':'CIMISS'})

    vercompare(func=func,ninit=9,init_interval=6,func_other_args={},show='animation')