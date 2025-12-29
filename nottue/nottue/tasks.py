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
             
             for j in range(0, len(data)):

                LotId = [i["LotId"] for i in data[j]]
                doy = [int(i["doy"]) for i in data[j]]
                year = [int(i["year"]) for i in data[j]]
                T = [float(i["temperature"]) for i in data[j]]
                wind = [int(i["wind"]) for i in data[j]]
                trappola = [i["trappola"] for i in data[j]]
            
                # CATTURE: possono essere None / "" nei giorni non campionati
                catture_raw = [i.get("catture", None) for i in data[j]]
            
                n = len(T)
            
                # =========================
                # PARAMETRI
                # =========================
                BASE_T = 10.4
                RISK2_VARL = 15
                RISK2_HART = 25
                EXTEND_DAYS = 7        # vento -> scadenza = oggi + 6
                MAX_WINDOW_DAYS = 10   # durata max finestra = 10 giorni (inclusivi)
                DAMAGE_DD = 176.0
            
                # =========================
                # OUTPUT GIORNALIERI
                # =========================
                rischio = [0] * n     # rischio registrato SOLO nel giorno di chiusura finestra
                danno = [0] * n       # numero episodi che raggiungono 176 quel giorno (0,1,2,...)
            
                # =========================
                # STATE INGRESSO
                # =========================
                if bool(state[0]) is True:
                    st = state[0]
            
                    # finestra
                    window_active = bool(st.get("window_active_t0", False))
                    window_start_idx = int(st.get("window_start_idx_t0", -1))
                    window_end_idx = int(st.get("window_end_idx_t0", -1))
            
                    cum_varl = float(st.get("cum_varl_t0", 0.0))
                    cum_hart = float(st.get("cum_hart_t0", 0.0))
                    risk_window_max = int(st.get("risk_window_max_t0", 0))
            
                    # episodi
                    active_episodes_in = st.get("active_episodes_t0", []) or []
                    episode_id_counter = int(st.get("episode_id_counter_t0", 0))
            
                    # ====== NUOVO: flag break basato SOLO su misura campionata con 0 ======
                    had_zero_catches = bool(st.get("had_zero_catches_t0", True))
            
                else:
                    window_active = False
                    window_start_idx = -1
                    window_end_idx = -1
            
                    cum_varl = 0.0
                    cum_hart = 0.0
                    risk_window_max = 0
            
                    active_episodes_in = []
                    episode_id_counter = 0
            
                    # all’inizio permettiamo che il primo episodio possa partire
                    had_zero_catches = True
            
                # =========================
                # EPISODI: serie DD per ciascun episodio (per plot)
                # dd_series lunga n con NaN quando non attivo
                # =========================
                episodes_all = []
                ep_map = {}
            
                for ep in active_episodes_in:
                    ep_id = int(ep["id"])
                    ep_obj = {
                        "id": ep_id,
                        "start_year": ep.get("start_year"),
                        "start_doy": ep.get("start_doy"),
                        "dd": float(ep.get("dd", 0.0)),
                        "dd_series": [np.nan] * n,
                        "finished": False,
                        "finish_year": None,
                        "finish_doy": None,
                    }
                    episodes_all.append(ep_obj)
                    ep_map[ep_id] = ep_obj
            
                # log utili
                window_events = []
                damage_events = []
            
                # =========================
                # LOOP GIORNALIERO
                # =========================
                for i in range(n):
            
                    # ----- campionamento catture: distinguo null (non campionato) da 0 (campionato e zero)
                    raw_c = catture_raw[i]
                    has_sample = (raw_c is not None) and (raw_c != "")
                    c = float(raw_c) if has_sample else 0.0
            
                    # ====== NUOVO: aggiorno break SOLO se ho misura e vale 0
                    if has_sample and c == 0:
                        had_zero_catches = True
            
                    # ---------------------------------------------------------
                    # 1) FINESTRA MOBILE: vento estende la scadenza, MA max 10 gg
                    # ---------------------------------------------------------
                    if wind[i] == 1:
                        if not window_active:
                            window_active = True
                            window_start_idx = i
                            window_end_idx = i + (EXTEND_DAYS - 1)  # oggi + 6
                            cum_varl = 0.0
                            cum_hart = 0.0
                            risk_window_max = 0
                        else:
                            # se il vento arriva entro scadenza, estendo
                            if i <= window_end_idx:
                                window_end_idx = max(window_end_idx, i + (EXTEND_DAYS - 1))
            
                    # limite massimo finestra: start..start+9
                    if window_active and window_start_idx >= 0:
                        max_end = window_start_idx + (MAX_WINDOW_DAYS - 1)
                        if window_end_idx > max_end:
                            window_end_idx = max_end
            
                    # ---------------------------------------------------------
                    # 2) ACCUMULO CATTURE & UPDATE RISCHIO
                    #    SOLO se finestra attiva e SOLO nei giorni campionati
                    # ---------------------------------------------------------
                    if window_active and has_sample:
                        if trappola[i] == "VARl":
                            cum_varl += c
                        elif trappola[i] in ("HARTSTACK", "Luminose"):
                            cum_hart += c
            
                        tot = cum_varl + cum_hart
            
                        # AND: rischio>0 solo se ho catture cumulative > 0 nella finestra
                        if tot > 0:
                            if (cum_varl >= RISK2_VARL) or (cum_hart >= RISK2_HART):
                                risk_window_max = max(risk_window_max, 2)
                            else:
                                risk_window_max = max(risk_window_max, 1)
            
                    # ---------------------------------------------------------
                    # 3) AGGIORNO DD per tutti gli episodi attivi (sovrapposti)
                    # ---------------------------------------------------------
                    dd_inc = max(T[i] - BASE_T, 0.0)
            
                    for ep_id, ep_obj in ep_map.items():
                        if not ep_obj["finished"]:
                            ep_obj["dd"] += dd_inc
                            ep_obj["dd_series"][i] = ep_obj["dd"]
            
                    # chiudo episodi che superano soglia oggi (possono essere >1)
                    finished_today = []
                    for ep_id, ep_obj in ep_map.items():
                        if (not ep_obj["finished"]) and (ep_obj["dd"] >= DAMAGE_DD):
                            ep_obj["finished"] = True
                            ep_obj["finish_year"] = year[i]
                            ep_obj["finish_doy"] = doy[i]
                            finished_today.append(ep_id)
            
                            damage_events.append({
                                "episode_id": ep_id,
                                "finish_year": year[i],
                                "finish_doy": doy[i],
                                "dd": ep_obj["dd"],
                            })
            
                    if finished_today:
                        danno[i] = len(finished_today)
            
                    # ---------------------------------------------------------
                    # 4) CHIUSURA FINESTRA: SOLO QUI certifico rischio
                    #    e SOLO QUI posso creare un nuovo episodio:
                    #    - risk>0
                    #    - had_zero_catches == True  (break reale: misura con 0)
                    # ---------------------------------------------------------
                    if window_active and i == window_end_idx:
            
                        rischio[i] = risk_window_max
            
                        window_events.append({
                            "start_year": year[window_start_idx] if window_start_idx >= 0 else None,
                            "start_doy": doy[window_start_idx] if window_start_idx >= 0 else None,
                            "end_year": year[i],
                            "end_doy": doy[i],
                            "length_days": (window_end_idx - window_start_idx + 1) if window_start_idx >= 0 else None,
                            "risk": risk_window_max,
                            "cum_varl": cum_varl,
                            "cum_hart": cum_hart,
                        })
            
                        # ====== NUOVO: anti “episodi multipli” se catture sempre >0 ======
                        if (risk_window_max > 0) and had_zero_catches:
                            episode_id_counter += 1
                            new_id = episode_id_counter
            
                            new_ep = {
                                "id": new_id,
                                "start_year": year[i],
                                "start_doy": doy[i],
                                "dd": 0.0,
                                "dd_series": [np.nan] * n,
                                "finished": False,
                                "finish_year": None,
                                "finish_doy": None,
                            }
                            episodes_all.append(new_ep)
                            ep_map[new_id] = new_ep
            
                            # dopo aver fatto partire un episodio, non ne faccio partire altri
                            # finché non vedo una MISURA campionata con catture == 0
                            had_zero_catches = False
            
                        # reset finestra
                        window_active = False
                        window_start_idx = -1
                        window_end_idx = -1
                        cum_varl = 0.0
                        cum_hart = 0.0
                        risk_window_max = 0
            
                # =========================
                # STATE USCITA: solo episodi non finiti
                # =========================
                active_episodes_out = []
                for ep in episodes_all:
                    if not ep["finished"]:
                        active_episodes_out.append({
                            "id": ep["id"],
                            "dd": ep["dd"],
                            "start_year": ep["start_year"],
                            "start_doy": ep["start_doy"],
                        })
            
                # =========================
                # RISULTATO
                # =========================
                df_new = {
                    "LotId": LotId[0],
                    "year": year[0],
                    "doy": doy,
            
                    "Rischio_evento_chiusura_finestra": rischio,
                    "Danno_eventi_giornalieri": danno,
            
                    "episodi_dd": [
                        {
                            "episode_id": ep["id"],
                            "start_year": ep["start_year"],
                            "start_doy": ep["start_doy"],
                            "finish_year": ep["finish_year"],
                            "finish_doy": ep["finish_doy"],
                            "dd_series": ep["dd_series"],
                        }
                        for ep in episodes_all
                    ],
            
                    "window_events": window_events,
                    "damage_events": damage_events,
            
                    # ===== state per prossima chiamata =====
                    "window_active_t0": window_active,
                    "window_start_idx_t0": window_start_idx,
                    "window_end_idx_t0": window_end_idx,
                    "cum_varl_t0": cum_varl,
                    "cum_hart_t0": cum_hart,
                    "risk_window_max_t0": risk_window_max,
            
                    "active_episodes_t0": active_episodes_out,
                    "episode_id_counter_t0": episode_id_counter,
            
                    # ====== NUOVO ======
                    "had_zero_catches_t0": had_zero_catches,
                }
            
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
            


