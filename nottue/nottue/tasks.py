#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 15:38:12 2024

@author: nicole
"""

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from nottue.models import Nottue
from rest_framework.parsers import JSONParser
from nottue.serializers import NottueListSerializer

import numpy as np
from celery import shared_task

@shared_task
#@csrf_exempt
@api_view(['GET', 'POST'])
def nottue_list(request, format=None):
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':
        #data = JSONParser().parse(request)
        serializer = NottueListSerializer(data=request.data, many=True)

        if serializer.is_valid():
             #serializer.save()
            
             data = [i["data"] for i in serializer.data]
             state = [i["state"] for i in serializer.data]
	     
             
             if bool(state[0])==True:
                 sommatermica_t0=float(state[0]['sommatermica_t0'])
             else:
                 sommatermica_t0=0
                 
             start_accum=0
             results=[]
             
             for j in range(0,len(data)):
                                                      
                LotId = [i["LotId"] for i in data[j]]
                doy=[int(i["doy"]) for i in data[j]]
                year=[int(i["year"]) for i in data[j]]
                Temp_data = [i["temperature"] for i in data[j]]
                wind= [i["wind"] for i in data[j]]
                catture= [i["catture"] for i in data[j]]
                trappola= [i["trappola"] for i in data[j]]
                
 
                T = Temp_data
                sommatermica=[0]*len(T)
                rischio=[0]*len(T)
                danno=[0]*len(T)
                                             
                
                for i in range(len(T)):
                
                    #Rischio basso: no venti da sud adatti (scirocco), nessuna cattura di adulti nella rete territoriale di trappole a 
                    #feromoni sessuali 
                    #Rischio medio: un evento di vento forte da sud adatto, catture di adulti nella rete di trappole a 
                    #feromoni sessuali inferiori ai livelli corrispondenti al rischio alto; 
                    #Rischio alto: uno o più (sovrapposizione di popolazioni) venti forti da sud, catture elevate delle 
                    #trappole della rete territoriale (> 15 adulti/settimana almeno in parte nelle trappole VARl o 
                    #sticky, > 25 adulti/settimana almeno in parte delle trappole HARTSTACK o luminose 
                    
                    ### Se Rischio medio o alto 
                    
                    ### Inizio calcolo somme termiche
                    
                    #somma_termica = (Tmax-Tmin)/2 - 10.4
                    
                        
                    if wind[i]==0 and catture[i]==0:
                        rischio[i]=0
                        
                    ### RICORDARE CHE LE CATTURE SONO SEMPRE SETTIMANALI!
                    if wind[i]==1 or ((catture[i] >= 15 and trappola[i] == "VARl") or (catture[i] >= 25 and (trappola[i] == "HARTSTACK" or trappola[i] == "Luminose"))):
                        rischio[i] = 2
                    
                    if wind[i]==1 or ((0 < catture[i] < 15 and trappola[i] == "VARl") or (0 < catture[i] < 25 and (trappola[i] == "HARTSTACK" or trappola[i] == "Luminose"))):
                        rischio[i] = 1
                    
                    if rischio[i] > 0:
                        start_accum = 1
                                    
                    if start_accum==1:
                        if i==0:
                            sommatermica[i] = sommatermica_t0 + max(T[i] - 10.4,0)
                                                
                        else:
                            sommatermica[i] = sommatermica[i-1] + max(T[i] - 10.4,0)
    
                    
                    # se somma_termica = 176
    
                    #il 50% della popolazione raggiunge lo stadio di sviluppo in grado di danneggiare le colture 
                    # (per gli altri stadi di sviluppo vedere file NOTTUEUSA1991 a pag 6)
    
                    if sommatermica[i] >= 176:
                        danno[i] = 1
            

            
             df_new={'LotId':LotId[0],'year':year[0],'doy':doy, 'Rischio': rischio, 'sommatermica_t0':sommatermica, 'danno':danno}   
             results.append(df_new)
        
             return JsonResponse(results, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
        
    
#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def nottue_detail(request, pk):
    try:
        nottue= Nottue.objects.get(pk=pk)
    except Nottue.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = NottueListSerializer(nottue)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = NottueListSerializer(nottue, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        nottue.delete()
        return HttpResponse(status=204)
            

