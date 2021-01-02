# Loading the necessary depedencies
import numpy as np
import pandas as pd

import bs4
import json
import time

# using selenium for web automation to recover the necessary data
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def yfinance_analysis(ticker_list):
    
    '''
    yfinance_analysis is a function which scrapes Yahoo Finance webpage for Analyst Buy/Sell Recommendations
    To use it simply pass in a list of ticker which the user is interested in obtaining analyst recommendation 
    and it will be returned in a dictionary
    
    Example:
    input: yfinance_analysis(['MSFT'])
    
    output: {'MSFT': 1.6}
    
    Disclaimer: The above example was true as of January 1st, 2021
    '''
    
    analyst_rec = dict(); # creates a dictionary to store buy/sell recommendations later on
    driver = webdriver.Chrome(executable_path='/Users/kanjomelo/.wdm/drivers/chromedriver/mac64/87.0.4280.88/chromedriver')
    driver.maximize_window()
        
    for count,ticker in enumerate(ticker_list):
        url = 'https://ca.finance.yahoo.com/quote/{ticker}'.format(ticker = ticker)
        driver.get(url)
        
        # scroll_function simulates the scrolling motion of a user to load js data of the page
        # could not determine a more 'pythonic' way that worked for this particular page
        def scroll_page(number_of_scrolls, sleep_time):
            for n in range(number_of_scrolls):
                time.sleep(sleep_time)
                screen_height = 3600
                driver.execute_script('window.scrollTo(0, {screen_height});'.format(screen_height = screen_height))
                time.sleep(sleep_time)
                driver.execute_script('window.scrollTo(0, {screen_height});'.format(screen_height = screen_height - 800))
        
        # this try/except prevent the page scroll from failing
        try:
            scroll_page(2,2)
            element_outerHTML = driver.find_element_by_xpath("//*[contains(@aria-label, 'on a scale of 1 to 5')]")
            html = element_outerHTML.get_attribute('outerHTML') # return the outerHTML of the tag which stores the rating
            soup=bs4.BeautifulSoup(html,'lxml')
            js_data = json.loads(soup.find('div').text) # return the value as JSON and convert to text
            
        except:
            scroll_page(2,2)
            element_outerHTML = driver.find_element_by_xpath("//*[contains(@aria-label, 'on a scale of 1 to 5')]")
            html = element_outerHTML.get_attribute('outerHTML') # return the outerHTML of the tag which stores the rating
            soup=bs4.BeautifulSoup(html,'lxml')
            js_data = json.loads(soup.find('div').text) # return the value as JSON and convert to text
            
        analyst_rec[ticker_list[count]] = js_data
    
    return analyst_rec # return the dictionary of financial analyst recommendations



def earnings_info(ticker_list):
    
    '''
    earnings_info is used to pull PE, EPS, Earnings Call DAte and 1Y Target Est. from Yahoo Finance Web Page
    To use it simply pass in a list of ticker which the user is interested in obtaining these values as of current time 
    and it will be returned in a dictionary
    
    Example:
    input: earnings_info(['MSFT'])
    
    output: {'MSFT': ['35.93', '6.20', 'Jan. 27, 2021', '241.21']}
    
    Disclaimer: The above example was true as of January 1st, 2021
    '''
    
    driver = webdriver.Chrome(executable_path='/Users/kanjomelo/.wdm/drivers/chromedriver/mac64/87.0.4280.88/chromedriver')
    driver.maximize_window()
    ticker_info = dict()
    
    # this allows the data to be organized easily for later into a data frame and joining with the other sources
    for count,ticker in enumerate(ticker_list):
        url = 'https://ca.finance.yahoo.com/quote/{ticker}'.format(ticker = ticker)
        driver.get(url)

        time.sleep(2)
        # xpath for PE, EPS, Earnings Call DAte and 1Y Target Est.
        xpath_list = ['3','4','5','8']
        xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/div/div[2]/div[2]/table/tbody/tr[{i}]/td[2]/span"
        
        determinants = []
        
        # to obtain the current price of the stock
        current_price_xpath = "//*[contains(@data-reactid,'32')] [contains(@class, 'Trsdu')]"
        element_innerHTML = driver.find_element_by_xpath(current_price_xpath)
        html = element_innerHTML.get_attribute('innerHTML')
        determinants.append(html)
        
        # to obtain the PE, EPS, Earnings Call DAte and 1Y Target Est. based on xpath obtained above
        for count1, xpath_num in enumerate(xpath_list):
            element_innerHTML = driver.find_element_by_xpath(xpath.format(i = xpath_num))
            html = element_innerHTML.get_attribute('innerHTML')
            determinants.append(html)
            
        ticker_info.update( {ticker:determinants} )
    
    return ticker_info # return a list containing PE, EPS, Earnings Call DAte and 1Y Target Est. for given ticker
    