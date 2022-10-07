import requests, json, warnings, contextlib, base64, os, urllib3, time
from urllib3.exceptions import InsecureRequestWarning
from datetime import date
from os import path
from venafi_requests import *
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#Environment variables fetched from Jenkins agent
usern = os.getenv('USERN')
passw = os.getenv('PASSW')
certificateType = os.getenv('CERTIFICATE_TYPE')
certificateDirectory = os.getenv('CERTIFICATE_DIRECTORY')
certificateName = os.getenv('CERTIFICATE_NAME')
SAN = os.getenv('SAN')

#Global Variables - Set up depending on your Venafi required parameters
#Certificate contact details
hqdomainFo = "codeforAD"
extEmail = "yourcorp@email.com"
extFirstName = "EMAIL GROUP NAME"
extLastName = "EMAIL GROUP NAME EXTENSION"
extAdditional = "yourcorp2nd@email.com"
extTelephone = "123456789"

def createCertificate(apiKey):
    requestUrl = "{}/YOURPATH/Certificates/request".format(host)
    
    #http body request
    if certificateType == "INTERNAL":
        requestPayload = {"PolicyDN": certificateDirectory, "ObjectName": certificateName, "Subject": certificateName ,"CustomFields": [{"Name": "Owner","Values": [hqdomainFo]}],"SubjectAltNames": []}
    elif certificateType == "EXTERNAL":
        requestPayload = {"PolicyDN": certificateDirectory, "ObjectName": certificateName, "CADN": "\\VED\\Policy\\CA Templates\\Entrust External CA","CustomFields": [{"Name": "Owner","Values": [hqdomainFo]}],"CASpecificAttributes": [{"Name": "EntrustNET CA:Email Address", "Value": extEmail},{"Name": "EntrustNET CA:First Name", "Value": extFirstName},{"Name": "EntrustNET CA:Last Name", "Value": extLastName},{"Name": "EntrustNET CA:Additional Field Value", "Value": extAdditional},{"Name": "EntrustNET CA:Telephone", "Value": extTelephone}],"SubjectAltNames": []}
        holder1 = {"TypeName":"2", "Name":certificateName}
        requestPayload["SubjectAltNames"].append(holder1)
        newSAN = str(SAN).split(",")
        if len(newSAN) > 0:
            for i in newSAN:
                holder = {"TypeName":"2", "Name":i}
                requestPayload["SubjectAltNames"].append(holder)
                requestPayload = json.dumps(requestPayload)
    #http headers request
                requestHeaders = {
                    'Content-Type': 'application/json',
                }
                requestHeaders["Authorization"] = 'Bearer ' + apiKey
                response = requests.request("POST", requestUrl, headers=requestHeaders, data=requestPayload, verify=False)
                status_code = response.status_code
                content = response.content
                content = json.loads(content)
                if status_code == 200:
                    return True
    return content

def main():
    #Get Api Key
    apiKey = getApiKey(usern, passw)
    if not apiKey:
        print("API Authorization failed.")
        return False
    x = createCertificate(apiKey)
    if x == True:
        print("Certificate " + certificateName + " was successfully created.")
    else:
        print("Certificate was not created.")
        print(x)
        print("\n\nEnd of Venafi Script")
        
if __name__ == "__main__":
    main()