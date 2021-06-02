#!/usr/bin/env python

import numpy as np
import datetime as dt
import re
import sys

#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------

def get_args(argv):

    filelist = []
    outfile = 'champ_'
    localtime = 0
    
    hours = 24

    help = 0
    
    for arg in argv:

        IsFound = 0

        if (not IsFound):

            m = re.match(r'-outfile=(.*)',arg)
            if m:
                outfile = m.group(1)
                IsFound = 1

            m = re.match(r'-localtime',arg)
            if m:
                localtime = 1
                IsFound = 1

            m = re.match(r'-help',arg)
            if m:
                help = 1
                IsFound = 1

            if IsFound==0 and not(arg==argv[0]):
                filelist.append(arg)


    args = {'filelist':filelist,
            'localtime': localtime,
            'help': help,
            'outfile': outfile}

    return args

#-----------------------------------------------------------------------------
# read in CHAMP Wind file
#-----------------------------------------------------------------------------

def read_champ_wind_file(filein):

    fpin = open(filein, 'r')

    # Read header:
    for line in fpin:

        # This should be the last line of the header:
        m = re.match(r'#                           m',line)
        if m:
            break
    
    data = {
        'times' : [],
        'lons' : [],
        'lats' : [],
        'alts' : [],
        'localtimes' : [],
        'east' : [],
        'north' : [],
        'along_east' : [],
        'along_north' : [],
        'cross_east' : [],
        'cross_north' : [],
        'file' : filein}
    
    # Read main data
    IsFirst = 1
    for line in fpin:
        cols = line.split()

        # figure out time:
        date = np.array(cols[0].split('-')).astype(int)
        time = np.array(cols[1].split(':')).astype(float).astype(int)
        data['times'].append(dt.datetime(date[0], date[1], date[2],
                                         time[0], time[1], time[2]))

        data['alts'].append(float(cols[3])/1000.0)
        data['lons'].append((float(cols[4])+360) % 360.0 )
        data['lats'].append(float(cols[5]))
        data['localtimes'].append(float(cols[6]))
        data['east'].append(float(cols[8]))
        data['north'].append(float(cols[9]))
        if (IsFirst):
            data['cross_east'].append(0.0)
            data['cross_north'].append(0.0)
            IsFirst = 0
        else:
            dn = data['lats'][-1] - data['lats'][-2]
            stretch = 1.0 /  np.cos(data['lats'][-1]*np.pi/180.0)
            de = (data['lons'][-1] - data['lons'][-2]) * stretch
            mag = np.sqrt(dn*dn + de*de)
            data['along_east'].append(de/mag)
            data['along_north'].append(dn/mag)

    data['along_east'][0] = data['along_east'][1]
    data['along_north'][0] = data['along_north'][1]
    # rotate data 90 deg ccw for cross-track direction
    data['cross_north'] = np.array(data['along_east'])
    data['cross_east'] = -np.array(data['along_north'])

    fpin.close()

    return data

#-----------------------------------------------------------------------------
# Write satellite file
#-----------------------------------------------------------------------------

def write_file(fileout, data):

    fpout = open(fileout, 'w')

    fpout.write('\n')
    fpout.write('Output from file: '+data['file']+'\n')
    fpout.write('Using champ.py\n')
    fpout.write('Data from ftp://thermosphere.tudelft.nl/version_01/CHAMP_data/\n')
    fpout.write('\n')
    fpout.write('Format:\n')
#    fpout.write('year month day hour minute second milli-sec lon lat alt\n')
#    fpout.write('\n')
#    fpout.write('#START\n')
#
#    lat0 = data['lats'][0]
#    IsReported = 0
#    for i,time in enumerate(data['times']):
#
#        t = ActualTime + dt.timedelta(seconds = time)
#        
#        date = t.strftime('%Y %m %d %H %M %S 00 ')
#        lon = (data['lons'][i] + 360.0) % 360.0
#        lat = data['lats'][i]
#        if ((lat >= 0) and (lat0 < 0) and (IsReported == 0)):
#            ut = t.hour + t.minute/60.0 + t.second/3600.0
#            LocalTime = (lon/15.0 + ut) % 24.0
#            print('Local Time of Ascending Node :', LocalTime)
#            IsReported = 1
#        lat0 = lat
#        pos = '%7.2f %7.2f %8.2f\n' % \
#            (lon, data['lats'][i], data['alts'][i])
#        fpout.write(date+pos)
    
    fpout.close()

    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Main Code!
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

args = get_args(sys.argv)

if (args["help"]):

    print('Usage : ')
    print('champ.py -outfile=output file)')
    print('         file[s] to read')
    print('Usage : ')

for i,infile in enumerate(args['filelist']):

    print('Reading file : '+infile)
    data = read_champ_wind_file(infile)
    if (args["localtime"]):
        for i, lt in enumerate(data["localtimes"]):
            if (i > 0):
                if ((data["lats"][i] > 0.0) and
                    (data["lats"][i-1] < 0.0)):
                    print("Time : ", data["times"][i])
                    print("   Local time of Ascending Node : ", lt)
                         

