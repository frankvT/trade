# tariffs.py
"""Defines different classes of tariffs"""
import numpy as np

class Tariff():
    def __init__(self, value):
        self.value = value
        self.tartype = "any"
        self.unit = ""

    def get_tartype(self):
        return self.tartype
    
    def get_unit(self):
        return self.unit
    
    def set_unit(self, u):
        self.unit = u 

class Specific(Tariff):        
    def __init__(self, value):
        Tariff.__init__(self, value)
        self.tartype = "specific tariff"
        self.unit = r'money per quantity, e.g. $/ton'

    def ave(self, p):
        # defined over p = tariff-inclusive price
        if np.isclose(p,0):
            return np.nan
        else: 
            return self.value/p
    
    def __str__(self):
        return f"{self.get_tartype()}, {self.get_unit()}. Value: {self.value} "

class Ave(Tariff):
    def __init__(self, value):
        Tariff.__init__(self, value)
        self.tartype = 'ad-valorem'
        self.unit = r'money per value, eg. x%/100'
    
    def ave(self, p):
        return self.value
    
    def __str__(self):
        return f"{self.get_tartype()}, {self.get_unit()}. Value: {self.value} "
