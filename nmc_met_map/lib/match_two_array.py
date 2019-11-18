# _*_ coding: utf-8 _*_

"""
  Usually used for match the sta_ID to all the Sta_ID which is used to verificate the forecast
"""

from datetime import datetime
import itertools
import string
from datetime import datetime, timedelta
import pkg_resources
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
import matplotlib.patheffects as mpatheffects
import matplotlib.ticker as mticker



def match_two_array(array1='none', array2='none'):
    """
    Arguments:
        Usually arary1 is station ID from the observed 1hr precipitation 
        array2 is station ID from the verification accordance.

    Return:
    
    idx1 and idx2 are the index of array1 and array2 where the station ID are the same
    """
    idx2=0
    idx1=0
    nsta1=len(array1)
    ns=0
    for i in range(0,nsta1):
        idx=np.where(array2 == array1[i])
        if(idx[0] >= 0):
            if(ns == 0):
                idx2=idx[0]
                idx1=i
            if(ns != 0):
                idx2=np.append(idx2,idx[0])
                idx1=np.append(idx1,i)
            ns=ns+1
    return idx1,idx2