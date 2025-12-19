#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 15:38:12 2024

@author: nicole
"""
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from pavone.models import Pavone
from rest_framework.parsers import JSONParser
from pavone.serializers import PavoneListSerializer

import numpy as np
from celery import shared_task

@shared_task
#@csrf_exempt
@api_view(['GET', 'POST'])
def pavone_list(request, format=None):
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':
        #data = JSONParser().parse(request)
        serializer = PavoneListSerializer(data=request.data, many=True)

        if serializer.is_valid():
             #serializer.save()
            
             data = [i["data"] for i in serializer.data]
             state = [i["state"] for i in serializer.data]
            
             len_data=len(data)
             
             if bool(state[0])==True:
                 hours_of_wetness_t0=float(state[0]['hours_of_wetness_t0'])
                 hours_of_dry_t0=float(state[0]['hours_of_dry_t0'])
#                 doy1=int(state[0]['doy'])
             else:
                 hours_of_wetness_t0=0
                 hours_of_dry_t0=0
#                 doy1=1
             
             for j in range(0,len(data)):
                                                      
                LotId = [i["LotId"] for i in data[j]]
                doy=[int(i["doy"]) for i in data[j]]
                year=[int(i["year"]) for i in data[j]]
                data_daily = [i["data_daily"] for i in data[j]]
                index=0 #doy.index(doy1)
                
                df=[]
                #Missing_values=[]
    
                InfCum1=0
                InfCum2=0

                for days in range(index,len(data_daily)):
                    #LotId = [i["LotId"] for i in data_daily[days]]
                    ver=all("hod" in d for d in data_daily[days])
                    if ver==True:
                        hod=[int(i["hod"]) for i in data_daily[days]]
                    else:
                        hod=[0]*24 
                        #Missing_values.append(doy[days])
                        #stop='Missing Value at day '+ str(days)
                        #return JsonResponse(Missing_values, safe=False, status=201)
                        df_new={'LotId':LotId[0],'year':year[0],'data':df}  
                        return JsonResponse(df_new, safe=False, status=201)
                    
                    ver=all("temperature" in d for d in data_daily[days])
                    if ver==True:
                        Temp_data=[float(i["temperature"]) for i in data_daily[days]]
                    else:
                        #Temp_data=[15]*24
                        #Missing_values.append(doy[days])
                        df_new={'LotId':LotId[0],'year':year[0],'data':df}  
                        return JsonResponse(df_new, safe=False, status=201)
                    
                    
                    ver=all("leafwetness" in d for d in data_daily[days])
                    if ver==True:
                        bagnatura_data=[int(i["leafwetness"]) for i in data_daily[days]]
                    else:
                        #bagnatura_data=[0]*24
                        #Missing_values.append(doy[days])
                        df_new={'LotId':LotId[0],'year':year[0],'data':df}  
                        return JsonResponse(df_new, safe=False, status=201)


                    bagnatura_data = [0 if i is None else i for i in bagnatura_data]
                    T = Temp_data
                    
                    
                    # Magarey et al., 2004
                    # The model estimates the wetness duration required to achieve a critical disease intensity at a given temperature. The
                    # critical disease threshold is defined here operationally as 20% disease incidence or 5% disease severity on an infected plant part
                    # at nonlimiting inoculum concentration.

                    ### parameters from Thomidis et al. 2021
              
                    T_min=5
                    T_max=25
                    T_opt=20
                    W_min=12
                    W_max=24
                    
                    j=0
                    f_t=[0]*len(T)
                    W_T=[0]*len(T)
                    infection=[0]*len(T)
                    hours_of_wetness=hours_of_wetness_t0
                    hours_of_dry=hours_of_dry_t0
                    
                    #Tomodis et al., 2021
                    # Continuous wet hours are summed to determine leaf wetness.
                    # However, if there is an interruption of fewer than or equal to 20 dry hours and low relative
                    # humidity (<70%), the summation of hours is continued. In contrast, if the interruption of dry hours is
                    # longer than 20 dry hours, a new summation of hours is started. Temperature is the event
                    # average temperature during each wet period. Cultivar susceptibility and inoculum level
                    # were not considered because insufficient information was available about their effects on
                    # the occurrence of infection.
                        
                    
                    # The wetness duration requirement (W(T)) for the critical disease threshold at temperature T is estimated from a temperature
                    # response function (f(T)) and the minimum value of the wetness duration requirement (Wmin):

                    while j <= len(T)-1:
                        if bagnatura_data[j]==1:
                            hours_of_wetness+=1
                        else:
                            hours_of_dry+=1
                        if hours_of_dry>20:
                            hours_of_wetness=0
                        if T[j]>=T_min and T[j]<=T_max:
                            f_t[j]=((T_max-T[j])/(T_max-T_opt))*((T[j]-T_min)/(T_opt-T_min))**((T_opt-T_min)/(T_max-T_opt))
                            W_T[j]=W_min/f_t[j] 
                        else:
                            f_t[j]=0                           
                            W_T[j]=10000
                        
                        if hours_of_wetness >= W_T[j] and hours_of_wetness <= W_max:
                            infection[j]=1
                        else:
                            infection[j]=0
                        
                        j+=1
                    
                    
                    # where W(T) = wetness duration requirement (in hours) for the critical disease threshold at temperature T, Wmin = the minimum
                    # value of the wetness duration requirement for the critical disease threshold at any temperature, and f(T) = temperature response
                    # function

                    # Thus, the model estimates a simple temperature-wetness response for each pathogen with the interaction between
                    # temperature and wetness ignored

                    
                    hours_of_wetness_t0=hours_of_wetness
                    hours_of_dry_t0=hours_of_dry
                    
                    df_days={'doy':doy[days], 'Infection': infection, 'hours_of_wetness_t0':hours_of_wetness_t0, 'hours_of_dry_t0':hours_of_dry_t0}
                    df.append(df_days)
            
             df_new={'LotId':LotId[0],'year':year[0],'data':df}   
        
             return JsonResponse(df_new, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
        
    
#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def pavone_detail(request, pk):
    try:
        pavone= Pavone.objects.get(pk=pk)
    except Pavone.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = PavoneListSerializer(pavone)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = PavoneListSerializer(pavone, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        pavone.delete()
        return HttpResponse(status=204)
            

