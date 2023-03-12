import json 
import sys
from datetime import datetime
import csv

# province = 'bangkok'
province = sys.argv[1]

print('\n\n\n','='*200)
print('3_combile_data')

try:
    with open(f'data/led_{province}_currentlink.json', 'r') as openfile:
        C = json.load(openfile)
except:
    C = {}
try:
    with open(f'data/led_{province}.json', 'r') as openfile:
        D = json.load(openfile)
except:
    D = {}
try:
    with open(f'data/gps_data_{province}.json', 'r') as openfile:
        G = json.load(openfile)
except:
    G = {}

last_day_key = str(max([int(x) for x in C.keys()]))
combile_data = {}
for page in list(C[last_day_key].keys()):
    link = C[last_day_key][page]
    if link in D.keys():
        data = D[link]

        if 'deed_number' in data.keys():
            gps = {}
            for d in data['deed_number']:
                if str(d) in G.keys():
                    gps[str(d)] = G[str(d)]
            data['gps_data'] = gps
 
        combile_data[page] = {
            'link' : link,
            'data' : data
        }

with open(f"data/led_{province}_current_combile_last.json", "w") as outfile:
    outfile.write(json.dumps(combile_data, indent=4))

with open('data/log.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([datetime.now(),'3_combile_data','finish', province])

print('combile data complete!!')