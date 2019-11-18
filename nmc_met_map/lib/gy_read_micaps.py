"""
Read micaps data file.
"""

import os.path
import numpy as np
import xarray as xr
import pandas as pd
from datetime import datetime

def read_micaps_8(fname, limit=None):
    """
    Read Micaps 8 type file (general scatter point)
    此类数据主要用于读城市报数据
    :param fname: micaps file name.
    :param limit: region limit, [min_lat, min_lon, max_lat, max_lon]
    :return: data, pandas type
    :Examples:
    >>> data = read_micaps_3('\\10.10.34.158/micaps/diamond/cityfcst_jm2/19070112.048')
    """

    # check file exist
    if not os.path.isfile(fname):
        return None

    # read contents
    try:
        with open(fname, 'r') as f:
            # txt = f.read().decode('GBK').replace('\n', ' ').split()
            txt = f.read().replace('\n', ' ').split()
    except IOError as err:
        print("Micaps 16 file error: " + str(err))
        return None

    # head information
    head_info = txt[2]

    # date and time
    nsta = int(txt[3])

    # cut data
    txt = np.array(txt[4:])
    txt.shape = [nsta, 4]

    # initial data
    columns = list(['ID', 'lon', 'lat', 'alt', 'Weather1','winddir1'
        ,'windsp1','Tmin','Tmax','Weather2','Winddir2','Windsp2'])
    #columns.extend(['V%s' % x for x in range(4)])
    data = pd.DataFrame(txt, columns=columns)

    # cut the region
    if limit is not None:
        data = data[(limit[0] <= data['lat']) & (data['lat'] <= limit[2]) &
                    (limit[1] <= data['lon']) & (data['lon'] <= limit[3])]

    data['nstation']=nsta

    # check records
    if len(data) == 0:
        return None
    # return
    return data