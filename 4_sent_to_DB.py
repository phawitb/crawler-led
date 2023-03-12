import pymongo
import json
import sys
from datetime import datetime
import csv
import configure

def isoDate(b,k):
    if k == 'bit_date':
        bb = b.split('/')
        iso_date = datetime(int(bb[2])-543, int(bb[1]), int(bb[0]), 0, 0, 0, 0)
        # iso_date = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return iso_date
    elif k == 'announce_date':
        bb = b.split('-')
        iso_date = datetime(int(bb[2])-543, int(bb[1]), int(bb[0]), 0, 0, 0, 0)
        # iso_date = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return iso_date
    elif k == 'timestamp_date':
        bb = b.split('-')
        iso_date = datetime(int(bb[0]), int(bb[1]), int(bb[2]), 0, 0, 0, 0)
        # iso_date = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return iso_date

def find_all_bid_dates(CB1):
    D = set()
    for k in CB1.keys():
        if 'sell_table' in CB1[k]['data'].keys():
            dd  = []
            for kk in CB1[k]['data']['sell_table'].keys():
                d = CB1[k]['data']['sell_table'][kk]['date']
                dd.append(d)
            D = D.union(set(dd))
    D = [isoDate(x,'bit_date') for x in D]
    return D

# province = 'bangkok'
province = sys.argv[1]

print('\n\n\n','='*200)
print('4_sent_to_DB.py')

client = pymongo.MongoClient("mongodb+srv://phawit:Signal3499@cluster0.p81pf.mongodb.net/?retryWrites=true&w=majority")
db = client.property

collection = db.led

try:
    with open(f'data/led_{province}_current_combile_previous.json', 'r') as openfile:
        CB0 = json.load(openfile)
except:
    CB0 = {}
try:
    with open(f'data/led_{province}_current_combile_last.json', 'r') as openfile:
        CB1 = json.load(openfile)
except:
    CB1 = {}

##update bid_dates province
bid_dates = find_all_bid_dates(CB1)
english_name = province
thai_name = configure.search_province[province][0]
index = configure.index_province(thai_name)
P = {
    '_id' : index,
    'english_name' : english_name,
    'thai_name' : thai_name,
    'bid_dates' : bid_dates
}
collection_provinces = db.provinces
A = collection_provinces.find_one_and_update({"_id":index}, {"$set" : P}, upsert = False )
if not A:
    collection_provinces.insert_one(P)

#get all chage data
chage_list = []
for p in CB1.keys():
    change = False
    if p in CB0.keys():
        if CB0[p] != CB1[p]:
            change = True
    else:
        change = True
    
    print('change',change)

    if change or configure.force_updateDB:
    # if True:
        D = CB1[p]['data']
        D['link'] = CB1[p]['link']
        D['area'] = f"{D['size2']}-{D['size1']}-{D['size0']}"

        if 'gps_data' in D.keys():
            D['GPS'] = [D['gps_data'][x]['gps'] for x in D['gps_data'].keys()]

        if 'sell_table' in D.keys():
            # print(D['sell_table'])
            Sta = [D['sell_table'][x]['sta'] for x in D['sell_table'].keys()]
            Sta2 = [D['sell_table'][x]['sta2'] for x in D['sell_table'].keys()]
            Date = [D['sell_table'][x]['date'] for x in D['sell_table'].keys()]

            r = ''
            idx = None
            if '' in Sta:
                b = Sta.copy()
                b.reverse()
                idx = len(b)-b.index('')-1
                r = f'พร้อมขาย! นัด{idx+1} {Date[idx]}'
            else:
                r = f'Done! {Sta[-1]} {Date[-1]}'
        
        D['last_sell_sta'] = r

        dt = datetime.now()
        ts = datetime.timestamp(dt)
        D['timestamp_date'] = str(datetime.now()).split()[0]

        bit_date = []
        for i in D['sell_table'].keys():
            d = D['sell_table'][i]['date']
            bit_date.append(d)
        bits = []
        for b in bit_date:
            iso_date = isoDate(b,'bit_date')
            bits.append(iso_date)
        bit_date = bits
        D['bit_date'] = bit_date

        if 'announce_date' in D.keys():
                D['announce_date'] = isoDate(D['announce_date'],'announce_date')
        D['timestamp_date'] = isoDate(D['timestamp_date'],'timestamp_date')

        D['order_id'] = int(p.split('/')[0]) + (int(p.split('/')[1])-1)*30
        D['province_index'] = configure.index_province(D['province'])

        print("D['bit_date']",D['bit_date'])
        
        chage_list.append(D)


#update mongoDB
for D in chage_list:
    A = collection.find_one_and_update({"link":D['link']}, {"$set" : D}, upsert = False )
    if not A:
        collection.insert_one(D)

    print("="*30)
    print(D)

print('Finish sent data to mongoDB')

with open(f'data/led_{province}_current_combile_last.json', 'r') as openfile:
        CB1 = json.load(openfile)
with open(f"data/led_{province}_current_combile_previous.json", "w") as outfile:
    outfile.write(json.dumps(CB1, indent=4))

with open('data/log.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([datetime.now(),'3_combile_data','finish', province,f'update{len(chage_list)}'])



