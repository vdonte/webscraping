import requests
from requests_html import HTMLSession
import json
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pathlib import Path
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


chrome_options = Options()
#chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

def clickListNext(delay = 3):
    #Next Button
    next_selector = "#salaries_table .pagination > ul > li.page-item.page-next"
    pNextEl = driver.find_element(By.CSS_SELECTOR, next_selector)
    if (pNextEl != None):
        #pNextEl.click()
        driver.execute_script("arguments[0].click();", pNextEl)
        driver.implicitly_wait(delay)


def extractPlayersItems(playersTable):
    tBodyContent = playersTable.find_element(By.TAG_NAME, "tbody")
    tBodtTrs = tBodyContent.find_elements(By.TAG_NAME, "tr")
    pagePlayerItems = []
    if (tBodtTrs != None):
        for playerIdx in np.arange(len(tBodtTrs)):
            thisPlayerItem = {}
            thisTr = tBodtTrs[playerIdx]
            thisPlayerNameEl = thisTr.find_element(By.CSS_SELECTOR, "td.name-column")
            thisPlayerLinkEl = thisPlayerNameEl.find_element(By.CSS_SELECTOR, ".firstcol")

            #playerName #playerLink
            playerName = "None"
            playerLink = "None"
            if (thisPlayerLinkEl != None):
                playerName = thisPlayerLinkEl.text
                playerLink = thisPlayerLinkEl.get_attribute("href")
            else:
                playerName = thisPlayerNameEl.text
                playerLink = "None"

            thisPlayerItem['playerName'] = playerName
            thisPlayerItem['playerLink'] = playerLink    


            thisGPWEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(3)")
            thisGPW = thisGPWEl.text
            thisPlayerItem['grosspw'] = thisGPW   

            thisGPYEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(4)")
            thisGPY = thisGPYEl.text
            thisPlayerItem['grosspy'] = thisGPY 

            thisGPYBEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(5)")
            thisGPYB = thisGPYBEl.text
            thisPlayerItem['grosspybonus'] = thisGPYB 

            thisSignedEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(6)")
            thisSigned = thisSignedEl.text
            thisPlayerItem['signed'] = thisSigned 

            thisSignedExEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(7)")
            thisSignedEx = thisSignedExEl.text
            thisPlayerItem['signedexp'] = thisSignedEx 

            thisSignedReleaseEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(10)")
            thisSignedRelease = thisSignedReleaseEl.text
            thisPlayerItem['signedrelease'] = thisSignedRelease 

            thisAgeEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(14)")
            thisAge = thisAgeEl.text
            thisPlayerItem['age'] = thisAge 

            thisCountryEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(15)")
            thisCountry = thisCountryEl.text
            thisPlayerItem['country'] = thisCountry 

            thisClubEl = thisTr.find_element(By.CSS_SELECTOR, "td:nth-child(16)").find_element(By.CSS_SELECTOR, ".firstcol")
            thisClub = thisClubEl.text
            thisPlayerItem['club'] = thisClub 

            pagePlayerItems.append(thisPlayerItem)
    print(f"{len(pagePlayerItems)} players found")
    return pagePlayerItems


def saveOutputFile(itemsObjs, filename, foldername = "results"):
    parentDir = Path(__file__).absolute().parent
    outputFolderName = f"{parentDir}/{foldername}".replace('\\', '/')
    filename_path = f"{outputFolderName}/{filename}"
    print (f"Creating file {filename_path} ...")

    #Dataframe of the itemObjs
    df1_itemsObjs = pd.DataFrame(itemsObjs)
    print("Dataframe shape:", df1_itemsObjs.shape)

    
    
    #Save output to .csv file
    osHasDir = False
    if os.path.isdir(outputFolderName):
        osHasDir = True
    else:    
        try:
            os.mkdir(outputFolderName)
            osHasDir = True
            
        except FileExistsError:
            osHasDir = False
            print(f"Folder '{outputFolderName}' already exists.")

    if (osHasDir == True) :
        try:
            
            df1_itemsObjs.to_csv(filename_path, index = False)
            print(f"Created {filename_path}")   
        except Exception as e:
            print (f"Could not create files: {e}")

def main(host_url, savetoFile = False):
    
    playerItems = []
    driverLoaded = False
    url = host_url
    totalPages = 0
    pageLimit = 5
    try:
        
        driver.get(url)
        driverLoaded = True
    except Exception as e:
        print("Connection failed!")

    if (driverLoaded == True):
        # Allow the page to fully 
        #driver.implicitly_wait(5)
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#salaries_table #table")))
        playersTable = driver.find_element(By.CSS_SELECTOR, "#salaries_table #table")
        paginationEl = driver.find_element(By.CSS_SELECTOR, "#salaries_table .pagination")


        if (playersTable != None):
            if (paginationEl != None):
                driver.implicitly_wait(3)
                paginationElItems = paginationEl.find_elements(By.CSS_SELECTOR, "#salaries_table .pagination .page-item")
                totalPages = int(paginationElItems[-2].text)
                pageLimit = totalPages

            if (totalPages > 0):
                print(f"{totalPages} pages fouund. Extraction in progress...")
                for idx in np.arange(pageLimit):
                    pageNumber = idx + 1
                    print(f"Extracting Page {pageNumber}")
                    if (pageNumber > 1) :
                        clickListNext()
                    playerItems.extend(extractPlayersItems(playersTable))
                    
                    time.sleep(3)

        driver.quit()
        if savetoFile != False: saveOutputFile(playerItems, savetoFile)
        print(f"Extraction completed!")
        print("Total players found", len(playerItems))

main("https://www.capology.com/uk/premier-league/salaries/", "premier_league.csv")
