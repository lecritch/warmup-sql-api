import glob
import pickle as pkl
import numpy as np
import pandas as pd


def pkl_dump(obj_name_list): 

    '''
    obj_name_list: 
    list of tuples as (obj, obj_name)
    
    '''
    
    for pair in obj_name_list:
        obj, file_name = pair
        
        files = glob.glob('test_objects/*.pkl')
        
        if not files:
                files = glob.glob('test_objects\*.pkl')
    
        existing_files = [get_file_name(file) for file in files]

        if file_name in existing_files:
            return print(f'can"t dump, {file_name} already exists')

        with open(f'test_objects/{file_name}.pkl', 'wb') as f:
            pkl.dump(obj, f)
        
    return
        
    
def pkl_load(file_name):
    
    try:
        with open(f'test_objects/{file_name}.pkl', 'rb') as f:
            obj = pkl.load(f)
    
    except:
        with open('test_objects\{}.pkl'.format(file_name), 'rb') as f:
                obj = pkl.load(f)
        
    return obj
    

def get_file_name(glob_listing):
    try:
        listing = (glob_listing
            .split('/')[1] #get the file name
            .split('.')[0] #remove .pkl
           )
    
    except:
        listing = (
            glob_listing
            .split('\\')[1] #get the file name
            .split('.')[0] #remove .pkl
           )
    
    return listing

def load_test_dict():
    files = glob.glob("test_objects/*.pkl")
    
    if not files:
        files = glob.glob("test_objects\*.pkl")
        
    return {get_file_name(file)
            : pkl_load(
                get_file_name(file)
            ) 
            for file in files} 
    
    
test_obj_dict = load_test_dict()

kwargs_dict = {
    np.ndarray:{},
    pd.core.series.Series:{},
    pd.core.frame.DataFrame:{'check_like':True}
}

run_test_dict = {
    np.ndarray: np.testing.assert_array_equal,
    pd.core.series.Series: pd.testing.assert_series_equal,
    pd.core.frame.DataFrame: pd.testing.assert_frame_equal
    }

def run_test(obj, name):
    kind = type(obj)
    
    try:
        if kind in run_test_dict.keys():
            run_test_dict[kind](obj, test_obj_dict[name], **kwargs_dict[kind])
        
        else:
            assert obj==test_obj_dict[name]
        return 'Hey, you did it.  Good job.'
    except AssertionError:
        return 'Try again'
    