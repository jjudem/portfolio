import requests, json, warnings, contextlib, base64, os, urllib3, time
from urllib3.exceptions import InsecureRequestWarning
from datetime import date
from os import path
from venafi_requests import *

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#Environment variables fetched from Jenkins agent
username = os.getenv('username')
password = os.getenv('password')

#Global Variables
newCertList = []

def main():
    #Certificate remaining days threshold
    thresholdDays = 40

    print("Venafi Certificate - Auto Renewal\n\n")

    #Get API key from stored Jenkins environment variables
    apiKey = getApiKey(username, password)
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

    initialCertificateDetails = getCertificateDetails2(certs)
    certificateList = open('../AWS - Automated Certificate Renewal/venafi-active-certificates.txt', 'r')
    apacCerts = certificateList.readlines()

    for apacCert in apacCerts:
        for i in initialCertificateDetails:
            if apacCert.strip() == i[0] and i[3] != 'None':
                if thresholdDays > int(float(i[3])):
                    newCertList.append([i[0],i[1],i[2],i[3]])
                if len(newCertList) > 0:
                    print("Found " + str(len(newCertList)) + " certificate/s eligible for renewal:\n")
                    for x in newCertList:
                        print(" - " + x[0] + " (" + x[3] + " day/s left)")
                    else:
                        print("No certificate/s eligible for renewal.")
                        print("\n\nEnd of Venafi Script")
                        return False
                print("\nInitiating renewal of expiring certificates...\n")
                for xCert in newCertList:
                    fixedCertPath = xCert[2] + "\\\\"
                    certName = xCert[0]
                    apiKey = getApiKey(username, password)
                    print(" - Renewing " + certName)
                    renewCertificate(apiKey, fixedCertPath, certName)
                    print("\n\nChecking certificate/s renewal status...")
                    time.sleep(60)
                    apiKey = getApiKey(username, password)
                    certs = getCertificates(apiKey)
                    certs = certs.get("Certificates")
                    finalCertDetails = getCertificateDetails2(certs)
                    certSummaryList = []
                    for cert in newCertList:
                        certName = cert[0]
                        for finalCert in finalCertDetails:
                            if certName == finalCert[0]:
                                certSummaryList.append(finalCert)
                                print("\nSuccessful renewals:")
                                o = 1
                                for i in certSummaryList:
                                    if 363 < int(float(i[3])):
                                        print(" - " + i[0])
                                        filename = "renewed{}.txt".format(o)
                                        fileWr(filename, "w+", str(i))
                                        o += 1
                                        print("\n\nFailed renewals:")
                                        y = 1
                                        for i in certSummaryList:
                                            if 363 > int(float(i[3])):
                                                print(" - " + i[0])
                                                filename = "failed{}.txt".format(y)
                                                fileWr(filename, "w+", str(i))
                                                y += 1
                                                print("\n\nEnd of Venafi Script")

if __name__ == "__main__":
    main()