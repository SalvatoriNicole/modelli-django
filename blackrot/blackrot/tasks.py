# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 11:29:38 2023

@author: Salvatori
"""

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
#from django.views.decorators.csrf import csrf_exempt
from blackrot.models import Blackrot
from rest_framework.parsers import JSONParser
from blackrot.serializers import BlackrotListSerializer

import numpy as np
import pandas as pd
from statistics import mean 
from celery import shared_task

@shared_task
#@csrf_exempt
@api_view(['GET', 'POST'])
def blackrot_list(request, format=None):
    if request.method == 'GET':
        return HttpResponse("I want POST requests")
    elif request.method == 'POST':
        #data = JSONParser().parse(request)
        serializer = BlackrotListSerializer(data=request.data, many=True)

        if serializer.is_valid():
              #serializer.save()
            
              data = [i["data"] for i in serializer.data]
              state = [i["state"] for i in serializer.data]
             
             
              if bool(state[0])==True:

                  ASCmat_t0 = [float(state[0]['ASCmat_t0'])]
                  COMmat_t0 = [float(state[0]['COMmat_t0'])] # questi due saranno valori singoli medi della giornata
                  H_postr_t0 = [float(state[0]['H_postr_t0'])]  # questo sarà l'ultimo valore dell'array
                  H_rain_t0 = [float(state[0]['H_rain_t0'])]  # questo sarà l'ultimo valore dell'
                  Hdry_t0 = [float(state[0]['Hdry_t0'])]  # questo sarà l'ultimo valore dell'array
                  RH_t0 = [float(state[0]['RH_t0'])]  # questo sarà l'ultimo valore dell'array
                  wetness_t0 = [float(state[0]['wetness_t0'])]
                  WD_t0=[float(state[0]['WD_t0'])]
                  SEV_asco_t0=[float(state[0]['SEV_asco_t0'])]
                  SEV_con_t0=[float(state[0]['SEV_con_t0'])]
                  ONS_leaf_t0=[float(state[0]['ONS_leaf_t0'])]
                  ONS_clus_t0=[float(state[0]['ONS_clus_t0'])]
                  DD_9_25_t0=[float(state[0]['DD_9_25_t0'])]
                  DD_10_t0=[float(state[0]['DD_10_t0'])]
                  DD_6_24_t0=[float(state[0]['DD_6_24_t0'])]
                  h4_rain_t0=[float(state[0]['h4_rain_t0'])]
                  doy1=float(state[0]['doy'])
                 
              else:
                  ASCmat_t0 =  [0]
                  COMmat_t0 = [0]
                  H_postr_t0 = [0]
                  H_rain_t0 = [0]
                  Hdry_t0 = [0]
                  RH_t0 = [0]
                  wetness_t0 = [0]
                  WD_t0= [0]
                  SEV_asco_t0= [0]
                  SEV_con_t0=[0]
                  ONS_leaf_t0=[0]
                  ONS_clus_t0=[0]
                  DD_9_25_t0=[0]
                  DD_10_t0=[0]
                  DD_6_24_t0=[0]
                  h4_rain_t0=[0]
                  doy1=1
             
              for j in range(0,len(data)):
                                                      
                LotId = [i["LotId"] for i in data[j]]
                doy=[int(i["doy"]) for i in data[j]]
                year=[int(i["year"]) for i in data[j]]
                data_daily = [i["data_daily"] for i in data[j]]
                
                index=doy.index(doy1)
                
                df=[]
                Missing_values=[]
    

                for days in range(index,len(data_daily)):
                    #LotId = [i["LotId"] for i in data_daily[days]]
                    
                    
                    ver=all("hod" in d for d in data_daily[days])
                    if ver==True:
                        hod=[int(i["hod"]) for i in data_daily[days]]
                    else:
                        hod=[0]*24 
                        Missing_values.append(doy[days])
                        #stop='Missing Value at day '+ str(days)
                        #return JsonResponse(Missing_values, safe=False, status=201)
                    
                    ver=all("temperature" in d for d in data_daily[days])
                    if ver==True:
                        Temp_data=[float(i["temperature"]) for i in data_daily[days]]
                    else:
                        Temp_data=[15]*24
                        Missing_values.append(doy[days])
                    
                    ver=all("humidity" in d for d in data_daily[days])
                    if ver==True:
                        RH_data=[float(i["humidity"]) for i in data_daily[days]]
                    else:
                        RH_data=[50]*24
                        Missing_values.append(doy[days])
                    
                    ver=all("leafwetness" in d for d in data_daily[days])
                    if ver==True:
                        bagnatura_data=[int(i["leafwetness"]) for i in data_daily[days]]
                    else:
                        bagnatura_data=[0]*24
                        Missing_values.append(doy[days])
                    
                    ver=all("rain" in d for d in data_daily[days])
                    if ver==True:
                        Rain_data=[float(i["rain"]) for i in data_daily[days]]
                    else:
                        Rain_data=[0]*24
                        Missing_values.append(doy[days])
                        
                    ver=all("GS" in d for d in data_daily[days])
                    if ver==True:
                        GS=[int(i["GS"]) for i in data_daily[days]]
                    else:
                        GS=[30]*24
                        Missing_values.append(doy[days])
                        
                    ver=all("treatment" in d for d in data_daily[days])
                    if ver==True:
                        treatment=[int(i["treatment"]) for i in data_daily[days]]
                    else:
                        treatment=[False]*24
                        Missing_values.append(doy[days])
                    
                    
                    Rain_data = [0 if i is None else i for i in Rain_data] #substitute None with 0
                    bagnatura_data = [0 if i is None else i for i in bagnatura_data]
                    RH_data = [0 if i is None else i for i in RH_data]
                    Temp_data = [0 if i is None else i for i in Temp_data]         
                    ##########################################################
                    # I) Production and maturation of inoculum in overwintered sources
                    # ASCOSPORE FROM MUMMIES

                    T = Temp_data
                    ASCMAT = []  # ASCMAT(j) ranges from 0 (no ascospores have matured until day
                    # j to I (all seasonal ascospores have matured)
                    # estimated contribution of ascospores to the total inoculum of the vineyard (on a 0 to 1 scale)
                    I = 0.7
                    ASCmat = []  # cumulative proportion of mature ascospores on jth day;
                    ASCmat_der = []  # rate of ascospore maturation, as the first order derivative of ASCmat
                    #DD_9_25 = []  # DD_9_25 in onesti et al., 2018
                    
                    
                    ######################## I DEGREE DAYS SONO GIORNALIERI!!!!! QUINDI ANCHE QUESTI DEVONO ESSERE INIZIALIZZATI

                    T = [0 if x <= 9 else x for x in T]
                    T = [x-9 if x > 9 and x <= 25 else x for x in T]
                    T = [16 if x > 25 else x for x in T]

                    j = 1  # starting from 2nd position, since I have the derivative to do

                    a = 12.75  # from Onesti et al., 2018
                    b = 0.005  # from Onesti et al., 2018
                    DD_9_25 = np.cumsum(T)/24
                    DD_9_25 = DD_9_25_t0+DD_9_25
                    #DD_9_25_pro = np.sum(T)/24 + DD_9_25_t0[0] ######################QUESTO VA CAPITO SE FACCIO U ARRAY UGUALE TUTTO IL GIORNO
                    #DD_9_25_pro=[DD_9_25]*(len(T)-1)
                    
                    a=(np.exp(-a*np.exp(-b*DD_9_25))).tolist()
                    ASCmat = ASCmat_t0 + a
                    while j <= len(T):
                        ASCmat_der.append(ASCmat[j]-ASCmat[j-1])  # derivata, dt==1 sempre
                        ASCMAT.append(I*ASCmat_der[j-1])
                        j += 1
                
                    
                    # # CONIDIA FROM MUMMIES
    
                    COMMAT = []  # COMMAT(j) ranges from 0 (no conidia have been produced until
                    # day j) to I all seasonal conidia from mummies have been produced)
                    I_1 = 0.3  # , estimate of the seasonal dose of conidia from mummies, expressed as the
                    # estimated contribution of conidia from mummies to the total inoculumof the vineyard
                    # (on a 0 to 1 scale);
                    COMmat = []  # cumulative proportion of mature conidia in mummies on jth day;
                    COMmat_der = []
                    DD_10 = []  # cumulative degree-days on day j, calculated from bud break
                    # (stage 08) using 10 °C as the minimum temperature, as follows: when T(j)≤10°,
                    #T(j)=0 when T(j)>10, T(j)=T(j)-10.
    
                    T = Temp_data
                    T = [0 if x <= 10 else x for x in T]
                    T = [x-10 if x > 10 else x for x in T]
    
                    j = 1
                    a = 4  # from Onesti et al., 2018
                    b = 0.005  # from Onesti et al., 2018
                    DD_10 = np.cumsum(T)/24
                    DD_10 = DD_10_t0+DD_10
                    a=(np.exp(-a*np.exp(-b*DD_10))).tolist()
                    COMmat = COMmat_t0 + a
                    # from Onesti et al. 2018
    
                    while j <= len(T):
                        COMmat_der.append(COMmat[j]-COMmat[j-1])  # derivata, dt==1 sempre
                        COMMAT.append(I_1*COMmat_der[j-1])
                        j += 1

                    
                    # ##########################################################
                    # # II) Infection caused by ascospores and/or conidia
                    # # SPORE RELEASE, DISPERSAL, AND DEPOSITION ON THE HOST SURFACE
    
                    SPOREL_asco = ASCMAT
                    SPOREL_con = COMMAT
    
                    R = Rain_data  # +0.5 #i valori erano troppo bassi quindi ho aggiunto 0.5
                    REL_asco = [0] * len(R)
                    REL_con = [0] * len(R)
                    H_postr = [0] * len(R)
                    H_rain = [0] * len(R)
                    # REL(s) ranges from 0 (no spore release) to 1 (all mature spores are released);
    
                    i = 0
    
                    # DEFINE H_postr FOR ASCOSPORE
                    while i <= len(R)-1:
    
                        if i == 0:
                            if H_postr_t0[i] > 0:
                                if R[i] > 0 and R[i] < 3:
                                    H_postr[i] = H_postr_t0[i] + 1
                                if R[i] >= 3:
                                    H_postr[i] = 1
                                if R[i] == 0:
                                    H_postr[i] = H_postr_t0[i]
     
                            if H_postr_t0[i] == 0:
                                if R[i] > 0 and R[i] < 3:
                                    H_postr[i] = 0
                                if R[i] >= 3:
                                    H_postr[i] = 1
                                if R[i] == 0:
                                    H_postr[i] = 0
    
                        if i > 0:
                            if R[i] >= 3:
                                H_postr[i] = 1
    
                            if R[i] > 0 and R[i] < 3:
                                if H_postr[i-1] == 0:
                                    H_postr[i] = 0
                                else:
                                    H_postr[i] = H_postr[i-1]+1
     
                            if R[i] == 0:
                                H_postr[i] = (H_postr[i-1])
    
                        REL_asco[i] = (1-0.195*0.57**(H_postr[i]))
                        i += 1
    
                    i = 0
                    release_time = 1000
                    count = 0
                    threshold = 0
                    zero_rain = 0
     
                    # DEFINE H_rain FOR CONIDIA
                    while i <= len(R)-1:
                        if i == 0:
                            if H_rain_t0[i] > 0:
                                if R[i] > 0 and R[i] < 3:
                                    H_rain[i] = H_rain_t0[i] + 1
                                if R[i] >= 3:
                                    H_rain[i] = 1
                                if R[i] == 0:
                                    H_rain[i] = 0
     
                            if H_rain_t0[i] == 0:
                                if R[i] < 3:
                                    H_rain[i] = 0
                                if R[i] >= 3:
                                    H_rain[i] = 1
                        if i > 0:
    
                            if R[i] >= 3:
                                H_rain[i] = 1
    
                            if R[i] > 0 and R[i] < 3:
                                if H_rain[i-1] == 0:
                                    H_rain[i] = 0
                                else:
                                    H_rain[i] = H_rain[i-1]+1
     
                            if R[i] == 0:
                                H_rain[i] = 0
    
                        REL_con[i] = (1/(1+np.exp(3.96-2.83*H_rain[i])))
                        i += 1
    
    
                    if GS[0] >= 11:  # BBCH=11 first leaf unfolded
                        unfolded = GS[0]-10
                    else:
                        unfolded = 0
                    DEP_asco = []
                    DEP_con = []
                    i = 0
    
                    Pdep = unfolded*0.07  
                    if Pdep > 1:
                        Pdep=1
     
                    while i < len(T):
                        DEP_asco.append(Pdep*REL_asco[i])
                        DEP_con.append(Pdep*REL_con[i])
                        i += 1
    
    
                    # SPORE SURVIVAL
                    alpha_asco = 2.94  # +-0.57
                    gamma_asco = 0.18  # +-0.05
                    alpha_con = 4.45  # +-1.88
                    gamma_con = 0.18  # +-0.08
     
                    RH = RH_data
                    Hdry = [0] * len(RH)
                    SUR_asco = [0] * len(RH)
                    SUR_con = [0] * len(RH)
     
                    i=0
                    
                    while i <= len(RH)-1:                       
                       
                        if i > 0:
                            Hdry_t0[0]=Hdry[i-1]
                            RH_t0[0]=RH[i-1]
    
                        if i == len(RH)-1:
                            Hdry_t0[0]=Hdry[i-1]
                            RH_t0[0]=RH[i-1]
                            RH_end=RH[i]
                       
                        else: 
                            RH_end=RH[i+1]
                       
                        if RH[i] <= 30:
                            if RH_t0[0]<=30 or RH_end <= 30:
                                Hdry[i]=Hdry_t0[0]+1
                            if RH_t0[0]>30 and RH_end> 30:
                                Hdry[i]=0
                               
                        if RH[i]>30:
                            if RH_t0[0]>30 or RH_end > 30:
                                Hdry[i]=0
                            if RH_t0[0] <=30 and RH_end <=30:
                                Hdry[i]=Hdry_t0[0]+1
    
                        SUR_asco[i] = (1/(1+np.exp(-alpha_asco+gamma_asco*Hdry[i])))
                        SUR_con[i] = (1/(1+np.exp(-alpha_con+gamma_con*Hdry[i])))
                        i += 1
    
    
    
                    # I don't multiply by REL since it is already included in DEP
                    SPODOSE_asco = [i1 * i2 * i3 for i1, i2,
                        i3 in zip(SPOREL_asco, DEP_asco, SUR_asco[0:len(DEP_asco)])] ### QUESTO DA CONTROLLARE SICURO
                    SPODOSE_con = [i1 * i2 * i3 for i1, i2,
                        i3 in zip(SPOREL_con, DEP_con, SUR_con[0:len(DEP_asco)])] ### QUESTO DA CONTROLLARE SICURO
    
                    SPODOSE=sum([sum(i) for i in zip(SPODOSE_asco, SPODOSE_con)])
                    # INFECTION OF SUSCEPTIBLE HOST TISSUE
                    T = Temp_data
                    wetness = bagnatura_data
    
                    WD = [0] * len(wetness)  # cumulative number of hours with wetness;
                    i = 0
    
                    while i <= len(wetness)-1:
                       
                       
                        if i > 0:
                            WD_t0[0]=WD[i-1]
                            wetness_t0[0]=wetness[i-1]
    
                        if i == len(wetness)-1:
                            WD_t0[0]=WD[i-1]
                            wetness_t0[0]=wetness[i-1]
                            wetness_end=wetness[i]
                       
                        else: 
                            wetness_end=wetness[i+1]
                       
                        if wetness[i] == 1:
                            if wetness_t0[0]==1 or wetness_end == 1:
                                WD[i]=WD_t0[0]+1
                            if wetness_t0[0]==0 and wetness_end == 0:
                                WD[i]=0
                               
                        if wetness[i]==0:
                            if wetness_t0[0]==0 or wetness_end ==0:
                                WD[i]=0
                            if wetness_t0[0] == 1 and wetness_end ==1:
                                WD[i]=WD_t0[0]+1
    
                        i += 1
    
                    WD.append(0)
                    T.append(0)
                    A = pd.DataFrame(list(zip(WD, T)), columns =['WD', 'T'])
                    Tw=[0]*(len(A)+1)
    
                    i=0
                    j=0
                    while i <= (len(A)-1):
                        if WD[i]>0:
                            j=i
                            while WD[j]>0 and j<(len(A)-1):
                                j=j+1
                            Tw[i:j]=[A.loc[i:j-1, 'T'].mean()]*(j-i)
                            i=j+1
                        else:
                            Tw[i]=0
                            i=i+1
                    Tw=Tw[0:len(WD)-1]
                    T=T[0:len(T)-1]
                    WD=WD[0:len(WD)-1]        
    
    
                    Tmin_asco= 7  # minimum temperature for infection
                    Tmin_con= 7
                    Tmax_asco = 31  # maximum temperature for infection
                    Tmax_con= 33
                    Topt_asco= 24
                    Topt_con = 24  # optimal temperature for infection  when Tmin≤Tw≤Tmax; f(s,T)=0.
                    WDmin_asco = 5  # minimum wetness duration requirement for infection by the spore at any temperature
                    WDmin_con= 6
    
                    f_asco_T= [0] * (len(RH))
                    f_con_T= [0] * (len(RH))
                    WD_asco_T= [0] * (len(RH))
                    WD_con_T= [0] * (len(RH))
                    j = 0
                    while j < len(Tw)-1:
                        if (Tmin_asco >= Tw[j] or Tw[j] >= Tmax_asco):
                            f_asco_T[j]= 0
                        else:
                            f_asco_T[j]= ((Tw[j]-Tmin_asco)/(Topt_asco-Tmin_asco)*((Tmax_asco-Tw[j]/(Tmax_asco-Topt_asco))**((Tmax_asco-Topt_asco)/(Topt_asco-Tmin_asco))))
                            WD_asco_T[j]= (WDmin_asco/f_asco_T[j])
     
                        if (Tmin_con >= Tw[j] or Tw[j] >= Tmax_con):
                            f_con_T[j]= 0
                        else:
                            f_con_T[j]= ((Tw[j]-Tmin_con)/(Topt_con-Tmin_con)*((Tmax_con-Tw[j])/(Tmax_con-Topt_con))**((Tmax_con-Topt_con)/(Topt_con-Tmin_con)))
                            WD_con_T[j]= WDmin_con/f_con_T[j]
                        j += 1
     
                    Teq_asco= [0] * (len(Tw))
                    Teq_con= [0] * (len(Tw))
                    SEVL_asco= [0] * (len(Tw))
                    SEVL_con= [0] * (len(Tw))
                    SEV_asco= [0] * (len(Tw))
                    SEV_con= [0] * (len(Tw))
                    i= 0
                    SEV_asco = SEV_asco_t0+ SEVL_asco
                    SEV_con = SEV_con_t0 + SEVL_con
                    #infection_asco=0
                    #infection_con=0
                    infection_asco=[0]*(len(Tw)-1)
                    infection_con=[0]*(len(Tw)-1)
                    for i in range(1, len(Tw)-1):
                        if WD[i] >= WD_asco_T[i]:  # IF INFECTION HAS OCCURED
                            #infection_asco=1
                            infection_asco[i-1]=1
                            if (Tmin_asco >= Tw[i] or Tw[i] >= Tmax_asco):
                                Teq_asco[i]= 0
                            else:
                                Teq_asco[i] = ((Tw[i]-Tmin_asco)/(Tmax_asco-Tmin_asco))
     
                                SEV_asco[i]= ((4.47*Teq_asco[i]**1.18 * (1-Teq_asco[i]))**1.35 * np.exp(-4.7*np.exp(-0.062*WD[i])))
                                SEVL_asco[i]= (SPODOSE_asco[i]*(SEV_asco[i]-SEV_asco[i-1]))
                                # where SEV(i)=relative infection severity; Teq(i)=
                                # equivalent of temperature, cal culated a s
                            
                        if WD[i] >= WD_con_T[i]:
                            #infection_con=1
                            infection_con[i-1]=1
                            if (Tmin_con >= Tw[i] or Tw[i] >= Tmax_con):
                                Teq_con[i]= 0
                            else:
                                Teq_con[i]= ((Tw[i])-Tmin_con)/(Tmax_con-Tmin_con)
     
                                SEV_con[i]= ((4.47*Teq_con[i]**1.18 * (1-Teq_con[i]))**1.35 * np.exp(-4.7*np.exp(-0.062*WD[i])))
                                SEVL_con[i]= (SPODOSE_con[i]*(SEV_con[i]-SEV_con[i-1]))
                    
                    # if infection_con==1 or infection_asco == 1:
                    #     infection=1
                    # else:
                    #     infection=0
                    if sum(infection_con)>=12 or sum(infection_asco)>= 12:
                        infection=1
                    else:
                        infection=0
                        
                    severity=[sum(i) for i in zip(SEVL_asco, SEVL_con)]  
                    mean_severity=mean(severity)
                    mean_SEV_asco=mean(SEV_asco)
                    mean_SEV_con=mean(SEV_con)
                    
                    # HOST SUSCEPTIBILITY
    
                    SUS= 0.995*np.exp(-0.5*((DD_10-144.4)/110.7)**2)
                    SEVC_asco = [i1 * i2 for i1, i2 in zip(SUS, SEVL_asco)]  # infection severity on clusters
                    SEVC_con= [i1 * i2 for i1, i2 in zip(SUS, SEVL_con)]
                    mean_SUS=mean([sum(i) for i in zip(SEVC_asco, SEVC_con)])
    
                    ##########################################################

                    # III) Disease onset
                    # APPEARANCE OF BLACK-ROT LESIONS AFTER AN INCUBATION PERIOD
    
                    T= Temp_data
     
                    T = [0 if x <= 6 else x for x in T]
                    T= [x-6 if x > 6 and x <= 24 else x for x in T]
                    T = [18 if x > 24 else x for x in T]
     
                    #DD_6_24 = np.cumsum(T)/24
                    #DD_6_24 = DD_6_24_t0+DD_6_24
                    
                    DD_6_24 = np.sum(T)/24 + DD_6_24_t0[0] ######################QUESTO VA CAPITO SE FACCIO U ARRAY UGUALE TUTTO IL GIORNO
                    DD_6_24=[DD_6_24]*(len(T)-1)
                    
                    f_GS= (1+1/(1+np.exp(7.10-2.23*DD_10/100))).tolist()
                    f_GS = [0] + f_GS
                    
                    ONS_leaf= [0] * len(RH)
                    der_ONS_leaf= [0] * len(RH)
                    ONS_leaf=ONS_leaf_t0+ONS_leaf
                    
                    ONS_clus= [0] * len(RH)
                    der_ONS_clus= [0] * len(RH)
                    ONS_leaf=ONS_clus_t0+ONS_clus
                    j= 0

                    
                    while j <= len(T)-2:
                        if DD_6_24[j]>=175 and DD_6_24[j]<=305: #for leaves
                            ONS_leaf.append(np.exp(-316.15*np.exp(-2.91*DD_6_24[j]/100)))
                            der_ONS_leaf.append(ONS_leaf[j]-ONS_leaf[j-1])
                        else:
                            infection=0
                        if DD_6_24[j]>=175*f_GS[j] and DD_6_24[j]<=305*f_GS[j]: #for clusters
                            ONS_clus.append(np.exp(-316.15*np.exp(-2.91*DD_6_24[j]/100)))
                            der_ONS_clus.append(ONS_clus[j]-ONS_clus[j-1])   
                        #else:
                         #   infection=0
                        j += 1
                        # where: ONS(j)=relative lesions onset, which ranges
                        # from 0 (no lesions appear) to 1 (all lesions have appeared);
                    mean_ONS_leaf=mean(ONS_leaf)
                    mean_ONS_clus=mean(ONS_clus)

                    # IV) Production of secondary inoculum.
                    # APPEARANCE OF PYCNIDIA ON LESIONS AFTER A LATENCY PERIOD
                    
                    i=0
                    sec_infection=0
                    h4_rain= [0] * len(R)
                    while i <= len(R)-1:
                        if DD_6_24[i]>=262 and DD_6_24[i]<=392: 
                            if i == 0:                            
                                if h4_rain_t0[i] > 0:
                                    if R[i] > 0 :
                                        h4_rain[i] = h4_rain_t0[i] + 1
                                    if R[i] == 0:
                                        h4_rain[i] = 0
         
                                if h4_rain_t0[i] == 0:
                                    if R[i] == 0:
                                        h4_rain[i] = 0
                                    if R[i] > 0:
                                        h4_rain[i] = 1
                            if i > 0:
       
                                if R[i] > 0:
                                    if h4_rain[i-1] == 0:
                                        h4_rain[i] = 1
                                    else:
                                        h4_rain[i] = h4_rain[i-1]+1
         
                                if R[i] == 0:
                                    h4_rain[i] = 0
                                    
                            if h4_rain[i]>=4:
                                sec_infection=1
    
                        i += 1
    
                    # PRODUCTION OF PYCNIDIA OVER THE INFECTIOUS PERIOD OF A LESION
                    RH= RH_data
    
                    DALA1= 1
                    DALA2= 7
                    DALA3= 15
                    a= 1.25
                    b= -109.4
                    c= 0.12
                    d= -11
                    # equation parameters values from table 1 of Onesti et al. 2017a
                    Y_RH1 = np.exp((-a*np.array(RH)+b)*np.exp(-DALA1*(c*np.array(RH)+d)))
                    Y_RH2= np.exp((-a*np.array(RH)+b)*np.exp(-DALA2*(c*np.array(RH)+d)))
                    Y_RH3 = np.exp((-a*np.array(RH)+b)*np.exp(-DALA3*(c*np.array(RH)+d)))  # rescaled
     
                    T = Temp_data
                    DALA= 6
                    A = 1  # fixed to 1 because the response variable was rescaled to 1
                    C= 1.85
                    D= 0.74
                    E = 1  # fixed to 1 because the response variable was rescaled to 1
                    F= 24.98
                    G= 0.48
                    H= 1.30
                    # equation parameters values from table 1 of Onesti et al. 2017a
                    f_T = E*((H+1)/H*H**(1/(H+1)))*((np.exp((np.array(T)-F)*G/(H+1)))/(1+np.exp((np.array(T)-F)*G)))  # function describing the effect of temperature
                    Y_T= A*(1-np.exp(-f_T*(DALA-C)**D))
     
                    Tmax = 40  # values from table 1 of Onesti et al. 2017a
                    Tmin = 10  # values from table 1 of Onesti et al. 2017a
                    # max and min temperaures at which pycnidia is able to produce
                    # conidia
     
                    T= [i for i in T if (i > Tmin and i < Tmax)]
                    Teq= (np.array(T)-Tmin)/(Tmax-Tmin)
                    a_CT= 23.37
                    b_CT= 1.42
                    c_CT= 3.92
                    # equation parameters values from table 1 of Onesti et al. 2017a
                    Y_CT= a_CT*Teq**(b_CT)*(1-Teq)**c_CT
 

                    ASCMat_t0=[ASCmat[-1]]
                    COMmat_t0 = [COMmat[-1]]
                    H_postr_t0 = [H_postr[-1]]
                    H_rain_t0 = [H_rain[-1]]
                    Hdry_t0 = [Hdry[-1]]
                    RH_t0 = [RH[-1]]
                    wetness_t0 = [wetness[-1]]
                    WD_t0=[WD[-1]]
                    SEV_asco_t0=[SEV_asco[-1]]
                    SEV_con_t0=[SEV_con[-1]]
                    ONS_leaf_t0=[ONS_leaf[-1]]
                    ONS_clus_t0=[ONS_clus[-1]]
                    DD_9_25_t0=[DD_9_25[-1]]
                    DD_10_t0=[DD_10[-1]]
                    DD_6_24_t0=[DD_6_24[-1]]
                    h4_rain_t0=[h4_rain_t0[-1]]
                                            
                        
                    df_days={'doy':doy[days],'SPODOSE':SPODOSE,'primary_infection':infection,
                              'severity': mean_severity,'susceptibility':mean_SUS,'ONS_leaf':mean_ONS_leaf,
                              'ONS_clus':mean_ONS_clus,'secondary_infection': sec_infection,'ASCMat_t0':ASCMat_t0[0], 'COMmat_t0':COMmat_t0[0], 'H_postr_t0':H_postr_t0[0],
                                        'H_rain_t0':H_rain_t0[0], 'Hdry_t0':Hdry_t0[0], 'RH_t0':RH_t0[0], 'wetness_t0':wetness_t0[0], 'WD_t0':WD_t0[0], 
                                        'SEV_asco_t0':SEV_asco_t0[0], 'SEV_con_t0':SEV_con_t0[0], 'ONS_leaf_t0':ONS_leaf_t0[0], 'ONS_clus_t0':ONS_clus_t0[0], 
                                        'DD_9_25_t0':DD_9_25_t0[0], 'DD_10_t0':DD_10_t0[0], 'DD_6_24_t0':DD_6_24_t0[0], 'h4_rain_t0':h4_rain_t0[0]}        
                   
                    #df_days={'prova':prova,'DD_6_24':DD_6_24,'infection':infection}
                    # allarmi

                    df.append(df_days)
              df_new={'LotId':LotId[0],'year':year[0],'Missing_values':Missing_values,'data':df}   
              return JsonResponse(df_new, safe=False, status=201)
        return JsonResponse(serializer.errors, safe=False, status=400)
        
    
#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def blackrot_detail(request, pk):
    try:
        blackrot = Blackrot.objects.get(pk=pk)
    except Blackrot.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = BlackrotListSerializer(blackrot)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = BlackrotListSerializer(blackrot, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, safe=False, status=400)

    elif request.method == 'DELETE':
        blackrot.delete()
        return HttpResponse(status=204)
            
