import requests, json, warnings, contextlib, base64, os, urllib3, time
from urllib3.exceptions import InsecureRequestWarning
from datetime import date
from os import path
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#Environment variables fetched from Jenkins agent
usern = os.getenv('usern')
passw = os.getenv('passw')
certName = os.getenv('VENAFI_CERTIFICATE_NAME')

#Global Variables
host = "YourVenafiHostname/IP/Address"
certPass = "defaultCertificatePassword"
certDetails = []
named_tuple = time.localtime()
data_time = time.strftime("%Y%m%d-%H:%M:%S", named_tuple)
log_data_time = time.strftime("%Y%m%d-%H%M%S", named_tuple)
log_data_time = str(log_data_time)
data_time = str(data_time)
log_file_name = ""
named_tuple = time.localtime()
current_date = time.strftime("%Y-%m-%d", named_tuple)
current_date = str(current_date)

#Main Python files, hold all functions for the whole pipeline
def fileWr(filename, action, text):
    f = open(filename, action)
    f.write(text)
    f.close()
    return True

#Get API key from provided username and password on Jenkins Agent
def getApiKey(usern, passw):
    #Authenticate Variables - Always Execute
    authUrl = "{}/VEDSDK/Authorize".format(host)
    authPayload = {"username": usern, "password": passw}
    authPayload = json.dumps(authPayload)
    authHeaders = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", authUrl, headers=authHeaders, data=authPayload, verify=False)
    status_code = response.status_code
    if status_code == 200:
        content = response.content
        content = json.loads(content)
        api_key = content.get("APIKey")
        return api_key
    return False

def getRequestedCertificate(apiKey, xCertPath, certName):
    #Retrieve Variables - Always Execute
    retrieveUrl = "{}/VEDSDK/Certificates/Retrieve".format(host)
    retrievePayload = {"CertificateDN": xCertPath + "\\"+ certName, "Format": "PKCS #12", "IncludePrivateKey": True, "password": certPass, "IncludeChain": True}
    retrievePayload = json.dumps(retrievePayload)
    retrieveHeaders = {
        'Cache-Control': 'no-cache',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Venafi-Api-Key': apiKey
    }
    response = requests.request("POST", retrieveUrl, headers=retrieveHeaders, data=retrievePayload, verify=False)
    status_code = response.status_code
    if status_code == 200:
        content = response.content
        content = json.loads(content)
        certificateData = content.get("CertificateData")
        cert1 = base64.b64decode(certificateData)
        f = open("cert.pfx", "wb")
        f.write(cert1)
        f.close()
        #Print Certificate if existing on stdln
        print("Certificate " + certName + " was retirieved successfully.")
        return True
    return False

def getCertificateDetails2(certs):
    certs_obj = []
    exactCert = []
    for i in range(len(certs)):
        cert = certs[i]
        guid = cert.get("Guid")
        name = cert.get("Name")
        path_loc = cert.get("ParentDn")
        x509 = cert.get("X509")
    if x509:
        valid_to = x509.get("ValidTo")
        if valid_to:
            date_time = valid_to.split("T")
            certificate_expiration_date = str(date_time[0])
            certificate_expiration_yr_month_day = certificate_expiration_date.split("-")
            certificate_expiration_year = int(certificate_expiration_yr_month_day[0])
            certificate_expiration_month = int(certificate_expiration_yr_month_day[1])
            certificate_expiration_day = int(certificate_expiration_yr_month_day[2])
            current_year_month_day = current_date.split("-")
            current_year = int(current_year_month_day[0])
            current_month = int(current_year_month_day[1])
            current_day = int(current_year_month_day[2])
            current_year_month_day = date(current_year, current_month, current_day)
            certificate_expiration_yr_month_day = date(certificate_expiration_year, certificate_expiration_month, certificate_expiration_day)
            certificate_remaining_expiration = certificate_expiration_yr_month_day - current_year_month_day
            certificate_remaining_expiration = str(certificate_remaining_expiration)
            certificate_remaining_expiration = certificate_remaining_expiration.split(",")
            certificate_remaining_expiration = certificate_remaining_expiration[0]
            certificate_remaining_expiration = certificate_remaining_expiration.replace(" days", "")
            certificate_remaining_expiration = certificate_remaining_expiration.replace(" day", "")
        else:
            certificate_remaining_expiration = "None"
    else:
        certificate_remaining_expiration = "None"
        certs_obj.append([name, guid, path_loc, certificate_remaining_expiration])
    return certs_obj

def getCertificates(key):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    headers['Authorization'] = 'Bearer {}'.format(key)
    url = "{}/yourVenafiPath/certificates/?limit=10000&disabled=0".format(host)
    response = requests.request("GET", url, headers=headers, data=None, verify=False)
    status_code = response.status_code
    if status_code == 200:
        content = response.content
        content = json.loads(content)
        return content
    return False

def getCertificateDetails(certs, xCertName):
    certs_obj = []
    exactCert = []
    for i in range(len(certs)):
        cert = certs[i]
        guid = cert.get("Guid")
        name = cert.get("Name")
        path_loc = cert.get("ParentDn")
        x509 = cert.get("X509")
        if x509:
            valid_to = x509.get("ValidTo")
            if valid_to:
                date_time = valid_to.split("T")
                certificate_expiration_date = str(date_time[0])
                certificate_expiration_yr_month_day = certificate_expiration_date.split("-")
                certificate_expiration_year = int(certificate_expiration_yr_month_day[0])
                certificate_expiration_month = int(certificate_expiration_yr_month_day[1])
                certificate_expiration_day = int(certificate_expiration_yr_month_day[2])
                current_year_month_day = current_date.split("-")
                current_year = int(current_year_month_day[0])
                current_month = int(current_year_month_day[1])
                current_day = int(current_year_month_day[2])
                current_year_month_day = date(current_year, current_month, current_day)
                certificate_expiration_yr_month_day = date(certificate_expiration_year, certificate_expiration_month, certificate_expiration_day)
                certificate_remaining_expiration = certificate_expiration_yr_month_day - current_year_month_day
                certificate_remaining_expiration = str(certificate_remaining_expiration)
                certificate_remaining_expiration = certificate_remaining_expiration.split(",")
                certificate_remaining_expiration = certificate_remaining_expiration[0]
                certificate_remaining_expiration = certificate_remaining_expiration.replace(" days", "")
                certificate_remaining_expiration = certificate_remaining_expiration.replace(" day", "")
            else:
                certificate_remaining_expiration = "None"
        else:
            certificate_remaining_expiration = "None"
            certs_obj.append([name, guid, path_loc, certificate_remaining_expiration])
            try:
                for i in certs_obj:
                    name = i[0]
                    if name == xCertName:
                        exactCert = i
                    break
                return exactCert
            except:
                print("Certificate " + xCertName + " was not found.")
    return False
        
#True = Renew; False = Don't Renew
def certificateRenewalCheck(remainingDays):
    if remainingDays < 45:
        return True
    elif remainingDays >= 45:
        return False

#Retrieve Variables - Always Execute
def renewCertificate(apiKey, xCertPath, certName):
    renewUrl = "{}/VEDSDK/Certificates/Renew".format(host)
    renewPayload = {"CertificateDN": xCertPath + certName}
    renewPayload = json.dumps(renewPayload)
    renewHeaders = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'X-Venafi-Api-Key': apiKey
    }
    response = requests.request("POST", renewUrl, headers=renewHeaders, data=renewPayload, verify=False)
    status_code = response.status_code
    if status_code == 200:
        content = response.content
        content = json.loads(content)
        renewalResult = content.get("Success")
        return renewalResult
    elif status_code != 200:
        content = response.content
        content = json.loads(content)
        error_msg = content.get("Error")
        if error_msg:
            return error_msg
    else:
        return content

def getOneCertificate(key, guid):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    headers['Authorization'] = 'Bearer {}'.format(key)
    url = "{}/vedsdk/certificates/{}".format(host, guid)
    response = requests.request("GET", url, headers=headers, data=None, verify=False)
    status_code = response.status_code
    if status_code == 200:
        content = response.content
        content = json.loads(content)
        processingDetails = content.get("ProcessingDetails")
        return processingDetails
    return False

def main():
    actions = os.getenv('ACTIONS').strip('][').split(', ')
    print("Start of Venafi Script")
    fileWr("buildRes.txt", "w+", "SUCCESS")
    apiKey = getApiKey(usern, passw)
    if not apiKey:
        print("API Authorization failed.")
        fileWr("buildRes.txt", "w+", "FAILURE")
        return False
    #Get all Certificates - exit if failed
    certs = getCertificates(apiKey)
    if not certs:
        print("No certificate was retrieved.")
        return False
    #Get certificate data - exit if failed
    certs = certs.get("Certificates")
    if not certs:
        print("No certificate was retrieved.")
        return False
    #Get exact certificate, path and remaining days
    initialCertificateDetails = getCertificateDetails(certs, certName)
    if initialCertificateDetails == []:
        print("Certificate: " + certName + " was not found on Venafi.\n")
        print("End of Venafi Script.")
        fileWr("buildRes.txt", "w+", "FAILURE")
        fileWr("buildResult1.txt", "w+", "FAILURE")
        fileWr("buildResult2.txt", "w+", "MISSING_CERTIFICATE")
        return False
    else:
        fixedCertPath = initialCertificateDetails[2] + "\\\\"
        fixedGuid = initialCertificateDetails[1]
        initialRemainingDays = int(initialCertificateDetails[3])
        fileWr("guid.txt", "w+", fixedGuid)
        print("Certificate: " + certName + " was found successfully on Venafi under " + fixedCertPath + " with " + str(initialRemainingDays) + " days remaining.")
        #Retrieve only
        if 'RETRIEVE' in actions and 'RENEW' not in actions:
            print("\nDownloading certificate from Venafi...")
            apiKey = getApiKey(usern, passw)
            a = getRequestedCertificate(apiKey, fixedCertPath, certName)
            if a == True:
                fileWr("var1.txt", "w+", "DO_OPENSSL")
            elif a == False:
                fileWr("var1.txt", "w+", "DO_NOT_OPENSSL")
        #Renew only
        if 'RENEW' in actions:
            print("\nChecking requirements before renewing......")
            apiKey = getApiKey(usern, passw)
            isRenewable = certificateRenewalCheck(initialRemainingDays)
            if isRenewable == True and "RETRIEVE":
                print("\nInitiating renewal of " + certName + ".....")
                apiKey = getApiKey(usern, passw)
                b = renewCertificate(apiKey, fixedCertPath, certName)
                if b == True:
                    print("\n---> Renewal was triggered!")
                    x = 0
                    validator = 1
                    while x <= 10:
                        x += 1
                        print("\n---> Checking the approval status...." + str(x) +"x")
                        time.sleep(10)
                        #Refresh Certificate Data in memory
                        apiKey = getApiKey(usern, passw)
                        certs = getCertificates(apiKey)
                        certs = certs.get("Certificates")
                        renewalCertDetails = getCertificateDetails(certs, certName)
                        renewalRemainingDays = int(renewalCertDetails[3])
                        if renewalRemainingDays > 363:
                            print("\n---> Certificate " + certName + " has been approved and renewed!")
                            print("\t- Certificate remaining days:\t" + str(renewalCertDetails[3]))
                            print("\t- Venafi certificate direct link:\t https://wprnedcoven001v/aperture/certificate/" + str(renewalCertDetails[1]))
                            validator += 5
                            break
                        else:
                            validator = 1
                            if validator == 1 and 'RETRIEVE' not in actions:
                                print("\n---> Certificate renewal is awaiting for some approvals, details:\n")
                                fileWr("certificatedays.txt", "w+", "Certificate " + certName + " is pending approvals.")
                                approval = getOneCertificate(apiKey, fixedGuid)
                                print(approval)
                                print("\t- Certificate in-approval process:\t" + str(approval['InProcess']))
                                print("\t- Certificate renewal status:\t" + str(approval['Status']))
                                print("\t- Venafi workflow TicketDN:\t" + str(approval['TicketDN']))
                                print("\t- Venafi direct certificate link:\t YOUR/VENAFI/HOST/AND/CERTIFICATE/PATH" + fixedGuid)
                                fileWr("buildRes.txt", "w+", "FAILURE")
                            if validator == 1 and 'RETRIEVE' in actions:
                                print("\Certificate " + certName + " did not pass the requirements for renewal.")
                                print("\Will proceed now with the Retrieval of the certificate.")
                                print("\nDownloading certificate from Venafi...")
                                apiKey = getApiKey(usern, passw)
                                a = getRequestedCertificate(apiKey, fixedCertPath, certName)
                                if a == True:
                                    fileWr("var1.txt", "w+", "DO_OPENSSL")
                                elif a == False:
                                    fileWr("var1.txt", "w+", "DO_NOT_OPENSSL")
                                if validator == 6 and 'RETRIEVE' in actions:
                                    print("\n Downloading new certificate from Venafi...")
                                    apiKey = getApiKey(usern, passw)
                                    certs = getCertificates(apiKey)
                                    certs = certs.get("Certificates")
                                    retrievedCert = getCertificateDetails(certs, certName)
                                    c = getRequestedCertificate(apiKey, fixedCertPath, certName)
                                    if c == True:
                                        fileWr("var1.txt", "w+", "DO_OPENSSL")
                                    elif c == False:
                                        fileWr("var1.txt", "w+", "DO_NOT_OPENSSL")
                if b != True:
                    print("\n---> Failed calling the Renewal API for this certificate renewal.")
                    print("\n---> Error: " + str(b))
                    fileWr("buildRes.txt", "w+", "FAILURE")
            elif isRenewable == False and 'RETRIEVE' not in actions:
                    print("\nCertificate " + certName + " remaining days are still long with " + str(initialRemainingDays) + " days remaining.")
                    print("\nCould not proceed with the renewal, exiting job.")
                    fileWr("certificatedays.txt", "w+", "Certificate " + certName + " remaining days are still long with " + str(initialRemainingDays) + " days remaining.")
                    fileWr("buildRes.txt", "w+", "FAILURE")
            elif isRenewable == False and 'RETRIEVE' in actions:
                print("\n Remaining action: RETRIEVE")
                print("\n Downloading current certificate in Venafi...")
                apiKey = getApiKey(usern, passw)
                certs = getCertificates(apiKey)
                certs = certs.get("Certificates")
                retrievedCert = getCertificateDetails(certs, certName)
                c = getRequestedCertificate(apiKey, fixedCertPath, certName)
                if c == True:
                    fileWr("var1.txt", "w+", "DO_OPENSSL")
                elif c == False:
                    fileWr("var1.txt", "w+", "DO_NOT_OPENSSL")
                    print("End of Venafi Script.")
                    
if __name__ == "__main__":
    main()
