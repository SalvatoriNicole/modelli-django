
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 11:23:17 2024

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

          

class State(models.Model):
    LotId =  models.TextField(default='000000')
    year= models.FloatField(default=2000) #models.IntegerField()
    doy = models.FloatField(default=1) #models.IntegerField()
    giorni_utili_t0 = models.FloatField(default=0) #models.IntegerField()
    
        
class Data(models.Model):
    LotId =  models.TextField(default='000000')
    year= models.FloatField(default=2000) #models.IntegerField()
    doy = models.FloatField(default=1) #models.IntegerField()
    mean_soil_temperature = models.FloatField(default=0)#,blank=False, null=False) 
    max_soil_temperature = models.FloatField(default=0)#,blank=False, null=False) 
    rain = models.FloatField(default=0)#,blank=False, null=False) 
    installation = models.BooleanField(default=False)
    
        
class Elateridi(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    state=models.ForeignKey(to=State, on_delete=models.CASCADE)
    data=models.ForeignKey(to=Data, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['created']
        #managed = False
