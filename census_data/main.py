import json
import csv

def geojson2csv(path_geojson, path_csv):
    res = []
    res.append(['pop', 'den', 'geometry', 'area'])
    with open(path_geojson, 'r') as f:
        geojson = json.load(f)
    for feature in geojson['features']:
        pop = feature['properties']['POP']
        geo = feature['geometry']['coordinates']
        area = feature['properties']['Shape__Area']
        scale = area / 10000
        if len(geo) != 1:
            raise Exception(f'Number of polygons is not 1: f{len(geo)}')
        geo = ', '.join([f'{i[0]} {i[1]}' for i in geo[0]])
        geo = f'POLYGON(({geo}))'
        res.append([pop, pop/scale, geo, area])
    with open(path_csv, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(res)