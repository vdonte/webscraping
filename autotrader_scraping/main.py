from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pathlib import Path
from rich import print
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
import time

chrome_options = Options()
# chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
base_url = "https://www.autotrader.co.uk/cars/dealers/search?advertising-locations=at_cars&dealerName=&forSale=on&make=&model=&page=1&postcode=CH44%208DF&radius=1501&refresh=true&sort=with-retailer-reviews&toOrder=on&utm_source=chatgpt.com"
outputfilename = "car_dealers_dataset.csv"
collectionItems = []
totalPages = 0
pageLimit = 5
currentPage = 0




def extractPaginationSection(topPagSection):
    topPageSoup = BeautifulSoup(topPagSection.get_attribute('innerHTML'), 'html.parser')
    topPageSoupContainer = topPageSoup.find_all("div", recursive=False)
    paginationObj = False
    
    if topPageSoupContainer != None:
        pagNextButton = topPageSoupContainer[0].find(attrs={"data-testid": "pagination-next"})
        pagNextButtonLink = pagNextButton["href"] if pagNextButton != None else None
        
        pagPreviousButton = topPageSoupContainer[0].find(attrs={"data-testid": "pagination-previous"})
        pagPreviousButtonLink = pagPreviousButton["href"] if pagPreviousButton != None else None
        
        pageInfoContent = topPageSoupContainer[0].find(attrs={"data-testid": "pagination-show"}, string=True).contents[0].replace("Page", "").strip().split("of") if topPageSoupContainer[0].find(attrs={"data-testid": "pagination-show"}, string=True) != None else None
        currentPageContent = int(pageInfoContent[0].replace(",", "").strip(" ")) if pageInfoContent != None else None
        totalPagesContent = int(pageInfoContent[1].replace(",", "").strip(" ")) if pageInfoContent != None else None

        paginationObj = {
            "previousLink": f"https://www.autotrader.co.uk/cars/dealers/search{pagPreviousButtonLink}" if pagPreviousButtonLink != None else None,
            "nextLink": f"https://www.autotrader.co.uk/cars/dealers/search{pagNextButtonLink}" if pagNextButtonLink != None else None,
            "currentPage": currentPageContent,
            "totalPages": totalPagesContent,
        }
        
    return paginationObj

def extractPageItemInfo(pageItemSection: BeautifulSoup):

    try:
        pageItemName = pageItemSection.find("div", recursive=False).find("header").find("h3").find("a").get_text()
        pageItemLink = pageItemSection.find("div", recursive=False).find("header").find("h3").find("a")['href']
        pageItemLink = f"https://www.autotrader.co.uk{pageItemLink}"
        
        thisItemObj = {}
        thisItemObj['name'] = pageItemName
        original_window = driver.current_window_handle
        driver.switch_to.new_window('tab')
        print(f"Retrieving '{pageItemName}' details...")
        driver.get(pageItemLink)
        time.sleep(1)
        pageContentSection = driver.find_element(By.CSS_SELECTOR, "#content > section.sc-il8olq-0.bbRXaL")
        pageContentSectionSoup = BeautifulSoup(pageContentSection.get_attribute('innerHTML'), 'html.parser') if pageContentSection != None else None
        pageContentSectionContainer = pageContentSectionSoup.find("div", recursive=False)

        

        if pageContentSectionContainer != None:
            pageContentInfoSection1 = pageContentSectionContainer.find_all("div", recursive=False)[1] if pageContentSectionContainer.find_all("div", recursive=False) != None else None
            if pageContentInfoSection1 != None:
                pageContentInfoFullName = pageContentInfoSection1.find_all("div", recursive=False)[1].find_all("div", recursive=False)[0].find("h1", recursive=False).get_text() if pageContentInfoSection1.find_all("div", recursive=False)[1] != None else None
                thisItemObj['fullname'] = pageContentInfoFullName

                pageContentInfoRating = pageContentInfoSection1.find_all("div", recursive=False)[1].find_all("div", recursive=False)[1].find("div", recursive=False).find_all("div", recursive=False)[0].find("p", recursive=False).get_text() if pageContentInfoSection1.find_all("div", recursive=False)[1] != None else None
                thisItemObj['rating'] = pageContentInfoRating

                pageContentInfoDescription = pageContentInfoSection1.find_all("div", recursive=False)[2].find_all("div", recursive=False) if pageContentInfoSection1.find_all("div", recursive=False)[2] != None else None
                pageContentInfoDescriptionText = ""
                if pageContentInfoDescription != None:
                    for i in pageContentInfoDescription:
                        pageContentInfoDescriptionText = pageContentInfoDescriptionText + (", " if pageContentInfoDescriptionText != "" else "") + i.get_text()

                thisItemObj['description'] = pageContentInfoDescriptionText

        pageContentContact = driver.find_elements(By.CSS_SELECTOR, "#content > *")[4]
        pageContentContactSoup = BeautifulSoup(pageContentContact.get_attribute('innerHTML'), 'html.parser') if pageContentContact != None else None
        pageContentContactContainer = pageContentContactSoup.find("div", recursive=False)

        if pageContentContactContainer != None:
            contactSections = pageContentContactContainer.find_all(recursive=False)[1].find_all(recursive=False)
            
            thisContactInfoObj = {}
            thisContactInfoObj['address'] = ""
            openingHours = None
            for thisIdx in np.arange(len(contactSections)):
                thisContactSection = contactSections[thisIdx]
                thisContactSectionChildren = thisContactSection.find_all(recursive=False)
                if thisContactSectionChildren != None:
                    
                    thisContactIsAddress = "Address" in thisContactSectionChildren[0].get_text()
                    thisContactIsOpening = "Opening hours" in thisContactSectionChildren[0].get_text()

                    if (thisContactIsAddress):
                        thisContactLis = thisContactSectionChildren[1].find_all(recursive=False)
                        for thisLi in thisContactLis:
                            thisLisText = thisLi.get_text()
                            if thisLisText != None or thisLisText != "":
                                thisContactInfoObj['address'] = thisContactInfoObj['address'] + (", " if thisContactInfoObj['address'] != "" else "") + thisLi.get_text()
                    elif thisContactIsOpening:
                        False
                    else:
                        
                        # thisContactInfos = thisContactSectionChildren[0].find_all(recursive=False)
                        # print(thisContactInfos)
                        for thisContactInfo in thisContactSectionChildren:
                            
                            thisContactInfoTitle = thisContactInfo.find_all(recursive=False)[0].get_text()
                            thisContactInfoName = thisContactInfoTitle.replace(" ", "_").lower()
                            thisContactInfoValue = thisContactInfo.find_all(recursive=False)[1].get_text()
                            thisContactInfoLink = False
                            if thisContactInfoValue == "website":
                                thisContactInfoLink = thisContactInfo.find_all(recursive=False)[1]['href'] if thisContactInfo.find_all(recursive=False)[1].attrs['href'] != None else None

                            thisContactInfoLink = False
                            
                            thisContactInfoObj[thisContactInfoTitle] = thisContactInfoValue
                            if thisContactInfoLink != False: thisContactInfoObj[thisContactInfoName]['link'] = thisContactInfoLink
                                            
            thisItemObj.update(thisContactInfoObj)
                        
                        

                        

                    

        thisItemObj['link'] = pageItemLink    
        driver.close()
        driver.switch_to.window(original_window)
    except Exception as e:
        print(f"Extraction Error - {e}")
        driver.close()
        driver.switch_to.window(original_window)
    return thisItemObj

def extractPageItems(pageItemsSection, currentPage):
    global collectionItems
    global outputfilename
    currentPageItems = []
    
    print(f"Collecting information from Page {currentPage}...")
    pageItemsSectionSoup = BeautifulSoup(pageItemsSection.get_attribute('outerHTML'), 'html.parser')
    #print(pageItemsSectionSoup)
    pageItemUl = pageItemsSectionSoup.find("ul")
    pageItemLis = pageItemUl.find_all("li", recursive=False) if pageItemUl != None else None

    if pageItemLis != None:
        for thisItemLi in pageItemLis:
            thisItemObj = extractPageItemInfo(thisItemLi)
            currentPageItems.append(thisItemObj)
    # print(currentPageItems)
    print(f"Total of {len(currentPageItems)} items found in this page")
    
    return currentPageItems
    
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
            print(f"Saved to file {filename_path}")   
        except Exception as e:
            print (f"Could not create files: {e}")
    print("\n")

def displaySummary():
    global currentPage
    global collectionItems

    print(f"Total pages: {currentPage}")
    print(f"Total items found: {len(collectionItems)}")

def robotCheckPass(base_url):
    loadBasePage(base_url)

def loadBasePage(base_url):
    global collectionItems
    global currentPage
    global totalPages
    global pageLimit

    driver.get(base_url)
    previousLink = None
    nextLink = None

    #Check for the record list elements and the pagination element
    recordSectionSl = "#content > div > article > div.sc-1mgwvar-8.bIaa-Dh"
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, recordSectionSl)))
    recordSectionEl = driver.find_element(By.CSS_SELECTOR, recordSectionSl)


    if (recordSectionEl != None):
        #topPagination
        time.sleep(2)
        allChildren = driver.find_elements(By.CSS_SELECTOR, "#content > div > article > div.sc-1mgwvar-8.bIaa-Dh > *")
        topPag = extractPaginationSection(allChildren[0])
        
        currentPage = topPag['currentPage']
        totalPages = topPag['totalPages']
        previousLink = topPag['previousLink']
        nextLink = topPag['nextLink']
        pageLimit = totalPages
        pageLimit = 100

         #Extract CollectionItems
        extractedPageItems = extractPageItems(allChildren[1], currentPage)
        collectionItems.extend(extractedPageItems)
        saveOutputFile(collectionItems, outputfilename)
        
        # End of the pages
        if currentPage == pageLimit: 
            driver.quit()
            displaySummary()
            if outputfilename != None:
                saveOutputFile(collectionItems, outputfilename)
        else:
            if nextLink != None: loadBasePage(nextLink)
    else:
        page_title = driver.title

        if page_title == "Just a moment...":
            
            robotCheckPSl = "#GFpwk5" #Verify you are human by completsing the action below.
            robotCheckPEl = driver.find_element(By.CSS_SELECTOR, robotCheckPSl)

            robotCheckBoxSl = "#TktRY1"
            robotCheckBoxEl = driver.find_element(By.CSS_SELECTOR, robotCheckBoxSl)
            
            robotCheckPass(base_url)

            if robotCheckPEl != None and robotCheckBoxEl != None:
                time.sleep(2)
            else: driver.quit()
        else: driver.quit()

def main():
    
    try:
       loadBasePage(base_url)
    except Exception as e:
        print(f"Connection failed! - {e}")
        
main()
