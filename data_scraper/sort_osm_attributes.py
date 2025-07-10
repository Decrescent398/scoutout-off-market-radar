import osmium
import pathlib
import datetime
import csv
from geopy.point import Point
from shapely.geometry import MultiPoint

DOWNLOAD_PATH = pathlib.Path("./data")
OUTPUT_PATH = DOWNLOAD_PATH / pathlib.Path("out")
OPL_OUTPUT = OUTPUT_PATH / pathlib.Path("opl")
OSM_PATH = DOWNLOAD_PATH / pathlib.Path(f"us-latest-{datetime.date.today()}.osm.pbf")

def sort_and_write_data():

    file_processer = osmium.FileProcessor(OSM_PATH).with_filter(osmium.filter.KeyFilter('building'))

    with open(OPL_OUTPUT/pathlib.Path('houses.csv').as_posix(), 'w', newline='') as file:

        writer = csv.writer(file, delimiter="|")
        #Filter's out a lot of houses, because most have incomplete addresses and cannot be crossreferenced for other data - I would prefer Google Places API (co-ordinate accuracy + addresses) but it's paid
        #https://taginfo.openstreetmap.org/keys/building#values - 79.50% of all buildings are of unspecified type which is inaccurate af
        #VERY BIG TODO: Refine this by moneying in API

        counties = []

        for obj in file_processer:
            if obj.tags['building'] in ['house', 'residential', 'apartments', 'detached', 'semidetached_house', 'terrace']:
                address = ''

                street = obj.tags.get("addr:street")
                suburb = obj.tags.get("addr:suburb")
                place = obj.tags.get("addr:place")
                county = obj.tags.get("addr:county")
                city = obj.tags.get("addr:city")
                state = obj.tags.get("addr:state")
                parts = [street, suburb, place, county, city, state]

                address = address + ", ".join(part for part in parts if part)

                if county not in counties:
                    counties.append(county)
                    
                if 'addr:flats' not in obj.tags:
                    if obj.tags.get("addr:housenumber"):
                        try:
                            writer.writerow([f"{obj.tags.get("addr:housenumber")} {address}", f"{obj.location.lat, obj.location.lon}"])
                        except AttributeError:
                            pass

                else: #https://wiki.openstreetmap.org/wiki/Key:addr:flats
                    ranges = obj.tags["addr:flats"].split(";")
                    for flat_range in ranges:
                        if "-" in flat_range:
                            try:
                                writer.writerows([[f"{flat}, {address}", f"{obj.location.lat, obj.location.lon}"] for flat in range(int(flat_range[0]), int(flat_range[-1])+1)])
                            except (AttributeError, ValueError):
                                pass
                        else:
                            try:
                                writer.writerow([f"{flat_range}, {address}", f"{obj.location.lat, obj.location.lon}"])
                            except AttributeError:
                                pass

sort_and_write_data()