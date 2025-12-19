# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 11:29:38 2023

@author: Salvatori
"""

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from phytodeg.models import PhytoDeg
from rest_framework.parsers import JSONParser
from phytodeg.serializers import PhytoDegListSerializer

import numpy as np
import random
from celery import shared_task

@shared_task
#@csrf_exempt
@api_view(['GET', 'POST'])
def phytodeg_list(request, format=None):
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':

        serializer = PhytoDegListSerializer(data=request.data)
        if serializer.is_valid():
            serialize_data = serializer.data
            list_data = list(serialize_data.values())
                                
           ### LISCIVIAZIONE 4 PARAMETRI
            
            # tc=list_data[0]
            # tf=list_data[1]
            # k=list_data[2]
            # lambdav=list_data[3]


            # random.seed(42)  # Per random
            # np.random.seed(42)  # Per numpy

            # t = np.array(range(40))
            # lisc1 = np.array([0,0,0,0,0,0,0]) 
            # lisc2 = np.array([random.randint(0, 1) for _ in range(33)])
            # lisc=np.concatenate((lisc1,lisc2))

            # sum_cum1 = np.cumsum(lisc[:tc]) 

            # x1 = np.exp(-k * sum_cum1)
 
            # sum_cum2 = np.cumsum(lisc[:])[tc:]

            
            # x2 = 1 * np.exp(-lambdav*(t[tc:]-tc)) * (1- (t[tc:]-tc)/(tf-tc)) * np.exp(-k * sum_cum2)
            # x = np.concatenate((x1, x2))


            #num_points = 10  # Numero di punti dati
            #t_data = np.sort(np.random.choice(t, num_points, replace=False))  # Prendi alcuni t casuali
            #data_values = np.linspace(1, 0, num_points)  # Dati decrescenti tra 1 e 0
            
            
            #df={'t':t.tolist(),'x':x.tolist()},'t_data':t_data.tolist(),'data_values':data_values.tolist()}   
 
            
            #### CURVE GAUSSIANE 8 PARAMETRI
            
            
            def gaussian(x, A, mu, sigma):
                return A * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

            def combined_function(x, A1, mu1, sigma1, A2, mu2, sigma2, C, D):
                f_x = gaussian(x, A1, mu1, sigma1)  # First Gaussian
                g_y = A2 * np.exp(-((f_x - mu2) ** 2) / (2 * sigma2 ** 2)) + C * f_x + D  # Second Gaussian
                return g_y

            # Generate x values in the positive domain
            x_data = np.linspace(0, 40, 100)

            # Define parameter values
            
            A1=list_data[0]
            mu1=list_data[1]
            sigma1=list_data[2]
            A2=list_data[3]
            mu2=list_data[4]
            sigma2=list_data[5]
            C=list_data[6]
            D=list_data[7]
            
            #params = [4.0, 15.0, 4.5, 10.5, 2.5, 0.8, 0.7, 3]
            params=[A1,mu1,sigma1,A2,mu2,sigma2,C,D]
            # Compute function values
            y_data = combined_function(x_data, *params)
                   
            df={'y':y_data.tolist(),'t':x_data.tolist()}                  
                     
            return JsonResponse(df, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
    
#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def phytodeg_detail(request, pk):
    try:
        phytodeg = PhytoDeg.objects.get(pk=pk)
    except PhytoDeg.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = PhytoDegListSerializer(phytodeg)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = PhytoDegListSerializer(phytodeg, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        phytodeg.delete()
        return HttpResponse(status=204)
            
