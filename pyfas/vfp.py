"""
Vfp class reads eclipse format read curves and allows generation of xarray objects to inspect/extract data
"""


import os
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

class Vfp:
    def __init__(self, fname, variables):
        self.fname = fname.split(os.sep)[-1]
        self.path = os.sep.join(fname.split(os.sep)[:-1])
        if self.path == '':
            self.abspath = self.fname
        else:
            self.abspath = self.path+os.sep+self.fname
        self._attributes = {}
        self.data = {}
        self.label = {}
        self.trends = {}
        self.time = ""

        self._attributes["variables"]=variables

        with open(self.abspath) as eclfile:
            rows=[]
            table_started=False
            reader = filter(lambda row: not row[:2] =='--', eclfile)
            for row in reader:
                if row[:7]=="VFPPROD":
                    table_started=True
                if table_started==True:
                    while "/" not in row:
                        row = row + " " + next(reader)
                        row = row.replace("\n","")
                        row = ' '.join(row.split())
                    rows.append(map(lambda x: float(x), row.replace(" /", "").replace("/", "").split()))
            self._attributes["rows"]=rows
            
            
    def to_dataarray(self):
        rows=self._attributes["rows"]
        variables=self._attributes["variables"]
        df=pd.DataFrame(rows[6:]).sort_values(list(range(len(variables)))) #Inserts table values in dataframe (neglecting variables)
        variables_index=list(range(len(variables)))
        df.set_index(variables_index, inplace=True) #creates index and column names based on table indices
        n=2 #skips VFPPROD line and line with flowrates (extracted later)
        idx=df.index.set_levels(rows[n:n+len(variables)])
        idx.rename(variables, inplace=True)

        df.index=idx
        df.columns=np.array(list(rows[1]))
        df=df.stack()
    
        #print(list(map(lambda x: df.index.levels[x].values.round(1), variables_index)))
        variables_index2=list(range(len(variables)+1))
        df.index = pd.MultiIndex.from_product(list(map(lambda x: df.index.levels[x].values  , variables_index2)))
        
        da=df.to_xarray()
        names_dict={}
        for i, variable in enumerate(self._attributes["variables"]):
            names_dict["level_"+str(i)]=variable
        names_dict["level_"+str(i+1)]="FLOW"
        da=da.rename(names_dict)

        return da
