#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 18:31:38 2024

@author: nicole
"""

# Create your models here.
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
#from django.contrib.postgres.fields import ArrayField

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])



class Daily(models.Model):
    hod = models.FloatField(default=1)# ,blank=False, null=False) 
    temperature = models.FloatField(default=0)#,blank=False, null=False) 
    leafwetness = models.FloatField(default=0)#,blank=False, null=False)             

class State(models.Model):
    LotId =  models.TextField(default='000000')
    year= models.FloatField(default=2000) #models.IntegerField()
    doy = models.FloatField(default=1) #models.IntegerField()
    LWD_t0 = models.FloatField(default=0) #models.IntegerField()
    y_t0 = models.FloatField(default=0) #models.IntegerField()
    
        
class Data(models.Model):
    daily=models.ForeignKey(to=Daily, on_delete=models.CASCADE)
    LotId =  models.TextField(default='000000')
    year= models.FloatField(default=2000) #models.IntegerField()
    doy = models.FloatField(default=1) #models.IntegerField()
  
    
class Pseudoperonospora(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    state=models.ForeignKey(to=State, on_delete=models.CASCADE)
    data=models.ForeignKey(to=Data, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['created']
        #managed = False
