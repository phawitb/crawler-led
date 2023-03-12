# run many file 
# https://stackoverflow.com/questions/59382293/how-to-run-several-python-files-in-specific-order-at-once
from webdriver_manager.chrome import ChromeDriverManager   #-------
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import json
from dateutil.relativedelta import *
import os
import configure
import sys
import csv

# province = 'bangkok'
province = sys.argv[1]
search_province = configure.search_province[province][1]           #'%A1%C3%D8%A7%E0%B7%BE%C1%CB%D2%B9%A4%C3'
chrome_headless = configure.chrome_headless

def scrolling_down(t):
    for i in range(t):
        driver.execute_script("window.scrollBy(0,2000)","")
        time.sleep(0.5)
        
def get_text(x):
    return driver.find_element(By.XPATH,x).text

def get_herf(x):
    attb = ['href','onclick','src','data-responsive']
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

print('\n\n\n','='*200)
print('1_get_led_data.py')
    
options = webdriver.ChromeOptions()
if chrome_headless:
    options.add_argument("headless")
options.add_argument('window-size=800x600')
driver = webdriver.Chrome(ChromeDriverManager(version=configure.chrome_version).install(),chrome_options=options)   #-----------------
# driver.maximize_window()
print('driver.get_window_size()',driver.get_window_size())

p = 1
driver.get(f'https://asset.led.go.th/newbidreg/default.asp?search=ok&search_asset_type_id=&search_tumbol=&search_ampur=&search_province={search_province}&search_region_name=&search_price_begin=&search_price_end=&search_bid_date=&search_rai=&search_quaterrai=&search_wa=&search_rai_if=1&search_quaterrai_if=1&search_wa_if=1&search_status=&search_person1=&page={p}')

try:
    max_page = get_text('/html/body/div[4]/div/div[2]/table[1]/tbody/tr/td[2]/div')
    max_page = int(max_page.split('/')[-1])
except:
    with open('data/log.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(),'1_get_led_data','fail', province])
    print('craeling fail...')
    sys.exit()

dtn = datetime.now().strftime("%Y%m%d")

def detail_row(r):
    L = ['lot','sell_order','case_id','type','size2','size1','size0','eva_price','tumbon','aumper','province']
    row = {}
    for i,l in enumerate(L):
        v = get_text(f'/html/body/div[4]/div/div[2]/div[2]/table/tbody/tr[{r}]/td[{i+1}]')
        row[l] = v.strip()
    return row

def click_row(i,data):
    click(f'/html/body/div[4]/div/div[2]/div[2]/table/tbody/tr[{i}]')
    driver.switch_to.window(driver.window_handles[1])
    # element_order = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/table[2]/tbody/tr/td[1]/strong/font/font')))
    element_order = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/table[2]/tbody/tr/td[1]/strong/font/font')))
    print('click_row',time.time(),element_order.text)
    
    try:
        p = [get_text('/html/body/div[1]/div/div/div[7]/div/div/div[2]/strong/font'),
        get_text('/html/body/div[1]/div/div/div[7]/div/div/div[4]/strong/font'),
        get_text('/html/body/div[1]/div/div/div[7]/div/div/div[6]/strong/font'),
        get_text('/html/body/div[1]/div/div/div[7]/div/div/div[8]/strong/font')]
        data['max_price'] = max([int(float(x.replace(',',''))) for x in p if x[0].isnumeric()])
    except:
        pass
    
    try:
        data['announce_date'] = get_text('/html/body/div[1]/div/div/div[7]/div/h6[1]/font')
    except:
        pass

    try:
        data['status'] = get_text('/html/body/div[1]/div/div/div[7]/div/h5/strong/font')
    except:
        pass
    
    rr = []
    for ii in range(1,7):
        r = []
        for i in range(1,5):
            v = get_text(f'/html/body/div[1]/div/div/div[6]/div/table/tbody/tr[{ii}]/td[{i}]/font/strong')
            r.append(v.strip())
        rr.append(r)
    sell_table = rr
    l = {}
    for s in sell_table:
        l[s[0]] = {
            'date' : s[1],
            'sta' : s[2],
            'sta2' : s[3]
        }
    data['sell_table'] = l
    
    imgs = []
    try:
        img = get_herf('/html/body/div[1]/div/div/div[5]/div/div/div/a/img')
        imgs.append(img)
    except:
        pass
    try:
        img = 'https://asset.led.go.th' + get_herf('/html/body/div[1]/div/div/div[5]/div/table[2]/tbody/tr/td[1]/div/div')
        imgs.append(img)
    except:
        pass
    if imgs:
        data['img'] = imgs
        

    
    try:
        data['pay_down'] = int(float(get_text('/html/body/div[1]/div/div/div[8]/strong[1]/font').replace(',','')))
    except:
        pass

    url = driver.current_url
    
    try:
        v = get_text('/html/body/div[1]/div/div/div[4]/div/div/div[5]/div')
        data['deed_number'] = [int(x) for x in v.split() if x.isnumeric()]
    except:
        try:
            data['deed_number'] = [int(x.strip('%')) for x in url.split('&deed_no=')[-1].split('&addrno=')[0].split(',')]
        except:
            pass
        # pass
        
    
    
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    
    return data,url



def data_page(D,C):

    driver.switch_to.window(driver.window_handles[0])
    
    if not dtn in C.keys():
        C[dtn] = {}

    for i in range(1,31):
        try:
            d = detail_row(i)
            data,url = click_row(i,d)
            D[url] = data
            C[dtn][f'{i}/{p}'] = url
            
            print('-'*50)
            print(f'{i}/{p} {url}')
            print(data)
        except:
            try:
                driver.close()
            except:
                pass
            try:
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass
    return D,C

    
if not os.path.exists('data'):
    os.makedirs('data')
    
try:
    with open(f'data/led_{province}.json', 'r') as openfile:
        D = json.load(openfile)
except:
    D = {}
try:
    with open(f'data/led_{province}_currentlink.json', 'r') as openfile:
        C = json.load(openfile)
except:
    C = {}

#find lastpage
d = list(C.keys())
if dtn in d:
    d = max([int(x) for x in d])
    p = C[str(d)].keys()
    last_page = max([int(x.split('/')[-1]) for x in p])
    start_page = last_page+1
else:
    start_page = 1

print('start_page',start_page)
# last_page = []
# last_page = C[dtn].keys()
# for k in C.keys():
#     last_page.append(int(C[k]['page'].split('/')[-1]))
# if last_page:
#     last_page = max(last_page)
# else:
#     last_page = 1
# print('last_page',last_page)

    
# max_page = 1  #--------
for p in range(start_page,max_page+1):
    
    # driver.get(f'https://asset.led.go.th/newbidreg/default.asp?search=ok&search_asset_type_id=&search_tumbol=&search_ampur=&search_province=%A1%C3%D8%A7%E0%B7%BE%C1%CB%D2%B9%A4%C3&search_region_name=&search_price_begin=&search_price_end=&search_bid_date=&search_rai=&search_quaterrai=&search_wa=&search_rai_if=1&search_quaterrai_if=1&search_wa_if=1&search_status=&search_person1=&page={p}')
    driver.get(f'https://asset.led.go.th/newbidreg/default.asp?search=ok&search_asset_type_id=&search_tumbol=&search_ampur=&search_province={search_province}&search_region_name=&search_price_begin=&search_price_end=&search_bid_date=&search_rai=&search_quaterrai=&search_wa=&search_rai_if=1&search_quaterrai_if=1&search_wa_if=1&search_status=&search_person1=&page={p}')

    element_page = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[2]/table[1]/tbody/tr/td[2]/div')))
    print(time.time(),element_page)

    try:
        with open(f'data/led_{province}.json', 'r') as openfile:
            D = json.load(openfile)
    except:
        D = {}
    try:
        with open(f'data/led_{province}_currentlink.json', 'r') as openfile:
            C = json.load(openfile)
    except:
        C = {}
    
    D,C = data_page(D,C)
    
    with open(f"data/led_{province}.json", "w") as outfile:
        outfile.write(json.dumps(D, indent=4))
    with open(f"data/led_{province}_currentlink.json", "w") as outfile:
        outfile.write(json.dumps(C, indent=4))

    # driver.close()


with open('data/log.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([datetime.now(),'1_get_led_data','finish', province,f'{max_page}pages'])
    
    
    
    
    
    

    
