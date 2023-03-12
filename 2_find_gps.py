from webdriver_manager.chrome import ChromeDriverManager   #-------
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import json
from dateutil.relativedelta import *
import os
from selenium.webdriver.support.ui import Select
import configure
import sys
import csv

# province = 'bangkok'
province = sys.argv[1]
thai_province = configure.search_province[province][0]
chrome_headless = configure.chrome_headless

print('\n\n\n','='*200)
print('2_find_gps')

options = webdriver.ChromeOptions()
if chrome_headless:
    options.add_argument("headless")
options.add_argument('window-size=800x600')
driver = webdriver.Chrome(ChromeDriverManager(version=configure.chrome_version).install(),chrome_options=options)   #-----------------
# driver.maximize_window()
print('driver.get_window_size()',driver.get_window_size())

driver.get('https://landsmaps.dol.go.th/')

def scrolling_down(t):
    for i in range(t):
        driver.execute_script("window.scrollBy(0,2000)","")
        time.sleep(0.5)
        
def get_text(x):
    return driver.find_element(By.XPATH,x).text

def get_herf(x):
    attb = ['href','onclick','src']
    for a in attb:
        v = driver.find_element(By.XPATH,x).get_attribute(a)
        if v:
            break 
    return v

def click(x):
    driver.find_element(By.XPATH,x).click()
    
def sent_key(x,val):
    driver.find_element(By.XPATH, x).send_keys(val)
    
def clear(x):
    driver.find_element(By.XPATH, x).clear()
    

def select_scroll(x,val):
    #     x = '/html/body/nav/form[1]/div/select'
        element= Select(driver.find_element(By.XPATH,x))
        element.select_by_visible_text(val)   # ddelement.select_by_value('12')
        
def list_aumphers(province):
    provinces = get_text('/html/body/nav/form[1]/div/select').split('\n')[1:]
    aumphers = []
    if province in provinces:
        select_scroll('/html/body/nav/form[1]/div/select',province)
        aumphers = get_text('/html/body/nav/form[2]/div/select').split('\n')[1:]
    return aumphers
        
def find_gps(province,aumper,deed_no):
    def read_box():
        data = {}
        L = ['deed_id','page_explor','land_id','position','tumbon','aumpher','province','area','eva_price','gps']
        for i,l in enumerate(L):
            
            driver.implicitly_wait(10)
            start = time.time()
            d = None
            while not d and time.time()-start < 10:
                d = get_text(f'/html/body/div[1]/div[3]/span/div/div[2]/div[2]/div/div[2]/div[{i+1}]/div[2]')
#                 print(d)
                data[l] = d

        return data
    
    # print('\n\n\nx',x)
    print('aumper',aumper)
    aums = [x for x in aumphers if aumper in x]
    print('aums',aums)
    
    for aumper in aums:
        print(aumper)
        try:
            select_scroll('/html/body/nav/form[1]/div/select',province)
            select_scroll('/html/body/nav/form[2]/div/select',aumper)

            clear('/html/body/nav/form[3]/span/input')
            sent_key('/html/body/nav/form[3]/span/input',deed_no)

            click('/html/body/nav/form[4]/button')
            time.sleep(3)
            box = read_box()
        #     click('/html/body/div[1]/div[3]/span/div/div[1]/button')
            return box
        except:
            pass
    return None


time.sleep(10)
try:
    click('/html/body/div[25]/div/div/div/div[1]/button/i')
except:
    pass

    
# province = 'นนทบุรี'
# aumper = '03-บางใหญ่'
# deed_no = '58211'
    
# find_gps(province,aumper,deed_no)

# province = 'กรุงเทพมหานคร'
# province = 'นนทบุรี'
print('119province',province)
aumphers = list_aumphers(thai_province)
print('aumphers',aumphers)
print('122province',province)

def find_exist_gps(id):
    try:
        with open(f'data/gps_data_{province}.json', 'r') as openfile:
            gps_data = json.load(openfile)
    except:
        gps_data = {}

    if id in gps_data.keys():
        return gps_data[id]
    
# gps_data = {}
# try:
with open(f'data/led_{province}.json', 'r') as openfile:
    data = json.load(openfile)
# except:
#     data = {}
    
count_found_gps = 0
count_notfound_gps = 0
for ii,i in enumerate(list(data.keys())):

    print(ii,'-'*20)

    with open(f'data/led_{province}.json', 'r') as openfile:
        data = json.load(openfile)
    try:
        with open(f'data/gps_data_{province}.json', 'r') as openfile:
            gps_data = json.load(openfile)
    except:
        gps_data = {}
        

    if 'deed_number' in data[i].keys():
        print(data[i]['deed_number'])

        deeds = data[i]['deed_number']
#         gps = {}
        data[i]['gps_data'] = {}
        for d in deeds:
            thai_province = data[i]['province'].strip()
            aumper = data[i]['aumper'].strip()
            deed_no = d
            
            a = find_exist_gps(str(d))
            if a:
                print('gps exist',a)
            else:
                a = find_gps(thai_province,aumper,deed_no)
                print('find gps from website',a)
            
            if a:
#                 gps[str(d)] = a
                gps_data[str(d)] = a
#                 break
                data[i]['gps_data'][str(d)] = a
                count_found_gps += 1
            else:
                count_notfound_gps += 1

    else:
        print('no gps from crawling')
    
    if data:
        with open(f"data/led_{province}.json", "w") as outfile:
            outfile.write(json.dumps(data, indent=4))
    with open(f"data/gps_data_{province}.json", "w") as outfile:
        outfile.write(json.dumps(gps_data, indent=4))

with open('data/log.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([datetime.now(),'2_find_gps','finish', province,f'found{count_found_gps}notfound{count_notfound_gps}'])
                
                

#     try:
#         print(data[i]['deed_number'])
#     except:
#         pass