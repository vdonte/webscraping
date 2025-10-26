import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from pypdf import PdfReader
from pypdf import PdfWriter
from pathlib import Path

#Resume PDF Parser
# Receives a resume file in pdf and parses the content of the pdf file

#setting up usefuk paths
parentDir = str(Path(__file__).absolute().parent).replace("\\", "/")
pdf_folder = "pdf_files"
pdf_filename = "resume.pdf"
pdf_path = (f"{parentDir}/{pdf_folder}/{pdf_filename}")
#Load the PDF reader
pdf_reader = PdfReader(pdf_path)

def getFileInfo(printInfoSummary = False):
    
    if (pdf_reader == None):
        pdf_fileInfo = False
    else:
        pdf_fileInfo = {}
        #PDF file metadata
        pdf_reader_metadata = pdf_reader.metadata
        metadata_author = pdf_reader_metadata.author
        pdf_fileInfo['author'] = metadata_author

        metadata_creationdate = pdf_reader_metadata['/CreationDate']
        pdf_fileInfo['creationdate'] = metadata_creationdate

        metadata_creator = pdf_reader_metadata.creator
        pdf_fileInfo['creator'] = metadata_creator

        metadata_keywords = pdf_reader_metadata.keywords
        pdf_fileInfo['keywords'] = metadata_keywords

        metadata_moddate = pdf_reader_metadata['/ModDate']
        pdf_fileInfo['moddate'] = metadata_moddate

        metadata_producer = pdf_reader_metadata.producer
        pdf_fileInfo['producer'] = metadata_producer

        metadata_subject = pdf_reader_metadata.subject
        pdf_fileInfo['subject'] = metadata_subject

        metadata_title = pdf_reader_metadata.title
        pdf_fileInfo['title'] = metadata_title

        total_pages = len(pdf_reader.pages)
        pdf_fileInfo['total_pages'] = total_pages

        infoSummary = f"""Author: {metadata_author}\nCreationDate: {metadata_creationdate}\nCreator: {metadata_creator}\nKeywords: {metadata_keywords}\nModDate: {metadata_moddate}\nProducer: {metadata_producer}\nSubject: {metadata_subject}\nTitle: {metadata_title}\nTotal Pages: {total_pages}"""

        pdf_fileInfo['info_summary'] = infoSummary
        if (printInfoSummary == True): print(infoSummary)
    
    return pdf_fileInfo

def parsePDF():
    pageObj = []
    pageContent = []
    contentItems = []
    pageContentObj = {}
    totalPages = getFileInfo()['total_pages']

    for thisPage in range(totalPages):
        thisContent = pdf_reader.pages[thisPage].extract_text().split("\n \n")
        
        pageObj.append(thisContent)
        contentItems = contentItems + thisContent
        
    for idxContentItem in range(len(contentItems)):
        thisContentItem = False
        if (idxContentItem > 0) :
            thisContentItem = contentItems[idxContentItem].strip(" ").split("\n", 1)
            if (thisContentItem[0] == "") :
                thisContentItem = thisContentItem[1].split("\n", 1)
        else:
            thisContentItem = contentItems[idxContentItem].strip(" ")
        pageContent.append(thisContentItem)

    for idxPageContent in range(len(pageContent)):
        thisPageContent = pageContent[idxPageContent]
        if (idxPageContent > 0) :
            access_name = thisPageContent[0].strip(" ").lower().replace(" ", "_")
            title_name = thisPageContent[0].strip(" ")
            pageContentObj[access_name] = {}
            pageContentObj[access_name]['title'] = title_name
            pageContentObj[access_name]['content'] = thisPageContent[1]
        else:
            access_name = "intro"
            title_name = thisPageContent[0].strip(" ")
            pageContentItem = thisPageContent.strip(" ").split("\n")
            pageContentObj[access_name] = {}
            pageContentObj[access_name]['title'] = pageContentItem[0]
            pageContentObj[access_name]['content'] = ["{}".format(x.strip(" ")) for x in pageContentItem[1:]]
    
    return pageContentObj


pdf_parse = parsePDF()
pdf_parse_keys = pdf_parse.keys()

for ikey in pdf_parse_keys:
    if (pdf_parse[ikey]['title'] != None):
        print(f"{pdf_parse[ikey]['title']}:", pdf_parse[ikey]['content'])





