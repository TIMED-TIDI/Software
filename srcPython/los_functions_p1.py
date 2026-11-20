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
    base = dt.datetime(year = 1980, month = 1, day = 6)
    for t in intimearray:
        outtime.append(base + dt.timedelta(seconds = t))

    return outtime

def sep_prof_1tel(tp_alt,rec_index,sc_sza):

    llen = len(tp_alt)
    index2 = np.arange(llen-1)+1
    index1 = np.arange(llen-1)

    index_all = np.arange(llen)

    lp = sc_sza>=90.0
    alt1 = tp_alt[lp]
    rec1 = rec_index[lp]
    sza1 = sc_sza[lp]
    index_n = index_all[lp]

    index2_1 = index_n[1:len(index_n)]
    index1_1 = index_n[0:-1]

    dalt1 = alt1[1:len(index_n)]-alt1[0:-1]
    fp = -dalt1 > 4
    ffp = index1_1<=index1_1[fp][0]
    index_sn = np.concatenate((index1_1[ffp][0],index2_1[fp]),axis=None)

    ffp = index2_1>=index2_1[fp][-1]
    index_en = np.concatenate((index1_1[fp],index2_1[ffp][-1]),axis=None)

    lp = sc_sza<90.0
    alt1 = tp_alt[lp]
    rec1 = rec_index[lp]
    sza1 = sc_sza[lp]
    index_d = index_all[lp]
    index2_1 = index_d[1:len(index_d)]
    index1_1 = index_d[0:-1]

    dalt1 = alt1[1:len(index_d)]-alt1[0:-1]
    fp = -dalt1 > 10.0
    ffp = index1_1<=index1_1[fp][0]
    index_sd = np.concatenate((index1_1[ffp][0],index2_1[fp]),axis=None)
    ffp = index2_1>=index2_1[fp][-1]
    index_ed = np.concatenate((index1_1[fp],index2_1[ffp][-1]),axis=None)

    flag = np.ones(len(rec_index))*np.nan
    prf = np.ones(len(rec_index))*np.nan

    flag[index_ed] = 1
    flag[index_en] = 1

    index_ee = np.concatenate((index_ed,index_en),axis=None)
    index_ee = np.sort(index_ee, axis=None)

    ddalt = tp_alt[index_ee[0:-1]+1]-tp_alt[index_ee[0:-1]]
    llp = abs(ddalt)<4

    if len(ddalt[llp])>0:
        flag[index_ee[0:-1][llp]] = 2

    #print('flag',np.nanmin(flag),np.nanmax(flag))

    prf[0] = 0
    for k11,k1 in enumerate(flag[0:-1]):

        if k1 != 1:

            prf[k11+1] = prf[k11]
        else:
            prf[k11+1] = prf[k11-1]+1

    return prf

def read_1file(ifile):
    '''
    - seperate by telescopes
    - label orbit, altitude profile, and warm/cold side
    - contains:
      1. sep_prof_1tel
      2. convert_to_datetime
    '''

    ncfile = Dataset(ifile, 'r')

    alltimes = np.array(ncfile.variables['time'][:], dtype='float64')

    angles = [45, 135, 225, 315, 405]
    tel_id = np.array(ncfile.variables['tel_id'][:])
    tp_lat = np.array(ncfile.variables['tp_lat'][:])
    tp_lon = np.array(ncfile.variables['tp_lon'][:])
    tp_alt = np.array(ncfile.variables['tp_alt'][:])

    sc_lon = np.array(ncfile.variables['sc_lon'][:])

    s_los = np.array(ncfile.variables['s'][:])
    s_var = np.array(ncfile.variables['var_s'][:])
    p_status = np.array(ncfile.variables['p_status'][:])
    table_index = np.array(ncfile.variables['table_index'][:])
    los_dir = np.array(ncfile.variables['los_direction'][:])
    asc_flag = np.array(ncfile.variables['ascending'][:])
    asc_flag = asc_flag.astype('U13')
    sc_sza = np.array(ncfile.variables['sc_sza'][:])
    tp_sza = np.array(ncfile.variables['tp_sza'][:])

    rec_index = np.array(ncfile.variables['rec_index'][:])
    b_angle = ncfile.getncattr('solar_beta_angle')

    times = {}
    tplon = {}
    tplat = {}
    tpalt = {}
    los = {}
    dir = {}
    var = {}
    ascflag = {}
    scsza = {}
    tpsza = {}
    recindex = {}
    orbid = {}
    prfid = {}
    warm = {}

    ### orb seperate
    orb0 = np.ones(len(rec_index))*np.nan
    lp = tp_alt>0
    orb = orb0[lp]
    asc_tmp = asc_flag[lp]
    orb[0] = 0
    for k11,k1 in enumerate(asc_tmp):
        if k11==0:
            continue

        if k1 == asc_tmp[k11-1]:
            orb[k11] = orb[k11-1]
        else:
            orb[k11] = orb[k11-1]+1
    orb0[lp] = orb
    asc_flag = asc_flag.flatten()
    fp = asc_flag=='T'
    tmp = orb0[fp]
    orb0[fp] = (tmp-np.nanmin(tmp))/2

    fp = asc_flag=='F'
    tmp = orb0[fp]
    orb0[fp] = (tmp-np.nanmin(tmp))/2

    ### alt profile seperate
    prf0 = np.ones(rec_index[-1])*np.nan
    for k11,a in enumerate(angles[0:4]):
        lp = (tel_id==a)&(tp_alt>0)
        prfs = sep_prof_1tel(tp_alt[lp],rec_index[lp],
                               sc_sza[lp])
        prf0[lp] = prfs

    ## warm- and cold- side
    warm_side = np.ones(len(tel_id))*np.nan
    lats = np.ones((4,2))*np.nan
    k=0
    for a in angles[0:4]:
        lats[k,:] = [np.nanmin(tp_lat[fp]),np.nanmax(tp_lat[fp])]
        k = k+1

    if b_angle>=0:
        if (lats[0,1]>lats[3,1]):
            warm_side[tel_id==45]   = np.ones(len(tel_id[tel_id==45]))
            warm_side[tel_id==135]  = np.ones(len(tel_id[tel_id==135]))
            warm_side[tel_id==225] = np.zeros(len(tel_id[tel_id==225]))
            warm_side[tel_id==315] = np.zeros(len(tel_id[tel_id==315]))
        else:
            warm_side[tel_id== 45] =  np.zeros(len(tel_id[tel_id==45]))
            warm_side[tel_id== 135] = np.zeros(len(tel_id[tel_id==135]))
            warm_side[tel_id== 225] =  np.ones(len(tel_id[tel_id==225]))
            warm_side[tel_id== 315] =  np.ones(len(tel_id[tel_id==315]))
    else:
        if (lats[0,1]<lats[3,1]):
            warm_side[tel_id==45]   = np.ones(len(tel_id[tel_id==45]))
            warm_side[tel_id==135]  = np.ones(len(tel_id[tel_id==135]))
            warm_side[tel_id==225] = np.zeros(len(tel_id[tel_id==225]))
            warm_side[tel_id==315] = np.zeros(len(tel_id[tel_id==315]))
        else:
            warm_side[tel_id== 45] =  np.zeros(len(tel_id[tel_id==45]))
            warm_side[tel_id== 135] = np.zeros(len(tel_id[tel_id==135]))
            warm_side[tel_id== 225] =  np.ones(len(tel_id[tel_id==225]))
            warm_side[tel_id== 315] =  np.ones(len(tel_id[tel_id==315]))

    for a in angles[0:4]:
        tmp = alltimes[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        times[a] = convert_to_datetime(tmp)
        tplon[a] = tp_lon[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        tplat[a] = tp_lat[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        tpalt[a] = tp_alt[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        los[a] = s_los[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        dir[a] = los_dir[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        var[a] = np.sqrt(s_var[(sc_lon>0) & (tel_id == a) & (p_status == 0)])
        ascflag[a] = asc_flag[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        scsza[a] = sc_sza[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        tpsza[a] = tp_sza[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        orbid[a] = orb0[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        prfid[a] = prf0[(sc_lon>0) & (tel_id == a) & (p_status == 0)]
        warm[a] = warm_side[(sc_lon>0) & (tel_id == a) & (p_status == 0)]

    ncfile.close()
    data = {'times' : times,
            'tplon' : tplon,
            'tplat' : tplat,
            'tpalt' : tpalt,
            'los' : los,
            'dir' : dir,
            'ascflag': ascflag,
            'scsza': scsza,
            'tpsza': tpsza,
            'var' : var,
            'orbid':orbid,
            'prfid':prfid,
            'warm':warm}
    return data

def get_1tel_df(tididata,angle):

    iS = 0
    iE = len(tididata["times"][angle])-1

    tplon = tididata["tplon"][angle][iS:iE]
    tplat = tididata["tplat"][angle][iS:iE]
    tpalt = tididata["tpalt"][angle][iS:iE]
    los = tididata["los"][angle][iS:iE]
    dir = tididata["dir"][angle][iS:iE]
    var = tididata["var"][angle][iS:iE]
    times = tididata["times"][angle][iS:iE]
    ascflag = tididata["ascflag"][angle][iS:iE]
    tpsza = tididata["tpsza"][angle][iS:iE]
    scsza = tididata["scsza"][angle][iS:iE]
    orbid = tididata["orbid"][angle][iS:iE]
    prfid = tididata["prfid"][angle][iS:iE]
    warm = tididata["warm"][angle][iS:iE]

    times = pd.to_datetime(times)

    df = pd.DataFrame(list(zip(
        times ,
        tplon ,
        tplat ,
        tpalt ,
        los  ,
        dir  ,
        ascflag,
        tpsza,
        scsza,
        var,
        orbid,
        prfid,
        warm
        )),columns=[
        'times' ,
        'tplon' ,
        'tplat' ,
        'tpalt' ,
        'los',
        'dir',
        'ascflag',
        'tpsza',
        'scsza',
        'var',
        'orbid',
        'prfid',
        'warm'])

    df = df.drop(columns=['tpsza'])

    return df

def interp_1prf(df):

    from scipy import interpolate
    from photutils.utils import ShepardIDWInterpolator as idw

    alt = np.asarray(df['tpalt'])
    BinAlt = 2.5
    balt = np.arange(np.min(alt),np.max(alt)+BinAlt/2,BinAlt)

    if len(balt) == len(df):
        return df

    cols = df.columns.values.tolist()
    dfp = pd.DataFrame(index=np.arange(len(balt)),columns=cols)

    print('-- alt of dataframe',alt)
    print('-- alt for interpolation',balt)
    print(df.info)

    from scipy import interp

    # -1. los,var using nearest
    x = np.asarray(df['tpalt'])
    y = np.asarray(df['los'])
    #f = interpolate.interp1d(x, y,kind='nearest')
    f = idw(x, y)
    dfp['los'] = f(balt,n_neighbors=2,power=2)

    y = np.asarray(df['var'])
    f = idw(x, y)
    dfp['var'] = f(balt,n_neighbors=2,power=2)

    # -2. times and lat using linear
    y = np.asarray(df['times'])
    y = pd.to_datetime(y)
    f = interpolate.interp1d(x, y)
    dfp['times'] = pd.to_datetime(f(balt))

    y = np.asarray(df['tplat'])
    f = interpolate.interp1d(x, y)
    dfp['tplat'] = f(balt)

    # -3. lon, dir eq k-1 value
    dfp.loc[0,'dir'] = df.iloc[0]['dir']
    dfp.loc[0,'tplon'] = df.iloc[0]['tplon']
    for k11,k1 in enumerate(balt):

        if k11==0:
            continue
        lp = x==k1
        if len(x[lp])==1:
            dfp.loc[k11,'dir'] = df['dir'][lp].values
            dfp.loc[k11,'tplon'] = df['tplon'][lp].values

        elif len(x[lp])== 0:
            dfp.loc[k11,'dir'] = dfp.loc[k11-1,'dir']
            dfp.loc[k11,'tplon'] = dfp.loc[k11-1,'tplon']
        else:
            sys.exit('error in interp_1prf')

    dfp['tpalt'] = balt
    dfp['ascflag'] = df.iloc[0]['ascflag']
    dfp['orbid'] = df.iloc[0]['orbid']
    dfp['prfid'] = df.iloc[0]['prfid']

    return dfp

def bin_1prf(df):

    '''
    bin each profile with an interval of 2.5 km
    '''

    cols = df.columns.values.tolist()
    dfp = pd.DataFrame(columns=cols)

    BinAlt = 2.5
    balt = np.arange(70,301,BinAlt)

    timeinp = []
    ascbin = []

    for k11,k1 in enumerate(balt):

        lp = (df['tpalt']>(k1-BinAlt/2))&(df['tpalt']<=(k1+BinAlt/2))
        if len(df[lp])==0:
            continue
        elif len(df[lp])==1:
            df1 = df[lp]
            indxm = df1.index[0]

            for ic in cols:
                #print('--',ic)
                if ic=='tpalt':
                    dfp.loc[k11,'tpalt'] = k1
                else:
                    dfp.loc[k11,ic] = df1.loc[indxm,ic]
        else:
            df1 = df[lp]

            los1 = np.asarray(df1['los'])
            var1 = np.asarray(df1['var'])

            tmp = var1**2
            wit = 1.0/tmp

            u_w = np.sum(wit*los1)/np.sum(wit) # weighted mean
            sd_1 = 1.0/np.sum(1.0/tmp)
            yvar1 = np.sqrt(sd_1)

            indx1 = np.asarray(df1.index)
            indxm0 = int(np.nanmedian(indx1))
            dd = abs(indx1-indxm0)
            indxm = indx1[np.nanargmin(dd)]
            #print('check index',indxm0,indxm)
            '''
            if indxm==6067:

                print(df1)
                print('--- indxm',indxm)
            '''
            for ic in cols:
                #print('--',ic)
                if ic=='tpalt':
                    dfp.loc[k11,ic] = k1
                elif ic == 'los':
                    dfp.loc[k11,ic] = u_w
                elif ic == 'var':
                    dfp.loc[k11,ic] = yvar1

                else:
                    dfp.loc[k11,ic] = df1.loc[indxm,ic]

    return dfp

def bin_prf(df):
    '''
    - bin each altitude profile with an interval of 2.5 km
    - contains:
      1. bin_1prf
    '''
    print('>>> start binning altitude profile...')

    lp = (abs(df['los'])<500)
    lp = lp&(abs(df['los'])>=df['var'])
    df = df[lp]
    prfid = np.asarray(df['prfid'])

    tmp = set(prfid)

    dfp = pd.DataFrame()
    for k11,k1 in enumerate(tmp):

        lp = prfid==k1
        dft = df[lp]
        dfp1 = bin_1prf(dft)
        dfp = dfp.append(dfp1,ignore_index=True)

    return dfp

def interp_prf(df):
    '''
    - interp each altitude profile
    - contains:
      1. interp_1prf
    '''

    prfid = np.asarray(df['prfid'])

    tmp = set(prfid)

    '''
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1,1,1)
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(1,1,1)
    '''
    dfp = pd.DataFrame()
    for k11,k1 in enumerate(tmp):

        lp = prfid==k1
        dft = df[lp]
        '''
        lp = ((dft['tplat']>-35)&(dft['tplat']<-30)&(
            dft['tplon']>100)&(dft['tplon']<120))
        if len(dft[lp])>0:
            print(dft.info)
        '''

        if len(dft)>2:
            df_inp = interp_1prf(dft)

            '''
            #fig = plt.figure()
            #ax = fig.add_subplot(1,1,1)
            ax = ax1
            #ax.plot(dft['los'],dft['tpalt'],'.',label='raw data')
            #ax.plot(losbin,balt,'r--')
            ax.errorbar(dft['los'],dft['tpalt'], xerr=dft['var'],
                        alpha=0.5, label='w-ave')
            ax.errorbar(df_inp['los'],df_inp['tpalt'], xerr=df_inp['var'],
                        alpha=0.5,label='interp')
            ax.set_xlim(-150,150)
            #ax.set_ylim(70,300)
            ax.set_ylim(70,120)
            ax.grid(True,linestyle='--')
            ax.set_xlabel('L1 LOS (m/s)')
            ax.set_ylabel('Alt (km)')
            ax.legend()
            #fig.savefig('L1_los_vs_alt_test_prfid{:04d}_242.png'.format(int(df['prfid'].iloc[0])),dpi=600)

            #fig = plt.figure()
            #ax = fig.add_subplot(1,1,1)
            ax = ax2
            ax.plot(dft['times'],dft['tpalt'],'+',label='w-ave')
            ax.plot(df_inp['times'],df_inp['tpalt'],'.-',label='interp')
            #ax.set_xlabel('UT')
            #ax.plot(df['tpalt'],'.-',label='raw data')
            #ax.set_xlabel('Data Point')
            ax.set_ylim(70,120)
            ax.set_xlabel('UT')
            ax.set_ylabel('Alt (km)')
            print(dft['prfid'])
            print(int(dft['prfid'].iloc[0]))
            #fig.savefig('L1_alt_test_prfid{:04d}_242.png'.format(int(df['prfid'].iloc[0])),dpi=600)
            '''
            dfp = dfp.append(df_inp,ignore_index=True)
    return df_inp

def process_1file(year,doys):

    ff = '/raid4/Data/Tidi/tidi.engin.umich.edu/los/2020/'
    savedir = './binprf/'

    for i in doys:

        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        df3 = pd.DataFrame()
        df4 = pd.DataFrame()

        dirr = ff+'/TIDI_PB_{:04d}{:03d}_*S0704_D011_R01.LOS'.format(
                int(year),int(i))
        file1 = glob.glob(dirr)
        if len(file1)==0:
            continue

        date = file1[0][-32:-25]
        print('reading...',date,file1[0])

        tididata = read_1file(file1[0])

        df01 = get_1tel_df(tididata,45)
        df02 = get_1tel_df(tididata,135)
        df03 = get_1tel_df(tididata,225)
        df04 = get_1tel_df(tididata,315)

        dfp1 = bin_prf(df01)
        dfp2 = bin_prf(df02)
        dfp3 = bin_prf(df03)
        dfp4 = bin_prf(df04)

        df1 = df1.append(dfp1,ignore_index=True)
        df2 = df2.append(dfp2,ignore_index=True)
        df3 = df3.append(dfp3,ignore_index=True)
        df4 = df4.append(dfp4,ignore_index=True)

        df1.to_pickle(savedir+'tidi_los_l1_tel1_'+date+'.pkl')
        df2.to_pickle(savedir+'tidi_los_l1_tel2_'+date+'.pkl')
        df3.to_pickle(savedir+'tidi_los_l1_tel3_'+date+'.pkl')
        df4.to_pickle(savedir+'tidi_los_l1_tel4_'+date+'.pkl')

    return

if __name__ == '__main__':

    import glob


    doys = np.arange(241,242,1)

    process_1file(2020,doys)

