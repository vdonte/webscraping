from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pathlib import Path
import os

#Start session
session = HTMLSession()

initObj = None
pagesCount = None
categoryTitle = None
categoryFileName = None
categoryUrl = None
pagesScraped = 0
itemsObjs = []
page_url_obj = {}
pageLinks = []
parentDir = None
outputFolderName = None

def initPage(page_url, categoryName):
    #load url
    host_url = page_url
    response = session.get(host_url)

    #get the page title
    page_title = response.html.find('title', first=True).text
    print ("Page Loaded - ", page_title)

    pagesListContainer = response.html.xpath('//*[@id="jm"]/main/div[2]/div[3]/section/div[3]', first=True)
    pageListSoup = BeautifulSoup(pagesListContainer.html, 'html.parser')
    pageListSoupItem = pageListSoup.find_all(class_ = "pg")
    pagesCount = int(pageListSoupItem[-1]['href'].split("#")[0].split("=")[1])
    print("Total Pages", pagesCount)
    
    categoryTitle = categoryName.replace("-", " ").title()
    outputFileName = categoryName.replace("-", "_")

    #The host category url
    host_category_url = f"{host_url}/{categoryName}"

    initObj = {}
    initObj['categoryTitle'] = categoryTitle
    initObj['categoryFileName'] = outputFileName
    initObj['categoryUrl'] = host_category_url
    initObj['pagesCount'] = pagesCount
    return initObj    

def loadPageItems(page_url):
    try:
        #load url
        url = page_url
        response = session.get(url)

        #render the page based on the url
        response.html.render(sleep = 1) #sleep = 1 for javascript pages

        

        itemsContainer = response.html.xpath('//*[@id="jm"]/main/div[2]/div[3]', first=True)
        itemsSoup = BeautifulSoup(itemsContainer.html, 'html.parser')

        itemSections = itemsSoup.find(class_="-pvs col12").find("div", class_="-phs -pvxs row _no-g _4cl-3cm-shs")

        #get the itemsList
        itemsList = itemSections.find_all("article")
        return itemsList
    except:
        print("Items not Loaded!")
        return []
    

def loadItem(itemsList, categoryTitle):
    #the array that contains all objects
    thisItemsObjs = []

    #loop through the item list
    for thisItem in itemsList:
        #This thisItem Link
        thisItem_link = thisItem.find("a", class_="core")['href']

        #This thisItem img
        thisItem_img = thisItem.find("div", class_="img-c").find("img", class_="img")['data-src']

        #This thisItem name
        thisItem_name = thisItem.find("div", class_="info").find("h3", class_="name").text.strip()

        #This thisItem price
        thisItem_price = thisItem.find("div", class_="info").find("div", class_="prc").text.split(" ")

        #This thisItem rating
        thisItem_rating = thisItem.find("div", class_="info").find("div", class_="rev").find("div", class_="stars _s").text if (thisItem.find("div", class_="info").find("div", class_="rev")) else "No Rating"

        #Setting up this ItemObj dict
        thisItemObj = {
            "name": f"{thisItem_name}",
            "price": f"{thisItem_price[1]}".replace(",", ""),
            "currency": "NGN" if (thisItem_price[0].strip() == "₦") else "NGN",
            "rating": f"{thisItem_rating}".split(" out of ")[0],
            "link": f"{categoryUrl}{thisItem_link}",
            "img": f"{thisItem_img}", 
            "categpry": f"{categoryTitle}"
        }
        # Append the dict to the thisItemsObjs list
        thisItemsObjs.append(thisItemObj)
    
    #return thisItemsObjs list
    return(thisItemsObjs)

def saveOutputFile():
    #Dataframe of the list of pageLinks extracted from
    df1_pageLinks = pd.DataFrame(pageLinks)


    #Dataframe of the itemObjs
    df1_itemsObjs = pd.DataFrame(itemsObjs)
    df1_itemsObjs = df1_itemsObjs[['name', 'price', 'categpry', 'currency', 'rating', 'img', 'link']]


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
            print ("Creating files...")
            if (df1_pageLinks is not False): 
                df1_pageLinks.to_csv(f"{outputFolderName}/{categoryFileName}_pagelinks.csv", index = False)
                print(f"Created {categoryFileName}_pagelinks.csv")
            if (df1_pageLinks is not False): 
                df1_itemsObjs.to_csv(f"{outputFolderName}/{categoryFileName}.csv", index = False)
                print(f"Created {categoryFileName}.csv")
        except:
            print ("Could not create files")




def main(host_url, categoryName):
    global initObj
    global pagesCount
    global categoryTitle
    global categoryFileName
    global categoryUrl
    global pagesScraped
    global itemsObjs
    global page_url_obj
    global pageLinks
    global parentDir
    global outputFolderName
    try:
        initObj = initPage(f"{host_url}{categoryName}", categoryName)
        pagesCount = initObj['pagesCount']
        categoryTitle = initObj['categoryTitle']
        categoryFileName = initObj['categoryFileName']
        categoryUrl = initObj['categoryUrl']
        pagesScraped = 0
        itemsObjs = []
        page_url_obj = {}
        pageLinks = []
        parentDir = Path(__file__).resolve().parent
        outputFolderName = f"{parentDir}/{categoryFileName}"
    except:
        print ("Page Not Loaded!")

    if (pagesCount > 0) :
        print("Scraping in progress, Please wait...")
        for i in np.arange(pagesCount):
            #Load first page
            page_url = f"{categoryUrl}{f'?page={i+1}' if (i>0 & i<pagesCount) else ""}"
            pageItemsList = loadPageItems(page_url)
            thisPageItemsObjs = loadItem(pageItemsList, categoryName)
            itemsObjs.extend(thisPageItemsObjs)
            pagesScraped += 1
            pagesScraped100 = int((pagesScraped/pagesCount) * 100)
            
            # THe page url obj
            page_url_obj['page_url'] = page_url
            page_url_obj['items_found'] = len(pageItemsList)

            #Append the page url obj to the global pageLinks
            pageLinks.append(page_url_obj)
            print(f"{pagesScraped100}% Completed", "Total Pages Scraped", f"{pagesScraped} of {pagesCount}", "Total Items Found", len(itemsObjs))

        if (pagesScraped == pagesCount):
            pagesScraped100 = int((pagesScraped/pagesCount) * 100)
            print(f"Scraping {pagesScraped100}% Completed!")
            print("Total Pages Scraped", pagesScraped, "Total Items Found", len(itemsObjs))
            saveOutputFile()
            session.close()

#Run Application
main("https://www.jumia.com.ng/", "beverages")
    







