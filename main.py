from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def delay():
    time.sleep(random.randrange(2, 5))

def writeToCsvRow(f, list):
    for elem in list:
        try:
            f.write(elem + ',')
        except:
            print("unicode error")
    f.write('\n')

#lets get it started with https://www.bizoo.ro/companii/
def buildLinks(startPage, driver):
    driver.get(startPage)
    list = []
    fileNames = []
    for i in range(1, 34):
        # daca nu este deschis suficient de mult nu vede categoriile
        sufix = ''
        while sufix == '':
            category = str(i)
            label = driver.find_element(By.XPATH, '//*[@id="mobileFitlers"]/div[2]/div/div[2]/div[%s]' % category)
            sufix = label.text
            print("largeste fereastra")
        print(sufix)
        #//*[@id="mobileFitlers"]/div[3]/div/div[1]/div[1]/label
        sufix = sufix.replace(' ', '-')
        sufix = sufix.replace('&', '-')
        sufix = sufix.replace('/', '')
        sufix = sufix.replace(',', '')
        sufix = sufix.replace('--', '-')
        link = startPage + sufix
        list.append(link)
        fileNames.append(sufix + '.csv')
    return list, fileNames

def buildNextPageLink(pageNo, eachLink):
    if pageNo == 1:
        return eachLink
    pageNo -= 1
    return eachLink + "/start-" + str(pageNo) + "0/10/"

def findPageNumber(link, driver):
    driver.get(link)
    return int(driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div[2]/div[22]/nav/ul/li[6]/a').text)


def getPhoneNumber(driver):
    number = 'XX'
    while number.find('XX') != -1 :
        # it has two locations: here, or on catch -show number-
        print(number)
        try:
            driver.find_element(By.XPATH, '/html/body/section/div/div/div[1]/div/div[2]/div[2]/div[2]/div[2]/h6/a').click()
            delay()
            number = driver.find_element(By.XPATH, '/html/body/section/div/div/div[1]/div/div[2]/div[2]/div[2]/div[2]/h6/a').text
        except:
            print('exception')
            driver.find_element(By.CLASS_NAME, 'show-number-button').click()
            delay()
            number = driver.find_element(By.CLASS_NAME, 'show-number-button').text
    return number


def getWebsite(driver):
    return driver.find_elements(By.CSS_SELECTOR, 'a.text-sm.text-muted').text

def getEmail(website):
    if website.find('http://www.') != -1:
        ret = website.replace('http://www.', 'contact@')
    elif website.find('https://www.') != -1:
        ret = website.replace('https://www.', 'contact@')
    else:
        ret = website.replace('https://', 'contact@')
    return ret

if __name__ == '__main__':
    #opening the driver
    options = Options()
    #options.add_argument('--headless')
    #options.add_argument('disable-gpu')
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.delete_all_cookies()
    driver.set_window_size(1920, 1080)

    startPage = 'https://www.bizoo.ro/companii/'

    #build links and file name for each category
    links, fileNames = buildLinks(startPage, driver)
    print(links)
    for category, fileName in zip(links, fileNames):
        print('Current link: ' + category)

        #try 2 times because bug no CSS
        try:
            pagesNumber = findPageNumber(category, driver)
        except:
            delay()
            pagesNumber = findPageNumber(category, driver)
        # backup because HDD not reliable
        output = open(fileName, 'a')
        # backup_output = open('C:\\bizooCompanies\\' + fileName , 'a')

        driver.close()
        # mining all pages of ONE category (200 - 300 pages)
        for eachPage in range(1, pagesNumber):

            nextPageLink = buildNextPageLink(eachPage, category)
            print('We are at page: ' + str(eachPage))
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.set_window_size(1920, 1080)
            #get companies links
            try:
                driver.get(nextPageLink)
                companies = driver.find_elements(By.CLASS_NAME, 'prod-name-link')
                companiesLinks = [company.get_attribute('href') for company in companies]
                companiesNames = [company.text for company in companies]
            except:
                print('error loading nextPage link : ' + nextPageLink)
                continue

            for companyLink, companyName in zip(companiesLinks, companiesNames):
                # extract data about the company
                try:
                    driver.get(companyLink)
                    delay()
                    phoneNumber = getPhoneNumber(driver)
                except:
                    continue
                try:
                    website = getWebsite(driver)
                    email = getEmail(website)
                except:
                    website = 'null'
                    email = 'null'
                # write it to csv files
                writeToCsvRow(output, [companyName, website, email, phoneNumber])
                # writeToCsvRow(backup_output, [companyName, website, email, phoneNumber])
                output.flush()
            # close to reopen driver
            driver.close()
            output.flush()
            # backup_output.flush()
