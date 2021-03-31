#!/usr/bin/env python

from netCDF4 import Dataset
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

file = "TIDI_PB_2021001_P0500_S0651_D010_R01.LOS"
file = "TIDI_PB_2021003_P0500_S0704_D011_R01.LOS"
ncfile = Dataset(file, 'r')

print(ncfile)

print("Variables in file : ")
for var in ncfile.variables.values():
    print(var.name)

date = ncfile.variables['ut_date']
print(date)
nlos, nchars = date.shape

time = np.double(np.array(ncfile.variables['time'][:]))
print(time[0]/(365.25*86400.0))

base = dt.datetime(year = 1980, month = 1, day = 6)
first = base + dt.timedelta(seconds = time[0])
last = base + dt.timedelta(seconds = time[-1])

print(first)
print(last)

nPts = 100

iStart = 0
iEnd = 12000

sc_lat = np.array(ncfile.variables['sc_lat'][:])[iStart:iEnd]
sc_lon = np.array(ncfile.variables['sc_lon'][:])[iStart:iEnd]
tp_lat = np.array(ncfile.variables['tp_lat'][:])[iStart:iEnd]
tp_lon = np.array(ncfile.variables['tp_lon'][:])[iStart:iEnd]
tp_alt = np.array(ncfile.variables['tp_alt'][:])[iStart:iEnd]
tel_id = np.array(ncfile.variables['tel_id'][:])[iStart:iEnd]
print(tel_id)

t_doppler = np.array(ncfile.variables['t_doppler'][:])[iStart:iEnd]
t_rot = np.array(ncfile.variables['t_rot'][:])[iStart:iEnd]
s_los = np.array(ncfile.variables['s'][:])[iStart:iEnd]
s_var = np.array(ncfile.variables['var_s'][:])[iStart:iEnd]
p_status = np.array(ncfile.variables['p_status'][:])[iStart:iEnd]
table_index = np.array(ncfile.variables['table_index'][:])[iStart:iEnd]
los_dir = np.array(ncfile.variables['los_direction'][:])[iStart:iEnd]

print(los_dir)


subtime = time[iStart:iEnd]

ncfile.close()

angle = 45

# According to documents:
# angles = 315 (5), 225 (4), 135 (3), 45 (2), 405 - cal (1)

#plt.scatter(lon, lat)
#
tplon = tp_lon[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]
tplat = tp_lat[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]
tpalt = tp_alt[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]

lon = sc_lon[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]
lat = sc_lat[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]
alt  = tpalt
tdop = t_doppler[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]
trot = t_rot[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]
los = s_los[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]
dir = los_dir[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]
var = np.sqrt(s_var[(sc_lon>0) & (tel_id == angle) & (p_status == 0)])


subsubtime = subtime[(sc_lon>0) & (tel_id == angle) & (p_status == 0)]

times = []
for t in subsubtime:
    times.append(base + dt.timedelta(seconds = t))

iPlotType = 0
maxi = 500.0

if (iPlotType == 0):    
    
    plt.plot(los,alt,'bo')
    plt.xlim(-maxi,maxi)

    for i,l in enumerate(los):
        if (np.abs(l) < maxi):
            a = alt[i]
            v = var[i]
            x = [l-v, l+v]
            y = [a, a]
            plt.plot(x,y,'r')
    
else:

    #plt.plot(times,alt,'b.')

    scale = 1.0 / 40.0
    plt.plot(lon[(alt>250)],lat[(alt>250)],'bo')
    plt.plot(tplon[(alt>250)],tplat[(alt>250)],'r.')

    for i,l in enumerate(los):
        a = alt[i]
        if ((np.abs(l) < maxi) & (a>250)):
            la = tplat[i]
            lo = tplon[i]
            d = dir[i] * np.pi / 180.0
            dx = l * scale * np.sin(d) / np.abs(np.cos(lat[i] * np.pi / 180.0))
            dy = l * scale * np.cos(d)
            x = [lo, lo + dx]
            y = [la, la + dy]
            plt.plot(x,y,'r')

            
#plt.plot(var,alt,'r.')


#print(times)

#plt.scatter(tp_lon[sc_lon>0], tp_lat[sc_lon>0],'r.')
plt.show()



