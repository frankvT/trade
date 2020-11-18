# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 10:53:06 2019
12/20 : added check of variable set in new versus old file
        added meta data file (XLSX)
24/01/20 : changed way of dropping not needed variables in function make_dataframe()

@author: VanTongeren_F
"""

import os
import shutil
import urllib
import xlrd
import pandas as pd
from datetime import datetime

# preliminaries: set up directories and paths
print('Python scripts to download and transform CPB monthly trade data, '
      'FvT Nov 2019','\n')

DOWNLOAD_ROOT = "https://www.cpb.nl/sites/default/files/wtmonitor/cpb-data-wtm.xlsx"
TRADE_URL= DOWNLOAD_ROOT
PROJECT_ROOT_DIR = "."

DOWNLOAD_DATE = datetime.strftime(datetime.today(),'%Y%m%d')

DATA_PATH = os.path.join(PROJECT_ROOT_DIR, "datasets")
TRADE_PATH = os.path.join(PROJECT_ROOT_DIR, "datasets", "CPB")

XLSX_NAME = "CPB_XX.XLSX"
XLSX_TMP ="CPB_"+DOWNLOAD_DATE+"_TMP.XLSX"

META_NAME= "CPB_meta.xlsx"
META_PATH = os.path.join(TRADE_PATH, META_NAME)

CSV_IDX_NAME = 'CPB_Trade_Data_IDX.csv'
CSV_VOL_NAME = 'CPB_Trade_Data_VOL.csv'

LOG_NAME = os.path.join(TRADE_PATH,'stamp.txt')


def fetch_trade_data(trade_url=TRADE_URL, trade_path=TRADE_PATH,
                     xlsx_name=XLSX_NAME, xlsx_tmp=XLSX_TMP):
    ''' Fetches CPB trade data from TRADE_URL.
        Assumes filename and filestructure remain the same.
        Creates directory <trade_path> to store the file if necessary.

        Parameters
        ----------
        trade_url: string
            URL of the CPB trade data, defaults to TRADE_URL.
        trade_path: string
            path where data are store, defaults to TRADE_PATH.
        xlsx_name: string
             partial file name for the downloaded data, defaults to XLSX_NAME
        xlsx_tmp: string.
             file  name for a temporary file to store the download,
             defaults to XLSX_TMP.

        Returns
        -------
            'stamp': string
                date stamp found in the downloaded file.
            'xlsx_path':
                filename  and path for the data file based on 'stamp'.

        Example
        -------
        >>> file_stamp, file_path = fetch_trade_data()
    '''

    if not os.path.isdir(trade_path):
        os.makedirs(trade_path)

    xlsx_tmp = os.path.join(trade_path, xlsx_tmp)
    stamp=''
    xlsx_path = ''

    # try fetching a new file and put it in xlsx_tmp
    try:
        urllib.request.urlretrieve(trade_url, xlsx_tmp)
        print('*** done downloading tradedata')
    except urllib.error.URLError as e:
        print(trade_url)
        print('*** URL error: ', e.reason)

    if os.path.isfile(xlsx_tmp):
        tmp=xlrd.open_workbook(xlsx_tmp)
        sheet=tmp.sheet_by_name('trade_out')

        #grab stamp in spreadsheet
        stamp =str(sheet.cell_value(3,1))
        stamp=stamp[:-8]

        # make complete filename with path based on stamp
        xlsx_name = xlsx_name[:-7]+stamp.replace(' ','')+'.XLSX'
        xlsx_path = os.path.join(trade_path, xlsx_name)

        # add filename info to stamp
        stamp=xlsx_path.replace('\\','/')+' ; '+stamp

    return stamp, xlsx_path
# end fetch_trade_data()

def is_new_stamp(stamp,fn=LOG_NAME):
    ''' Returns 'True' if the stamp does not exist in the log file (plain text).
    - appends stamp to log file if stamp is new
    - creates a new log file if it does not exist
    - backups existing log file.

    Parameters
    ----------

    stamp: string

    fn: string.

    Returns
    -------
    stamp_new: boolean
      True if stamp is not in log file

    Example
    -------
    >>> is_new_file = is_new_stamp(file_stamp)

    '''
    fn_bak=fn[:-4] + '~.bak'
    stamps=[]

    if os.path.isfile(fn):
        try:                                 # make backup copy of log file
            shutil.copyfile(fn, fn_bak)
        except shutil.SameFileError:
            pass

        with open(fn) as f:
            stamps= str(f.readlines())
    else:                                    #create a new log file
        with open(fn,'w') as f:              # open for write
            f.write('Download file   CPB data datestamp \n')

    stamp_new = stamp not in stamps

    if stamp_new:                     # new stamp, so append to log file
        with open(fn, 'a') as f:      # open for append
            f.write(stamp)
            f.write('\n')
        f.close()
    return stamp_new
#end is_new_stamp()

def write_new_file(new, dest_path, trade_path=TRADE_PATH, tmp=XLSX_TMP):
    '''
    Writes the xlsx data file to disk if it is new.
    Deletes temporary file.

    Parameters
    ----------
    new : boolean

    dest_path : string
       path to store the file.

    trade_path : string
        path where downloaded file is stored, defaults to TRADE_PATH

    tmp : string
       name of downloaded temporary file, defaults to XLSX_TMP

    Returns
    -------
    none

    '''
    tmp_path= os.path.join(trade_path, tmp)

    if new:
        try:
            shutil.copy2(tmp_path,dest_path)
        except shutil.ExecError:
            pass
    try:
        os.remove(tmp_path)
    except OSError:
        pass
#end write_new_file()

def check_variables(var_list, check_list):
    '''
    checks the set of variabels in var_list against the set in check_list

    Parameters
    ----------
    var_list: list-like  arry of strings
    check_list: list- like array of strings

    Returns
    -------
    check: boolean True if the two sets are the same, false otherwise
    raises SystemExit to terminate the program if the two sets are different
    '''

    set_check=set(check_list)
    set_vars=set(var_list)
    check= len(set_check) & len(set_vars) == len(set_check)

    if not check:
        print(f"The set of variables is the same = {check}")
        print('Variables in check_list that are not in current variable list:',
              set_check - set_vars)
        print('Variables in current variable list that are not in check_list:',
             set_vars - set_check)
        print('\n Please check the downloaded file manually - I quit now.. \n')

        raise SystemExit

    return check

def get_meta(meta_path=META_PATH):
    '''
    reads XLSX file with meta data
    Parameters
    ----------
    meta_path: a valid pathmane to the XLSX files containing meta data

    Returns
    --------
    meta: Pandas dataframe
    '''
    meta=pd.read_excel(meta_path, 'meta', header =0)

    return meta
def make_volume_dataframe(df):
    ''' Making data set of volume data from trade index numbers '''

    #make sure variable names are the index, so the transpose will pivot around that one
    tmp= df.copy()
    tmp.set_index('longname',inplace=True, drop=True)
    tmp.columns=tmp.columns.str.replace("m","-")
    # multiply all columns with base values, found in columnn 0
    df_vol= tmp.iloc[:, 1:].apply(lambda c: c * tmp.iloc[:,0])

    # transpose dataframe so that time is on the vertical axis
    df_vol=df_vol.transpose()
    df_vol.index=pd.period_range(start=df_vol.index[0],
                                        end=df_vol.index[-1], freq='M')
    df_vol.columns= df_vol.columns.str.lower()
    df_vol.columns= df_vol.columns.str.rstrip()

    return df_vol

def make_index_dataframe(df):
    ''' Making data set of trade indexes '''
    df_idx = df.copy()
    df_idx = df_idx.drop('value 2010 USD bln', axis='columns') #drop this column also

#make sure variable names are the index, so the transpose will pivot around that one
    df_idx.set_index('longname',inplace=True, drop=True)

    df_idx.columns=df_idx.columns.str.replace("m","-")

# transpose dataframe so that time is on the vertical axis
    df_idx=df_idx.transpose()
    df_idx.index=pd.period_range(start=df_idx.index[0],
                                        end=df_idx.index[-1], freq='M')
    df_idx.columns= df_idx.columns.str.lower()
    df_idx.columns= df_idx.columns.str.rstrip()
    return df_idx

def make_dataframes(xlsx_path):
    ''' Makes a Pandas dataframe from excel file with CPB data.
    - checks if CPB filestructure remained the same.
    - retains only trade level variables and drops price information.
    - renames variables so that variable names are unique.
    - transposes the data so that time is on the vertical axis and variables
      on the horizontal axis.

      Parameters
      ----------
      xlsx_path: string
          a valid path to the untransformed XLSX file from CPB.

      Returns
      -------
      df_transposed:
          a cleaned dataframe with time on the vertical axis
    '''

    df = pd.read_excel(xlsx_path, 'trade_out',skiprows=[0,1,2,4,5,6],
                       header =0)
    meta=get_meta()

# drop empty rows and columns
    df.dropna(how='all', axis='rows',inplace=True)
    df.dropna(how='all', axis='columns',inplace=True)

# rename unnamed columns(not really necessary as they will be dropped later)
    df.rename(columns={'Unnamed: 2': 'CPB_varlabel',
                      'Unnamed: 3': 'value 2010 USD bln'}, inplace = True)

# keep only trade volumes data. Those have 'qnmi'in the CPB_varlabel name
    to_keep=['QNMI' in str(z).upper() for z in df.loc[:,'CPB_varlabel']]
    df=df[to_keep]

#check the list of variables in the new file against existing list in meta
#NOTE: check_variables() exits program if the the sets of variables differ
    var_list=df.loc[:,'CPB_varlabel']
    check_list = meta['CPB_varlabel']

    check_variables(var_list, check_list)

# insert nicer variable longnames from the meta file by merging the 2 df
    df=pd.merge(meta,df, how='left', on='CPB_varlabel')

#drop all variables that we do not need for the clean df
    df=df.drop([df.columns[2]],axis='columns') #drop old CPB var name
    df=df.drop('CPB_varlabel', axis='columns') #drop CPB varlabel

    df_vol= make_volume_dataframe(df)
    df_index = make_index_dataframe(df)

    return df_index, df_vol
# end make_dataframes()

def write_dataframe_toCSV(df1,df2, data_path=DATA_PATH, csv_name1=CSV_IDX_NAME,\
                          csv_name2=CSV_VOL_NAME):
    ''' writes cleaned dataframe to CSV in <data_path>
    overwites any existing version
    '''
    if not os.path.isdir(data_path):
            os.makedirs(data_path)

    csv_path=os.path.join(data_path,csv_name1)
    df1.to_csv(csv_path)

    csv_path=os.path.join(data_path,csv_name2)
    df2.to_csv(csv_path)

# end write_dataframe_toCSV()

def print_report(new, stamp, file_path):
    ''' prints a simple report of the process on stdout
    '''

    print('-------------------------------------------------------------','\n')
    if stamp == '':
        print('*** no file could be downloaded at this time')
        print('*** there may be an existing file in', TRADE_PATH,'\n')

    else:
        print('*** data file is in: ', os.path.join(TRADE_PATH, file_path),'\n')
        if new:
            print('*** this is a new file with CPB date stamp ',stamp)
            print('*** cleaned trade data saved to:   \n',
                    os.path.join(DATA_PATH,CSV_IDX_NAME),'\n',
                    os.path.join(DATA_PATH,CSV_VOL_NAME))
        else:
            print('*** this is an existing file with CPB date stamp ', stamp)
            print('*** no further transformations done')
            print('*** a cleaned version in CSV format is in the following:\n',
                   os.path.join(DATA_PATH,CSV_IDX_NAME),'\n',
                   os.path.join(DATA_PATH,CSV_VOL_NAME))
        print('*** the meta data information is in ',META_PATH,'\n')
        print('*** the following variables are available: \n', get_meta())
        print('-------------------------------------------------------------','\n')
# end print_report

def main():
    '''organizes the program flow of fetchtradedata.py
    '''

    file_stamp, file_path = fetch_trade_data()
    is_new_file           = is_new_stamp(file_stamp)
    write_new_file(is_new_file,file_path)

    if is_new_file:
        idx_df, vol_df = make_dataframes(file_path)
        write_dataframe_toCSV(idx_df, vol_df)

    print_report(is_new_file,file_stamp,file_path)

#end main()

if __name__ == "__main__":
    main()
