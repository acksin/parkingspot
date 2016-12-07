import json
import numpy
import pandas as pd
import os
from multiprocessing import Pool

SPOT_PRICE_FILE_NAME = 'spot_prices.csv'
SPOT_PRICES_SPLIT_DIR = 'spot_prices_split'

STATS_DIR = 'output'

REDIS_HOST = "acksin.xe1zhw.0001.usw2.cache.amazonaws.com"

PATH = "./spot_prices_split"

OUTPUT = './output'

ondemand = {}

inst_types = json.loads(open('instanceTypes.json').read())

for i in inst_types['regions']:
    for inst in i['instanceTypes']:
        if inst['utilization'] is not 'emr' and inst['prices'].has_key('ondemand'):
            #print("{} {} {}".format(i['region'], inst['type'], inst['prices']['ondemand']['hourly']))
            if not ondemand.has_key(i['region']):
                ondemand[i['region']] = {}
            ondemand[i['region']][inst['type']] = inst['prices']['ondemand']['hourly']

def os_name(os):
    if os == 'Linux/UNIX':
        return 'linux'
    elif os == 'Windows':
        return 'windows'

def run_metrics(m):
    try:
        az = m[0]
        inst_type = m[1]
        o = m[2]

        f = pd.read_csv('spot_prices_split/{}/{}/{}/spot_prices.csv'.format(az, inst_type, o), names=['AZ', 'InstType', 'OS', 'Price', 'Timestamp'], parse_dates=[4], sep=',')
        f.Price = f['Price'].apply(lambda x: float(x[1:]))
        f['Hour'] = f.apply(lambda x: x.Timestamp.hour, axis=1)
        f['Weekday'] = f.apply(lambda x: x.Timestamp.weekday(), axis=1)

        for day in f.Weekday.unique():
            for hour in f.Hour.unique():
                    key = "{}/{}/{}/{}/{}".format(az, inst_type, o, day, hour)
                    print key

                    content = f[(f.Hour == hour) & (f.Weekday == day)]

                    recommended_bid = content.Price.mean() + content.Price.std()
                    try:
                        ondemand_price = ondemand[az[:-1]][inst_type]
                        savings = (1.0 - recommended_bid / ondemand_price) * 100
                    except:
                        ondemand_price = -1
                        savings = -1

                    (1.0 - recommended_bid / ondemand_price) * 100

                    out = {
                        "Median": content.Price.median(),
                        "Mean": content.Price.mean(),
                        "StdDev": content.Price.std(),
                        "RecommendedBid": recommended_bid,
                        "Savings": savings,
                        "OnDemandPrice": ondemand_price,
                        "Len": len(content),
                    }

                    try:
                        os.makedirs(os.path.join(OUTPUT, key))
                    except:
                        pass

                    open(os.path.join(OUTPUT, key, 'stats.json'), 'w+').write(json.dumps(out))
    except:
        print "err {}-{}-{}".format(az, inst_type, o)

if __name__ == '__main__':
    combos = []
    for az in os.listdir(SPOT_PRICES_SPLIT_DIR):
        for inst_type in os.listdir(os.path.join(SPOT_PRICES_SPLIT_DIR, az)):
            for o in ['windows', 'linux']:
                combos.append((az, inst_type, o,))

    print len(combos)
    pool = Pool(processes=8)
    pool.map(run_metrics, combos)
