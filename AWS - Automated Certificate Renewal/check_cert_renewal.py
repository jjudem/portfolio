import requests, json, warnings, contextlib, base64, os, urllib3, time
from urllib3.exceptions import InsecureRequestWarning
from datetime import date
from os import path
from venafi_requests import *
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#Environment variables fetched from Jenkins agent
usern = os.getenv('usern')
passw = os.getenv('passw')

def main():
    #Get API key from stored Jenkins environment variables
    newCertList = []
    thresholdDays = 363
    print("Venafi Certificate - Check Certificate Renewals\n\n")
    apiKey = getApiKey(usern, passw)
    if not apiKey:
        print("API Authorization failed.")
        return False
    
    #Get all Certificates
    certs = getCertificates(apiKey)
    if not certs:
        print("No certificate was retrieved.")
        return False
    
    #Get certificate data
    certs = certs.get("Certificates")
    if not certs:
        print("No certificate was retrieved.")
        return False
    
    #Get exact certificate, path and remaining days
    initialCertificateDetails = getCertificateDetails2(certs)
    certificateList = open('../AWS - Automated Certificate Renewal/venafi-active-certificates.txt', 'r')
    apacCerts = certificateList.readlines()
    for apacCert in apacCerts:
        for i in initialCertificateDetails:
            if apacCert.strip() == i[0] and i[3] != 'None':
                if thresholdDays < int(float(i[3])) and int(float(i[3])) < 366:
                    newCertList.append([i[0],i[1],i[2],i[3]])
                    if len(newCertList) > 0:
                        y = 1
                        print("Found renewed certificate: " + str(len(newCertList)) + "\n")
                        for x in newCertList:
                            print(" - " + x[0] + " (" + x[3] + " day/s left)")
                            if 363 < int(float(x[3])):
                                filename = "venafichecked{}.txt".format(y)
                                fileWr(filename, "w+", str(x))
                                y += 1
                            else:
                                print("No recently renewed certificate.")
                            return False
        
if __name__ == "__main__":
    main()