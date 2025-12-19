#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 15:38:12 2024

@author: nicole
"""

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from elateridi.models import Elateridi
from rest_framework.parsers import JSONParser
from elateridi.serializers import ElateridiListSerializer

import numpy as np
from celery import shared_task

@shared_task
#@csrf_exempt
@api_view(['GET', 'POST'])
def elateridi_list(request, format=None):
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':
        #data = JSONParser().parse(request)
        serializer = ElateridiListSerializer(data=request.data, many=True)

        if serializer.is_valid():
             #serializer.save()
            
             data = [i["data"] for i in serializer.data]
             state = [i["state"] for i in serializer.data]
            
             
             if bool(state[0])==True:
                 giorni_utili_t0=float(state[0]['giorni_utili_t0'])
                 
             else:
                 giorni_utili_t0=0
                 
             results=[]
             
             for j in range(0,len(data)):
                                                      
                LotId = [i["LotId"] for i in data[j]]
                doy=[int(i["doy"]) for i in data[j]]
                year=[int(i["year"]) for i in data[j]]
                Temp_data_mean = [i["mean_soil_temperature"] for i in data[j]]
                Temp_data_max = [i["max_soil_temperature"] for i in data[j]]
                rain= [i["rain"] for i in data[j]]
                installation= [i["installation"] for i in data[j]]
                
                
 
                T = Temp_data_mean
                sommatermica=[0]*len(T)
                gauge_back=[0]*len(T)   
                estrazione =[0]*len(T)
                giorni_utili =[0]*len(T)
                
                doy_back=list(reversed(doy))
                Temp_data_mean_back=list(reversed(Temp_data_mean))
                Temp_data_max_back=list(reversed(Temp_data_max))
                rain_back=list(reversed(rain))
                
                        
                
                for i in range(len(T)):
                
                    """
                    A) PREVISIONE GIORNI UTILI PER POSA TRAPPOLE 

                    Quando la temperatura media giornaliera del terreno a -10cm si prevede supererà i 7°C, 
                    il DSS indicherà la possibilità di installare le trappole (cruscotto verde); il cruscotto sarà rosso 
                    con T <7°C e > 29°C; 

                    il cruscotto sarà rosso anche con terreno saturo (giorni con piogge > 25 mm) – 
                    valutazione giorni di saturazione con piogge elevate (sensori umidità del suolo da valorizzare 
                    se presenti). Rosso anche con siccità (assenza di pioggia > 15 gg e T max > 20°C) . 
                    """
                    if installation[i]==0:
                    
                        if  7 < Temp_data_mean_back[i] < 15:
                            gauge_back[i]=1 #gauge verde
                        
                        if rain_back[i] >= 25 or all(x==0 for x in rain_back[i:i+15]) or Temp_data_max_back[i]>=20:
                            gauge_back[i]=0 #gauge rosso
                            
                    if installation[i]==1:
                            gauge_back[i]=1 
             
                gauge=list(reversed(gauge_back))
                 
                for k in range(len(T)):   
                    
                    
                    if installation[k] == 1 and Temp_data_mean[k] >= 7 and rain[k]<25:
                        giorni_utili[k]=giorni_utili_t0 + 1
                        giorni_utili_t0=giorni_utili[k]
                    else:
                        
                        if k==0:
                            giorni_utili[k]=giorni_utili_t0
                    
                        else:
                            giorni_utili[k]=giorni_utili[k-1]
                        
                        giorni_utili_t0=giorni_utili[k]
                    
                        
                    if giorni_utili[k] > 10:
                        estrazione=1
                    else:
                        estrazione=0
                    """
                    B) PREVISIONE PRELIEVO TRAPPOLE DOPO INSTALLAZIONE
                    Il DSS dal giorno dell’installazione deve considerare la temperatura maggiore di 7°C per 10 giorni 
                    utili, anche non consecutivi dando la previsione della data di preleivo (all’11simo giorno utile dalla
                    posa). Successivamente il DSS deve prevedere la data di raccolta delle trappole in anticipo.
                    Durante il periodo in cui le trappole rimangono nel terreno, se avviene una precipitazione maggiore 
                    dei 25 mm, allora questa giornata non sarà utile.
                    
                    Quando si raggiungono i 10 giorni utili, dai dati meteo, il DSS avviserà l’utente di estrarre le trappole dal terreno.
                    """
                    

            
             df_new={'LotId':LotId[0],'year':year[0],'doy':doy, 'Gauge': gauge, 'giorni_utili':giorni_utili, 'Estrazione':estrazione}   
             results.append(df_new)
        
             return JsonResponse(results, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
        
    
#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def elateridi_detail(request, pk):
    try:
        elateridi= Elateridi.objects.get(pk=pk)
    except Elateridi.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ElateridiListSerializer(elateridi)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ElateridiListSerializer(elateridi, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        elateridi.delete()
        return HttpResponse(status=204)
            

