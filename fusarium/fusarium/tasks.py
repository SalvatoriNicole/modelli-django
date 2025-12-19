#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 17:42:22 2024

@author: nicole
"""
#### Model from Li et al. 2022

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from fusarium.models import Fusarium
from rest_framework.parsers import JSONParser
from fusarium.serializers import FusariumListSerializer
from django.views.decorators.csrf import csrf_exempt

import numpy as np
from celery import shared_task
import math


@shared_task
@csrf_exempt
@api_view(['GET', 'POST'])
def fusarium_list(request, format=None):
    
    
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':
        serializer = FusariumListSerializer(data=request.data, many=True)
        if serializer.is_valid():

             data = [i["data"] for i in serializer.data]
             state = [i["state"] for i in serializer.data]
            
             len_data=len(data)
             
             if bool(state[0])==True:
                RintMax_P_t0=float(state[0]['RintMax_P_t0']) #max mm of rain per hour in the previous day
                RH80_t0=float(state[0]['RH80_t0']) #numero di ore con RH>80
                Rtot_P_t0=float(state[0]['Rtot_P_t0']) #totale di pioggia (mm) nel giorno precedente
                rain_streak=float(state[0]['rain_streak_t0'])
             else:
                RintMax_P_t0=0
                RH80_t0=0
                Rtot_P_t0=0
                rain_streak=0
                
             for j in range(0,len(data)):
                                                      
                LotId = [i["LotId"] for i in data[j]]
                doy=[int(i["doy"]) for i in data[j]]
                year=[int(i["year"]) for i in data[j]]
                data_daily = [i["data_daily"] for i in data[j]]
                #index=doy.index(doy1)
                
                df=[]

                for days in range(0,len(data_daily)):
                    
                    
                    # Controllo per i dati di temperatura
                    ver = all("temperature" in d for d in data_daily[days])
                    if ver:
                        Temp_data = [float(i["temperature"]) for i in data_daily[days]]
                    else:
                        # Sostituisci con la media della giornata se non ci sono dati
                        Temp_data = [float(i["temperature"]) for i in data_daily[days] if "temperature" in i]
                        if not Temp_data:
                            Temp_data = [15] * 24  # Sostituisci con una temperatura standard, ad esempio 15°C
                    
                    # Controllo per i dati di bagnatura
                    ver = all("leafwetness" in d for d in data_daily[days])
                    if ver:
                        bagnatura_data = [int(i["leafwetness"]) for i in data_daily[days]]
                    else:
                        bagnatura_data = [0] * 24  # Sostituisci con 0 se non ci sono dati
                    
                    # Controllo per le ore del giorno
                    ver = all("hod" in d for d in data_daily[days])
                    if ver:
                        hod = [int(i["hod"]) for i in data_daily[days]]
                    else:
                        # Crea un elenco di ore consecutive
                        hod = list(range(24))  # Ore da 0 a 23
                        
                     # Controllo per i dati di pioggia
                    
                    ver=all("rain" in d for d in data_daily[days])
                    if ver:
                        rain=[int(i["rain"]) for i in data_daily[days]]
                    else:
                       # Sostituisci con 0 se non ci sono dati
                       rain = [float(i["rain"]) for i in data_daily[days] if "rain" in i]
                       if not rain:
                           rain = [0] * 24  # Sostituisci con nessuna pioggia
                   
                    
                    ver=all("humidity" in d for d in data_daily[days])
                    if ver:
                        RH_data=[float(i["humidity"]) for i in data_daily[days]]
                    else:
                         # Sostituisci con 70 se non ci sono dati
                         RH_data = [float(i["humidity"]) for i in data_daily[days] if "humidity" in i]
                         if not RH_data:
                             rain = [70] * 24  # Sostituisci con una umidità standard, ad esempio 70%
 
                    
                    if doy[days] >= 180 and doy[days] < 325:
                        GS=0
                    elif doy[days] >= 325 and doy[days] < 350:
                        GS= 0.1 #GS=10 #semina - emergenza
                    elif doy[days] >= 350 and doy[days] < 365:
                        GS= 0.21 #GS=21 #accestimento
                    elif doy[days] >= 365 or doy[days] < 61:
                        GS= 0.35 #GS=35 #levata
                    elif doy[days] >= 61 and doy[days] < 106:
                        GS= 0.51 #51  #spigatura/fioritura
                    elif doy[days] >= 106 and doy[days] < 167:
                        GS= 0.35 #71 #maturazione
                    else:
                        GS= 0.21 #89 #disseccamento
                    

                    bagnatura_data = [0 if i is None else i for i in bagnatura_data]
                    Temp_data = [0 if i is None else i for i in Temp_data]
                    rain = [0 if i is None else i for i in rain] 
                    RH_data = [0 if i is None else i for i in RH_data] 
                
                    #calcolo per il giorno precedente, andrà poi nel t0 successivo
                    RintMax_P = max(rain)
                    Rtot_P = sum(rain)
                    RH80 = sum(1 for rh in RH_data if rh >= 80)

                    # RintMax_P=[RintMax_P_t0]*len(Temp_data) #max mm of rain per hour in the previous day
                    # RH80=[RH80_t0]*len(Temp_data) #numero di ore con RH>80
                    # Rtot_P=[Rtot_P_t0]*len(Temp_data) #totale di pioggia (mm) nel giorno precedente
                    Y_rain=[0]*len(Temp_data)
                    Y_norain=[0]*len(Temp_data)
                    
                    # Imposta il valore di W in base alla sequenza di giorni di pioggia
                    if rain_streak == 1:
                        W = 1.1
                    elif rain_streak == 2:
                        W = 2.5
                    elif rain_streak == 3:
                        W = 1.2
                    elif rain_streak >= 4:
                        W = 0.8
                    else:
                        W = 1.1  # Default per giorni senza pioggia
                    
                    
                    i=0
                    

                    in_t=15 #incubation time. valore tra 4 e 20, vedi fig.2, che dipenderebbe da SPO e T ma dicui non abbiamo equazione
                    Y_95 = 0 #variabile dummy che vale 0 o 1
                    
                    list_SPO=[0]*len(Temp_data)
                    list_DIS=[0]*len(Temp_data)
                    list_INF=[0]*len(Temp_data)
                    list_INV=[0]*len(Temp_data)
                    
                    
                    while i<=len(Temp_data)-2:
                        
                        ### sporulation rate
                        
                        Tmin=5
                        Tmax=35

                        Teq=(Temp_data[i]-Tmin)/(Tmax-Tmin)

                        if Teq  <= 1:
                            list_SPO[i]=np.power(25.98 * Teq**8.59 * (1 - Teq), 0.24) / (1 + np.exp(5.52 - 0.51 * in_t))
                        else:
                            list_SPO[i]=0
                        ### dispersal rate
                        ## from Rossi et al. 2002
                        

                        # estimated number of conidia per m3 of air per day, in days with and without rain. E va bene tenere per m3 di aria in quanto
                        # la nostra simulazione è per singola pianta
                        Y_rain[i]=-839.7+410.3*W+4.08*Temp_data[i]**2+115.45*RintMax_P_t0-455.9*Y_95
                        Y_norain[i]=-682.3+45.68*Temp_data[i]+21.5*RH80_t0+107*Rtot_P_t0
                      
                        if rain[i]>0:
                            list_DIS[i]=max(0,Y_rain[i])
                        if rain[i]==0:
                            list_DIS[i]=max(0,Y_norain[i])
                        
                        i+=1
                        
                        #### Infection rate 
                        list_INF[i]=max(0,np.real(-0.099-0.363*in_t+0.07808*in_t*Temp_data[i]-0.00591*in_t*Temp_data[i]**2+0.000199*in_t*Temp_data[i]**3-0.00000*in_t*Temp_data[i]**4))

                        ### Invasion by mycelium
                        Tmin=0
                        Tmax=38
                        Teq=(Temp_data[i]-Tmin)/(Tmax-Tmin)

                        list_INV[i]=max(0,np.real((5.53*Teq**1.55*(1-Teq))**1.35))

                    SPO=np.mean(np.real(list_SPO))
                    DIS=np.mean(list_DIS)
                    INF=np.mean(list_INF)
                    INV=np.mean(np.real(list_INV))
                    
                    FHB_risk=(SPO*DIS*INF*GS)/1000
                    TOX_risk=(INF*GS*INV)
                        

                    Rtot_P_t0=Rtot_P #max mm of rain per hour in the previous day
                    RintMax_P_t0=RintMax_P #numero di ore con RH>80
                    RH80_t0 = RH80
                    
                    if Rtot_P > 0:
                        rain_streak += 1
                    else:
                        rain_streak = 0
                

                    
                    df_days={'doy':doy[days],'Fusarium risk': FHB_risk, 'Toxicity risk': TOX_risk, 
                             'Rtot_P_t0':Rtot_P_t0, 'RintMax_P_t0':RintMax_P_t0, 'RH80_t0':RH80_t0,
                             'rain_streak':rain_streak}
                    df.append(df_days)
                    
            
             df_new={'LotId':LotId[0],'year':year[0],'data':df}   
        
             return JsonResponse(df_new, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
        
    
@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def fusarium_detail(request, pk):
    try:
        fusarium = Fusarium.objects.get(pk=pk)
    except Fusarium.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = FusariumListSerializer(fusarium)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = FusariumListSerializer(fusarium, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        fusarium.delete()
        return HttpResponse(status=204)
            
