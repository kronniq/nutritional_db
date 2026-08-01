#! python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 16:51:51 2023

@author: kronq
"""
from col_heads import col_heads

default_fields = ['Energ_Kcal', 
                  'Lipid_Tot_(g)', 
                  'FA_Sat_(g)', 
                  'Cholestrl_(mg)', 
                  'Carbohydrt_(g)', 
                  'Sugar_Tot_(g)',
                  'Fiber_TD_(g)', 
                  'Protein_(g)', 
                  'Vit_A_IU', 
                  'Vit_C_(mg)', 
                  'Thiamin_(mg)', 
                  'Niacin_(mg)', 
                  'Sodium_(mg)', 
                  'Potassium_(mg)', 
                  'Phosphorus_(mg)', 
                  'Iron_(mg)',
                  'Calcium_(mg)',
                  'GmWt_1',
                  'GmWt_Desc1']


def choose_fields():
    
    while True:
        fields = input('Enter fields(separated by space): ').split()
        if fields:
            for field in fields:
                if field not in col_heads:
                    print('Bad field name(s)')
                    continue
            return default_fields + fields
        else:
            return default_fields
            
choose_fields()