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

#times = []
#for iLos in np.arange(nlos):
#    d = ''
#    for c in date[0][:]:
#        d = d+c.decode("utf-8")
#    times.append(dt.datetime.strptime(d,"%Y%j"))
#print(times)



time = np.double(np.array(ncfile.variables['time'][:]))
print(time[0]/(365.25*86400.0))

base = dt.datetime(year = 1980, month = 1, day = 6)
first = base + dt.timedelta(seconds = time[0])
last = base + dt.timedelta(seconds = time[-1])

print(first)
print(last)

nPts = 100

sc_lat = np.array(ncfile.variables['sc_lat'][:])[0:nPts]
sc_lon = np.array(ncfile.variables['sc_lon'][:])[0:nPts]

tp_lat = np.array(ncfile.variables['tp_lat'][:])[0:nPts]
tp_lon = np.array(ncfile.variables['tp_lon'][:])[0:nPts]
tp_alt = np.array(ncfile.variables['tp_alt'][:])[0:nPts]
print(tp_alt)

tel_id = np.array(ncfile.variables['tel_id'][:])[0:nPts]
print(tel_id)

ncfile.close()

lon = sc_lon[sc_lon>0]
lat = sc_lat[sc_lon>0]
plt.scatter(lon, lat)

lon = tp_lon[sc_lon>0]
lat = tp_lat[sc_lon>0]
#col = tel_id[sc_lon>0]
col = tp_alt[sc_lon>0]
plt.scatter(lon, lat, c=col)


#plt.scatter(tp_lon[sc_lon>0], tp_lat[sc_lon>0],'r.')
plt.show()



