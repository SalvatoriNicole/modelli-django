# Create your models here.
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
#from django.contrib.postgres.fields import ArrayField

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])



class Daily(models.Model):
    hod = models.FloatField(default=1) 
    temperature = models.FloatField(default=0) 
    humidity = models.FloatField(default=10) 
    leafwetness = models.FloatField(default=0) 
    rain = models.FloatField(default=0) 
    GS = models.FloatField(default=0) 
    treatment=models.BooleanField(default=0)    
            

class State(models.Model):
    LotId =  models.TextField(default='000000')
    year= models.FloatField(default=2000) #models.IntegerField()
    doy = models.FloatField(default=1) #models.IntegerField()
    ASCmat_t0 = models.FloatField(default=0) #models.IntegerField()
    COMmat_t0 = models.FloatField(default=0) #models.IntegerField()
    H_postr_t0 = models.FloatField(default=0) #models.IntegerField()
    H_rain_t0 = models.FloatField(default=0) #models.IntegerField()
    Hdry_t0 = models.FloatField(default=0) #models.IntegerField()
    RH_t0 = models.FloatField(default=0) #models.IntegerField()
    wetness_t0 = models.FloatField(default=0) #models.IntegerField()
    WD_t0 = models.FloatField(default=0) #models.IntegerField()
    SEV_asco_t0 = models.FloatField(default=0) #models.IntegerField()
    SEV_con_t0 = models.FloatField(default=0) #models.IntegerField()
    ONS_leaf_t0 = models.FloatField(default=0) #models.IntegerField()
    ONS_clus_t0 = models.FloatField(default=0) #models.IntegerField()
    DD_9_25_t0=models.FloatField(default=0)
    DD_10_t0=models.FloatField(default=0)
    DD_6_24_t0=models.FloatField(default=0)
    h4_rain_t0=models.FloatField(default=0)
        
class Data(models.Model):
    daily=models.ForeignKey(to=Daily, on_delete=models.CASCADE)
    LotId =  models.TextField(default='000000')
    year= models.FloatField(default=2000) #models.IntegerField()
    doy = models.FloatField(default=1) #models.IntegerField()

    
    
class Blackrot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    state=models.ForeignKey(to=State, on_delete=models.CASCADE)
    data=models.ForeignKey(to=Data, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['created']
        #managed = False
