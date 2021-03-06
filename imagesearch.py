# -*- coding: utf-8 -*-
"""ImageSearch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Cy9-hAyfcQHydEa8sdq1CVGPeFQnyvJD
"""

# Import all packages, give prompt to pip install any needed packages.

try:
    import sys
    import os
    import glob
    import requests
    import webbrowser
    from selenium import webdriver
    from PIL import Image
    from PIL.ExifTags import TAGS
    from PIL.ExifTags import GPSTAGS
    
except:
    print("Not all Python dependencies have been installed on this computer.")
    
    try:
        import os
    except:
        question = input("os is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            !{sys.executable} -m pip install os
        else:
            print('Program terminated, os needed for operation of program.')
            raise SystemExit

    try:
        import glob
    except:
        question = input("glob is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            !{sys.executable} -m pip install glob
        else:
            print('Program terminated, glob needed for operation of program.')
            sys.exit(1)
                
    try:
        import requests
    except:
        question = input("requests is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            !{sys.executable} -m pip install requests
        else:
            print('Program terminated, requests needed for operation of program.')
            sys.exit(1)
                
    try:
        import webbrowser
    except:
        question = input("webbrowser is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            !{sys.executable} -m pip install webbrowser
        else:
            print('Program terminated, webbrowser needed for operation of program.')
            sys.exit(1)
    
    try:
        from selenium import webdriver

    except:
        question = input("selenium is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            !{sys.executable} -m pip install selenium
        else:
            print('Program terminated, selenium needed for operation of program.')
            sys.exit(1)

    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        from PIL.ExifTags import GPSTAGS
    except:
        question = input("PIL is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            !{sys.executable} -m pip install PIL
        else:
            print('Program terminated, PIL needed for operation of program.')
            sys.exit(1)

# find location of chromedriver, or prompt user to install
try:
    __file__ = 'chromedriver'
    chrome_path = os.path.dirname(os.path.realpath(__file__)) +'/'+str(__file__)
except:
    try:
        __file__ = 'chromedriver.exe'
        chrome_path = os.path.dirname(os.path.realpath(__file__))+'/'+str(__file__)
    except:
        raise Exception("""Error: Please install Google Chrome and Chromedriver.
                         See: https://chromedriver.chromium.org/downloads
                         for further details.""")
print(chrome_path)
print("Chromedriver successfully located")

from os import listdir
from os.path import isfile, join

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

def get_exif(filename):
    '''
    Function to get exif data from image.
    '''
    image = Image.open(filename)
    image.verify()
    return image._getexif()

def get_labeled_exif(exif):
    '''
    Converts exit data to labelled exif data.
    '''
    labeled = {}
    if not exif:
        print("No EXIF metadata found")
        return
    
    for (key, val) in exif.items():
        labeled[TAGS.get(key)] = val
    return labeled

def get_geotagging(exif):
    if not exif:
        print("No EXIF metadata found")
        return
    
    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                print("No EXIF geotagging found")
                return
                
            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]

    return geotagging

def get_decimal_from_dms(dms, ref):
    '''
    Function to convert from dms (degrees, minutes, seconds) to decimal.
    '''
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)

def get_coordinates(geotags):
    '''
    Function to return the latitude and longitude for where an image was taken,
    given the geotag input.
    '''
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
    return (lat,lon)

# user input of directory of images.
folderPath = input('Please enter the filepath of the directory.\n') # Tell them to drag directory to textbox

# format the filepath string to find all images contained in file.
#if folderPath[-1] != '/' and folderPath[-1] != '*':
#    folderPath += '/*'
#elif folderPath[-1] == '/':
#    folderPath += '*'
    
# format the filepath string when inputted in a common incorrect format
# (from dragging file to input box in Ubuntu).
if 'file://' in folderPath:
    folderPath = folderPath.replace('file://','')
    
#filePathList = glob.glob(folderPath)
filePathList = get_filepaths(folderPath)

if not filePathList:
    raise Exception("Error: Folder is empty or doesn't exist. Check that the correct directory has been inputted.")

print(filePathList)

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert 
import time

urlList = []

for i in range(len(filePathList)):
    
    # reverse image search
    filePath = filePathList[i]
    searchUrl = 'http://www.google.com/searchbyimage/upload'
    multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
    response = requests.post(searchUrl, files=multipart, allow_redirects=False)
    fetchUrl = response.headers['Location']
    #webbrowser.open(fetchUrl)
    urlList.append(fetchUrl)
    
    # Hides selenium window
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    
    # click on link to show similar images
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(fetchUrl)
    time.sleep(3)
    
    # Continue past pop-ups
    # if EC.alert_is_present():
        # alert = driver.switch_to.alert
        # alert.accept()
    
    driver.add_cookie({"name": "key", "value": "value"})
    driver.find_element_by_xpath("""//*[@id="Z6bGOb"]/a""").click()
    
    elems = driver.find_elements_by_xpath("//a[@class='VFACy kGQAp sMi44c lNHeqe WGvvNb']") 
    
    print('imagename = ', os.path.basename(filePathList[i]))
    print('filepath =', filePathList[i], '\n')

    if len(elems) > 1:
        print(len(elems), 'URL links returned from Google Image Search\n')
        for elem in elems:
            print(elem.get_attribute("href"))
    elif len(elems) == 1:
        print(len(elems), 'URL link returned from Google Image Search\n')
        print(elems.get_attribute("href"))
    elif not elems:
        print('No URL links returned from Google Image Search\n')

    driver.close()
    
    
    exif = get_exif(filePathList[i])
    labeled = get_labeled_exif(exif)
    geotags = get_geotagging(exif)
    print(labeled, '\n')
    
    try:
        print('Lat, Long = ', get_coordinates(geotags), '\n')
    except:
        print('No coordinates found from exif data analysis.\n')
    print('---------------\n')
    
    # GET EXIF DATA, Check if the pictures found through the links contain EXIF data
    # Gather usernames & other data from results

exif = get_exif(filePathList[0])
labeled = get_labeled_exif(exif)
print(labeled)

try:
    exif = get_exif(filePathList[1])
    geotags = get_geotagging(exif)
    print(geotags)
    print('Lat, Long = ', get_coordinates(geotags))
except:
    print('No EXIF metadata found.')



'''
Second side project:

Goal: To automate access to nomenclature databases to find
all new species in the last 5 years for a genus. An
automatic Google search can look for potential sales online.
'''

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


"""
TO DO:

INSERT PROMPT FOR GENUS AND SPECIES HERE
"""
print("Please specify the species.")
response = ''
while response.lower() not in {"plant", "reptile", "amphibian"}:
    response = input("Options available:  plant   reptile   amphibian  ")
print("You selected: " + response)

# category = input('''Currently this software supports searches for plants, reptiles, and amphibians. 
# Please specify whether the species of interest is a plant, reptile, or amphibian.''')

binomial = input('Please input the binomial name (genus and species) of the organism.')

# PROMPT YEAR RANGE

#category = 'plant'
#binomial = 'Paphiopedilum rungsuriyanum'
#multiple returns = 'Astragalus'

#category = 'reptile'
#binomial = 'Antaresia maculosus'

#category = 'amphibians'
#binomial = 'Andrias davidianus'

def print_element(items, true):
    '''
    Function to print top 10 elements based on result.
    '''
    if true:
        print('Results found for ' + binomial + ".")
    num = len(items)
    if num > 9:
        print('Here are the top 10 results:')
    print('')
    num = 0
    for i in items:
        print(i.text)
        print('')
        num += 1
        if num == 10:
            break

from webdriver_manager.chrome import ChromeDriverManager
browser = webdriver.Chrome(ChromeDriverManager().install())

plant_category = ['plant', 'Plant', 'plants', 'Plants', 'plantae', 'Plantae']
reptile_category = ['reptile', 'Reptile', 'reptiles', 'Reptiles', 'reptilia', 'Reptilia']
amphibian_category = ['amphibian', 'Amphibian', 'amphibians', 'Amphibians', 'amphibia', 'Amphibia']

# response belongs to plant category
if response in plant_category:
    browser.get('https://ipni.org/')
    
    # click advanced search button
    # link = browser.find_element_by_xpath('//*[@id="index-container"]/div/div[1]/div/div[2]/button[2]/span')
    link = browser.find_element_by_xpath('//button[@aria-label="Advanced Search"]')
    link.click()
    
    # Load panel
    time.sleep(5)

    # deal with cookie notification
    try:
        browser.find_element_by_xpath('/html/body/div[2]/a').click()
    except:
        pass
    
    # entry into search boxes and search
    genus = browser.find_element_by_id('genus')
    species =  browser.find_element_by_id('species')
    year = browser.find_element_by_id('published-after')
    genus.send_keys(binomial)
    # species.send_keys(response)
    year.send_keys('2018')
    
    link = browser.find_element_by_xpath('//*[@id="plant"]/form/button[1]')
    link.click()
    
    # Load results
    time.sleep(3)
    
    # Advanced search failed try direct search
    try:
        browser.find_element_by_class_name('no-results')
        close = browser.find_elements_by_class_name('close')
        close = close[:-1]
        for item in close:
            item.click()
            time.sleep(0.5)
        search = browser.find_element_by_id('search-tokenfield')
        search.send_keys(binomial)
        browser.find_element_by_id('search-button').click()
        time.sleep(4)
    except:
        pass
    
    nprint = True
    
    # If both searches fail return "No results."
    try:
        browser.find_element_by_class_name('no-results')
        print("No results.")
        nprint = False
    except:
        pass
        
    elements = browser.find_elements_by_class_name('list-group-item')
    print_element(elements, nprint)
    browser.close() 
    
    
# response belongs to reptile category
elif response in reptile_category:
    browser.get('http://reptile-database.reptarium.cz/')
    browser.find_element_by_link_text('Advanced search').click()

    # binomial = "Afroedura"
    # Load panel
    time.sleep(3)
    genus = browser.find_element_by_xpath('//input[@name = "genus"]')
    species = browser.find_element_by_xpath('//input[@name = "species"]')
    year = browser.find_element_by_xpath('//input[@name = "year"]')

    # try to fill in advanced search if the binomial is a 2-word input
    if len(binomial) == 2:
        genus.send_keys(binomial.split()[0])
        species.send_keys(binomial.split()[1])
    else:
        genus.send_keys(binomial)
    year.send_keys('2018 OR 2019 OR 2020')
    browser.find_element_by_xpath('//input[@value = "Search"]').click()
    time.sleep(3)

    # Advanced search failed try direct search
    try:
        if browser.find_element_by_xpath('//div[@id = "content"]/p[1]').text == "No species were found.":
            browser.find_element_by_link_text("home").click()
            time.sleep(3)
            browser.find_element_by_xpath('//input[@name="search"]').send_keys(binomial)
            browser.find_element_by_xpath('//input[@value="Search"]').click()
            time.sleep(3)
    except:
        pass

    nprint = True

    # If both searches fail return "No result."
    try:
        if browser.find_element_by_xpath('//div[@id="content"]/p').text == "No species were found.":
            print('No result.')
            nprint = False
    except:
        pass

    # try if there is a single result(new page pop up)
    try:
        if browser.find_element_by_xpath('//div[@id="content"]/h1/em').text == binomial:
            print('Result found for ' + binomial + ".")
    except:
        pass

    # if multiple results, print top 10
    elements = browser.find_elements_by_xpath('//div[@id="content"]/ul[2]/li')
    print_element(elements, nprint)
    browser.close()

 
# response belongs to amphibian category(the web does not have date attribute)   
else:
    browser.get('https://amphibiaweb.org/')
    browser.find_element_by_xpath('//input[@value="Search the Database"]').click()

    # binomial = "Caecilia"
    # Load panel
    time.sleep(3)

    name = browser.find_element_by_xpath('//*[@id="main"]/table/tbody/tr/td/form/p/table[2]/tbody/tr[1]/td[3]/input')
    name.send_keys(binomial)

    search = browser.find_element_by_xpath('//*[@id="main"]/table/tbody/tr/td/form/p/table[1]/tbody/tr/td[1]/input[1]')
    search.click()
    # Load page
    time.sleep(3)

    nprint = True

    # try if there is no result
    try:
        if browser.find_element_by_xpath('//html/body/blockquote/h2').text == "Sorry - no matches. Please try again.":
            print('No result.')
            nprint = False
    except:
        pass

    # try if there is a single result(new page pop up)
    try:
        getName = browser.find_element_by_xpath('/html[1]/body[1]/table[1]/tbody[1]'
                                            '/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/i[1]/font[1]').text
        if getName == binomial:
            print('Result found for ' + binomial + ".")
    except:
        pass

    # if multiple results, print top 10
    elements = browser.find_elements_by_xpath('//div[@id="main"]/p[4]/table/tbody/tr/td[1]/a')
    print_element(elements, nprint)
    browser.close()
    

#search = browser.find_element_by_name('q')
#search.send_keys("google search through python")
#search.send_keys(Keys.RETURN) # hit return after you enter search text
#time.sleep(5) # sleep for 5 seconds so you can see the results
#browser.quit()

browser.find_element_by_xpath('//*[@id="c-page-body"]/div[2]').text

browser.find_element_by_class_name('list-group-item').text



<input type="text" name="genus" id="frm-AdvancedSearchForm-genus" autocomplete="off" class="acInput">

browser.get('http://reptile-database.reptarium.cz/')
link = browser.find_element_by_link_text('Advanced search')
link.click()





'''

Mostly Nonsense/Test Code Below:


'''

driver = webdriver.Chrome(chrome_path)
driver.get(fetchUrl)
driver.find_element_by_xpath("""//*[@id="Z6bGOb"]/a""").click()

elements = driver.find_elements_by_class_name('WGvvNb')

print('filepath =', filePathList[i])
print('URL links from Google Image Search:\n')

for element in elements:
    #print(element.text)
    print(element.find_element_by_xpath('..').find_element_by_xpath('..').get_attribute('href'))
    #print('')

if len(elements) > 1:
    print(len(elements), 'URL links returned from Google Image Search')
elif len(elements = 1):
    print(len(elements), 'URL link returned from Google Image Search')
elif not elements:
    print('No URL links returned from Google Image Search')
    print('')
    
print('---------------')

text = driver.find_elements_by_class_name('WGvvNb')
text.find_elements_by_xpath('..').find_elements_by_xpath('..').get_attribute('href')

#driver.find_elements_by_class_name('VFACy kGQAp')
driver.find_element_by_class_name('WGvvNb').get_attribute('href')

posts = driver.find_elements_by_class_name('fxgdke')
for post in posts:
    print(post.text)

import PIL.Image
image = PIL.Image.open(filePathList[0])
exif = image._getexif()
print(exif)

gpsinfo = {}
for key in exif['GPSInfo'].keys():
    decode = ExifTags.GPSTAGS.get(key,key)
    gpsinfo[decode] = exif['GPSInfo'][key]
print(gpsinfo)

import exifread
tags = exifread.process_file(open(filePathList[0], 'rb'))                                              
geo = {i:tags[i] for i in tags.keys() if i.startswith('GPS')}
geo

import datetime
now = datetime.datetime.now()
print(now.year)

from tkinter import *

window = tk.Tk()
greeting = tk.Label(text="Hello, Tkinter")
greeting.pack()
mainloop()

master = Tk()
Label(master,text='First Name').grid(row=0)
Label(master,text='Last Name').grid(row=1)

e1 = Entry(master)
e2 = Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

mainloop()

window = tk.Tk()

label = tk.Label(text="Hello, Tkinter", fg="white", bg="black", width=100, height=100)
label.pack()

entry = tk.Entry(fg="yellow", bg="blue", width=50)
entry.pack()

button = tk.Button(
    text="Click me!",
    width=25,
    height=5,
    bg="blue",
    fg="yellow",
)
button.pack()




mainloop()

import tkinter as tk
window = tk.Tk()
label = tk.Label(text="Name")
entry = tk.Entry()

label.pack()
entry.pack()
#mainloop()

name = entry.get()

import tkinter as tk

master = tk.Tk()
tk.Label(master, text="First Name").grid(row=0)
tk.Label(master, text="Last Name").grid(row=1)

e1 = tk.Entry(master)
e2 = tk.Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

master.mainloop()

import tkinter as tk

def show_entry_fields():
    print("First Name: %s\nLast Name: %s" % (e1.get(), e2.get()))

master = tk.Tk()
tk.Label(master, 
         text="First Name").grid(row=0)
tk.Label(master, 
         text="Last Name").grid(row=1)

e1 = tk.Entry(master)
e2 = tk.Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

tk.Button(master, 
          text='Quit', 
          command=master.quit).grid(row=3, 
                                    column=0, 
                                    sticky=tk.W, 
                                    pady=4)
tk.Button(master, 
          text='Show', command=show_entry_fields).grid(row=3, 
                                                       column=1, 
                                                       sticky=tk.W, 
                                                       pady=4)

tk.mainloop()

'''
This part is for combining kivy and code
'''

'''
Part1: Search the image
'''

'''
Part2 : Do the online search
'''

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from selenium import webdriver
import time

# Create screens
Builder.load_file('main.kv')

# Declare screens
class MenuScreen(Screen):
    pass


class ImageScreen(Screen):
    pass


class SpeciesScreen(Screen):
    pass


class PlantSearch(Screen):
    plant_name_text_input = ObjectProperty(None)
    result_name_text_output = ObjectProperty(None)
    binomial_name = StringProperty('')
    result = ''
    chromeDriverPath = r'd:\chromedriver.exe'
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    browser = webdriver.Chrome(chromeDriverPath, chrome_options=option)

    def save_data(self):
        self.binomial_name = self.plant_name_text_input.text
        print(self.binomial_name)

    def search_data(self):
        self.browser.get('https://ipni.org/')

        # click advanced search button
        link = self.browser.find_element_by_xpath('//button[@aria-label="Advanced Search"]')
        link.click()

        # Load panel
        time.sleep(5)

        # deal with cookie notification
        try:
            self.browser.find_element_by_xpath('/html/body/div[2]/a').click()
        except:
            pass

        # entry into search boxes and search
        genus = self.browser.find_element_by_id('genus')
        species = self.browser.find_element_by_id('species')
        year = self.browser.find_element_by_id('published-after')
        genus.send_keys(self.binomial_name)
        # species.send_keys(response)
        year.send_keys('2018')

        link = self.browser.find_element_by_xpath('//*[@id="plant"]/form/button[1]')
        link.click()

        # Load results
        time.sleep(3)

        # Advanced search failed try direct search
        try:
            self.browser.find_element_by_class_name('no-results')
            close = self.browser.find_elements_by_class_name('close')
            close = close[:-1]
            for item in close:
                item.click()
                time.sleep(0.5)
            search = self.browser.find_element_by_id('search-tokenfield')
            search.send_keys(self.binomial_name)
            self.browser.find_element_by_id('search-button').click()
            time.sleep(4)
        except:
            pass

        nprint = True

        # If both searches fail return "No results."
        try:
            self.browser.find_element_by_class_name('no-results')
            self.result = "No results."
            nprint = False

        except:
            pass

        elements = self.browser.find_elements_by_class_name('list-group-item')
        if nprint:
            self.result = 'Results found for '
            self.result += self.binomial_name
            self.result += "."
            self.result += '\n'
            #print('Results found for ' + self.binomial_name + ".")
        num = len(elements)
        if num > 9:
            self.result += 'Here are the top 10 results:'
            self.result += '\n'
            #print('Here are the top 10 results:')
        #print('')
        num = 0
        for i in elements:
            self.result += i.text
            self.result += '\n'
            #print(i.text)
            #print('')
            num += 1
            if num == 10:
                break
            # GET LINKS

        self.browser.close()

    def print_result(self):
        self.result_name_text_output.text = self.result
        print(self.result)


class ReptileSearch(Screen):
    reptile_name_text_input = ObjectProperty(None)
    result_name_text_output = ObjectProperty(None)
    binomial_name = StringProperty('')
    result = ''
    chromeDriverPath = r'd:\chromedriver.exe'
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    browser = webdriver.Chrome(chromeDriverPath, chrome_options=option)
    #browser = webdriver.Chrome(r'd:\chromedriver.exe')

    def save_data(self):
        self.binomial_name = self.reptile_name_text_input.text
        print(self.binomial_name)

    def search_data(self):
        self.browser.get('http://reptile-database.reptarium.cz/')
        self.browser.find_element_by_link_text('Advanced search').click()

        # Load panel
        time.sleep(3)
        genus = self.browser.find_element_by_xpath('//input[@name = "genus"]')
        species = self.browser.find_element_by_xpath('//input[@name = "species"]')
        year = self.browser.find_element_by_xpath('//input[@name = "year"]')

        # try to fill in advanced search if the binomial is a 2-word input
        if len(self.binomial_name) == 2:
            genus.send_keys(self.binomial_name.split()[0])
            species.send_keys(self.binomial_name.split()[1])
        else:
            genus.send_keys(self.binomial_name)
        year.send_keys('2018 OR 2019 OR 2020')
        self.browser.find_element_by_xpath('//input[@value = "Search"]').click()
        time.sleep(3)

        # Advanced search failed try direct search
        try:
            if self.browser.find_element_by_xpath('//div[@id = "content"]/p[1]').text == "No species were found.":
                self.browser.find_element_by_link_text("home").click()
                time.sleep(3)
                self.browser.find_element_by_xpath('//input[@name="search"]').send_keys(self.binomial_name)
                self.browser.find_element_by_xpath('//input[@value="Search"]').click()
                time.sleep(3)
        except:
            pass

        nprint = True

        # If both searches fail return "No result."
        try:
            if self.browser.find_element_by_xpath('//div[@id="content"]/p').text == "No species were found.":
                self.result = 'No results.'
                nprint = False
        except:
            pass

        # try if there is a single result(new page pop up)
        try:
            if self.browser.find_element_by_xpath('//div[@id="content"]/h1/em').text == self.binomial_name:
                self.result = 'Results found for '
                self.result += self.binomial_name
                self.result += "."
                self.result += '\n'
        except:
            pass

        # if multiple results, print top 10
        elements = self.browser.find_elements_by_xpath('//div[@id="content"]/ul[2]/li')
        if nprint:
            self.result = 'Results found for '
            self.result += self.binomial_name
            self.result += "."
            self.result += '\n'
            #print('Results found for ' + self.binomial_name + ".")
        num = len(elements)
        if num > 9:
            self.result += 'Here are the top 10 results:'
            self.result += '\n'
            #print('Here are the top 10 results:')
        #print('')
        num = 0
        for i in elements:
            self.result += i.text
            self.result += '\n'
            #print(i.text)
            #print('')
            num += 1
            if num == 10:
                break
            # GET LINKS

        self.browser.close()



    def print_result(self):
        self.result_name_text_output.text = self.result
        print(self.result)





class AmphibianSearch(Screen):
    amphibian_name_text_input = ObjectProperty(None)
    result_name_text_output = ObjectProperty(None)
    binomial_name = StringProperty('')
    result = ''
    chromeDriverPath = r'd:\chromedriver.exe'
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    browser = webdriver.Chrome(chromeDriverPath, chrome_options=option)

    def save_data(self):
        self.binomial_name = self.amphibian_name_text_input.text
        print(self.binomial_name)

    def search_data(self):
        self.browser.get('https://amphibiaweb.org/')
        self.browser.find_element_by_xpath('//input[@value="Search the Database"]').click()

        # Load panel
        time.sleep(3)

        name = self.browser.find_element_by_xpath(
            '//*[@id="main"]/table/tbody/tr/td/form/p/table[2]/tbody/tr[1]/td[3]/input')
        name.send_keys(self.binomial_name)

        search = self.browser.find_element_by_xpath(
            '//*[@id="main"]/table/tbody/tr/td/form/p/table[1]/tbody/tr/td[1]/input[1]')
        search.click()
        # Load page
        time.sleep(3)

        nprint = True

        # try if there is no result
        try:
            if self.browser.find_element_by_xpath(
                    '//html/body/blockquote/h2').text == "Sorry - no matches. Please try again.":
                self.result = 'No results.'
                nprint = False
        except:
            pass

        # try if there is a single result
        try:
            getName = self.browser.find_element_by_xpath('/html[1]/body[1]/table[1]/tbody[1]'
                                                    '/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/i[1]/font[1]').text
            if getName == self.binomial_name:
                self.result = 'Results found for '
                self.result += self.binomial_name
                self.result += "."

        except:
            pass

        # if multiple results, print top 10
        elements = self.browser.find_elements_by_xpath('//div[@id="main"]/p[4]/table/tbody/tr/td[1]/a')
        if nprint:
            self.result = 'Results found for '
            self.result += self.binomial_name
            self.result += "."
            self.result += '\n'
        num = len(elements)
        if num > 9:
            self.result += 'Here are the top 10 results:'
            self.result += '\n'
            # print('Here are the top 10 results:')
            # print('')
        num = 0
        for i in elements:
            self.result += i.text
            self.result += '\n'
            # print(i.text)
            # print('')
            num += 1
            if num == 10:
                break
            # GET LINKS

        self.browser.close()

    def print_result(self):
        self.result_name_text_output.text = self.result
        print(self.result)


class FilepathScreen(Screen):
    def build(self):
        return GetFilepath()


class GetFilepath(BoxLayout):
    def get_filepath(self, **kwargs):
        super(GetFilepath, self).get_filepath(**kwargs)
        self.orientation = "vertical"
        my_user_input = TextInput()
        self.add_widget(my_user_input)
        filepath = Label(text="initial value")
        self.add_widget(filepath)

        def callback(instance, value):
            filepath.text = value

        my_user_input.bind(text=callback)


class SearchApp(App):
    title = 'Search App'
    pass

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ImageScreen(name='image'))
        sm.add_widget(SpeciesScreen(name='species'))
        sm.add_widget(PlantSearch(name='plant'))
        sm.add_widget(ReptileSearch(name='reptile'))
        sm.add_widget(AmphibianSearch(name='amphibian'))
        sm.add_widget(FilepathScreen(name='filepaths'))

        return sm


if __name__ == '__main__':
    SearchApp().run()

'''
The main.kv file
'''

<MenuScreen>:
    BoxLayout:
        Button:
            text: 'Search Image'
            on_press: root.manager.current = 'image'
        Button:
            text: 'Search Species'
            on_press: root.manager.current = 'species'

<SpeciesScreen>:
    BoxLayout:
        Button:
            text: 'PLANT'
            on_press: root.manager.current = 'plant'
        Button:
            text: 'REPTILE'
            on_press: root.manager.current = 'reptile'
        Button:
            text: 'AMPHIBIAN'
            on_press: root.manager.current = 'amphibian'
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'

<ImageScreen>:
    BoxLayout:
        Button:
            text: 'Please enter the filepath of the directory.'
            on_press: root.manager.current = 'filepaths'
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'

<PlantSearch>:
    plant_name_text_input: plant_name
    result_name_text_output: result_list
    BoxLayout:
        Label:
            text: "Plant Name:"

        TextInput:
            id: plant_name
            multiline: False

        TextInput:
            id: result_list
            text: 'Please type the plant name'
            multiline: True


        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'

        Button:
            text: "Search the Data"
            on_press: root.save_data()
            on_release: root.search_data()

        Button:
            text: "Print Result"
            on_release: root.print_result()




<ReptileSearch>:
    reptile_name_text_input: reptile_name
    result_name_text_output: result_list
    BoxLayout:
    BoxLayout:
        Label:
            text: "Reptile Name:"

        TextInput:
            id: reptile_name
            multiline: False

        TextInput:
            id: result_list
            text: 'Please type the reptile name'
            multiline: True


        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'

        Button:
            text: "Search the Data"
            on_press: root.save_data()
            on_release: root.search_data()

        Button:
            text: "Print Result"
            on_release: root.print_result()

        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'

<AmphibianSearch>:
    amphibian_name_text_input: amphibian_name
    result_name_text_output: result_list
    BoxLayout:
    BoxLayout:
        Label:
            text: "Amphibian Name:"

        TextInput:
            id: amphibian_name
            multiline: False

        TextInput:
            id: result_list
            text: 'Please type the amphibian name'
            multiline: True


        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'

        Button:
            text: "Search the Data"
            on_press: root.save_data()
            on_release: root.search_data()

        Button:
            text: "Print Result"
            on_release: root.print_result()

        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'