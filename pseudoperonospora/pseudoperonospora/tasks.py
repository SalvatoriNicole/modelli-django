#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 17:42:22 2024

@author: nicole
"""
#### Model from Li et al. 2022

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
#from django.views.decorators.csrf import csrf_exempt
from pseudoperonospora.models import Pseudoperonospora
from rest_framework.parsers import JSONParser
from pseudoperonospora.serializers import PseudoperonosporaListSerializer

import numpy as np
from celery import shared_task
import math

@shared_task
#@csrf_exempt
@api_view(['GET', 'POST'])
def pseudoperonospora_list(request, format=None):
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':
        serializer = PseudoperonosporaListSerializer(data=request.data, many=True)
        if serializer.is_valid():

             data = [i["data"] for i in serializer.data]
             state = [i["state"] for i in serializer.data]
            
             len_data=len(data)
             
             if bool(state[0])==True:
                 LWD_t0=float(state[0]['LWD_t0'])
                 y_t0=float(state[0]['y_t0'])
                 #doy1=int(state[0]['doy'])
             else:
                 LWD_t0=0
                 y_t0=0
                 #doy1=1
             
             for j in range(0,len(data)):
                                                      
                LotId = [i["LotId"] for i in data[j]]
                doy=[int(i["doy"]) for i in data[j]]
                year=[int(i["year"]) for i in data[j]]
                data_daily = [i["data_daily"] for i in data[j]]
                #index=doy.index(doy1)
                
                df=[]
                start=0
                symptoms = 0
                #Missing_values=[]

                for days in range(0,len(data_daily)):
                    #LotId = [i["LotId"] for i in data_daily[days]]
                    ver=all("hod" in d for d in data_daily[days])
                    if ver==True:
                        hod=[int(i["hod"]) for i in data_daily[days]]
                    else:
                        df_new={'LotId':LotId[0],'year':year[0],'data':df}  
                        return JsonResponse(df_new, safe=False, status=201)
                    
                    ver=all("temperature" in d for d in data_daily[days])
                    if ver==True:
                        Temp_data=[float(i["temperature"]) for i in data_daily[days]]
                    else:
                        df_new={'LotId':LotId[0],'year':year[0],'data':df}  
                        return JsonResponse(df_new, safe=False, status=201)

                    
                    ver=all("leafwetness" in d for d in data_daily[days])
                    if ver==True:
                        bagnatura_data=[int(i["leafwetness"]) for i in data_daily[days]]
                    else:
                        df_new={'LotId':LotId[0],'year':year[0],'data':df}  
                        return JsonResponse(df_new, safe=False, status=201)
                   
                    
                    len_data_daily=len(bagnatura_data)

                    bagnatura_data = [0 if i is None else i for i in bagnatura_data]
                    Temp_data = [0 if i is None else i for i in Temp_data]
                
                    LWD = [LWD_t0] * len(Temp_data)
                    TLWD = [0] * len(Temp_data)
                    if symptoms==1:
                        start=0
                        symptoms=0
                        y_t0=0
                    y = [y_t0] * len(Temp_data)
                    i=1
                    
                    a=40 #40
                    b=15 #2
                    c=5
                    d=30

                    while i<=len(Temp_data)-2:
                        if bagnatura_data[i]==1 or (LWD[i-1] >0 and bagnatura_data[i+1]==1):
                                LWD[i]=LWD[i-1]+1
                                TLWD[i]=Temp_data[i]
                        else:
                                LWD[i]=0
                    
                        #start=0
                        if LWD[i]*TLWD[i]>=a and LWD[i] >=b and (TLWD[i]>=c and TLWD[i]<=d):
                            start=1    
                            symptoms=0
                        # else:
                        #     # if symptoms == 1:
                        #     start=0
                        #Once the infection is done, the incubation period starts and it needs a couple of days to finish.
                        # It is an integration of hourly average temperature (Th).  The incubation finishes when the integration of y>=1, when leaves are predicted to be symptomatic   
                        if start==1:
                            y[i]=0.0165/(1+10389.2*math.exp(-0.5743*Temp_data[i]))
                        i+=1
                        
                    
                    if sum(y)>=1:
                        symptoms=1
                    
                    y_t0=sum(y)
                    LWD_t0=LWD[-1]    
                    
                    df_days={'doy':doy[days], 'start_infection': start, 'Symptoms': symptoms, 'y_t0':y_t0, 'LWD_t0':LWD_t0}
                    df.append(df_days)
            
             df_new={'LotId':LotId[0],'year':year[0],'data':df}   
        
             return JsonResponse(df_new, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
        
    
#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def pseudoperonospora_detail(request, pk):
    try:
        pseudoperonospora = Pseudoperonospora.objects.get(pk=pk)
    except Pseudoperonospora.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = PseudoperonosporaListSerializer(pseudoperonospora)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = PseudoperonosporaListSerializer(pseudoperonospora, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        pseudoperonospora.delete()
        return HttpResponse(status=204)
            

