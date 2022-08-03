# Nt Function Creator v1.0
# Author: Ibranum (Evan Read)
# Uses: Python 3
# Date: 07/29/2022 -> 08/01/2022
# Description: Creates a function to match a Microsoft-defined Nt function for the Sharem program using a user-fed URL

from multiprocessing.connection import wait
import validators
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

def urlCheck():
    #url = "" # User-defined URL
    #url = "http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FNT%20Objects%2FProcess%2FNtCreateProcess.html"
    #url = "http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FAtoms%2FNtAddAtom.html"
    #url = "http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FNT%20Objects%2FThread%2FNtDelayExecution.html"
    #url = "https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-zwdeletefile"
    #url = "https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-zwcreateevent"
    #url = "https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-zwsetevent"

    url = ""
    urlType = ""

    while True:
        if url == "":
            url = input("[ 📝 ] Please enter a URL: ")
        if validators.url(url):
            if "undocumented.ntinternals.net" in url:
                print("[ ✅ ] URL is valid")
                urlType = "ntinternals"
                break
            elif "docs.microsoft.com" in url:
                print("[ ✅ ] URL is valid")
                urlType = "msdn"
                break
            else: 
                print("[ ❌ ] URL is not valid")
                url = ""
                continue
        else:
            print("[ ❌ ] Invalid URL")
            continue

    return url, urlType

def getMSDNSite(url):
    targetXPath = "/html/body/div[2]/div/section/div/div[1]/main/div[3]/pre/code/span"

    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    driver.get(url)

    try:
        #driver.switch_to.frame("content")
        html = driver.page_source
        time.sleep(2)

        xpathOutput = driver.find_element(By.XPATH, targetXPath).text
        functionName = driver.find_element(By.XPATH, "/html/body/div[2]/div/section/div/div[1]/main/div[3]/pre/code/span/span/span[1]").text

        driver.close()

        if "Zw" in functionName:
            functionName = functionName.replace("Zw", "Nt")

        return xpathOutput, functionName 
    except:
        print("[ ❌ ] Could not find function information")
        driver.close()
        exit()

def getNTInternalSite(url):
    # Assuming link is to undocumented ntinternals website
    # Link Example: http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FNT%20Objects%2FProcess%2FNtCreateProcess.html
    targetXPath = "/html/body/pre"

    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    driver.get(url)

    try:
        driver.switch_to.frame("content")
        html = driver.page_source
        time.sleep(2)

        xpathOutput = driver.find_element(By.XPATH, targetXPath).text
        functionName = driver.find_element(By.XPATH, "/html/body/div[2]").text

        driver.close()

        return xpathOutput, functionName 
    except:
        print("[ ❌ ] Could not find function information")
        driver.close()
        exit()

def ptypeRegex(xpathOutput, urlType, functionName):
    if urlType == "ntinternals":
        inOrOut = []
        typeField = re.findall("(?:OUT) \w+|(?:IN )\w+", xpathOutput)
        for i in range(len(typeField)):
            inOrOut.append(typeField[i].split(" "))

        return inOrOut

    elif urlType == "msdn":
        inOrOut = []
        xClean = 1
        xpathOutput = cleanMSDN(xpathOutput, functionName, xClean)
        
        typeField = re.findall("[A-Z_]{2,20}", xpathOutput)
        for i in range(len(typeField)):
            inOrOut.append(typeField[i].split(" "))

        return inOrOut

def printPtypes(inOrOut, urlType):
    if urlType == "ntinternals":
        #print(inOrOut[0][1]) # Iterate over first one, leave second in the one position for pTypes
        print('    pTypes = [', end="")
        for i in range(len(inOrOut)):
            print("'", end="")
            print(inOrOut[i][1], end="")
            if i != len(inOrOut)-1:
                print("', ", end="")
            else:
                print("']", end="") # Close pTypes list 

    elif urlType == "msdn":
        #print(inOrOut[0][1]) # Iterate over first one, leave second in the one position for pTypes
        print('    pTypes = [', end="")
        for i in range(len(inOrOut)):
            print("'", end="")
            print(inOrOut[i], end="")
            if i != len(inOrOut)-1:
                print("', ", end="")
            else:
                print("']", end="")

def pnamesRegex(xpathOutput, inOrOut, urlType, functionName):
    if urlType == "ntinternals":

        for i in range(len(inOrOut)):
            if inOrOut[i][1] in xpathOutput:
                xpathOutput = xpathOutput.replace(inOrOut[i][1], "")

        xpathOutput = str(xpathOutput)
        removalChars = [" OPTIONAL", "IN", "OUT", "NTAPI", "NTSTATUS", "NTSYSAPI"]
        for i in range(len(removalChars)):
            xpathOutput = xpathOutput.replace(removalChars[i], "")
        xpathOutput = xpathOutput.replace(")", '    ')
        xpathOutput = xpathOutput.replace(",", '    ')

        # This is where it used to iterate through to make sure no pTypes were present

        listNames = []
        typeField = re.findall("(\w+ )", xpathOutput)

        for i in range(len(typeField)):
            typeField[i] = typeField[i].replace(" ", '')

        return typeField
    
    elif urlType == "msdn":
        xClean = 1
        xpathOutput = cleanMSDN(xpathOutput, functionName, xClean)
        xClean = 0
        inOrOut = cleanMSDN(str(inOrOut), functionName, xClean)

        inOrOut = inOrOut.split()

        for i in range(len(inOrOut)):
            if inOrOut[i] in xpathOutput:
                xpathOutput = xpathOutput.replace(inOrOut[i], "")

        # This is where it used to iterate through to make sure no pTypes were present

        listNames = []
        typeField = re.findall("\w+", xpathOutput)

        for i in range(len(typeField)):
            typeField[i] = typeField[i].replace(" ", '')

        for i in range(len(typeField)-1): # why does this work???????
            #print(typeField[i])
            if "Zw" in str(typeField[i]):
                typeField.pop(i)

        return typeField

def printPnames(pnames):
    print('    pNames = [', end="")
    for i in range(len(pnames)):
        print("'", end="")
        print(pnames[i], end="")
        if i != len(pnames)-1:
            print("', ", end="")
        else:
            print("']", end="") # Close pTypes list

def printFinishedFunction(ptypes, pnames, functionName, urlType):
    print("[ ⏯ ] Function Start:\n")
    
    print("def " + functionName + "(self, uc: Uc, eip: int, esp: int, callAddr: int, em: EMU):")
    printPtypes(ptypes, urlType) # Print pTypes
    print("")
    printPnames(pnames) # Print pNames
    print("")
    print("    pVals = self.makeArgVals(uc, em, esp, len(pTypes))\n")

    print("    pVals[] = getLookupVal(pVals[], ReverseLookups.NTSTATUS)\n")

    print("    pTypes, pVals = findStringsParms(uc, pTypes, pVals, skip=[]\n")

    print("    retVal = 0")
    print("    retValStr = getLookUpVal(retVal, ReverseLookUps.NTSTATUS")
    print("    uc.reg_write(UC_X86_REG_EAX, retVal)")
    print("    logged_calls = ['" + functionName + "', hex(callAddr), retValStr, 'NTSTATUS', pVals, pTypes, pNames, False]\n")

    print("    return logged_calls" + "\n")

    print("[ ⏹ ] Function Stop")

def cleanMSDN(xpathOutput, functionName, xClean):
    functionName2 = functionName.replace("Nt", 'Zw')
    xpathOutput = str(xpathOutput)
    removalChars = [", optional", "in", "out", "NTAPI", "NTSYSAPI", "[", "]", functionName, ")", "(", ";", ",", "'", functionName2]
    for i in range(len(removalChars)):
        xpathOutput = xpathOutput.replace(removalChars[i], "")

    if xClean == 1:
        xpathOutput = xpathOutput.replace("NTSTATUS", '', 1)

    return xpathOutput

def main():
    print("[ 🔥 ] Welcome to the Nt Function Creator") # Yes, I like using emojis in the my programs
    inOrOut = ""
    pnames = ""
    functionName = ""

    url, urlType = urlCheck() # Get and check URL from user

    if urlType == "ntinternals":
        xpathOutput, functionName = getNTInternalSite(url) # Use Selenium to grab info from user URL
        inOrOut = ptypeRegex(xpathOutput, urlType, functionName) # Get ptypes from the xpath output using Regex
        pnames = pnamesRegex(xpathOutput, inOrOut, urlType, functionName) # Get pnames from the xpath output using Regex
    elif urlType == "msdn":
        xpathOutput, functionName = getMSDNSite(url) # Use Selenium to grab info from user URL

        inOrOut = ptypeRegex(xpathOutput, urlType, functionName) # Get ptypes from the xpath output using Regex
        pnames = pnamesRegex(xpathOutput, inOrOut, urlType, functionName) # Get pnames from the xpath output using Regex

    if urlType == "msdn":
        xClean = 0
        inOrOut = cleanMSDN(inOrOut, functionName, xClean)
        inOrOut = inOrOut.split()
    #print(inOrOut)
    printFinishedFunction(inOrOut, pnames, functionName, urlType) # Print finished function


if __name__ == "__main__":
    main()





