# Create your models here.
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
#from django.contrib.postgres.fields import ArrayField

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

    
        
class Data(models.Model):
    LotId =  models.TextField(default='000000')
    year= models.FloatField(default=2000) #models.IntegerField()
    month = models.TextField(default='000000') #in formato di tre lettere e.g. 'Mar', a parte for June e July
    location = models.TextField(default='000000') 
    semina = models.TextField(default='000000') 
    
class Chooseplants(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    data=models.ForeignKey(to=Data, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['created']
        #managed = False
