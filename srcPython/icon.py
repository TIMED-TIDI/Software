#!/usr/bin/env python
# coding: utf-8

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import re
import sys

#-----------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------

def get_args(argv):

    filelist = []

    help = 0

    for arg in argv:

        IsFound = 0

        if (not IsFound):
            m = re.match(r'-help',arg)
            if m:
                help = 1
                IsFound = 1

            if IsFound==0 and not(arg==argv[0]):
                filelist.append(arg)


    args = {'filelist':filelist,
            'help': help}

    return args


def convert_to_datetime(intime):
    intimearray = np.array(intime, dtype='float64')
    outtime = []
    base = dt.datetime(year = 1970, month = 1, day = 1)
    for t in intimearray:
        outtime.append(base + dt.timedelta(seconds = t/1000.0))
    return outtime

def read_1file_l1(ifile):

    ncfile = Dataset(ifile, 'r')
    alltimes = np.array(ncfile.variables['Epoch'][:], dtype='float64')
    lat = np.array(ncfile.variables['ICON_L21_Latitude'][:])
    lon = np.array(ncfile.variables['ICON_L21_Longitude'][:])
    alt = np.array(ncfile.variables['ICON_L21_Altitude'][:])
    qflag = np.array(ncfile.variables['ICON_L21_Wind_Quality'][:])
    los = np.array(ncfile.variables['ICON_L21_Line_of_Sight_Wind'][:],dtype='float64')
    err = np.array(ncfile.variables['ICON_L21_Line_of_Sight_Wind_Error'][:],dtype='float64')
    dir = np.array(ncfile.variables['ICON_L21_Line_of_Sight_Azimuth'][:])
    node = np.array(ncfile.variables['ICON_L21_Orbit_Node'][:])

    lp = (alltimes > 0)&(node != -127)
    lat,lon,alt,los,err,dir = lat[lp,:],lon[lp,:],alt[lp,:],los[lp,:],err[lp,:],dir[lp,:]
    qflag = qflag[lp,:]
    alltimes,node = alltimes[lp],node[lp]
    alltimes = convert_to_datetime(alltimes)

    df = pd.DataFrame()
    for i,it in enumerate(alltimes):

        df0 = pd.DataFrame()

        df0['lat'] = lat[i,:]
        df0['lon'] = lon[i,:]
        df0['alt'] = alt[i,:]
        df0['dir'] = dir[i,:]
        df0['los'] = los[i,:]
        df0['err'] = err[i,:]
        df0['qflag'] = qflag[i,:]
        indexNames = df0[(df0['los']==9.969209968386869e+36)|
                         (df0['err']==9.969209968386869e+36)].index
        df0.drop(indexNames,inplace=True)
        df0 = df0[df0['qflag']==1]
        df0['node'] = node[i]
        df0['times'] = it

        df = df.append(df0,ignore_index=True)


    #plt.plot(df['lon'],df['lat'],'.')
    #plt.show()
    return df


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Main Code!
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

args = get_args(sys.argv)

if (args["help"]):

    print('Usage : ')
    print('icon.py file[s] to read')
    print('Usage : ')

df = pd.DataFrame()
for i,infile in enumerate(args['filelist']):

    print('Reading file : '+infile)
    df0 = read_1file_l1(infile)
    df = df.append(df0,ignore_index=True)

#print(df.info)


