import csv

def make_countries():
    io1 = open('data/countries.csv','r')
    res = csv.DictReader(io1)
    v = {}
    for r in res:
        code = r['code']
        v[code] = r['name']
    return v
    