#!/usr/bin/env python

from netCDF4 import Dataset
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import argparse

# ----------------------------------------------------------------------
# Function to parse input arguments
# ----------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(description = 'Process TIDI data files.')
    parser.add_argument('files', metavar = 'file', nargs = '+', \
                        help = 'Files to process')
    parser.add_argument('--foo', nargs='?', help='foo help', \
                        default='blah')
    parser.add_argument('--alt', '-alt', nargs=1, \
                        help='altitude to plot (km)', \
                        default=95.0, type = float)
    parser.add_argument('--latplot', '-latplot', \
                        help='Make a lat vs time plot', action='store_true')
    parser.add_argument('--altplot', '-altplot', \
                        help='Make a scatter plot of LOS wind vs alt', \
                        action='store_true')

    args = parser.parse_args()

    return args

# ----------------------------------------------------------------------
# Main Code
# ----------------------------------------------------------------------

def convert_to_datetime(intime):

    intimearray = np.array(intime, dtype='float64')
    outtime = []
    base = dt.datetime(year = 1980, month = 1, day = 6)
    for t in intimearray:
        outtime.append(base + dt.timedelta(seconds = t))

    return outtime
    
# ----------------------------------------------------------------------
# Read TIDI Data
# ----------------------------------------------------------------------

def read_tidi_data(file):

    ncfile = Dataset(file, 'r')

    #print("Variables in file : ")
    #for var in ncfile.variables.values():
    #    print(var.name)

    #time = np.double(np.array(ncfile.variables['time'][:]))
    #print(time[0]/(365.25*86400.0))
    #
    #first = base + dt.timedelta(seconds = time[0])
    #last = base + dt.timedelta(seconds = time[-1])

    alltimes = np.array(ncfile.variables['time'][:], dtype='float64')

    #angles = 315 (5), 225 (4), 135 (3), 45 (2), 405 - cal (1)
    angles = [45, 135, 225, 315, 405]
    
    sc_lat = np.array(ncfile.variables['sc_lat'][:])
    tel_id = np.array(ncfile.variables['tel_id'][:])

    sc_lat = np.array(ncfile.variables['sc_lat'][:])
    sc_lon = np.array(ncfile.variables['sc_lon'][:])
    tp_lat = np.array(ncfile.variables['tp_lat'][:])
    tp_lon = np.array(ncfile.variables['tp_lon'][:])
    tp_alt = np.array(ncfile.variables['tp_alt'][:])
    tel_id = np.array(ncfile.variables['tel_id'][:])
    t_doppler = np.array(ncfile.variables['t_doppler'][:])
    t_rot = np.array(ncfile.variables['t_rot'][:])
    s_los = np.array(ncfile.variables['s'][:])
    s_var = np.array(ncfile.variables['var_s'][:])
    p_status = np.array(ncfile.variables['p_status'][:])
    table_index = np.array(ncfile.variables['table_index'][:])
    los_dir = np.array(ncfile.variables['los_direction'][:])
    asc_flag = np.array(ncfile.variables['ascending'][:])
    asc_flag = asc_flag.astype('U13')
    sc_sza = np.array(ncfile.variables['sc_sza'][:])
    tp_sza = np.array(ncfile.variables['tp_sza'][:])
        
    times = {}
    tplon = {}
    tplat = {}
    tpalt = {}
    sclon = {}
    sclat = {}
    scalt = {}
    tdop = {}
    trot = {}
    los = {}
    dir = {}
    var = {}
    ascflag = {}
    scsza = {}
    tpsza = {}
    
    for a in angles:
        tmp = alltimes[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        times[a] = convert_to_datetime(tmp)
        tplon[a] = tp_lon[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        tplat[a] = tp_lat[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        tpalt[a] = tp_alt[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        sclon[a] = sc_lon[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        sclat[a] = sc_lat[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        scalt[a] = tpalt[a]
        tdop[a] = t_doppler[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        trot[a] = t_rot[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        los[a] = s_los[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        dir[a] = los_dir[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        var[a] = np.sqrt(s_var[(sc_lon>0) & (tel_id == a) & (p_status == 0)])
        ascflag[a] = asc_flag[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        scsza[a] = sc_sza[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        tpsza[a] = tp_sza[(sc_lon>0) & (tel_id == a) & (p_status == 0)]

    ncfile.close()
    data = {'times' : times,
            'tplon' : tplon,
            'tplat' : tplat,
            'tpalt' : tpalt,
            'sclon' : sclon,
            'sclat' : sclat,
            'scalt' : scalt,
            'tdop' : tdop,
            'trot' : trot,
            'los' : los,
            'dir' : dir,
            'var' : var}

    return data
    
# ----------------------------------------------------------------------
# Main Code
# ----------------------------------------------------------------------


args = parse_args()
print(args.files)
print(args.alt)
print(args.latplot)

file = args.files[-1]

tididata = read_tidi_data(file)

iS = 0
iE = 1000

angle = 135

tplon = tididata["tplon"][angle][iS:iE]
tplat = tididata["tplat"][angle][iS:iE]
tpalt = tididata["tpalt"][angle][iS:iE]
lon = tididata["sclon"][angle][iS:iE]
lat = tididata["sclat"][angle][iS:iE]
alt  = tididata["scalt"][angle][iS:iE]
tdop = tididata["tdop"][angle][iS:iE]
trot = tididata["trot"][angle][iS:iE]
los = tididata["los"][angle][iS:iE]
dir = tididata["dir"][angle][iS:iE]
var = tididata["var"][angle][iS:iE]
times = tididata["times"][angle][iS:iE]

maxi = 500.0

if (args.altplot):    
    

    for i,l in enumerate(los):
        if ((np.abs(l) < maxi) and (np.abs(l) > var[i])):
            print(l,var[i])
            plt.plot([l], alt[i], 'bo')
            a = alt[i]
            v = var[i]
            x = [l-v, l+v]
            y = [a, a]
            plt.plot(x,y,'r')
    plt.xlim(-maxi,maxi)
    
else:

    #plt.plot(times,alt,'b.')

    # can we figure out how to plot two telescopes here, both on the
    # same side of the S/C, so that we can get real wind vectors?

    scale = 1.0 / 40.0

    for i,l in enumerate(los):
        a = alt[i]
        v = var[i]
        if ((np.abs(l) < maxi) & (a>250) & (np.abs(l) > v)):
            la = tplat[i]
            lo = tplon[i]
            print(la, lo, dir[i])

            plt.plot(lon[i],lat[i],'bo')
            plt.plot(tplon[i],tplat[i],'r.')


            d = dir[i] * np.pi / 180.0
            dx = np.sin(d) / np.abs(np.cos(lat[i] * np.pi / 180.0))
            dy = np.cos(d)

            dr = np.sqrt(dx*dx + dy*dy)
            xhat = dx/dr
            yhat = dy/dr
            vx = l * scale * xhat
            vy = l * scale * yhat
            x = [lo, lo + vx]
            y = [la, la + vy]
            plt.plot(x,y,'r')

            scla = lat[i]
            sclo = lon[i]
            x = [sclo, lo]
            y = [scla, la]
            #plt.plot(x,y,'g')

    plt.axes().set_aspect('equal')
            
plt.show()



