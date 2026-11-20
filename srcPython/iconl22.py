#!/usr/bin/env python
# coding: utf-8

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt


def convert_to_datetime(intime):
    intimearray = np.array(intime, dtype='float64')
    outtime = []
    base = dt.datetime(year = 1970, month = 1, day = 1)
    for t in intimearray:
        outtime.append(base + dt.timedelta(seconds = t/1000.0))
    return outtime

def read_l22_1file(ifile)

    #ifile = './l2-2_001/ICON_L2-2_MIGHTI_Vector-Wind-Green_2020-01-01_v04r000.NC'
    ncfile = Dataset(ifile, 'r')

    alltimes = np.array(ncfile.variables['Epoch'][:], dtype='float64')
    lat = np.array(ncfile.variables['ICON_L22_Latitude'][:])
    lon = np.array(ncfile.variables['ICON_L22_Longitude'][:])
    alt = np.array(ncfile.variables['ICON_L22_Altitude'][:])
    qflag = np.array(ncfile.variables['ICON_L22_Wind_Quality'][:])
    v = np.array(ncfile.variables['ICON_L22_Meridional_Wind'][:],dtype='float64')
    verr = np.array(ncfile.variables['ICON_L22_Meridional_Wind_Error'][:],dtype='float64')
    u = np.array(ncfile.variables['ICON_L22_Zonal_Wind'][:],dtype='float64')
    uerr = np.array(ncfile.variables['ICON_L22_Zonal_Wind_Error'][:],dtype='float64')
    node = np.array(ncfile.variables['ICON_L22_Orbit_Node'][:])

    lp = (alltimes > 0)
    lat,lon = lat[lp,:],lon[lp,:]
    alltimes = alltimes[lp]
    u,uerr,v,verr = u[lp,:],uerr[lp,:],v[lp,:],verr[lp,:]
    node,qflag = node[lp,:],qflag[lp,:]

    alltimes = convert_to_datetime(alltimes)

    df = pd.DataFrame()
    for i,it in enumerate(alltimes[0:len(alltimes)]):

        df0 = pd.DataFrame()
        df0['lat'] = lat[i,:]
        df0['lon'] = lon[i,:]
        df0['alt'] = alt
        df0['u'] = u[i,:]
        df0['v'] = v[i,:]
        df0['uerr'] = uerr[i,:]
        df0['verr'] = verr[i,:]
        df0['qflag'] = qflag[i,:]
        df0['node'] = node[i,:]
        indexNames = df0[(df0['u']==9.969209968386869e+36)|
                         (df0['v']==9.969209968386869e+36)].index
        df0.drop(indexNames,inplace=True)
        df0 = df0[(df0['qflag']==1)&(df0['node'] != -127)]
        df0['times'] = it

        df = df.append(df0,ignore_index=True)

    return df



