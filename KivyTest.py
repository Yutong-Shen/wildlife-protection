#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image, AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from openpyxl import Workbook, load_workbook
from kivy.core.window import Window
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.clock import Clock
import time, threading

# Import all packages, give prompt to pip install any needed packages.

try:
    import sys
    import os
    import glob
    import requests
    import webbrowser
    import pandas as pd
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
            get_ipython().system('{sys.executable} -m pip install os')
        else:
            print('Program terminated, os needed for operation of program.')
            raise SystemExit

    try:
        import glob
    except:
        question = input("glob is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            get_ipython().system('{sys.executable} -m pip install glob')
        else:
            print('Program terminated, glob needed for operation of program.')
            sys.exit(1)
                
    try:
        import requests
    except:
        question = input("requests is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            get_ipython().system('{sys.executable} -m pip install requests')
        else:
            print('Program terminated, requests needed for operation of program.')
            sys.exit(1)
                
    try:
        import webbrowser
    except:
        question = input("webbrowser is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            get_ipython().system('{sys.executable} -m pip install webbrowser')
        else:
            print('Program terminated, webbrowser needed for operation of program.')
            sys.exit(1)
    
    try:
        from selenium import webdriver

    except:
        question = input("selenium is not installed. Do you want to pip install? y/n: ")
        if question == "y":
            get_ipython().system('{sys.executable} -m pip install selenium')
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
            get_ipython().system('{sys.executable} -m pip install PIL')
        else:
            print('Program terminated, PIL needed for operation of program.')
            sys.exit(1)

# Create screens
#Builder.load_file('main.kv')
Window.size = (800, 600)

Config.set('graphics', 'resizable', True) 

# Create screens
Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        Button:
            size_hint: .6, .6
            pos_hint: {'y': .2}
            background_normal: 'SearchImage.png'
            on_press: root.manager.current = 'filepaths'
        Button:
            size_hint: .6, .6
            pos_hint: {'y': .2}
            background_normal: 'SearchIcon.png'
            on_press: root.manager.current = 'species'
            
<SpeciesScreen>:

    BoxLayout:
        Button:
            text: 'PLANT'
            bold: True
            background_normal: 'Plant.jpg'
            on_press: root.manager.current = 'plant'
        Button:
            text: 'REPTILE'
            bold: True
            background_normal: 'Reptile.jpg'
            on_press: root.manager.current = 'reptile'
        Button:
            text: 'AMPHIBIAN'
            bold: True
            background_normal: 'Amphibian.jpg'
            on_press: root.manager.current = 'amphibian'
            
<PlantSearch>:
    plant_name_text_input: plant_name
    result_name_text_output: result_list
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            cols: 2
            Label:
                text: "Plant Name:"
                size_hint: (0.3, None)
                height: 50
            TextInput:
                id: plant_name
                multiline: True
                size_hint: (0.7, None)
                height: 50

        TextInput:
            id: result_list
            text: 'Please type the plant name'
            multiline: True
            size_hint: (1, None)
            height: 500
        GridLayout:
            cols: 3
            Button:
                text: 'Back to menu'
                size_hint: (0.3, None)
                height:50
                on_press: root.manager.current = 'menu'

            Button:
                text: "Search the Data"
                size_hint: (0.3, None)
                height:50
                on_press: root.save_data()
                on_release: root.process_button_click()

            Button:
                text: "Print Result"
                size_hint: (0.3, None)
                height: 50
                on_release: root.print_result()
        GridLayout:
            cols: 1
            Button:
                text: 'Save to csv'
                size_hint: (0.3, None)
                height:50
                on_press: root.save_to_csv()

<ReptileSearch>:
    reptile_name_text_input: reptile_name
    result_name_text_output: result_list
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            cols: 2
            Label:
                text: "Reptile Name:"
                size_hint: (0.3, None)
                height: 50
            TextInput:
                id: reptile_name
                multiline: True
                size_hint: (0.7, None)
                height: 50

        TextInput:
            id: result_list
            text: 'Please type the reptile name'
            multiline: True
            size_hint: (1, None)
            height: 500

        GridLayout:
            cols: 3
            Button:
                text: 'Back to menu'
                size_hint: (0.3, None)
                height:50
                on_press: root.manager.current = 'menu'

            Button:
                text: "Search the Data"
                size_hint: (0.3, None)
                height:50
                on_press: root.save_data()
                on_release: root.process_button_click()

            Button:
                text: "Print Result"
                size_hint: (0.3, None)
                height: 50
                on_release: root.print_result()
        GridLayout:
            cols: 1
            Button:
                text: 'Save to csv'
                size_hint: (0.3, None)
                height:50
                on_press: root.save_to_csv()


<AmphibianSearch>:
    amphibian_name_text_input: amphibian_name
    result_name_text_output: result_list
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            cols: 2
            Label:
                text: "Amphibian Name:"
                size_hint: (0.3, None)
                height: 50
            TextInput:
                id: amphibian_name
                multiline: True
                size_hint: (0.7, None)
                height: 50

        TextInput:
            id: result_list
            text: 'Please type the amphibian name'
            multiline: True
            size_hint: (1, None)
            height: 500

        GridLayout:
            cols: 3
            Button:
                text: 'Back to menu'
                size_hint: (0.3, None)
                height:50
                on_press: root.manager.current = 'menu'

            Button:
                text: "Search the Data"
                size_hint: (0.3, None)
                height:50
                on_press: root.save_data()
                on_release: root.process_button_click()

            Button:
                text: "Print Result"
                size_hint: (0.3, None)
                height: 50
                on_release: root.print_result()
        GridLayout:
            cols: 1
            Button:
                text: 'Save to csv'
                size_hint: (0.3, None)
                height:50
                on_press: root.save_to_csv()
                 
<FilepathScreen>:
    file_name_text_input: filepath
    result_name_text_output: result_list
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            cols: 2
            Label:
                text: "Filepath:"
                size_hint: (0.3, None)
                height: 50
            TextInput:
                id: filepath
                multiline: True
                size_hint: (0.7, None)
                height: 50

        TextInput:
            id: result_list
            text: 'Please type the full filepath above.'
            multiline: True
            size_hint: (1, None)
            height: 500
        GridLayout:
            cols: 3
            Button:
                text: 'Back to menu'
                size_hint: (0.3, None)
                height:50
                on_press: root.manager.current = 'menu'

            Button:
                text: "Search the Data"
                size_hint: (0.3, None)
                height:50
                on_press: root.save_data()
                on_release: root.process_button_click()

            Button:
                text: "Print Result"
                size_hint: (0.3, None)
                height: 50
                on_release: root.print_result()

        GridLayout:
            cols: 1
            Button:
                text: 'Save to csv'
                size_hint: (0.3, None)
                height:50
                on_press: root.save_to_csv()

<PopupBox>:
    pop_up_text: _pop_up_text
    size_hint: .5, .5
    auto_dismiss: True
    title: 'Status'   

    BoxLayout:
        orientation: "vertical"
        Label:
            id: _pop_up_text
            text: ''
""")

# Declare screens
class MenuScreen(Screen):
    pass

class SpeciesScreen(Screen):
    pass

class PlantSearch(Screen):
    class PlantSearch(Screen):
        plant_name_text_input = ObjectProperty(None)
        result_name_text_output = ObjectProperty(None)
        df = ObjectProperty(None)
        binomial_name = StringProperty('')
        result = ''

    def save_data(self):
        self.binomial_name = self.plant_name_text_input.text
        print(self.binomial_name)
        
    def show_popup(self):
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text('Loading...')
        self.pop_up.open()

    def process_button_click(self):
        # Open the pop up
        self.show_popup()
        
        mythread = threading.Thread(target=self.search_data)
        mythread.start()

    def search_data(self):        
        #chromeDriverPath = r'd:\chromedriver.exe'
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
        browser.get('https://ipni.org/')

        # click advanced search button
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
        species = browser.find_element_by_id('species')
        year = browser.find_element_by_id('published-after')
        genus.send_keys(self.binomial_name)
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
            search.send_keys(self.binomial_name)
            browser.find_element_by_id('search-button').click()
            time.sleep(4)
        except:
            pass

        nprint = True

        # If both searches fail return "No results."
        try:
            browser.find_element_by_class_name('no-results')
            self.result = "No results."
            nprint = False

        except:
            pass

        elements = browser.find_elements_by_class_name('list-group-item')
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

        browser.close()
        self.pop_up.dismiss()

    def print_result(self):
        self.result_name_text_output.text = self.result

    def save_to_csv(self):
        self.df.to_csv('SearchResults.csv',index=False)
        

class ReptileSearch(Screen):
    reptile_name_text_input = ObjectProperty(None)
    result_name_text_output = ObjectProperty(None)
    df = ObjectProperty(None)
    binomial_name = StringProperty('')
    result = ''

    #browser = webdriver.Chrome(r'd:\chromedriver.exe')

    def save_data(self):
        self.binomial_name = self.reptile_name_text_input.text
        print(self.binomial_name)
        
    def show_popup(self):
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text('Loading...')
        self.pop_up.open()

    def process_button_click(self):
        # Open the pop up
        self.show_popup()
        
        mythread = threading.Thread(target=self.search_data)
        mythread.start()

    def search_data(self):
        #chromeDriverPath = r'd:\chromedriver.exe'
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
        browser.get('http://reptile-database.reptarium.cz/')
        browser.find_element_by_link_text('Advanced search').click()

        # Load panel
        time.sleep(3)
        genus = browser.find_element_by_xpath('//input[@name = "genus"]')
        species = browser.find_element_by_xpath('//input[@name = "species"]')
        year = browser.find_element_by_xpath('//input[@name = "year"]')

        # try to fill in advanced search if the binomial is a 2-word input
        if len(self.binomial_name) == 2:
            genus.send_keys(self.binomial_name.split()[0])
            species.send_keys(self.binomial_name.split()[1])
        else:
            genus.send_keys(self.binomial_name)
        year.send_keys('2018 OR 2019 OR 2020')
        browser.find_element_by_xpath('//input[@value = "Search"]').click()
        time.sleep(3)

        # Advanced search failed try direct search
        try:
            if browser.find_element_by_xpath('//div[@id = "content"]/p[1]').text == "No species were found.":
                browser.find_element_by_link_text("home").click()
                time.sleep(3)
                browser.find_element_by_xpath('//input[@name="search"]').send_keys(self.binomial_name)
                browser.find_element_by_xpath('//input[@value="Search"]').click()
                time.sleep(3)
        except:
            pass

        nprint = True

        # If both searches fail return "No result."
        try:
            if browser.find_element_by_xpath('//div[@id="content"]/p').text == "No species were found.":
                self.result = 'No results.'
                nprint = False
        except:
            pass

        # try if there is a single result(new page pop up)
        try:
            if browser.find_element_by_xpath('//div[@id="content"]/h1/em').text == self.binomial_name:
                self.result = 'Results found for '
                self.result += self.binomial_name
                self.result += "."
                self.result += '\n'
        except:
            pass

        # if multiple results, print top 10
        elements = browser.find_elements_by_xpath('//div[@id="content"]/ul[2]/li')
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

        browser.close()
        self.pop_up.dismiss()

    def print_result(self):
        self.result_name_text_output.text = self.result
        
    def save_to_csv(self):
        self.df.to_csv('SearchResults.csv',index=False)

class PopupBox(Popup):
    pop_up_text = ObjectProperty()
    def update_pop_up_text(self, p_message):
        self.pop_up_text.text = p_message

# Does not return anything because looking for 10 results when only returns one link
class AmphibianSearch(Screen):
    amphibian_name_text_input = ObjectProperty(None)
    result_name_text_output = ObjectProperty(None)
    df = ObjectProperty(None)
    binomial_name = StringProperty('')
    result = ''


    def save_data(self):
        self.binomial_name = self.amphibian_name_text_input.text
        print(self.binomial_name)
        
    def show_popup(self):
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text('Loading...')
        self.pop_up.open()

    def process_button_click(self):
        # Open the pop up
        self.show_popup()
        
        mythread = threading.Thread(target=self.search_data)
        mythread.start()

    def search_data(self):
        #chromeDriverPath = r'd:\chromedriver.exe'
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
        browser.get('https://amphibiaweb.org/')
        browser.find_element_by_xpath('//input[@value="Search the Database"]').click()

        # Load panel
        time.sleep(3)

        name = browser.find_element_by_xpath(
            '//*[@id="main"]/table/tbody/tr/td/form/p/table[2]/tbody/tr[1]/td[3]/input')
        name.send_keys(self.binomial_name)

        search = browser.find_element_by_xpath(
            '//*[@id="main"]/table/tbody/tr/td/form/p/table[1]/tbody/tr/td[1]/input[1]')
        search.click()
        # Load page
        time.sleep(3)

        nprint = True

        # try if there is no result
        try:
            if browser.find_element_by_xpath(
                    '//html/body/blockquote/h2').text == "Sorry - no matches. Please try again.":
                self.result = 'No results.'
                nprint = False
        except:
            pass

        # try if there is a single result
        try:
            getName = browser.find_element_by_xpath('/html[1]/body[1]/table[1]/tbody[1]'
                                                    '/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/i[1]/font[1]').text
            if getName == self.binomial_name:
                self.result = 'Result found for '
                self.result += self.binomial_name
                self.result += ".\n"
                self.result += getName

        except:
            pass

        # if multiple results, print top 10
        items = list()
        elements = browser.find_elements_by_xpath('//div[@id="main"]/p[4]/table/tbody/tr/td[1]/a')
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
            items.append(elem.get_attribute("href"))
            num += 1
            if num == 10:
                break
            # GET LINKS
        self.df = pd.DataFrame(items, columns = ['Links'])

        browser.close()
        self.pop_up.dismiss()

    def print_result(self):
        self.result_name_text_output.text = self.result
    
    def save_to_csv(self):
        self.df.to_csv('SearchResults.csv',index=False)

class FilepathScreen(Screen):
    file_name_text_input = ObjectProperty(None)
    result_name_text_output = ObjectProperty(None)
    df = ObjectProperty(None)
    file_name = StringProperty('')
    result = ''

    def save_data(self):
        self.file_name = self.file_name_text_input.text
        print(self.file_name)
        
    def show_popup(self):
        self.pop_up = Factory.PopupBox()
        self.pop_up.update_pop_up_text('Loading...')
        self.pop_up.open()

    def process_button_click(self):
        # Open the pop up
        self.show_popup()
        
        mythread = threading.Thread(target=self.search_data)
        mythread.start()

    def search_data(self):
        # reverse image search
        filePath = self.file_name
        searchUrl = 'http://www.google.com/searchbyimage/upload'
        multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
        response = requests.post(searchUrl, files=multipart, allow_redirects=False)
        fetchUrl = response.headers['Location']
        #webbrowser.open(fetchUrl)

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

        driver.add_cookie({"name": "key", "value": "value"})
        driver.find_element_by_xpath("""//*[@id="Z6bGOb"]/a""").click()

        elems = driver.find_elements_by_xpath("//a[@class='VFACy kGQAp sMi44c lNHeqe WGvvNb']") 

        print('imagename = ', os.path.basename(filePath))
        print('filepath =', filePath, '\n')
        items = list()

        if len(elems) > 1:
            self.result += str(len(elems))
            self.result += 'URL links returned from Google Image Search\n'
            for elem in elems:
                self.result += elem.get_attribute("href")
                self.result += "\n"
                items.append(elem.get_attribute("href"))
            self.df = pd.DataFrame(items, columns = ['Links'])
        elif len(elems) == 1:
            self.result += str(len(elems))
            self.result += 'URL link returned from Google Image Search\n'
            self.result += elems.get_attribute("href")
        elif not elems:
            self.result += 'No URL links returned from Google Image Search\n'

        driver.close()
        self.pop_up.dismiss()
            
    def print_result(self):
        self.result_name_text_output.text = self.result
    
    def save_to_csv(self):
        self.df.to_csv('SearchResults.csv',index=False)

class SearchApp(App):
    title = 'Search App'
    pass

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SpeciesScreen(name='species'))
        sm.add_widget(PlantSearch(name='plant'))
        sm.add_widget(ReptileSearch(name='reptile'))
        sm.add_widget(AmphibianSearch(name='amphibian'))
        sm.add_widget(FilepathScreen(name='filepaths'))

        return sm

if __name__ == '__main__':
    SearchApp().run()

