import os
import collections
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io as sio




def pretty_dict(ndict, indent=0, print_type=False):
    """Visualizes the tree-like structure of a dictionary
    Arguments:
        ndict {dict} -- [the python dictionary to be visualized]
    Keyword Arguments:
        indent {int} -- [number of tab spaces for the indentation]
        (default: {0})
        print_type {bool} -- [True if variable types are printed]
        (default: {False})
    """
    if isinstance(ndict, dict):
        for key, value in ndict.items():
            if print_type:
                print(
                    "\t" * indent + "Key: " + str(key) + ",\t" + "Type: ", type(value),
                )
                pretty_dict(value, indent + 1, True)
            else:
                print("\t" * indent + "Key: " + str(key))
                pretty_dict(value, indent + 1)



def mat2dict(filename):
    """Converts MoVi mat files to a python nested dictionary.
    This makes a cleaner representation compared to sio.loadmat
    Arguments:
        filename {str} -- The path pointing to the .mat file which contains
        MoVi style mat structs
    Returns:
        dict -- A nested dictionary similar to the MoVi style MATLAB struct
    """
    # Reading MATLAB file
    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)

    # Converting mat-objects to a dictionary
    for key in data:
        if key != "__header__" and key != "__global__" and key != "__version__":
            if isinstance(data[key], sio.matlab.mio5_params.mat_struct):
                data_out = matobj2dict(data[key])
    return data_out




def matobj2dict(matobj):
    """A recursive function which converts nested mat object
    to a nested python dictionaries
    Arguments:
        matobj {sio.matlab.mio5_params.mat_struct} -- nested mat object
    Returns:
        dict -- a nested dictionary
    """
    ndict = {}
    for fieldname in matobj._fieldnames:
        attr = matobj.__dict__[fieldname]
        if isinstance(attr, sio.matlab.mio5_params.mat_struct):
            ndict[fieldname] = matobj2dict(attr)
        elif isinstance(attr, np.ndarray) and fieldname == "move":
            for ind, val in np.ndenumerate(attr):
                ndict[
                    fieldname
                    + str(ind).replace(",", "").replace(")", "").replace("(", "_")
                ] = matobj2dict(val)
        elif fieldname == "skel":
            tree = []
            for ind in range(len(attr)):
                tree.append(matobj2dict(attr[ind]))
            ndict[fieldname] = tree
        else:
            ndict[fieldname] = attr
    return ndict



# Converting dictionary to namedTuple
def dict2ntuple(ndict):
    """Converts nested (or simple) dictionary to namedTuples
    so that the attributes are accessible by dotted notation.
    Example: subj = mat2dicts(matefilename)
    subj = subj('Subject_15')
    n_subj = dict2ntuple(subj)
    IMU = n_subj.IMU
    Arguments:
        ndict {dict}: python dictionary to be converted to a
        namecTuple. Make sure all keys are made by letters or
        underscore (key names must not by prefixed with underscore)
    Returns:
        namedTuple -- a nested namedTuple object
    """

    if isinstance(ndict, collections.Mapping) and not isinstance(ndict, ProtectedDict):
        for key, value in ndict.items():
            ndict[key] = dict2ntuple(value)
        return dict2tuple(ndict)
    return ndict



