#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys, json
import pandas as pd
import types
from botocore.client import Config
import ibm_boto3
import datetime
import requests
import tempfile
import pycbrf

#from pprint import pprint
from opencage.geocoder import OpenCageGeocode
from math import radians, cos, sin, asin, sqrt


#import ibmfunctions

def main(dict):

    print (dict['action'])
    
    res = ""
    
    if (dict['action']=="test"):
        res =   "Проверка отклика"
        return { 'response': res }

    # if user is asking about bank account
    if (dict['action']=="account"):
        res= getAccount(dict) 
        return res

    if (dict['action']=="scoring"):
        #res =   getScore(dict['age'], dict['bmi']) 
        res =   getScore(dict) 
        return { 'response': res }

    if (dict['action']=="list_atm"):
        atms = getATMlist(dict)
        
        selectedATMs = [atm for atm in atms['data']['atms'] if atm['address']['city'] == "Тольятти"] #and atm['deviceId'] == 155358 
        #selectedATMs = [atm for atm in atms['data']['atms'] if atm['address']['city'] == "Москва"]

        res = selectedATMs # resp[0:500]
        return { 'response': res }
         
    if (dict['action']=="find_atm"):
        
        city = dict['city'] # params.get('city')
        address = dict['address'] # params.get('address')
        atms = getATMlist(dict) #get_all_atms()
        key = 'f99c930c9aeb46bcbc00624ad480250d'
        geocoder = OpenCageGeocode(key)
        #print(city + '' + address)
        result = geocoder.geocode(city + ' ' + address, no_annotations='1')
        #pprint(result)
        longitude = float(result[0]['geometry']['lng'])
        latitude = float(result[0]['geometry']['lat'])
        answer = {'atm': nearest_atm(get_city_atms(atms, city), latitude, longitude)}

        return answer
   
    if (dict['action']=="currency_rate"):
        type_of_currency = dict['currency']
        today_date = datetime.date.today()
        res = str(pycbrf.ExchangeRates(today_date)[type_of_currency].rate)
        # answer = {'rate': str(pycbrf.ExchangeRates(today_date)[type_of_currency].rate)}
        return { 'response': res }
        
    entity = 'unknown'
    if 'entity' in dict:
        entity = dict['entity']
    else:
        entity = 'unknown'
    res = getEntityDescriptionFromCSV(entity, dict)
    return { 'response': res }
    
  
# Check if account is personal or buisness
def getAccount(dict):
    response={"result":""}
    if dict['accountID'] == 11111111 and dict['OTP'] == 123:
        response["result"]="Welcome Mike Hudson\nAccount No:11111111"
              
    elif dict['accountID'] == 22222222 and dict['OTP'] == 456 :
        response["result"] = "Welcome Veronica Gomez\nAccount No:22222222"
   
         
    else:
        response["result"] = "Incorrect credentials"
     
    return  response


#Read Data from excel file  
def getEntityDescriptionFromCSV(entity, dict):
    # @hidden_cell
    # The following code accesses a file in your IBM Cloud Object Storage. It includes your credentials.
    # You might want to remove those credentials before you share the notebook.
    p_endpoint_url = "s3.private.eu-gb.cloud-object-storage.appdomain.cloud"
    p_file_name = "plans.csv"
    p_api_key = "ZrFo7ofyjMC8WjPRl64POdlAyPNFuZbdy0dvViBM2KeE"
    p_bucket_name = "telecom-bucket-2"
    p_service_instance_id = "crn:v1:bluemix:public:cloud-object-storage:global:a/92a251eb5188417fb348a2349e816e2b:ffc2d55e-f6c7-4d44-8886-e1c62fe1c7c0::"

    
    client = ibm_boto3.client(service_name='s3',
    ibm_api_key_id= p_api_key,
    ibm_service_instance_id= p_service_instance_id,
    config=Config(signature_version='oauth'),
    endpoint_url= "https://" + p_endpoint_url)
    body = client.get_object(Bucket= p_bucket_name,Key= p_file_name)['Body']
   
    if not hasattr(body, "__iter__"): body.__iter__ = types.MethodType( __iter__, body )
    
    df_data_1 = pd.read_csv(body, encoding = "ISO-8859-1")
    
    entity = entity.lower()
    
    row = df_data_1.query('entity == @entity')[['description']]
    reponse = ''
    idx = row.index
    try:
        idx = idx[0]
        response = df_data_1.iloc[idx, 1] + ''
    except IndexError:
        response = 'Sorry cannot find a definition in my knowledge base'
    
    ## !!!!! Usachev
    #response =   getScore()  

    return response



#def getScore(pAge, pBMI):
def getScore(p_dict):
    import requests
    API_KEY = "bSoPUFqb2Dt6NsBWgwThgHpylGq6mn5pYVmqbm6oHpml"
    model = 'https://eu-gb.ml.cloud.ibm.com/ml/v4/deployments/506e5136-3a0e-475e-a5b3-1f6833196821/predictions?version=2021-06-25'
    token_response = requests.post('https://iam.cloud.ibm.com/identity/token', 
                                   data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
    mltoken = token_response.json()["access_token"]
    array_of_input_fields =    ["age", "sex", "bmi", "children", "smoker", "region"]
    array_of_values_to_score = [ 30,  'female',   20,      2,       'no',    'southwest' ]
    array_of_values_to_score[0] = p_dict['age'] #pAge
    array_of_values_to_score[1] = p_dict['sex'] 
    array_of_values_to_score[2] = p_dict['bmi'] #pBMI
    array_of_values_to_score[3] = p_dict['children'] 
    array_of_values_to_score[4] = p_dict['smoker'] 
    
    request_json = { "input_data": [{"fields": [array_of_input_fields], "values": [array_of_values_to_score]} ] }
    response_json = requests.post( model, json=request_json, headers={'Authorization': 'Bearer ' + mltoken})
    #response_json = "ssss"
    return  response_json.json()
    #print("Scoring response:" , response_json.json())
    
    
def getATMlist(dict):
    # @hidden_cell
    # The following code accesses a file in your IBM Cloud Object Storage. It includes your credentials.
    # You might want to remove those credentials before you share the notebook.
    p_endpoint_url = "s3.private.eu-gb.cloud-object-storage.appdomain.cloud"
    p_file_name = "plans.csv"
    p_api_key = "ZrFo7ofyjMC8WjPRl64POdlAyPNFuZbdy0dvViBM2KeE"
    p_bucket_name = "telecom-bucket-2"
    p_service_instance_id = "crn:v1:bluemix:public:cloud-object-storage:global:a/92a251eb5188417fb348a2349e816e2b:ffc2d55e-f6c7-4d44-8886-e1c62fe1c7c0::"
    
    client = ibm_boto3.client(service_name='s3',
    ibm_api_key_id= p_api_key,
    ibm_service_instance_id= p_service_instance_id,
    config=Config(signature_version='oauth'),
    endpoint_url= "https://" + p_endpoint_url)
 
    body_cer = client.get_object(Bucket= p_bucket_name,Key='apidevelopers.cer')['Body']
    #if not hasattr(body_bank_key, "__iter__"): body_bank_key.__iter__ = types.MethodType( __iter__, body_bank_key )
    body_key = client.get_object(Bucket= p_bucket_name,Key='apidevelopers.key')['Body']
    
    client_cert = body_cer.read()
    client_key = body_key.read()
    
    tmp_cert = tempfile.NamedTemporaryFile(delete=False)
    tmp_cert.write(client_cert)
    tmp_cert.close()

    tmp_key = tempfile.NamedTemporaryFile(delete=False)
    tmp_key.write(client_key)
    tmp_key.close()
    
    url = 'https://apiws.alfabank.ru/alfabank/alfadevportal/atm-service/atms'
    headers = {
        'x-ibm-client-id': "21c20450-5329-46f4-a00d-eaa4561b6249",
        'accept': "application/json",
        'Content-Type': "application/json",
    }
    response = requests.get(url, headers=headers, cert=(tmp_cert.name, tmp_key.name))
    
    return response.json()
    
    #return response.text

def haversine(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние в километрах между двумя точками, учитывая окружность Земли.
    https://en.wikipedia.org/wiki/Haversine_formula
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, (lon1, lat1, lon2, lat2))
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def get_address(atms, index):
    address = atms['data']['atms'][index]['address']
    city = address['city']
    location = address['location']
    return f'{city}, {location}'

def get_city_atms(atms, city):
    city_atms = [atm for atm in atms['data']['atms'] if atm['address']['city'] == city]
    return city_atms


def nearest_atm(atms, lat, lon):
    kms = []
    for atm in atms:
        coordinates = atm['coordinates']
        kms.append(haversine(float(coordinates['latitude']), float(coordinates['longitude']), lat, lon))
    print(kms)
    return atms[kms.index(min(kms))]

