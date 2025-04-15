# batch update activities via cityworks api
# by Peter Sherman 2024-10-21
# Make sure the .csv import files doesn't have any & or # characters
# {"RequestId":"448352","ReqCustFieldCatId":"284334","CustomFieldValues":{"263178": "No"}}

import requests
from datetime import datetime, date
import json
import time
import os
import pandas as pd
import csv

# # Get Token
# # Define the endpoint and payload for getting the token
# url = "https://example.com/api/token" 
# payload = { "username": "your_username", "password": "your_password" } 
# headers = { "Content-Type": "application/json" } 
# # Make the POST request to get the token 
# response = requests.post(url, data=json.dumps(payload), headers=headers)
# if response.status_code == 200: 
#     #token = response.json().get("Token")
#     # token is nested inside Value
#     token = response.json().get("Value", {}).get("Token")
#     print(f"Token: {token}") 
# else: 
#     print(f"Failed to get token. Status code: {response.status_code}") 
#     token = None
# # End Token

dataSourcesDir = '/Users/shermanp/code/'
fileCsv = 'unimproved-streets-insp-create.csv'

# setup pandas dataframes
failedwebhooks = pd.read_csv(dataSourcesDir+fileCsv)
failedWebhooksDF = pd.DataFrame(failedwebhooks)

api_calls_made = 0
errorList = {}

outputfile = '/Users/shermanp/code/outputfile.txt'

for index, row in failedWebhooksDF.iterrows():
    FID = row['COR_FACILI']
    Address = row['Address']
    Priority = row['Priority']
    LeafZones = row['COR_LEAF_I']
    Location = row['PMS Section']
    print(FID)
    url = 'https://<host url>/<site>/services/Ams/Inspection/Create?data={"Facility_Id": "'+str(FID)+'", "Address": "'+str(Address)+'", "Location": "'+str(Location)+'", "Priority": "'+str(Priority)+'", "MapPage": "'+str(LeafZones)+'", "InspTemplateId": 282295, "EntityType":"STREETS", "DomainId":284007 }&Token=<token>'
    response = requests.post(url)
    time.sleep(2)
    data = response.json()
    print(data['Status'])
    
    if response.status_code == 200 and data['Status'] == 0:
        print("created inspection successfully")
        response_dict = response.json()
        inspection_id = response_dict['Value']['InspectionId']
        url='https://<host url>/<site>/services/ams/inspection/addentity?data={"GetGISData": true,"EntityType": "Streets", "Entityuid":"'+str(FID)+'","InspectionId":'+str(inspection_id)+'}&Token=<token>'
        response = requests.post(url)
        time.sleep(2)
        if response.status_code == 200:
            print("updated entity successfully")
        else:
            print(f"Error:{response.status_code}, {response.json()}" )
            #with open(outputfile, 'w') as f:
            #    f.write(f'Facilityid: {FID} | Max_Count: {api_calls_made} | ERROR entity add\n')
            errorList[FID] = Address
        
        urlUpdate='https://<host url>/<site>/services/ams/inspection/update?data={"Answers":[{"AnswerId": 277975, "AnswerValue":"'+str(Address)+'","InspectionId":'+str(inspection_id)+', "QuestionId": 292281}],"InspectionId":'+str(inspection_id)+'}&Token=<token>'
        responseUpdate = requests.post(urlUpdate)
        time.sleep(2)
        if response.status_code == 200:
            print("updated question successfully")
        else:
            print(f"Error:{response.status_code}, {response.json()}" )
            #with open(outputfile, 'w') as f:
                #f.write(f'Facilityid: {FID} | Max_Count: {api_calls_made} | ERROR entity add\n')
            errorList[FID] = Address

    else:
        print(f"Error: {response.status_code}, {response.json()}")
        #with open(outputfile, 'w') as f:
            #f.write(f'ID: {FID} | Max_Count: {api_calls_made} | ERROR\n')
        errorList[FID] = Address
    
    api_calls_made += 1
    print(api_calls_made)

print(errorList)


with open(outputfile, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write the header
    writer.writerow(errorList.keys())
    
    # Write the data rows
    rows = zip(*errorList.values())
    writer.writerows(rows)

print(f"Data has been written to {outputfile}")

print('Completed')
