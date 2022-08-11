# Nt Function Creator v1.0
# Author: Ibranum (Evan Read)
# Uses: Python 3
# Date: 07/29/2022 -> 08/03/2022
# Description: Creates a function to match a Microsoft-defined Nt function for the Sharem program using a user-fed URL

from multiprocessing.connection import wait
import validators
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

# make option to grab options from internal sharem folder
# make option to load in comma-separated url file
# make option to load in comma-separated function names file

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
        print("[ 🧵 ] ptype regex 1: " + str(xpathOutput))
        if "IN OUT" in xpathOutput:
            print("[ ❌❌❌ ] IN OUT found")
            xpathOutput = xpathOutput.replace("IN OUT", "IN")

        typeField = re.findall("(?:OUT) \w+|(?:IN )\w+", xpathOutput)
        for i in range(len(typeField)):
            inOrOut.append(typeField[i].split(" "))

        print("[ 📫 ] ptype regex 2: " + str(inOrOut))
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
        print("[ 🫡 ] pnamesregex 1 " + str(xpathOutput))
        for i in range(len(inOrOut)):
            if inOrOut[i][1] in xpathOutput:
                print("[ 🤪 ] pnamesregex inoroutloop " + str(inOrOut[i][1]))
                xpathOutput = xpathOutput.replace(inOrOut[i][1], "")
        if "OUT P" or "IN P" in xpathOutput:
            #print("[ ❌❌❌ ] OUT P or IN P found")
            xpathOutput = xpathOutput.replace("OUT P", "OUT")
            xpathOutput = xpathOutput.replace("IN P", "IN")

        xpathOutput = str(xpathOutput)
        print("[ 🤨 ] pnamesregex 2 " + xpathOutput)
        removalChars = [" OPTIONAL", "IN", "OUT", "NTAPI", "NTSYSAPI"]
        for i in range(len(removalChars)):
            xpathOutput = xpathOutput.replace(removalChars[i], "")
        xpathOutput = xpathOutput.replace(")", '    ')
        xpathOutput = xpathOutput.replace(",", '    ')
        print("[ ❌ ] pnamesregex 3 " + xpathOutput)
        xpathOutput = xpathOutput.replace("NTSTATUS", '', 1) # remove first occurence of ntstatus
        print("[ 📘 ] pnamesregex 4 " + xpathOutput)
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

    print("[ ⏹ ] Function Stop\n")

def cleanMSDN(xpathOutput, functionName, xClean):
    functionName2 = functionName.replace("Nt", 'Zw')
    xpathOutput = str(xpathOutput)
    removalChars = [", optional", "in", "out", "NTAPI", "NTSYSAPI", "[", "]", functionName, ")", "(", ";", ",", "'", functionName2]
    for i in range(len(removalChars)):
        xpathOutput = xpathOutput.replace(removalChars[i], "")

    if xClean == 1:
        xpathOutput = xpathOutput.replace("NTSTATUS", '', 1)

    return xpathOutput

def searchUndocumented(wantedFunction):
    #options = webdriver.FirefoxOptions()
    #options.headless = True
    #driver = webdriver.Firefox(options=options)
    driver = webdriver.Firefox()

    url = "http://undocumented.ntinternals.net/"
    driver.get(url)
    #driver.refresh()
    time.sleep(3)
    driver.switch_to.frame("hleftframe")

    driver.switch_to.frame(1) # switch to iframe using index instead of name
    driver.find_element(By.XPATH, "/html/body/table/tbody/tr[2]/td[3]/a/font").click()
    time.sleep(1)
    driver.switch_to.default_content()

    # Submits search on search tab, enters it in the search bar
    searchXpath = "/html/body/form/table/tbody/tr/td[1]/input"
    driver.switch_to.frame("hleftframe")
    driver.switch_to.frame("toc")
    searchingNT = driver.find_element(By.XPATH, searchXpath)
    searchingNT.click()
    searchingNT.send_keys(wantedFunction)
    searchingNT.submit()

    # clicks first option in search bar
    newXpath = "/html/body/form/select/option"
    searchingNT = driver.find_element(By.XPATH, newXpath)
    searchingNT.click()

    optionXpath = "/html/body/div[1]"
    driver.switch_to.default_content()
    driver.switch_to.frame("content")

    time.sleep(2)
    
    try:
        webTitle = driver.find_element(By.XPATH, optionXpath).text
    except: 
        print("[ ⚠ ] Trying alternate route for " + wantedFunction)
        optionXpath = "/html/body/div[2]"
        webTitle = driver.find_element(By.XPATH, optionXpath).text

    while True:
        
        #print(webTitle)

        if webTitle == wantedFunction:
            break
        else:
            for i in range(1, 6):
                driver.switch_to.default_content()
                driver.switch_to.frame("hleftframe")
                driver.switch_to.frame("toc")
                xpathAlt = "/html/body/form/select/option[2]"
                xpathAlt = xpathAlt.replace("2", str(i))
                #print(xpathAlt)
                searchingNT = driver.find_element(By.XPATH, xpathAlt)
                searchingNT.click()
                time.sleep(1)
                driver.switch_to.default_content()
                driver.switch_to.frame("content")

       
                webTitle = driver.find_element(By.XPATH, "/html/body/div[1]").text
                #print(webTitle)
                optionXpath = xpathAlt
                if webTitle == wantedFunction:
                    break

    driver.switch_to.default_content()
    driver.switch_to.frame("content")

    targetXPath = "/html/body/pre"
    html = driver.page_source
    time.sleep(2)

    xpathOutput = driver.find_element(By.XPATH, targetXPath).text
    functionName = driver.find_element(By.XPATH, "/html/body/div[2]").text

    driver.close()

    print(xpathOutput)
    print(functionName)

    return xpathOutput, functionName

def starterOptions():
    print("[ 🔥 ] Welcome to the Nt Function Creator") # Yes, I like using emojis in the my programs
    print("Starting Options")
    print("1. Enter a function name")
    print("2. Enter a URL")
    print("3. Exit")
    print("[ ⌨️ ] Enter your choice: ", end="")
    choice = input()
    return choice


def main():
    loop = 1
    while loop == 1:
        #wantedFunction = "NtAddAtom"
        choice = starterOptions()
        #print("reached")
        #print(choice)
        if choice == "1" or choice == 1:
            #print("reached2")
            print("[ ⏯ ] Enter the function name: ", end="")
            wantedFunction = input()
            xpathOutput, functionName = searchUndocumented(wantedFunction)
            inOrOut = ptypeRegex(xpathOutput, "ntinternals", functionName) # Get ptypes from the xpath output using Regex
            pnames = pnamesRegex(xpathOutput, inOrOut, "ntinternals", functionName)
            printFinishedFunction(inOrOut, pnames, functionName, "ntinternals")

        elif choice == 2 or choice == "2":
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
        
        elif choice == 3 or choice == "3":
            loop = 0
            print("[ ⚠ ] Exiting")
            break

def Originalmain():
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





