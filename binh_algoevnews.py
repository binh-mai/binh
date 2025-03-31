import requests
from time import sleep
import numpy as np

s = requests.Session()
s.headers.update({'X-API-key': 'L7F4EJ9X'})

# Global Variables

TP_EPS_MOE = 0.02
AS_EPS_MOE = 0.04
BA_EPS_MOE = 0.06

TP_OWN_MOE = 20
AS_OWN_MOE = 25
BA_OWN_MOE = 30

OWN_ADJUSTMENT = 0.05 # TODO: adjust this for different companies

# cost of equity & terminal growth rate\
TERMINAL_GROW = 0.02
TP_COE = 0.05
AS_COE = 0.075
BA_COE = 0.10

# prior year EPS
TP_PRIOR_EPS = 1.43
AS_PRIOR_EPS = 1.55
BA_PRIOR_EPS = 1.50

# Divdend payout ratios
TP_DIV_RATIO = 0.8
AS_DIV_RATIO = 0.5
BA_DIV_RATIO = 0

# PE ratio
TP_PE_RATIO = 12
AS_PE_RATIO = 16
BA_PE_RATIO = 20

GROSS_LIMIT = 100000
MAX_LONG_EXPOSURE_LIMIT = 50000
MAX_SHORT_EXPOSURE_LIMIT = -50000
ORDER_LIMIT = 5000

SPREAD = 0.4

def get_tick():
    resp = s.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick'], case['status']
  
# parse through news and udate lower, middle & high eps + ownership estimates
# TODO: speed up (e.g., 2 functions of reading different news types - eps estimate, institutional ownerships / multiprocessing different companies?)

# input all the estimates, parse through news if there are new news -> update the estimates accordingly (each quarter with different MOE)
def get_news(eps_estimates, lower_eps_estimates, upper_eps_estimates, ownership_estimates, lower_ownership_estimates, upper_ownership_estimates, eps):
    resp = s.get ('http://localhost:9999/v1/news', params = {'limit': 50}) # default limit is 20
    if resp.ok:
        news_query = resp.json()
        
        for i in news_query[::-1]: # iterating backwards through the list, news items are ordered newest to oldest         

            if i['headline'].find("TP") > -1:
    
                if i['headline'].find("Analyst") > -1:
                    
                    if i['headline'].find("#1") > -1:
                        eps_estimates[0, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ])
                        eps_estimates[0, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ])
                        eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        
                        lower_eps_estimates[0, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ]) - TP_EPS_MOE
                        lower_eps_estimates[0, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) - TP_EPS_MOE * 2
                        lower_eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - TP_EPS_MOE * 3
                        lower_eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - TP_EPS_MOE * 4
                        
                        upper_eps_estimates[0, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ]) + TP_EPS_MOE
                        upper_eps_estimates[0, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) + TP_EPS_MOE * 2
                        upper_eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + TP_EPS_MOE * 3
                        upper_eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + TP_EPS_MOE * 4
                        
                    if i['headline'].find("#2") > -1:
                        eps_estimates[0, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ])
                        eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        
                        lower_eps_estimates[0, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) - TP_EPS_MOE
                        lower_eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - TP_EPS_MOE * 2
                        lower_eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - TP_EPS_MOE * 3
                        
                        upper_eps_estimates[0, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) + TP_EPS_MOE
                        upper_eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + TP_EPS_MOE * 2
                        upper_eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + TP_EPS_MOE * 3
                        

                    if i['headline'].find("#3") > -1:
                        eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        
                        lower_eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - TP_EPS_MOE
                        lower_eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - TP_EPS_MOE * 2
                        
                        upper_eps_estimates[0, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + TP_EPS_MOE
                        upper_eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + TP_EPS_MOE * 2

                    if i['headline'].find("#4") > -1:
                        eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        lower_eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - TP_EPS_MOE
                        upper_eps_estimates[0, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + TP_EPS_MOE
                    
                if i['headline'].find("institutional") > -1:
                    
                    if i['headline'].find("Q1") > -1:
                        ownership_estimates[0, 0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])  
                        lower_ownership_estimates[0,0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - TP_OWN_MOE
                        upper_ownership_estimates[0,0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + TP_OWN_MOE
                    
                    if i['headline'].find("Q2") > -1:
                        ownership_estimates[0, 1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])  
                        lower_ownership_estimates[0,1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (TP_OWN_MOE - OWN_ADJUSTMENT)
                        upper_ownership_estimates[0,1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (TP_OWN_MOE - OWN_ADJUSTMENT)

                    if i['headline'].find("Q3") > -1:
                        ownership_estimates[0, 2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])
                        lower_ownership_estimates[0,2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (TP_OWN_MOE - OWN_ADJUSTMENT * 2)
                        upper_ownership_estimates[0,2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (TP_OWN_MOE - OWN_ADJUSTMENT * 2)
                                                       

                    if i['headline'].find("Q4") > -1:
                        ownership_estimates[0, 3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])  
                        lower_ownership_estimates[0,3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (TP_OWN_MOE - OWN_ADJUSTMENT * 3)
                        upper_ownership_estimates[0,3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (TP_OWN_MOE - OWN_ADJUSTMENT * 3)
                                                               
                
            if i['headline'].find("AS") > -1:
                
                if i['headline'].find("Analyst") > -1:
                    
                    if i['headline'].find("#1") > -1:
                        eps_estimates[1, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ])
                        eps_estimates[1, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ])
                        eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        
                        lower_eps_estimates[1, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ]) - AS_EPS_MOE
                        lower_eps_estimates[1, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) - AS_EPS_MOE * 2
                        lower_eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - AS_EPS_MOE * 3
                        lower_eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - AS_EPS_MOE * 4
                        
                        upper_eps_estimates[1, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ]) + AS_EPS_MOE
                        upper_eps_estimates[1, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) + AS_EPS_MOE * 2
                        upper_eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + AS_EPS_MOE * 3
                        upper_eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + AS_EPS_MOE * 4
                        
                    if i['headline'].find("#2") > -1:
                        # update actual q1 eps
                        eps_estimates[1, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ])
                        eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        
                        lower_eps_estimates[1, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) - AS_EPS_MOE
                        lower_eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - AS_EPS_MOE * 2
                        lower_eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - AS_EPS_MOE * 3
                        
                        upper_eps_estimates[1, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) + AS_EPS_MOE
                        upper_eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + AS_EPS_MOE * 2
                        upper_eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + AS_EPS_MOE * 3
                        

                    if i['headline'].find("#3") > -1:
                        # update actual q1 and q2 eps
                        eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        
                        lower_eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - AS_EPS_MOE
                        lower_eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - AS_EPS_MOE * 2
                        
                        upper_eps_estimates[1, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + AS_EPS_MOE
                        upper_eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + AS_EPS_MOE * 2

                    if i['headline'].find("#4") > -1:
                        # update actual q1, q2, and q3 estimates
                        eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        lower_eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - AS_EPS_MOE
                        upper_eps_estimates[1, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + AS_EPS_MOE
                
                    
                if i['headline'].find("institutional") > -1:
                    
                    if i['headline'].find("Q1") > -1:
                        ownership_estimates[1, 0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])  
                        lower_ownership_estimates[1,0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (AS_OWN_MOE)
                        upper_ownership_estimates[1,0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (AS_OWN_MOE)
                    
                    if i['headline'].find("Q2") > -1:
                        ownership_estimates[1, 1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])   
                        lower_ownership_estimates[1,1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (AS_OWN_MOE - OWN_ADJUSTMENT)
                        upper_ownership_estimates[1,1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (AS_OWN_MOE - OWN_ADJUSTMENT)

                    if i['headline'].find("Q3") > -1:
                        ownership_estimates[1, 2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])  
                        lower_ownership_estimates[1,2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (AS_OWN_MOE - OWN_ADJUSTMENT * 2)
                        upper_ownership_estimates[1,2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (AS_OWN_MOE - OWN_ADJUSTMENT * 2)

                    if i['headline'].find("Q4") > -1:
                        ownership_estimates[1, 3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])                                                    
                        lower_ownership_estimates[1,3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (AS_OWN_MOE - OWN_ADJUSTMENT * 3)
                        upper_ownership_estimates[1,3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (AS_OWN_MOE - OWN_ADJUSTMENT * 3)
                        
            if i['headline'].find("BA") > -1:
                
                if i['headline'].find("Analyst") > -1:
                    
                    if i['headline'].find("#1") > -1:
                        eps_estimates[2, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ])
                        eps_estimates[2, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ])
                        eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])

                        lower_eps_estimates[2, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ]) - BA_EPS_MOE
                        lower_eps_estimates[2, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) - BA_EPS_MOE * 2
                        lower_eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - BA_EPS_MOE * 3
                        lower_eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - BA_EPS_MOE * 4
                        
                        upper_eps_estimates[2, 0] = float(i['body'][i['body'].find("Q1:") + 5 : i['body'].find("Q1:") + 9 ]) + BA_EPS_MOE
                        upper_eps_estimates[2, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) + BA_EPS_MOE * 2
                        upper_eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + BA_EPS_MOE * 3
                        upper_eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + BA_EPS_MOE * 4
                        
                    if i['headline'].find("#2") > -1:
                        eps_estimates[2, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ])
                        eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        
                        lower_eps_estimates[2, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) - BA_EPS_MOE
                        lower_eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - BA_EPS_MOE * 2
                        lower_eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - BA_EPS_MOE * 3
                        
                        upper_eps_estimates[2, 1] = float(i['body'][i['body'].find("Q2:") + 5 : i['body'].find("Q2:") + 9 ]) + BA_EPS_MOE
                        upper_eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + BA_EPS_MOE * 2
                        upper_eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + BA_EPS_MOE * 3

                    if i['headline'].find("#3") > -1:
                        eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ])
                        eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        
                        lower_eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) - BA_EPS_MOE
                        lower_eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - BA_EPS_MOE * 2
                        
                        upper_eps_estimates[2, 2] = float(i['body'][i['body'].find("Q3:") + 5 : i['body'].find("Q3:") + 9 ]) + BA_EPS_MOE
                        upper_eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + BA_EPS_MOE * 2


                    if i['headline'].find("#4") > -1:
                        eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ])
                        lower_eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) - BA_EPS_MOE
                        upper_eps_estimates[2, 3] = float(i['body'][i['body'].find("Q4:") + 5 : i['body'].find("Q4:") + 9 ]) + BA_EPS_MOE
                    
                if i['headline'].find("institutional") > -1:
                    
                    if i['headline'].find("Q1") > -1:
                        ownership_estimates[2, 0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])  
                        lower_ownership_estimates[2,0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (BA_OWN_MOE)
                        upper_ownership_estimates[2,0] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (BA_OWN_MOE)
                    
                    if i['headline'].find("Q2") > -1:
                        ownership_estimates[2, 1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])  
                        lower_ownership_estimates[2,1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (BA_OWN_MOE - OWN_ADJUSTMENT)
                        upper_ownership_estimates[2,1] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (BA_OWN_MOE - OWN_ADJUSTMENT)

                    if i['headline'].find("Q3") > -1:
                        ownership_estimates[2, 2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])                                                            
                        lower_ownership_estimates[2,2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (BA_OWN_MOE - OWN_ADJUSTMENT * 2)
                        upper_ownership_estimates[2,2] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (BA_OWN_MOE - OWN_ADJUSTMENT * 2)
                        
                    if i['headline'].find("Q4") > -1:
                        ownership_estimates[2, 3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")])
                        lower_ownership_estimates[2,3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) - (BA_OWN_MOE - OWN_ADJUSTMENT * 3)
                        upper_ownership_estimates[2,3] = float(i['body'][i['body'].find("%") - 5 : i['body'].find("%")]) + (BA_OWN_MOE - OWN_ADJUSTMENT * 3)
                
            if i['headline'].find("Earnings release") > -1:
                                    
                if i['headline'].find("Q1") > -1:
                    eps[0, 0] = float(i['body'][i['body'].find("TP Q1:") + 32 : i['body'].find("TP Q1:") + 36 ])
                    eps[1, 0] = float(i['body'][i['body'].find("AS Q1:") + 32 : i['body'].find("AS Q1:") + 36 ])
                    eps[2, 0] = float(i['body'][i['body'].find("BA Q1:") + 32 : i['body'].find("BA Q1:") + 36 ])
                    
                if i['headline'].find("Q2") > -1:
                    eps[0, 1] = float(i['body'][i['body'].find("TP Q2:") + 32 : i['body'].find("TP Q2:") + 36 ])
                    eps[1, 1] = float(i['body'][i['body'].find("AS Q2:") + 32 : i['body'].find("AS Q2:") + 36 ])
                    eps[2, 1] = float(i['body'][i['body'].find("BA Q2:") + 32 : i['body'].find("BA Q2:") + 36 ])

                if i['headline'].find("Q3") > -1:
                    eps[0, 2] = float(i['body'][i['body'].find("TP Q3:") + 32 : i['body'].find("TP Q3:") + 36 ])
                    eps[1, 2] = float(i['body'][i['body'].find("AS Q3:") + 32 : i['body'].find("AS Q3:") + 36 ])
                    eps[2, 2] = float(i['body'][i['body'].find("BA Q3:") + 32 : i['body'].find("BA Q3:") + 36 ])

                if i['headline'].find("Q4") > -1:
                    eps[0, 3] = float(i['body'][i['body'].find("TP Q4:") + 32 : i['body'].find("TP Q4:") + 36 ])
                    eps[1, 3] = float(i['body'][i['body'].find("AS Q4:") + 32 : i['body'].find("AS Q4:") + 36 ])
                    eps[2, 3] = float(i['body'][i['body'].find("BA Q4:") + 32 : i['body'].find("BA Q4:") + 36 ])
                                
        return eps_estimates, lower_eps_estimates, upper_eps_estimates, ownership_estimates, lower_ownership_estimates, upper_ownership_estimates, eps     

def calculate_ddm(eps, div_ratio, growth_rate, cost_of_equity, terminal_growth = 0.2):
    div = eps * div_ratio
    stage1 = ((div * (1 + growth_rate)) / (cost_of_equity - growth_rate)) * \
             (1 - ((1 + growth_rate) / (1 + cost_of_equity))**5)
    stage2 = ((div * ((1 + growth_rate)**5) * (1 + terminal_growth)) / (cost_of_equity - terminal_growth)) / \
             (1 + cost_of_equity)**5
    return stage1 + stage2

def get_bid_ask(ticker):
    payload = {'ticker': ticker}
    resp = s.get ('http://localhost:9999/v1/securities/book', params = payload)
    if resp.ok:
        book = resp.json()
        bid_side_book = book['bids']
        ask_side_book = book['asks']
       
        bid_prices_book = [item["price"] for item in bid_side_book]
        ask_prices_book = [item['price'] for item in ask_side_book]
    
    # if the market book is empty, python cannot assign a value on a list that is empty.
    # TODO: if market book is empty -> enter orders at highest/lowest allowable price on simulation/ or a range -> once order get filled/close in the market or factor in main code
    # or when market book get very short (e.g., only 5 orders or less -> enter limit orders)
    if len(bid_prices_book) == 0:
        best_bid_price = -1
    else:
        best_bid_price = bid_prices_book[0]
    if len(ask_prices_book) == 0:
        best_ask_price = -1
    else:
        best_ask_price = ask_prices_book[0]
    
    return best_bid_price, best_ask_price
 
    
def get_position():
    resp = s.get ('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        gross_position = abs(book[0]['position']) + abs(book[1]['position']) + abs(book[2]['position'])
        net_position = book[0]['position'] + book[1]['position'] + book[2]['position']
        tp_position = book[0]['position']
        as_position = book[1]['position']
        ba_position = book[2]['position']
        return gross_position, net_position, tp_position, as_position, ba_position
    
def cancel_all_orders():
    s.post('http://localhost:9999/v1/commands/cancel', params={'all': 1})

# helper: calculate ddm
def calculate_ddm(COE, TERMINAL_GROW, div_growth, dividend):
    year1_div = dividend * (1+div_growth)
    year6_div = dividend * (1+div_growth)**5
    ddm_1 = (year1_div/(COE-div_growth)) * (1 - ((1+div_growth)/(1+COE))**5)
    ddm_2 = (year6_div/(COE-TERMINAL_GROW)) / (1+COE)**5

    return ddm_1 + ddm_2

# helper: calculate min & max prices with lower/upper bounds of ownership, ddm, pe 
def calculate_min_max_price(lower_own, upper_own, lower_ddm, upper_ddm, lower_pe, upper_pe): 
    # lo_own_lo_ddm_lo_pe 
    p1 = (lower_own/100) * lower_ddm + (1- (lower_own/100)) * lower_pe
    # lo_own_lo_ddm_hi_pe 
    p2 = (lower_own/100) * lower_ddm + (1- (lower_own/100)) * upper_pe
    # lo_own_hi_ddm_lo_pe 
    p3 = (lower_own/100) * upper_ddm + (1- (lower_own/100)) * lower_pe
    # lo_own_hi_ddm_hi_pe 
    p4 = (lower_own/100) * upper_ddm + (1- (lower_own/100)) * upper_pe

    # hi_own_lo_ddm_lo_pe 
    p5 = (upper_own/100) * lower_ddm + (1- (upper_own/100)) * lower_pe
    # hi_own_lo_ddm_hi_pe 
    p6 = (upper_own/100) * lower_ddm + (1- (upper_own/100)) * upper_pe
    # hi_own_hi_ddm_lo_pe 
    p7 = (upper_own/100) * upper_ddm + (1- (upper_own/100)) * lower_pe
    # hi_own_hi_ddm_hi_pe 
    p8 = (upper_own/100) * upper_ddm + (1- (upper_own/100)) * upper_pe

    max_price = max(p1, p2, p3, p4, p5, p6, p7, p8)
    min_price = min(p1, p2, p3, p4, p5, p6, p7, p8)

    return max_price, min_price

def get_gross_position(ticker): # GROSS POSITION
    resp = s.get('http://localhost:9999/v1/securities')
    if resp.ok:
        securities = resp.json()
        for stock in securities:
            if stock['ticker'] == ticker:
                return int(stock['position'])  # Convert position to integer
        return 0  # Return 0 if the ticker is not found


def get_time_sales(ticker):
    pass


def get_open_orders(ticker):
    resp = s.get('http://localhost:9999/v1/orders')
    if resp.ok:
        orders = resp.json()
        # Filter orders to include only those with status 'OPEN'
        open_orders = [order for order in orders if order.get('status') == 'OPEN']
        return open_orders


def cancel_order(order_id):
    s.delete('http://localhost:9999/v1/orders/' + str(order_id))


# def close_bad_orders(ticker):
#     open_orders = get_open_orders(ticker)
    
#     for order in open_orders:
#         order_timestamp = order['tick']
#         order_id = order['order_id']
#         current_time = get_tick()  # Use tick as a proxy for time
        
#         if current_time - order_timestamp > 15: #and quantity_filled == 0
#             cancel_order(order_id)

def get_min_max_price(ticker):
    payload = {'ticker': ticker}
    resp = s.get('http://localhost:9999/v1/securities', params=payload)
    if resp.ok:
        for stock in resp.json():
            if stock['ticker'] == ticker:
                return stock['min_price'], stock['max_price']
    return None, None

##################################################### MAIN ################################################
def main():
    
    ticker_list = ['TP', 'AS', 'BA']
    market_prices = np.array([0., 0., 0., 0., 0., 0.])
    market_prices = market_prices.reshape(3, 2) # matrix for current bid & ask P of 3 stocks
    
    # matrices for estimates 
    eps_estimates = np.zeros((3, 4))
    lower_eps_estimates = np.zeros((3, 4))
    upper_eps_estimates = np.zeros((3, 4))

    ownership_estimates = np.zeros((3, 4))
    lower_ownership_estimates = np.zeros((3, 4))
    upper_ownership_estimates = np.zeros((3, 4))

    # record actual eps 
    # TODO: actual ownerships?
    eps = np.zeros((3, 4))
    
    # TODO: put the distribution results in the midpoint values matrices instead of last year values / estimates instead of 0?
    # update lower and upper bound using distrbution mean +- standard deviation? (1 std?)
    eps_val = np.array([0.40, 0.33, 0.33, 0.37, 0.35, 0.45, 0.50, 0.25, 0.15, 0.50, 0.60, 0.25]).reshape(3,4)
    lower_eps_val = np.array([0.40, 0.33, 0.33, 0.37, 0.35, 0.45, 0.50, 0.25, 0.15, 0.50, 0.60, 0.25]).reshape(3,4)
    upper_eps_val = np.array([0.40, 0.33, 0.33, 0.37, 0.35, 0.45, 0.50, 0.25, 0.15, 0.50, 0.60, 0.25]).reshape(3,4)

    own_val = np.array([50.0, 50.0, 50.0]).reshape(3,1)
    lower_own_val = np.array([50.0, 50.0, 50.0]).reshape(3,1)
    upper_own_val = np.array([50.0, 50.0, 50.0]).reshape(3,1)


    # create array for stock prices
    
    # TODO: different logic when tick == 1 
    while True:
        tick, status = get_tick()
        gross_position, net_position, tp_position, as_position, ba_position = get_position()
        if status != 'ACTIVE':
            print("Case Inactive")
            sleep(1)

        if status == 'ACTIVE' and tick < 15:
            for ticker in ticker_list:
                min_poss_price, max_poss_price = get_min_max_price(ticker)
                min_price = max(0.01, min_poss_price)
                max_price = min(100, max_poss_price)
            
                if gross_position + ORDER_LIMIT < GROSS_LIMIT: 
                    qty_to_buy = min(ORDER_LIMIT, (GROSS_LIMIT - gross_position))
                    s.post('http://localhost:9999/v1/orders', params={
                                    'ticker': ticker,
                                    'type': 'LIMIT',
                                    'quantity': qty_to_buy,
                                    'action': 'BUY',
                                    'price': min_price
                                })
                    qty_to_sell = min(ORDER_LIMIT, (GROSS_LIMIT - gross_position))
                            
                    s.post('http://localhost:9999/v1/orders', params={
                        'ticker': ticker,
                        'type': 'LIMIT',
                        'quantity': qty_to_sell,
                        'action': 'SELL',
                        'price': max_price
                    })

                    sleep(0.2)

        if status == 'ACTIVE' and tick >= 15:
            for i in range(3):
                ticker_symbol = ticker_list[i]
                market_prices[i, 0], market_prices[i, 1] = get_bid_ask(ticker_symbol)
                
            eps_estimates, lower_eps_estimates, upper_eps_estimates, ownership_estimates, lower_ownership_estimates, upper_ownership_estimates, eps = get_news(eps_estimates, lower_eps_estimates, upper_eps_estimates, ownership_estimates, lower_ownership_estimates, upper_ownership_estimates, eps)
            gross_position, net_position, tp_position, as_position, ba_position = get_position()
            
            print(tp_position)
            print(as_position)
            print(ba_position)
            
            
            print("--- EPS Estimates ---")
            print(eps_estimates)
            print("--- Ownership Estimates ---")
            print(ownership_estimates)
            print("--- EPS ---")
            print(eps)
            

            # loop through matrices, if estimates is not 0 -> update the (midpoint) values matrices accordinly, else estimates remain the same as last year 
            # loop through range of 4 to get to the latest quarter -> can speed it up by breaking down? if condition of sec between -> Q1, 2, 3, 4, etc. 
            for i in range(3):
                for j in range(4):
                    if eps_estimates[i, j] != 0:
                        eps_val[i, j] = eps_estimates[i, j]
                        lower_eps_val[i, j] = lower_eps_estimates[i, j]
                        upper_eps_val[i, j] = upper_eps_estimates[i, j]
                    if ownership_estimates[i, j] != 0:
                        own_val[i, 0] = ownership_estimates[i, j]
                        lower_own_val[i, 0] = lower_ownership_estimates[i, j]
                        upper_own_val[i, 0] = upper_ownership_estimates[i, j]
                    if eps[i, j] != 0:
                        eps_val[i, j] = eps[i, j]
                        lower_eps_val[i, j] = eps[i, j]
                        upper_eps_val[i, j] = eps[i, j]
                        
    # could build in lower and upper bound logic here 
    # could organize stock prices by doing lower/upper eps * (lower, actual, and upper ownership)                
            print("--- EPS for Valuation - Mid point, lower and upper bounds respectively ---")
            print(eps_val)
            print(lower_eps_val)
            print(upper_eps_val)

            print("--- Ownership for Valuation - Midpoint, lower and upper bounds respectively---")
            print(own_val)
            print(lower_own_val)
            print(upper_own_val)
            
        # The minimum and maximum valuations based on EPS and ownership estimates are relevant. So code in the logic to find the lowest and highest prices
            
            ##########################################################  Teldar Paper (TP) VALUATION  ######################################################################
            # sum annual eps (3 ranges: midpoint, lower, upper)
            TP_eps = eps_val.sum(axis = 1)[0]
            lower_TP_eps = lower_eps_val.sum(axis = 1)[0]
            upper_TP_eps = upper_eps_val.sum(axis = 1)[0]

            # annual dividend growth rate using 3 different annual eps ranges
            TP_g = (TP_eps / TP_PRIOR_EPS) - 1
            lower_TP_g = (lower_TP_eps / TP_PRIOR_EPS) - 1
            upper_TP_g = (upper_TP_eps/ TP_PRIOR_EPS) - 1

            # dividend amount based on 3 different annual eps ranges (pay 80% dividend)
            TP_div = TP_eps * TP_DIV_RATIO
            lower_TP_div = lower_TP_eps * TP_DIV_RATIO
            upper_TP_div = upper_TP_eps * TP_DIV_RATIO

            # DDM valuation with 3 ranges
            TP_DDM = calculate_ddm(TP_COE, TERMINAL_GROW, TP_g, TP_div)
            lower_TP_DDM = calculate_ddm(TP_COE, TERMINAL_GROW, lower_TP_g, lower_TP_div)
            upper_TP_DDM = calculate_ddm(TP_COE, TERMINAL_GROW, upper_TP_g, upper_TP_div)

            # PE valuation with 3 ranges
            TP_pe = TP_eps * TP_PE_RATIO 
            lower_TP_pe = lower_TP_eps * TP_PE_RATIO
            upper_TP_pe = upper_TP_eps * TP_PE_RATIO
            
            # Teldar Paper (TP)
            TP_val = (own_val[0, 0] / 100) * TP_DDM + (1 - (own_val[0,0] / 100)) * TP_pe
            TP_max_price, TP_min_price = calculate_min_max_price(lower_own_val[0, 0], upper_own_val[0, 0], lower_TP_DDM, upper_TP_DDM, lower_TP_pe, upper_TP_pe)
                        
            ##########################################################  Anacott Steel (AS) VALUATION  ######################################################################
            # sum annual eps (3 ranges: midpoint, lower, upper)
            AS_eps = eps_val.sum(axis = 1)[1]
            lower_AS_eps = lower_eps_val.sum(axis =1)[1]
            upper_AS_eps = upper_eps_val.sum(axis =1)[1]

            # annual dividend growth rate using 3 different annual eps ranges
            AS_g = (AS_eps / AS_PRIOR_EPS) - 1
            lower_AS_g = (lower_AS_eps / AS_PRIOR_EPS) - 1
            upper_AS_g = (upper_AS_eps / AS_PRIOR_EPS) - 1

            # dividend amount based on 3 different annual eps ranges (pay 50% dividend)
            AS_div = AS_eps * AS_DIV_RATIO
            lower_AS_div = lower_AS_eps * AS_DIV_RATIO
            upper_AS_div = upper_AS_eps * AS_DIV_RATIO

            # DDM valuation with 3 ranges
            AS_DDM = calculate_ddm(AS_COE, TERMINAL_GROW, AS_g, AS_div)
            lower_AS_DDM = calculate_ddm(AS_COE, TERMINAL_GROW, lower_AS_g, lower_AS_div)
            upper_AS_DDM = calculate_ddm(AS_COE, TERMINAL_GROW, upper_AS_g, upper_AS_div)

            # PE valuation with 3 ranges
            AS_pe = AS_eps * AS_PE_RATIO
            lower_AS_pe = lower_AS_eps * AS_PE_RATIO
            upper_AS_pe = upper_AS_eps * AS_PE_RATIO
            
            # Anacott Steel (AS)
            AS_val = (own_val[1, 0] / 100) * AS_DDM + (1 - (own_val[1,0] / 100)) * AS_pe
            AS_max_price, AS_min_price = calculate_min_max_price(lower_own_val[1, 0], upper_own_val[1, 0], lower_AS_DDM, upper_AS_DDM, lower_AS_pe, upper_AS_pe)

            ##########################################################  Bluestar Airlines (BA) VALUATION  ######################################################################
            # sum annual eps (3 ranges: midpoint, lower, upper)
            BA_eps = eps_val.sum(axis = 1)[2]
            lower_BA_eps = lower_eps_val.sum(axis = 1)[2]
            upper_BA_eps = upper_eps_val.sum(axis = 1)[2]

            # annual dividend growth rate using 3 different annual eps ranges
            BA_g = (BA_eps / BA_PRIOR_EPS) - 1
            lower_BA_g = (lower_BA_eps / BA_PRIOR_EPS) - 1
            upper_BA_g = (upper_BA_eps / BA_PRIOR_EPS) - 1

            # PE valuation by institutional investors (modified by EPS growth)
            BA_pe_inst = BA_PE_RATIO * (1 + BA_g) * BA_eps
            lower_BA_pe_inst = BA_PE_RATIO * (1 + lower_BA_g) * lower_BA_eps
            upper_BA_pe_inst = BA_PE_RATIO * (1 + upper_BA_g) * upper_BA_eps

            # PE valuation by retail investors (normal method)
            BA_pe_retail = BA_eps * BA_PE_RATIO
            lower_BA_pe_retail = lower_BA_eps * BA_PE_RATIO
            upper_BA_pe_retail = upper_BA_eps * BA_PE_RATIO
            
            # Bluestar Airlines (BA)
            BA_val = (own_val[2, 0] / 100) * BA_pe_inst + (1 - (own_val[2,0] / 100)) * BA_pe_retail
            BA_max_price, BA_min_price = calculate_min_max_price(lower_own_val[2, 0], upper_own_val[2, 0], lower_BA_pe_inst, upper_BA_pe_inst, lower_BA_pe_retail, upper_BA_pe_retail)
            
            
            # Create values based on lower and upper bounds of different things. store in array
            print("--- TP Valuation ---")
            print (TP_val)
            print("--- AS Valuation --")
            print(AS_val)
            print("--- BA Valuation ---")
            print(BA_val)
            
            min_prices = np.array([TP_min_price, AS_min_price, BA_min_price])
            max_prices = np.array([TP_max_price, AS_max_price, BA_max_price])
            estimate_prices = np.array([TP_val, AS_val, BA_val])
            
            print(min_prices)
            print(max_prices)
        
    #################################### STRATEGY 1 - buy when undervalued, sell when overvalued ###########################################
            
            for i in range(3):
                
                ticker = ticker_list[i]  # Get the ticker name from the list
                market_prices[i, 0], market_prices[i, 1] = get_bid_ask(ticker)        

                bid_prices = market_prices[:, 0]  # Bid prices for all stocks
                ask_prices = market_prices[:, 1]  # Ask prices for all stocks
                # Check if we are within the trading limit

                min_poss_price, max_poss_price = get_min_max_price(ticker)
                min_price = max(0.01, min_poss_price)
                max_price = min(100, max_poss_price)

                if gross_position < GROSS_LIMIT - ORDER_LIMIT and abs(net_position) < MAX_LONG_EXPOSURE_LIMIT:
                    qty_to_buy = min(ORDER_LIMIT, (GROSS_LIMIT - gross_position))

                    # Buy Condition: Minimum valuation > Ask Price
                    # if ask_prices[i] < min_prices[i]:
                        # Calculate the number of shares to buy without exceeding order limit
                    qty_to_buy = min(ORDER_LIMIT, (GROSS_LIMIT - gross_position))
                    buy_price = estimate_prices[i] - SPREAD * (estimate_prices[i] - min_prices[i])

                    if ask_prices[i] == -1: # if ask side is empty 
                        for i in range(3):
                            print(f"No order in book. Buying {qty_to_buy} shares of {ticker} at {min_poss_price}")
                            s.post('http://localhost:9999/v1/orders', params={
                                'ticker': ticker,
                                'type': 'LIMIT',
                                'quantity': qty_to_buy,
                                'action': 'BUY',
                                'price': min_price + 0.5
                            })
                    elif ask_prices[i] < min_prices[i]:

                        print(f"Buying {qty_to_buy} shares of {ticker} at {min_prices[i]}")
                        s.post('http://localhost:9999/v1/orders', params={
                            'ticker': ticker,
                            'type': 'LIMIT',
                            'quantity': qty_to_buy,
                            'action': 'BUY', 
                            'price' : ask_prices[i] + 0.5
                        })
                    elif ask_prices[i] < buy_price:
                        print(f"Buying {qty_to_buy} shares of {ticker} at {buy_price}")
                        s.post('http://localhost:9999/v1/orders', params={
                            'ticker': ticker,
                            'type': 'LIMIT',
                            'quantity': qty_to_buy,
                            'action': 'BUY', 
                            'price' : buy_price
                        })
                    sleep(0.1)
            
                    cancel_all_orders()

                if gross_position < GROSS_LIMIT - ORDER_LIMIT and abs(net_position) < MAX_LONG_EXPOSURE_LIMIT:
                    # Sell Condition: Maximum valuation < Bid Price
                    # if bid_prices[i] > max_prices[i]:
                        # Calculate the number of shares to sell without exceeding order limit
                    qty_to_sell = min(ORDER_LIMIT, (GROSS_LIMIT - gross_position))
                    sell_price = estimate_prices[i] + SPREAD * (max_prices[i] - estimate_prices[i])

                    if bid_prices[i] == -1: # if bid side is empty 
                        for i in range(3):
                            print(f"No order in book. Selling {qty_to_sell} shares of {ticker} at {max_poss_price}")
                            s.post('http://localhost:9999/v1/orders', params={
                                'ticker': ticker,
                                'type': 'LIMIT',
                                'quantity': qty_to_sell,
                                'action': 'SELL',
                                'price': max_price - 0.5
                            })

                    elif bid_prices[i] > max_prices[i]:
                        print(f"Selling {qty_to_sell} shares of {ticker} at {max_prices[i]}")
                        s.post('http://localhost:9999/v1/orders', params={
                            'ticker': ticker,
                            'type': 'LIMIT',
                            'quantity': qty_to_sell,
                            'action': 'SELL',
                            'price': bid_prices[i] - 0.5
                        })

                    elif bid_prices[i] > sell_price:
                        print(f"Selling {qty_to_sell} shares of {ticker} at {sell_price}")
                        s.post('http://localhost:9999/v1/orders', params={
                            'ticker': ticker,
                            'type': 'LIMIT',
                            'quantity': qty_to_sell,
                            'action': 'SELL',
                            'price': sell_price
                        })
                    sleep(0.1)
            
                    cancel_all_orders()
                                        
                gross_position, net_position, tp_position, as_position, ba_position = get_position()
            
            # close_bad_orders(ticker)
        # sleep(0.5)
        
    
if __name__ == '__main__':
    main()

