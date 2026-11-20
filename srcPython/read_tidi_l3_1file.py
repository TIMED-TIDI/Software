#!/usr/bin/env python
# coding: utf-8

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import glob
import tial_fits
import pickle
import os.path

def convert_to_datetime(intime):
    intimearray = np.array(intime, dtype='float64')
    outtime = []
    base = dt.datetime(year = 1980, month = 1, day = 6)
    for t in intimearray:
        outtime.append(base + dt.timedelta(seconds = t))
    return outtime

def read_tidi_data(ifile):


    print(ifile)

    ncfile = Dataset(ifile, 'r')

    varss = ['time','lat','lon','alt_retrieved','data_ok',
        'u','v','p_status',
        'ascending']


    alltimes = np.array(ncfile.variables['time'][:], dtype='float64')
    lat = np.array(ncfile.variables['lat'][:])
    lon = np.array(ncfile.variables['lon'][:])
    alt = np.array(ncfile.variables['alt_retrieved'][:])

    u = np.array(ncfile.variables['u'][:])                   #2d
    v = np.array(ncfile.variables['v'][:])                   #2d
    var_u = np.array(ncfile.variables['var_u'][:])           #2d
    var_v = np.array(ncfile.variables['var_v'][:])           #2d

    lst = np.array(ncfile.variables['lst'][:])
    sza = np.array(ncfile.variables['sza'][:])

    p_status = np.array(ncfile.variables['p_status'][:])

    data_ok = np.array(ncfile.variables['data_ok'][:])
    data_ok = data_ok[:,0].astype('U13')
    asc_flag = np.array(ncfile.variables['ascending'][:])
    #print(asc_flag.shape)
    asc_flag = asc_flag[:,0].astype('U13')


    warm = np.array(ncfile.variables['measure_track'][:])
    warm = warm[:,0].astype('U13')

    lp =(lon>=0)&(lat>=-90)&(data_ok == 'T')&(p_status == 0)

    alltimes = alltimes[lp]
    lon,lat = lon[lp],lat[lp]
    lst = lst[lp]
    sza = sza[lp]

    u,v = u[lp,:], v[lp,:]
    var_u,var_v = var_u[lp,:], var_v[lp,:]


    asc_flag = asc_flag[lp]
    warm = warm[lp]

    ncfile.close()

    time = convert_to_datetime(alltimes)

    data = {'time' : time,
        'lon'     : lon,
        'lat'     : lat,
        'alt'     : alt,
        'u'       : u,
        'v'       : v,
        'var_u'   : np.sqrt(var_u),
        'var_v'   : np.sqrt(var_v),
        'lst'     : lst,
        'sza'     : sza,
        'warm'    : warm,
        'ascflag' : asc_flag}

    return data

if __name__ == '__main__':

    ifile = 'TIDI_PB_2020001_P0100_S0450_D011_R01.VEC'
    data = read_tidi_data(ifile)



