def Cassandra_dir(data_type=None,data_source=None,var_name=None,lvl=None
    ):

    dir_mdl_high={
            'ECMWF':{
                    'HGT':'ECMWF_HR/HGT/',
                    'UGRD':'ECMWF_HR/UGRD/',
                    'VGRD':'ECMWF_HR/VGRD/',
                    'IR':'GRAPES_GFS/MET_10/'
                    },
            'GRAPES_GFS':{
                    'HGT':'GRAPES_GFS/HGT/',
                    'UGRD':'GRAPES_GFS/UGRD/',
                    'VGRD':'GRAPES_GFS/VGRD/',
                    'IR':'GRAPES_GFS/INFRARED_BRIGHTNESS_TEMPERATURE/'
                    },
            'NCEP_GFS':{
                    'HGT':'NCEP_GFS/HGT/',
                    'UGRD':'NCEP_GFS/UGRD/',
                    'VGRD':'NCEP_GFS/VGRD/',
                    'IR':None
                    },
            'OBS':{            
                    'PLOT':'UPPER_AIR/PLOT/'
                    }
            }

    dir_mdl_sfc={
            'ECMWF':{
                    'u10m':'ECMWF_HR/UGRD_10M/',
                    'v10m':'ECMWF_HR/VGRD_10M/',
                    'PRMSL':'ECMWF_HR/PRMSL/',
                    'RAIN24':'ECMWF_HR/RAIN24/',
                    'RAIN06':'ECMWF_HR/RAIN06/',
                    'RAINC06':'ECMWF_HR/RAINC06/',
                    'TCWV':'ECMWF_HR/TCWV/',
                    '10M_GUST_3H':'ECMWF_HR/10_METER_WIND_GUST_IN_THE_LAST_3_HOURS/2M_ABOVE_GROUND/',
                    '10M_GUST_6H':'ECMWF_HR/10_METER_WIND_GUST_IN_THE_LAST_6_HOURS/2M_ABOVE_GROUND/',
                    'LCDC':'ECMWF_HR/LCDC/',
                    'TCDC':'ECMWF_HR/TCDC/'
                    },
            'GRAPES_GFS':{
                    'u10m':'GRAPES_GFS/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'GRAPES_GFS/VGRD/10M_ABOVE_GROUND/',
                    'PRMSL':'GRAPES_GFS/PRMSL/',
                    'RAIN24':'GRAPES_GFS/RAIN24/',
                    'RAIN06':'GRAPES_GFS/RAIN06/',
                    'RAINC06':'GRAPES_GFS/RAINC06/',
                    'TCWV':'GRAPES_GFS/PWAT/ENTIRE_ATMOSPHERE/',
                    '10M_GUST_3H':None
                    },
            'NCEP_GFS':{
                    'u10m':'NCEP_GFS/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'NCEP_GFS/VGRD/10M_ABOVE_GROUND/',
                    'PRMSL':'NCEP_GFS/PRMSL/',
                    'RAIN24':'NCEP_GFS/RAIN24/',
                    'RAIN06':'NCEP_GFS/RAIN06/',
                    'RAINC06':'NCEP_GFS/RAINC06/',
                    'TCWV':'NCEP_GFS/PWAT/ENTIRE_ATMOSPHERE/',
                    '10M_GUST':None
                    },

            'OBS':{
                'Tmx_2m':'SURFACE/TMP_MAX_24H_ALL_STATION/',
                'PLOT_GLOBAL_3H':'SURFACE/PLOT_GLOBAL_3H/',
                'CREF':'RADARMOSAIC/CREF/'
                    },

            'SCMOC':{
                    'u10m':'NWFD_SCMOC/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'NWFD_SCMOC/VGRD/10M_ABOVE_GROUND/',
                    'RAIN24':'NWFD_SCMOC/RAIN24/',
                    'RAIN06':'NWFD_SCMOC/RAIN06/',
                    'RAIN03':'NWFD_SCMOC/RAIN03/',
                    'Tmx_2m':'NWFD_SCMOC/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'Tmn_2m':'NWFD_SCMOC/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'T2m':'NWFD_SCMOC/TMP/2M_ABOVE_GROUND/',
                    'VIS':'NWFD_SCMOC/VIS_SURFACE/',
                    'rh2m':'NWFD_SCMOC/RH/2M_ABOVE_GROUND/'
                    },
            'SMERGE':{
                    'u10m':'NWFD_SMERGE/UGRD/10M_ABOVE_GROUND/',
                    'v10m':'NWFD_SMERGE/VGRD/10M_ABOVE_GROUND/',
                    'RAIN24':'NWFD_SMERGE/RAIN24/',
                    'RAIN06':'NWFD_SMERGE/RAIN06/',
                    'RAIN03':'NWFD_SMERGE/RAIN03/',
                    'Tmx_2m':'NWFD_SMERGE/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'Tmn_2m':'NWFD_SMERGE/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/',
                    'T2m':'NWFD_SMERGE/TMP/2M_ABOVE_GROUND/',  
                    'rh2m':'NWFD_SMERGE/RH/2M_ABOVE_GROUND/'               
                    },
            'CLDAS':{
                    'Tmx_2m':"CLDAS/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/"  
                    } 
            }
    if(data_type== 'high'):
        dir_full=dir_mdl_high[data_source][var_name]+str(lvl)+'/'

    if(data_type== 'surface'):
        dir_full=dir_mdl_sfc[data_source][var_name]

    return dir_full