# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Created on Tue Feb 27 15:38:12 2024

# @author: nicole
# """

# from django.http import HttpResponse, JsonResponse
# from rest_framework.decorators import api_view
# from elateridi.models import Elateridi
# from rest_framework.parsers import JSONParser
# from elateridi.serializers import ElateridiListSerializer

# import numpy as np
# from celery import shared_task

# @shared_task
# #@csrf_exempt
# @api_view(['GET', 'POST'])
# def elateridi_list(request, format=None):
#     if request.method == 'GET':
#         return HttpResponse("I want POST requests")
#     elif request.method == 'POST':
#         #data = JSONParser().parse(request)
#         serializer = ElateridiListSerializer(data=request.data, many=True)

#         if serializer.is_valid():
#              #serializer.save()
            
#              data = [i["data"] for i in serializer.data]
#              state = [i["state"] for i in serializer.data]
            
             
#              if bool(state[0])==True:
#                  giorni_utili_t0=float(state[0]['giorni_utili_t0'])
                 
#              else:
#                  giorni_utili_t0=0
                 
#              results=[]
             
#              for j in range(0,len(data)):
                                                      
#                 LotId = [i["LotId"] for i in data[j]]
#                 doy=[int(i["doy"]) for i in data[j]]
#                 year=[int(i["year"]) for i in data[j]]
#                 Temp_data_mean = [i["mean_soil_temperature"] for i in data[j]]
#                 Temp_data_max = [i["max_soil_temperature"] for i in data[j]]
#                 rain= [i["rain"] for i in data[j]]
#                 installation= [i["installation"] for i in data[j]]
                
                
 
#                 T = Temp_data_mean
#                 sommatermica=[0]*len(T)
#                 gauge_back=[0]*len(T)   
#                 estrazione =[0]*len(T)
#                 giorni_utili =[0]*len(T)
                
#                 doy_back=list(reversed(doy))
#                 Temp_data_mean_back=list(reversed(Temp_data_mean))
#                 Temp_data_max_back=list(reversed(Temp_data_max))
#                 rain_back=list(reversed(rain))
                
                        
                
#                 for i in range(len(T)):
                
#                     """
#                     A) PREVISIONE GIORNI UTILI PER POSA TRAPPOLE 

#                     Quando la temperatura media giornaliera del terreno a -10cm si prevede supererà i 7°C, 
#                     il DSS indicherà la possibilità di installare le trappole (cruscotto verde); il cruscotto sarà rosso 
#                     con T <7°C e > 29°C; 

#                     il cruscotto sarà rosso anche con terreno saturo (giorni con piogge > 25 mm) – 
#                     valutazione giorni di saturazione con piogge elevate (sensori umidità del suolo da valorizzare 
#                     se presenti). Rosso anche con siccità (assenza di pioggia > 15 gg e T max > 20°C) . 
#                     """
#                     if installation[i]==0:
                    
#                         if  7 < Temp_data_mean_back[i] < 15:
#                             gauge_back[i]=1 #gauge verde
                        
#                         if rain_back[i] >= 25 or all(x==0 for x in rain_back[i:i+15]) or Temp_data_max_back[i]>=20:
#                             gauge_back[i]=0 #gauge rosso
                            
#                     if installation[i]==1:
#                             gauge_back[i]=1 
             
#                 gauge=list(reversed(gauge_back))
                 
#                 for k in range(len(T)):   
                    
                    
#                     if installation[k] == 1 and Temp_data_mean[k] >= 7 and rain[k]<25:
#                         giorni_utili[k]=giorni_utili_t0 + 1
#                         giorni_utili_t0=giorni_utili[k]
#                     else:
                        
#                         if k==0:
#                             giorni_utili[k]=giorni_utili_t0
                    
#                         else:
#                             giorni_utili[k]=giorni_utili[k-1]
                        
#                         giorni_utili_t0=giorni_utili[k]
                    
                        
#                     if giorni_utili[k] > 10:
#                         estrazione=1
#                     else:
#                         estrazione=0
#                     """
#                     B) PREVISIONE PRELIEVO TRAPPOLE DOPO INSTALLAZIONE
#                     Il DSS dal giorno dell’installazione deve considerare la temperatura maggiore di 7°C per 10 giorni 
#                     utili, anche non consecutivi dando la previsione della data di preleivo (all’11simo giorno utile dalla
#                     posa). Successivamente il DSS deve prevedere la data di raccolta delle trappole in anticipo.
#                     Durante il periodo in cui le trappole rimangono nel terreno, se avviene una precipitazione maggiore 
#                     dei 25 mm, allora questa giornata non sarà utile.
                    
#                     Quando si raggiungono i 10 giorni utili, dai dati meteo, il DSS avviserà l’utente di estrarre le trappole dal terreno.
#                     """
                    

            
#              df_new={'LotId':LotId[0],'year':year[0],'doy':doy, 'Gauge': gauge, 'giorni_utili':giorni_utili, 'Estrazione':estrazione}   
#              results.append(df_new)
        
#              return JsonResponse(results, safe=False, status=201)
#         return JsonResponse(serializer.errors, safe=False, status=400)
        
    
# #@csrf_exempt
# @api_view(['GET', 'PUT', 'DELETE'])
# def elateridi_detail(request, pk):
#     try:
#         elateridi= Elateridi.objects.get(pk=pk)
#     except Elateridi.DoesNotExist:
#         return HttpResponse(status=404)

#     if request.method == 'GET':
#         serializer = ElateridiListSerializer(elateridi)
#         return JsonResponse(serializer.data, safe=False)

#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = ElateridiListSerializer(elateridi, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, safe=False, status=400)

#     elif request.method == 'DELETE':
#         elateridi.delete()
#         return HttpResponse(status=204)
            

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 15:38:12 2024
@author: nicole
"""

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from elateridi.models import Elateridi
from elateridi.serializers import ElateridiListSerializer


#@csrf_exempt
@api_view(['GET', 'POST'])
def elateridi_list(request, format=None):

    if request.method == 'GET':
        return HttpResponse("I want POST requests")

    elif request.method == 'POST':

        serializer = ElateridiListSerializer(data=request.data, many=True)

        if serializer.is_valid():

            # tua struttura: data + state
            data = [i["data"] for i in serializer.data]
            state = [i["state"] for i in serializer.data]

            results = []

            for j in range(0, len(data)):

                # ---------------------------------------------------------
                # 0) STATE: leggo stato precedente (per streaming giorno-per-giorno)
                # ---------------------------------------------------------
                if bool(state[j]) is True:
                    prev_state = state[j]
                else:
                    prev_state = {}

                # runs attive + contatore per run_id
                active_runs = prev_state.get("active_runs", [])
                run_counter = int(prev_state.get("run_counter", 0))

                # history per siccità (ultimi 15 giorni)
                rain_history = prev_state.get("rain_history", [])
                tmax_history = prev_state.get("tmax_history", [])

                if rain_history is None:
                    rain_history = []
                if tmax_history is None:
                    tmax_history = []

                # ---------------------------------------------------------
                # 1) DATI: possono essere 365 giorni o 1 giorno
                # ---------------------------------------------------------
                LotId = [i["LotId"] for i in data[j]]
                doy = [int(i["doy"]) for i in data[j]]
                year = [int(i["year"]) for i in data[j]]

                Temp_data_mean = [float(i["mean_soil_temperature"]) for i in data[j]]
                Temp_data_max  = [float(i["max_soil_temperature"]) for i in data[j]]
                rain = [float(i["rain"]) for i in data[j]]

                # installation==1 SOLO il giorno della posa
                installation = [int(i["installation"]) for i in data[j]]

                T = Temp_data_mean
                n = len(T)

                # ---------------------------------------------------------
                # 2) Preparo struttura runs in memoria (dal prev_state)
                # ---------------------------------------------------------
                active_runs_new = []
                for r in active_runs:
                    active_runs_new.append({
                        "run_id": r.get("run_id"),
                        "install_year": int(r.get("install_year")),
                        "install_doy": int(r.get("install_doy")),
                        "giorni_utili_t0": int(r.get("giorni_utili_t0", 0)),
                        "done": bool(r.get("done", False))
                    })

                # Per l’OUTPUT: per ogni run voglio una lista lunga n (valori per i giorni di questa chiamata)
                # La costruisco dinamicamente: run_id -> {"...":..., "giorni_utili": [...], "Estrazione":[...]}
                runs_out_map = {}

                def ensure_run_out(r):
                    rid = r["run_id"]
                    if rid not in runs_out_map:
                        runs_out_map[rid] = {
                            "run_id": rid,
                            "install_year": r["install_year"],
                            "install_doy": r["install_doy"],
                            "giorni_utili": [],
                            "Estrazione": []
                        }

                # ---------------------------------------------------------
                # 3) A) GAUGE + siccità streaming + B) RUNS streaming
                #    (scorro i giorni ricevuti e aggiorno tutto)
                # ---------------------------------------------------------
                gauge = [0] * n

                # uso buffer rolling per siccità: aggiorno ad ogni giorno
                # partendo dall'history arrivata nello state
                rain_buf = list(rain_history)
                tmax_buf = list(tmax_history)

                for k in range(n):

                    # --- aggiorno HISTORY (rolling) con il giorno corrente ---
                    rain_buf.append(rain[k])
                    tmax_buf.append(Temp_data_max[k])

                    if len(rain_buf) > 15:
                        rain_buf = rain_buf[-15:]
                    if len(tmax_buf) > 15:
                        tmax_buf = tmax_buf[-15:]

                    # --- calcolo siccità corretta in streaming ---
                    no_rain_15 = (len(rain_buf) == 15 and all(x == 0 for x in rain_buf))
                    drought = (no_rain_15 and tmax_buf[-1] >= 20)

                    # --- A) GAUGE (giornaliero) ---
                    if installation[k] == 1:
                        # giorno posa: verde
                        gauge[k] = 1
                    else:
                        g = 1 if (7 < Temp_data_mean[k] < 15) else 0

                        # saturazione
                        saturation = (rain[k] >= 25)

                        # rosso anche se troppo freddo/caldo (coerente col tuo testo)
                        if saturation or drought or Temp_data_mean[k] <= 7 or Temp_data_mean[k] > 29:
                            g = 0

                        gauge[k] = g

                    # --- B) RUNS: se oggi posa -> nuova run ---
                    if installation[k] == 1:
                        run_counter += 1
                        run_id = f"run_{run_counter}_y{year[k]}_d{doy[k]}"

                        new_run = {
                            "run_id": run_id,
                            "install_year": year[k],
                            "install_doy": doy[k],
                            "giorni_utili_t0": 0,
                            "done": False
                        }
                        active_runs_new.append(new_run)

                    # --- aggiorno TUTTE le run attive con il meteo di oggi ---
                    for r in active_runs_new:

                        # mi assicuro che questa run esista anche nell'output
                        ensure_run_out(r)

                        if r["done"] is True:
                            # run già completata: rimane in estrazione
                            runs_out_map[r["run_id"]]["giorni_utili"].append(r["giorni_utili_t0"])
                            runs_out_map[r["run_id"]]["Estrazione"].append(1)
                            continue

                        # giorno utile (come tua regola B):
                        # Tmean >=7 (e <=29) e rain<25
                        if Temp_data_mean[k] >= 7 and Temp_data_mean[k] <= 29 and rain[k] < 25:
                            r["giorni_utili_t0"] = r["giorni_utili_t0"] + 1

                        # estrazione quando supero 10 giorni utili (all’11° utile)
                        if r["giorni_utili_t0"] > 10:
                            r["done"] = True
                            estr = 1
                        else:
                            estr = 0

                        runs_out_map[r["run_id"]]["giorni_utili"].append(r["giorni_utili_t0"])
                        runs_out_map[r["run_id"]]["Estrazione"].append(estr)

                # ---------------------------------------------------------
                # 4) preparo runs in lista (ordine di creazione)
                # ---------------------------------------------------------
                runs = []
                for r in active_runs_new:
                    rid = r["run_id"]
                    # runs_out_map ha già le liste lunghe n
                    runs.append(runs_out_map[rid])

                # ---------------------------------------------------------
                # 5) aggiorno state da restituire (fondamentale per giorno dopo)
                # ---------------------------------------------------------
                new_state = {
                    "run_counter": run_counter,
                    "active_runs": active_runs_new,
                    "rain_history": rain_buf,   # ultimi 15 dopo l’ultimo giorno processato
                    "tmax_history": tmax_buf
                }

                # ---------------------------------------------------------
                # 6) output finale (tua struttura)
                # ---------------------------------------------------------
                df_new = {
                    "LotId": LotId[0],
                    "year": year[0],
                    "doy": doy,
                    "Gauge": gauge,
                    "runs": runs,
                    "state": new_state
                }

                results.append(df_new)

            return JsonResponse(results, safe=False, status=201)

        return JsonResponse(serializer.errors, safe=False, status=400)


#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def elateridi_detail(request, pk):
    try:
        elateridi = Elateridi.objects.get(pk=pk)
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



            

