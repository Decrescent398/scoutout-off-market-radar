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
    references = osmium.IdTracker()

    with osmium.SimpleWriter(OPL_OUTPUT/pathlib.Path('houses.opl'), overwrite=True) as writer:
        for obj in file_processer:
            if obj.tags['building'] == 'house':
                writer.add(obj)
                references.add_references(obj)

    references.complete_backward_references(OSM_PATH, relation_depth=10)

    def get_query():
        with open(OPL_OUTPUT/pathlib.Path('houses.opl')) as infile:
            reader = csv.reader(infile, delimiter=' ')
            iterator = list(reader)
            for house_data_point in reader:
                if house_data_point[0].startswith('n'):
                    point = Point(house_data_point[-2], house_data_point[-1])
                    return point.format('dms')
                elif house_data_point[0].startswith('w'):
                    for node in house_data_point[-1].split(','):
                        coordinate_list = [(line[-2], line[-1]) for line in iterator if line.startswith(node)]
                        multi_point = MultiPoint(coordinate_list)
                        return multi_point.centorid
                elif house_data_point[0].startswith('r'):
                    way_centroids = []
                    for way in house_data_point[-1].split(','):
                        nodes = [line[-1].split(',') for line in iterator if line.startswith(way)]
                        for node in nodes:
                            coordinate_list = [(line[-2], line[-1]) for line in iterator if line.startswith(node)]
                            node_multi_point = MultiPoint(coordinate_list)
                            way_centroids.append(node_multi_point.centroid)
                    way_multipoint = MultiPoint(way_centroids)
                    return way_multipoint.centroid
    
    get_query()

sort_and_write_data()