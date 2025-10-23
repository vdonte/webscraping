from playwright.sync_api import sync_playwright, Playwright
from rich import print
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pathlib import Path
import os
import time

base_url = "https://sofifa.com"
playerObjs = []

def saveOutputFile(itemsObjs, filename, foldername = "results"):
    parentDir = Path(__file__).absolute().parent
    outputFolderName = f"{parentDir}/{foldername}".replace('\\', '/')
    filename_path = f"{outputFolderName}/{filename}"
    print (f"Writing to file {filename_path} ...")

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



def run(playwright: Playwright):
    #https://sofifa.com/players?col=oa&sort=desc&offset=0
    start_url = f"{base_url}/players?col=oa&sort=desc&offset=0"
    chrome = playwright.chromium
    browser = chrome.launch(headless=False)
    page = browser.new_page()
    page.goto(start_url, wait_until='domcontentloaded')
    outputFilename = "player_dataset.csv"
    pageNumber = 1
    itemsLimit = 100
    #Locating the player record selector


    def extractPlayerInfo(thisPlayerName, thisPlayerLink):
        try:
            print(f"{len(playerObjs)+1}. Retrieving '{thisPlayerName}' details...")

            playerPage = browser.new_page(base_url = base_url)
            playerPage.goto (thisPlayerLink, wait_until='domcontentloaded')
            
            playerDetailsElSelector = "#body > main:nth-child(5) > article"
            playerPage.wait_for_selector(playerDetailsElSelector)
            playerDetailsSelector = playerPage.locator(playerDetailsElSelector)
            playerDetails = BeautifulSoup(playerDetailsSelector.inner_html(), 'html.parser')


            thisPlayerObj = {}
            thisPlayerObj['name'] = ""
            thisPlayerObj['fullname'] = ""
            thisPlayerObj['playerData'] = ""
            thisPlayerObj['playerPos'] = ""
            thisPlayerObj['playerCountry'] = ""
            thisPlayerObj['overallRating'] = ""
            thisPlayerObj['potential'] = ""
            thisPlayerObj['playerValue'] = ""
            thisPlayerObj['playerWage'] = ""
            thisPlayerObj['preferedFoot'] = ""
            thisPlayerObj['releaseClause'] = ""
            thisPlayerObj['clubName'] = ""
            thisPlayerObj['league'] = ""
            thisPlayerObj['clubKitNumber'] = ""
            thisPlayerObj['contractStart'] = ""
            thisPlayerObj['contractEnd'] = ""
            thisPlayerObj['nationalTeam'] = ""
            thisPlayerObj['countryKitNumber'] = ""
            thisPlayerObj['profileImg'] = ""
            thisPlayerObj['playerLink'] = ""


            playerProfileEl = playerDetails.find(class_ = "profile")
            playerProfileFullName = playerProfileEl.find("h1")
            playerProfileData = playerProfileEl.find("p").decode_contents().split("<br/>")[1]
            playerProfileData = playerProfileData.replace("y.o.", "").replace(",", "").replace("(", "").replace(")", "")
            playerCountry = playerProfileEl.find("p").find('a').attrs['title']
            playerPosEl = playerProfileEl.find("p").find_all('span')
            playerPos = ""
            for thisPlayerPosEl in playerPosEl: playerPos = playerPos + thisPlayerPosEl.get_text() + " "
            profileImg = playerProfileEl.find("img").attrs['data-srcset'].split(", ")[1].split(" ")[0]
            
            thisPlayerObj['name'] = thisPlayerName
            thisPlayerObj['fullname'] = playerProfileFullName.get_text()
            thisPlayerObj['playerData'] = playerProfileData.split(" ")
            thisPlayerObj['playerPos'] = playerPos.strip()
            thisPlayerObj['playerCountry'] = playerCountry

            if playerDetails.find_all("div", class_ = "grid")[0]:
                playerDataGrid0 = playerDetails.find_all("div", class_ = "grid")[0]
                overallRating = playerDataGrid0.find_all("div", class_="col")[0].find("em").get_text()
                potential = playerDataGrid0.find_all("div", class_="col")[1].find("em").get_text()
                playerValue = playerDataGrid0.find_all("div", class_="col")[2].find("em").get_text()
                playerWage = playerDataGrid0.find_all("div", class_="col")[3].find("em").get_text()

                thisPlayerObj['overallRating'] = overallRating
                thisPlayerObj['potential'] = potential
                thisPlayerObj['playerValue'] = playerValue
                thisPlayerObj['playerWage'] = playerWage

            if playerDetails.find_all("div", class_ = "grid")[1]:
                playerDataGrid1 = playerDetails.find_all("div", class_ = "grid")[1]

                #Profile
                if playerDataGrid1.find_all("div", class_="col")[0] != None:
                    if len(playerDataGrid1.find_all("div", class_="col")[0].find_all("p")) > 0:
                        preferedFoot = playerDataGrid1.find_all("div", class_="col")[0].find_all("p")[0].get_text().replace("Preferred foot", "").strip() if playerDataGrid1.find_all("div", class_="col")[0].find_all("p")[0] != None else ""
                        releaseClause = playerDataGrid1.find_all("div", class_="col")[0].find_all("p")[6].get_text().replace("Release clause", "").strip() if playerDataGrid1.find_all("div", class_="col")[0].find_all("p")[6] != None else ""
                        thisPlayerObj['preferedFoot'] = preferedFoot
                        thisPlayerObj['releaseClause'] = releaseClause

                #Club
                if playerDataGrid1.find_all("div", class_="col")[2] != None:
                    sectionName = playerDataGrid1.find_all("div", class_="col")[2].find("h5").get_text() if playerDataGrid1.find_all("div", class_="col")[2].find("h5") != None else False
                    clubTeamSection = playerDataGrid1.find_all("div", class_="col")[2] if sectionName == "Club" else playerDataGrid1.find_all("div", class_="col")[3]
                    if clubTeamSection != None:
                        if len(clubTeamSection.find_all("p")) > 0:
                            clubName = clubTeamSection.find_all("p")[0].find("a").get_text().strip() if clubTeamSection.find_all("p")[0] != None else ""
                            league = clubTeamSection.find_all("p")[1].find("a").get_text().strip() if clubTeamSection.find_all("p")[1] != None else ""
                            clubKitNumber = clubTeamSection.find_all("p")[4].get_text().replace("Kit number", "").strip() if clubTeamSection.find_all("p")[4] != None else ""
                            contractStart = clubTeamSection.find_all("p")[5].get_text().replace("Joined", "").strip() if clubTeamSection.find_all("p")[5] != None else ""
                            contractEnd = clubTeamSection.find_all("p")[6].get_text().replace("Contract valid until", "").strip() if clubTeamSection.find_all("p")[6] != None else ""

                            thisPlayerObj['clubName'] = clubName
                            thisPlayerObj['league'] = league
                            thisPlayerObj['clubKitNumber'] = clubKitNumber
                            thisPlayerObj['contractStart'] = contractStart
                            thisPlayerObj['contractEnd'] = contractEnd

                #Nation
                if playerDataGrid1.find_all("div", class_="col")[3] != None:
                    sectionName = playerDataGrid1.find_all("div", class_="col")[3].find("h5").get_text() if playerDataGrid1.find_all("div", class_="col")[3].find("h5") != None else False
                    natTeamSection = playerDataGrid1.find_all("div", class_="col")[3] if sectionName == "National team" else playerDataGrid1.find_all("div", class_="col")[2]
                    if natTeamSection != None:
                        if len(natTeamSection.find_all("p")) > 0:
                            nationalTeam = natTeamSection.find_all("p")[0].find("a").get_text().strip() if natTeamSection.find_all("p")[0] != None else ""
                            nationalTeamKitNumber = natTeamSection.find_all("p")[4].get_text().replace("Kit number", "").strip() if natTeamSection.find_all("p")[4] != None else ""
                            thisPlayerObj['nationalTeam'] = nationalTeam
                            thisPlayerObj['countryKitNumber'] = nationalTeamKitNumber

            

            
            thisPlayerObj['profileImg'] = profileImg
            thisPlayerObj['playerLink'] = thisPlayerLink


            playerPage.close()
        except:
            playerPage.close()

        return thisPlayerObj
        


    
    
    while True:
        time.sleep(1)
        if len(playerObjs) > 0: saveOutputFile(playerObjs, outputFilename)
        print(f"Scanning Page {pageNumber}")
        endOfOperation = False
        tr_selector = "body > main > article > table > tbody > tr"
        page.wait_for_selector(tr_selector)
        playerRecords = page.locator(tr_selector).all()

        if (playerRecords is not None):
            for playerRecord in playerRecords:
                thisPlayerRecord = playerRecord
                thisPlayerData = thisPlayerRecord.locator("td").all()
                thisPlayerLinkEl = thisPlayerData[1].locator("a").nth(0)
                thisPlayerLink = thisPlayerLinkEl.get_attribute("href")
                thisPlayerName = thisPlayerLinkEl.inner_text()
                thisPlayerObj = extractPlayerInfo(thisPlayerName, thisPlayerLink)

                print(thisPlayerObj)
                playerObjs.append(thisPlayerObj)
                #print(thisPlayerObj)

        
                
        if endOfOperation == True:
            print(f"Total Players Added: {len(playerObjs)}")
            if len(playerObjs) > 0: saveOutputFile(playerObjs, outputFilename)
            page.close()
            return False
        else:
            #Check for next locator
            paginationSelector = "#body > main > article > div.pagination"
            page.wait_for_selector(paginationSelector)
            paginationLocator = page.locator(paginationSelector)
            pageinationLastButton = paginationLocator.locator("a").last

            if (pageinationLastButton is not None):
                buttonName = pageinationLastButton.inner_text().strip().lower()
                print(buttonName)

                if (buttonName == "next"):
                    buttonLink = f"{base_url}{pageinationLastButton.get_attribute("href")}"
                    page.goto(buttonLink)
                    pageNumber = pageNumber + 1
                    
                else:
                    endOfOperation = True
        
        
        

    

with sync_playwright() as playwright:
    try:
        run(playwright)
    except:
        print("Connection Error!")
