from netCDF4 import Dataset
import datetime as dt
import numpy as np
import pandas as pd
import glob
import tidi_los_read as los_1d

def get_df1(tididata,angle):

    iS = 0
    iE = len(tididata["times"][angle])-1

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
    ascflag = tididata["ascflag"][angle][iS:iE]
    scsza = tididata["scsza"][angle][iS:iE]
    tpsza = tididata["tpsza"][angle][iS:iE]

    times = pd.to_datetime(times)

    df1 =  pd.DataFrame(list(zip(
        times ,
        tplon ,
        tplat ,
        tpalt ,
        lon  ,
        lat  ,
        alt  ,
        tdop ,
        trot ,
        los  ,
        dir  ,
        ascflag,
        scsza,
        tpsza,
        var
        )),columns=[
        'times' ,
        'tplon' ,
        'tplat' ,
        'tpalt' ,
        'lon',
        'lat',
        'alt',
        'tdop',
        'trot',
        'los',
        'dir',
        'ascflag',
        'scsza',
        'tpsza',
        'var'])

    return df1

if __name__ == '__main__':

    # you need to add a data directory here
    # datapath = '.'

    filedir = datapath+'*.LOS'

    filenames=glob.glob(filedir)
    nfiles = len(filenames)

    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    df4 = pd.DataFrame()

    for ifile0,ifile in enumerate(filenames):
        print('reading...',ifile0,'/',nfiles,ifile)

        tididata = los_1d.read_tidi_data(ifile)
        #angles = [45, 135, 225, 315, 405]
        df10 = get_df1(tididata,45)
        df20 = get_df1(tididata,135)
        df30 = get_df1(tididata,225)
        df40 = get_df1(tididata,315)

        df1 = df1.append(df10,ignore_index=True)
        df2 = df2.append(df20,ignore_index=True)
        df3 = df3.append(df30,ignore_index=True)
        df4 = df4.append(df40,ignore_index=True)


