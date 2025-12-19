# Create your models here.
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class PhytoDeg(models.Model):
    created = models.DateTimeField(auto_now_add=True)
   # tc = models.IntegerField(default=5)
   # tf = models.IntegerField(default=10) 
   # k = models.FloatField(default=1)
   # lambdav = models.FloatField(default=1)
    A1 = models.FloatField(default=5)
    mu1 = models.FloatField(default=10) 
    sigma1 = models.FloatField(default=1)
    A2 = models.FloatField(default=1)
    mu2 = models.FloatField(default=10) 
    sigma2 = models.FloatField(default=1)
    C = models.FloatField(default=10) 
    D = models.FloatField(default=1)
    
    class Meta:
        ordering = ['created']
