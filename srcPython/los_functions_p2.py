
from netCDF4 import Dataset
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import glob
import scipy.special


def grid_each_orbit_weight_orbid(df1):

    BinLat = 5
    latinp = np.arange(-90+BinLat/2,90,BinLat)
    nlat = len(latinp)
    num_orb = set(np.asarray(df1['orbid']))
    cols = df1.columns

    losinp = np.ones((len(num_orb),nlat))*np.nan
    weight = np.zeros((len(num_orb),nlat))

    #print('-->>> orbit number',num_orb)

    dfp = pd.DataFrame(columns=df1.columns)
    for k22,i in enumerate(num_orb):

        dft1 = df1[df1['orbid']==i]

        los1 = np.asarray(dft1['los'])
        var1 = np.asarray(dft1['var'])
        dir1 = np.asarray(dft1['dir'])
        tplon1 = np.asarray(dft1['tplon'])
        tplat1 = np.asarray(dft1['tplat'])
        times1 = dft1['times']

        dfp1 = pd.DataFrame(columns=df1.columns)
        for k11,k1 in enumerate(latinp):

            lp = (tplat1>=(k1-BinLat/2))&(tplat1<=(k1+BinLat/2))
            if len(tplat1[lp])==0:
                continue
            dftmp0 = dft1[lp]

            los2 = los1[lp]
            var2 = var1[lp]
            times2 = times1[lp]


            tmp = var2**2
            wit = 1.0/tmp

            # variance weight
            u_w = np.sum(wit*los2)/np.sum(wit) # weighted mean
            sd_2 = 1.0/np.sum(1.0/tmp)         # std of the weighted mean
            yvar1 = np.sqrt(sd_2)

            dftmp0.reset_index(drop=True,inplace=True)
            indx1 = np.asarray(dftmp0.index)
            indxm0 = int(np.nanmedian(indx1))
            dd = abs(indx1-indxm0)
            indxm = indx1[np.nanargmin(dd)]

            for ic in cols:
                if ic=='tplat':
                    dfp1.loc[k11,ic] = k1
                elif ic == 'los':
                    dfp1.loc[k11,ic] = u_w
                elif ic == 'var':
                    dfp1.loc[k11,ic] = yvar1

                else:
                    dfp1.loc[k11,ic] = dftmp0.loc[indxm,ic]
            losinp[k22,k11] = u_w
            weight[k22,k11] = len(dftmp0)/yvar1

        dfp = dfp.append(dfp1,ignore_index=True)

    return dfp,losinp,weight

def harm_sph_func(vars,a,b):

    lon,lat = vars

    y = np.ones(len(lon))*np.nan
    colat = (90.0-lat)/180.0*np.pi
    z = np.cos(colat)
    pmn = scipy.special.lpmv(m, n, z)

    y = pmn * (a * np.cos(lon/180.0 * np.pi * m) +
            b * np.sin(lon/180.0 * np.pi * m))
    return y

def fit_func_lsq(lon,lat,var,f_odd):
    from scipy.optimize import curve_fit

    # the associated Legendre function of the first kind of order m and degree n
    # m: 0-5
    # n-m: 0-5
    # (0-9,0-24 by Eliasen and Machenhauer (1968))
    # n-m odd chosen only

    global m,n

    lon = np.reshape(lon,(len(lon),-1))
    lat = np.reshape(lat,(len(lat),-1))
    var = np.reshape(var,(len(var),-1))
    lp = var==var

    lon,lat,var = lon[lp],lat[lp],var[lp]

    lon,lat = lon.astype(float),lat.astype(float)
    p0 = [20,20]
    lb = []
    ub = []

    cmpn = mpl.cm.get_cmap('bwr')
    ipp = -1

    vmean = np.nanmean(var)
    y = var.copy()-vmean

    for n in np.arange(10):
        for m in np.arange(5):

            if f_odd==1:
                if ((n-m)%2==0)|(n<m)|((n-m)>24):
                    continue
            else:
                if (n<m)|((n-m)>24):
                    continue
            ipp=ipp+1
            params1,pcov1 = curve_fit(harm_sph_func, (lon,lat),y,p0=p0)
            #print('m/n',m,n,params1)
            y_lsq = harm_sph_func((lon,lat), *params1)

            if ipp==0:
                ys = y_lsq.copy()
            else:
                ys = ys + y_lsq

    return lon,lat,ys+vmean

def curvefit():
    popt,_ = curve_fit(objective,x,y)
    y_new = objective(x_new,popt)
    return y_new

def cal_wind_los_dir(los1,dir1,los2,dir2):

    sinphi1 = np.sin((dir1/180*np.pi))
    cosphi1 = np.cos((dir1/180*np.pi))

    sinphi2 = np.sin((dir2/180*np.pi))
    cosphi2 = np.cos((dir2/180*np.pi))

    v = -(los1 * sinphi2 - los2 * sinphi1)/(
            cosphi1 * sinphi2 - cosphi2 * sinphi1)
    u = -(los1 * cosphi2 - los2 * cosphi1)/(
            sinphi1 * cosphi2 - sinphi2 * cosphi1)

    return u,v

def cal_wind_vector_nearest(df1,df2):

    colums = ['times','tplat','tplon','dir','los','var']
    cols = colums.copy()
    colums.extend(['dir2','los2','var2','u','v','uvar','vvar'])
    df_wvec = df1[cols].copy()

    df_wvec['dir2'] = np.ones(len(df1))*np.nan
    df_wvec['los2'] = np.ones(len(df1))*np.nan
    df_wvec['u'] = np.ones(len(df1))*np.nan
    df_wvec['v'] = np.ones(len(df1))*np.nan

    npts = len(df1['tplat'])
    u = np.ones(npts)*np.nan
    v = np.ones(npts)*np.nan
    uvar = np.ones(npts)*np.nan
    vvar = np.ones(npts)*np.nan
    losa2 = np.ones(npts)*np.nan
    vara2 = np.ones(npts)*np.nan
    dira2 = np.ones(npts)*np.nan

    lontest = []
    lattest = []
    lontest1 = []
    lattest1 = []
    detdir = []

    for k in np.arange(npts):

        lon1,lat1 = df1['tplon'].iloc[k],df1['tplat'].iloc[k]

        lont = np.asarray(df2['tplon'])
        latt = np.asarray(df2['tplat'])

        lp1 = (latt>(lat1-2.5))&(latt<(lat1+2.5))
        lef = lon1-5
        rigt = lon1+5

        if lef <0:
            lp2 = (lont>(lef+360))|(lont<rigt)
        elif rigt > 360:
            lp2 = (lont<(rigt%360))|(lont>lef)
        else:
            lp2 = (lont>lef)&(lont<rigt)

        lp = lp1&lp2

        dftmp = df2[lp]

        lont2 = np.asarray(dftmp['tplon'])

        if (len(lont2))==0:
            continue

        # group 1
        lont2_a = lont2[abs(lont2-lon1)<=10]

        flag_gp1 = 0

        if len(lont2_a) !=0:

            idx1 = np.argmin((abs(lont2_a-lon1)))
            abslon1 = np.nanmin(abs(lont2_a-lon1))
            flag_gp1 = 1
        # group 2

        lont2_a = lont2[abs(lont2-lon1)>=350]

        flag_gp2 = 0
        if len(lont2_a) !=0:
            idx2 = np.argmax((abs(lont2_a-lon1)))
            abslon2 = np.nanmax(abs(lont2_a-lon1))
            if abslon2>360:
                sys.exit('abslon2>360!')
            flag_gp2 = 1

        if (flag_gp1==1)&(flag_gp2==1):

            if abslon1<(360-abslon2):
                idx = idx1
            else:
                idx = idx2
        elif (flag_gp1==1)&(flag_gp2==0):
            idx = idx1
        elif (flag_gp1==0)&(flag_gp2==1):
            idx = idx2
        else:
            sys.exit('check groups')

        df_ipt = dftmp.iloc[idx]

        detdir.append((df_ipt['dir']-df1['dir'].iloc[k]))

        lontest.append(df_ipt['tplon'])
        lattest.append(df_ipt['tplat'])

        lontest1.append(lon1)
        lattest1.append(lat1)

        los1 = df1['los'].iloc[k]
        var1 = df1['var'].iloc[k]
        dir1 = df1['dir'].iloc[k]

        los2 = df_ipt['los']
        var2 = df_ipt['var']
        dir2 = df_ipt['dir']

        u[k],v[k] = cal_wind_los_dir(los1,dir1,los2,dir2)
        uvar[k],vvar[k] = cal_wind_los_dir(var1,dir1,var2,dir2)
        losa2[k],dira2[k],vara2[k] = los2,dir2, var2

    df_wvec['los2']=losa2
    df_wvec['var2']=vara2
    df_wvec['dir2']=dira2
    df_wvec['u']=u
    df_wvec['v']=v
    df_wvec['uvar']=abs(uvar)
    df_wvec['vvar']=abs(vvar)

    return df_wvec

def cal_1day_2tel(ifile1,ifile2):

    dfall = pd.DataFrame()
    date = ifile1[0][-11:-4]

    if ascf == 'F':
        asf = 'DES'
    else:
        asf = 'AS'

    df01 = pd.read_pickle(ifile1)
    df02 = pd.read_pickle(ifile2)

    df01 = df01[(df01['tpalt']==alt_in)&(df01['ascflag']==ascf)]
    df02 = df02[(df02['tpalt']==alt_in)&(df02['ascflag']==ascf)]

    if (len(df01)==0)|(len(df02)==0):
        return pd.DataFrame()

    df01,lost1,weit1 = grid_each_orbit_weight_orbid(df01)
    df02,lost2,weit2 = grid_each_orbit_weight_orbid(df02)

    dfall = cal_wind_vector_nearest(df01,df02)

    dfall.dropna(subset=['u'],inplace=True)
    if len(dfall)<10:
        return pd.DataFrame()

    lon = np.asarray(dfall['tplon'])
    lat = np.asarray(dfall['tplat'])
    los = np.asarray(dfall['los'])
    u = np.asarray(dfall['u'])
    v = np.asarray(dfall['v'])
    uvar = np.asarray(dfall['uvar'])
    vvar = np.asarray(dfall['vvar'])

    lonf,latf,u_fit = fit_func_lsq(lon,lat,u,0)
    lonf,latf,v_fit = fit_func_lsq(lon,lat,v,0)

    dfall['u_fit'] = np.ones(len(dfall))*np.nan
    dfall['v_fit'] = np.ones(len(dfall))*np.nan

    dfall['u_fit'].iloc[u==u] = u_fit
    dfall['v_fit'].iloc[v==v] = v_fit

    return dfall

if __name__ == '__main__':

    global alt_in,ascf

    # set year and doy
    # set altitude,ascend/descend(T/F)
    # set data directory(dirr)

    alt_in = 95
    ascf = 'F'

    dirr = './binprf/'
    year = 2020
    doys = np.arange(10)

    df1 = pd.DataFrame()
    for i in doys:

        ff = '{:04d}{:03d}.pkl'.format(int(year),int(i))

        filedir1 = dirr+'tidi_los_l1_tel1_'+ff
        filedir2 = dirr+'tidi_los_l1_tel2_'+ff
        files1=glob.glob(filedir1)
        files2=glob.glob(filedir2)

        if (len(files1)==0)|(len(files2)==0):
            continue

        df01 = cal_1day_2tel(files1[0],files2[0])
        df1=df1.append(df01,ignore_index = True)







