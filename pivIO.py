# -*- coding: utf-8 -*-
import _pickle as pickle

def savePIV(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f, -1)
        
def loadPIV(path):
    with open(path, 'rb') as f:
        return pickle.load(f)