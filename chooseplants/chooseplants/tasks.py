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
from chooseplants.models import Chooseplants
from rest_framework.parsers import JSONParser
from chooseplants.serializers import ChooseplantsListSerializer
from celery import shared_task


### pacchetti per script
import pandas as pd
import openpyxl
import json

@shared_task
#@csrf_exempt
@api_view(['GET', 'POST'])
def chooseplants_list(request, format=None):
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':
        #data = JSONParser().parse(request)
        serializer = ChooseplantsListSerializer(data=request.data, many=True)

        if serializer.is_valid():
              #serializer.save()
            
              data = [i["data"] for i in serializer.data]
              LotId = data[0][0]['LotId']
              month = data[0][0]['month'] #in formato di tre lettere e.g. 'Mar', a parte for June e July
              year =  data[0][0]['year']
              location= data[0][0]['location']
              semina = data[0][0]['semina'] 
              
              dataframe = pd.read_excel('static/Calendario semina.xlsx',sheet_name=location)   
              b=dataframe[month] 
              
            #     ##### DEFINISCI CHE TIPO DI SEMINA
            # #### il tipo di semina è definito dall'utente
              
              x=b.str.findall(semina)
              x=[" ".join(x[i]) for i in range(0,len(x)-1)]
              x=pd.Series(x)
              srhc = x.index[x.str.contains(semina)]
              list_index=srhc.tolist()
              
              #list_vegetables=dataframe.iloc[list_index,[0,14,15,16,17]] #scegli solo colonne di interesse
              list_vegetables=dataframe.iloc[list_index,[0]] #scegli solo colonne di interesse
              
              df={'LotId':LotId,'year':year,'vegetables':list_vegetables.values.tolist()}
              return JsonResponse(df, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
        
    
#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def chooseplants_detail(request, pk):
    try:
        chooseplants = Chooseplants.objects.get(pk=pk)
    except Chooseplants.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ChooseplantsListSerializer(chooseplants)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ChooseplantsListSerializer(chooseplants, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        chooseplants.delete()
        return HttpResponse(status=204)



