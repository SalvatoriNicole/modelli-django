"""
Created on Thu Mar 14 11:22:31 2024

@author: nicole
"""

"""
Primo Step
Dati in Input:
    - nord. , sud, est
    - tipo di semina
    - data

Dati in Output:
    - piante filtrate

Secondo Step
Dati di Input:
    - piante scelte
    - coordinate zona sole
    - coordinate zona ombra
    
Dati di Output:
    - mappa
    - consigli su rotazioni
"""

### pacchetti per django

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from cropdistribution.models import Cropdistribution
from rest_framework.parsers import JSONParser
from cropdistribution.serializers import CropdistributionListSerializer
from celery import shared_task


### pacchetti per script
import pandas as pd
import numpy as np
import json
from geopy import distance
import statistics
import re
import itertools
import random
import math
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


@shared_task
#@csrf_exempt
@api_view(['GET', 'POST'])
def cropdistribution_list(request, format=None):
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':
        #data = JSONParser().parse(request)
        serializer = CropdistributionListSerializer(data=request.data, many=True)

        if serializer.is_valid():
              #serializer.save()
            
            data = [i["data"] for i in serializer.data]
              
            LotId = data[0][0]['LotId']
            year = data[0][0]['year']
            location = data[0][0]['location']
            month=data[0][0]['month']
            semina=data[0][0]['semina']
            vegetables = data[0][0]['vegetables'] #[float(data[0]['list_vegetables'])]
            coordinates = data[0][0]['coordinates']
            coordinates_ombra = data[0][0]['coordinates_ombra']
            
            # ### per fare le prove 
            # LotId = data[0]['data'][0]['LotId']
            # year = data[0]['data'][0]['year']
            # location = data[0]['data'][0]['location']
            # month=data[0]['data'][0]['month']
            # semina=data[0]['data'][0]['semina']
            # vegetables = data[0]['data'][0]['vegetables'] #[float(data[0]['list_vegetables'])]
            # coordinates = data[0]['data'][0]['coordinates']
            # coordinates_ombra = data[0]['data'][0]['coordinates_ombra']
            
            vegetables=np.array(vegetables)
            coordinates=np.array(coordinates)
            coordinates_ombra=np.array(coordinates_ombra)
         
         
            dataframe = pd.read_excel('static/Calendario semina.xlsx',sheet_name=location)   
            b=dataframe[month] 
         
         #     ##### DEFINISCI CHE TIPO DI SEMINA
         # #### il tipo di semina è definito dall'utente
         
            x=b.str.findall(semina)
            x=[" ".join(x[i]) for i in range(0,len(x)-1)]
            x=pd.Series(x)
            srhc = x.index[x.str.contains(semina)]
            list_index=srhc.tolist()
         
            list_vegetables=dataframe.iloc[list_index,[0,14,15,16,17]] #scegli solo colonne di interesse
            a=[list_vegetables.loc[list_vegetables['Plants'] == vegetables[i]] for i in range(0,len(vegetables)-1)]         
            chosen_vegetables=pd.concat(a)
            
            dataframe1 = pd.read_excel('static/Crop distribution map.xlsx',sheet_name='Consociazioni')
            dataframe2 = pd.read_excel('static/Crop distribution map.xlsx',sheet_name='Rotazioni')
            a=[dataframe2.loc[dataframe2['Pianta'] == vegetables[i].upper()] for i in range(0,len(vegetables)-1)]         
            consumo_suolo=pd.concat(a).values.tolist()
            
            i=0
            keys=[]
            values=[]
            
            keys=[dataframe1.loc[i,"Piante"] for i in range(0,len(dataframe1)-1)]
            values=[dataframe1.loc[i,"Buona"].split(" - ") for i in range(0,len(dataframe1)-1)]
            consociazioni_buone = {keys[i]: values[i] for i in range(len(keys))}
            
            keys=[dataframe1.loc[i,"Piante"] for i in range(0,len(dataframe1)-1)]
            values=[dataframe1.loc[i,"Cattiva"].split(" - ") for i in range(0,len(dataframe1)-1)]
            consociazioni_cattive = {keys[i]: values[i] for i in range(len(keys))}
            
        
            
             # # #### CHECK SE TRA LE VEGETABLES SCELTE CI SONO CONSOCIAZIONI BUONE O CATTIVE
            
            consociazioni_buone_scelte=[consociazioni_buone.get(chosen_vegetables.iloc[i,0].upper()) for i in range(0,len(chosen_vegetables))]
            consociazioni_cattive_scelte=[consociazioni_cattive.get(chosen_vegetables.iloc[i,0].upper()) for i in range(0,len(chosen_vegetables))]
            chosen_vegetables = chosen_vegetables.assign(cons_buone=consociazioni_buone_scelte,cons_cattive=consociazioni_cattive_scelte)
            chosen_vegetables ["cons_buone"].fillna("Nessuna", inplace = True)
            chosen_vegetables ["cons_cattive"].fillna("Nessuna", inplace = True)
            ### crea le coppie di consociazioni e do dei punteggi
            coppie=[(chosen_vegetables.iloc[i,0],chosen_vegetables.iloc[j,0]) for i in range(0,len(chosen_vegetables)) for j in range(0,len(chosen_vegetables))]
            
            positive= []
            negative= []
            for i in range(0,len(coppie)):
                    j=np.where(chosen_vegetables["Plants"] == coppie[i][0])[0][0]
                    D='\\b'+coppie[i][1].upper()+'\\b'
                    # #CONSOCIAZIONI POSITIVE
                    if coppie[i][1].upper() == " ".join(re.findall(D," ".join(chosen_vegetables.iloc[j,5]).upper())):   
                        positive.append([i,j])
                        coppie[i]=coppie[i]+(1,)           
                        
                    #CONSOCIAZIONI NEGATIVE
                    elif coppie[i][1].upper() == " ".join(re.findall(D," ".join(chosen_vegetables.iloc[j,6]).upper())):   
                        negative.append([i,j])
                        coppie[i]=coppie[i]+(-1,)         
                    else: 
                        coppie[i]=coppie[i]+(0,)
            
            
            # ##### SOLE
            # ### calcola le distanze tra i vari punti per definire le dimensioni della matrice
            
            
            coordinates_from=(coordinates[0,0],coordinates[0,1])
            coordinates_to=(coordinates[1,0],coordinates[1,1])
            distance1=distance.distance(coordinates_from,coordinates_to).m  #distanza tra pixels in m
            
            coordinates_to=(coordinates[2,0],coordinates[2,1])
            distance2=distance.distance(coordinates_from,coordinates_to).m 
            
            coordinates_to=(coordinates[3,0],coordinates[3,1])
            distance3=distance.distance(coordinates_from,coordinates_to).m  
            
            distances=[distance1,distance2,distance3]
            dim1_mat=min(distances)  #lunghezza lato corto
            dim2_mat=statistics.median(distances) #lunghezza lato lungo (la mediana, in quanto il valore max è la diagonale)
            
            
            distanza_max_piante=max(chosen_vegetables['Space within plants'])/100 #in metri ###DISTANZA MASSIMA!!! 
            distanza_max_linee=max(chosen_vegetables['Space within rows'])/100 #in metri
            
            distanza_minima_piante=min(chosen_vegetables['Space within plants'])/100 #in metri ###DISTANZA MASSIMA!!! 
            distanza_minima_linee=min(chosen_vegetables['Space within rows'])/100 #in metri
            ### questa diventa la dimensione dei pixel
            ### quindi il numero dei pixels = dim_mat/distanza_minima_piante
            
            n_pixels1=round(dim1_mat/distanza_max_piante)
            n_pixels2=round(dim2_mat/distanza_max_linee)
            
            
            
            # ##################### OMBRA
                        
            # #### calcola le distanze tra i vari punti per definire le dimensioni della matrice
            
            coordinates_from=(coordinates_ombra[0,0],coordinates_ombra[0,1])
            coordinates_to=(coordinates_ombra[1,0],coordinates_ombra[1,1])
            distance1=distance.distance(coordinates_from,coordinates_to).m  #distanza tra pixels in m
            
            coordinates_to=(coordinates[2,0],coordinates[2,1])
            distance2=distance.distance(coordinates_from,coordinates_to).m 
            
            coordinates_to=(coordinates[3,0],coordinates[3,1])
            distance3=distance.distance(coordinates_from,coordinates_to).m  
            
            distances=[distance1,distance2,distance3]
            dim1_mat=min(distances)  #lunghezza lato corto
            dim2_mat=statistics.median(distances) #lunghezza lato lungo (la mediana, in quanto il valore max è la diagonale)
            
            distanza_max_piante_ombra=max(chosen_vegetables['Space within plants'])/100 #in metri
            distanza_max_linee_ombra=max(chosen_vegetables['Space within rows'])/100 #in metri
            
            distanza_minima_piante_ombra=min(chosen_vegetables['Space within plants'])/100 #in metri
            distanza_minima_linee_ombra=min(chosen_vegetables['Space within rows'])/100 #in metri
            ### questa diventa la dimensione dei pixel
            ### quindi il numero dei pixels = dim_mat/distanza_minima_piante
            
            n_pixels1_ombra=round(dim1_mat/distanza_max_piante_ombra)
            n_pixels2_ombra=round(dim2_mat/distanza_max_linee_ombra)
            
                   
            # #######################
            
            # ########## ALGORITMO DI OTTIMIZZAZIONE
            
            
            groups=chosen_vegetables.groupby(['Sun'])
            gruppi=[groups.get_group(x) for x in groups.groups]
            
            ##### TUTTE LE PIANTE UGUALI
            if len(gruppi) == 1:
                array=[]
                for i in range(0,len(coppie)):
                    array.append(coppie[i][2])
                preferences=np.reshape(array, (int(len(coppie)/len(chosen_vegetables)), int(len(coppie)/len(chosen_vegetables))))
            
                num_plants = len(preferences)
            
                permutations=list(itertools.permutations(list(range(0,num_plants))))
            
                j=0
                fit=[]
                fitness=[]
                for k in range(0,len(permutations)):
                    initial_positions= np.concatenate([permutations[k],permutations[k]])
                    for i in range(0,len(initial_positions)-1):
                        j=i+1
                        fit.append(preferences[initial_positions[i],initial_positions[j]])
            
                    fitness.append(sum(fit))
                    fit=[]
                    
                best_fit=fitness.index(max(fitness))
                indices = [i for i, x in enumerate(fitness) if x == max(fitness)]
            
            
                index=random.randint(0, len(indices)-1)
                index_vegetables=permutations[indices[index]]
            
                ordered_vegetables=[chosen_vegetables.iloc[index_vegetables[i]][0] for i in range(0,len(index_vegetables))]

                veg_map=ordered_vegetables
                veg_matrix=np.array([veg_map]).transpose()    
            
                  
            
            # ### PIANTE DA SOLE O DA OMBRA 
            
            if len(gruppi) > 1:    
                
                
                pianteombra=groups.get_group('Mezzombra')
                piantesole=groups.get_group('Molto sole')
            
                array=[]
                for i in range(0,len(coppie)):
                    array.append(coppie[i][2])
                preferences=np.reshape(array, (int(len(coppie)/len(chosen_vegetables)), int(len(coppie)/len(chosen_vegetables))))
                
                #### faccio doppia permutazione per le piante in sole e piante all'ombra
                index_sun=np.where(chosen_vegetables["Sun"] == "Molto sole")
                index_shadow=np.where(chosen_vegetables["Sun"] == "Mezzombra")
                
                
                num_plants_sun = len(piantesole)
                num_plants_ombra = len(pianteombra)
                
                permutations_sole=list(itertools.permutations(index_sun[0]))
                permutations_ombra=list(itertools.permutations(index_shadow[0]))
                
                j=0
                fit=[]
                fitness=[]
                
                initial_positions_sole= [np.concatenate([permutations_sole[k],permutations_sole[k]]) for k in range(0,len(permutations_sole))]
                initial_positions_ombra= [np.concatenate([permutations_ombra[k],permutations_ombra[k]]) for k in range(0,len(permutations_ombra))]
                
                initial_positions=[]
            
                for i in range(0,len(initial_positions_sole)):
                    for j in range(0,len(initial_positions_ombra)):
                        initial_positions.append(np.concatenate([initial_positions_sole[i],initial_positions_ombra[j]]))
                        initial_positions.append(np.concatenate([initial_positions_ombra[j],initial_positions_sole[i]]))
            
            # ### rendo i due vettori sole e ombra della stessa lunghezza
                if len(initial_positions_sole[0]) > len(initial_positions_ombra[0]):
                    ripetizioni=len(initial_positions_sole[0])/len(initial_positions_ombra[0])
                    for i in range(len(initial_positions_ombra)):
                        #ripeto il vettore più piccolo tot volte fino a raggiungere il vettore grande
                        initial_positions_ombra[i]=np.tile(initial_positions_ombra[i],math.ceil(ripetizioni)) 
                        
                    ## se la divisione della lunghezza dei due vettori non è un numero intero, allora il vettore più piccolo sarà diventato più grande, e quindi 
                    ## lo riporto alla dimensione corretta
                    if len(initial_positions_ombra[0]) > len(initial_positions_sole[0]): 
                        for i in range(len(initial_positions_ombra)):
                            initial_positions_ombra[i]=initial_positions_ombra[i][0:len(initial_positions_sole[0])]
                
            #     ### faccio la stessa cosa nell'altro caso
                
                if len(initial_positions_ombra[0]) > len(initial_positions_sole[0]):
                    ripetizioni=len(initial_positions_ombra[1])/len(initial_positions_sole[1])
                    for i in range(len(initial_positions_sole)):
                        #ripeto il vettore più piccolo tot volte fino a raggiungere il vettore grande
                        initial_positions_sole[i]=np.tile(initial_positions_sole[i],math.ceil(ripetizioni)) 
                        
                    ## se la divisione della lunghezza dei due vettori non è un numero intero, allora il vettore più piccolo sarà diventato più grande, e quindi 
                    ## lo riporto alla dimensione corretta
                    if len(initial_positions_sole[0]) > len(initial_positions_ombra[0]): 
                        for i in range(len(initial_positions_sole)):
                            initial_positions_sole[i]=initial_positions_sole[i][0:len(initial_positions_ombra[0])]
                
                
                polygon = Polygon(coordinates)
                point = Polygon(coordinates_ombra)
                #### per capire se la zona di sole e ombra è interna o osterna alla zona di sole
                
                if polygon.contains(point)==True: 
                
                    twoD_matrix=[]  
                    twoD_positions=[] 
                    for i in range(0,len(initial_positions_sole)):
                        for j in range(0,len(initial_positions_ombra)):  
                            
                            twoD_matrix=np.append([[initial_positions_sole[i]]], [[initial_positions_ombra[j]]],axis=1)
                            twoD_sole=np.append([[initial_positions_sole[i]]], [[initial_positions_sole[i]]],axis=1)
                            result=np.concatenate((twoD_sole, twoD_matrix,twoD_sole), axis=-1)
                            twoD_positions.append(result)   
                   
                    i=0
                    fit1=[]
                    fit2=[]
                    fit3=[]
                    fitness=[]
                    for i in range(0,len(twoD_positions)):
                        for colonna in range(0,len(twoD_positions[0][0][0])-1):
                            riga0=0
                            fit1.append(preferences[twoD_positions[i][0][riga0][colonna],twoD_positions[i][0][riga0][colonna+1]]) #fit tra riga 0
                            riga1=1
                            fit2.append(preferences[twoD_positions[i][0][riga1][colonna],twoD_positions[i][0][riga1][colonna+1]]) #fit tra riga 1
                            fit3.append(preferences[twoD_positions[i][0][riga0][colonna],twoD_positions[i][0][riga1][colonna]]) #fit tra riga 0 riga 1 (per colonne)
                        
                        ##### devo fare la stessa cosa nell'altra dimensione
                        
                        fit=fit1+fit2+fit3
                        fitness.append(sum(fit))
                        fit1=[]
                        fit2=[]
                        fit3=[]
                        fit=[]
                    
                    
                    best_fit=fitness.index(max(fitness))
                    indices = [i for i, x in enumerate(fitness) if x == max(fitness)]
                    
                    index=random.randint(0, len(indices)-1)
                    index_vegetables=twoD_positions[indices[index]]
                    
                    
                    ordered_vegetables_top_bottom=[chosen_vegetables.iloc[index_vegetables[0][0][i]][0] for i in range(0,len(index_vegetables[0][0]))]
                    ordered_vegetables=[chosen_vegetables.iloc[index_vegetables[0][1][i]][0] for i in range(0,len(index_vegetables[0][0]))]
                    
                    ##### TROVATA LA LISTA OTTIMALE DI PIANTE, ADESSO VA MESSA DENTRO LA MAPPA
            
                    veg_map=ordered_vegetables
                    veg_matrix=np.array([veg_map]).transpose()
                    veg_map_top_bottom=ordered_vegetables_top_bottom
                    veg_matrix_top_bottom=np.array([veg_map_top_bottom]).transpose()
                    
                    veg_matrix=np.concatenate((veg_matrix_top_bottom,veg_matrix,veg_matrix_top_bottom),axis=1)
            
                else:
                    j=0
                    fit=[]
                    fitness=[]
                
                    
                    initial_positions=[]
                    for i in range(0,len(initial_positions_sole)):
                        for j in range(0,len(initial_positions_ombra)):
                            initial_positions.append(np.concatenate([initial_positions_sole[i],initial_positions_ombra[j]]))
                            initial_positions.append(np.concatenate([initial_positions_ombra[j],initial_positions_sole[i]]))
                    
                            
                    for i in range(0,len(initial_positions)):
                        for j in range(0,len(initial_positions[i])-1):
                            k=j+1
                            fit.append(preferences[initial_positions[i][j],initial_positions[i][k]])
                            
                        fitness.append(sum(fit))
                        fit=[]
                    
                    
                    best_fit=fitness.index(max(fitness))
                    indices = [i for i, x in enumerate(fitness) if x == max(fitness)]
                    
                    index=random.randint(0, len(indices)-1)
                    index_vegetables=initial_positions[indices[index]]
                    
                    ordered_vegetables=[chosen_vegetables.iloc[index_vegetables[i]][0] for i in range(0,len(index_vegetables))]
                    ##### TROVATA LA LISTA OTTIMALE DI PIANTE, ADESSO VA MESSA DENTRO LA MAPPA
                    veg_map=ordered_vegetables
                    veg_matrix=np.array([veg_map]).transpose()    
            
            # ############## CREATE MAPS WITH SHAPEFILES https://towardsdatascience.com/create-categorical-choropleth-with-python-122da5ae6764
            
            # Associa un valore numerico univoco a ciascuna stringa
            string_to_numeric = {chosen_vegetables.iloc[i][0]: i for i in range(len(chosen_vegetables))}
            
            # Crea una matrice numerica
            numeric_matrix = np.vectorize(string_to_numeric.get)(veg_matrix)
            # get the unique values from data
            # i.e. a sorted list of all values in data
            values = np.unique(numeric_matrix.ravel())
            
            label=[chosen_vegetables.iloc[i][0].format(l=values[i]) for i in range(len(values))]
            numeric_matrix = np.vectorize(string_to_numeric.get)(veg_matrix).tolist()
            
            df={'LotId':LotId,'year':year,'numeric_matrix':numeric_matrix,'label':label, 'min_distance_between_plants':distanza_minima_piante,
            'min_distance_between_rows':distanza_minima_linee,'min_distance_between_plants_shadow':distanza_minima_piante_ombra,
            'min_distance_between_rows_shadow':distanza_minima_linee_ombra, 'max_distance_between_plants':distanza_max_piante,
            'max_distance_between_rows':distanza_max_linee,'max_distance_between_plants_shadow':distanza_max_piante_ombra,
            'max_distance_between_rows_shadow':distanza_max_linee_ombra,'consumo_suolo':consumo_suolo}   
            
    
            #df={'data':data}   
            return JsonResponse(df, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
        
    
#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def cropdistribution_detail(request, pk):
    try:
        cropdistribution = Cropdistribution.objects.get(pk=pk)
    except Cropdistribution.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = CropdistributionListSerializer(cropdistribution)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = CropdistributionListSerializer(cropdistribution, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        cropdistribution.delete()
        return HttpResponse(status=204)