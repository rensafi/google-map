#!/usr/bin/env python

import sys
import math
import random
import colorsys
import tempfile
import argparse

import GeoIP

import pygmaps

def parse_cmd_args():

    parser = argparse.ArgumentParser(description="Plot IP address locations "
                                                 "on a world map.")

    parser.add_argument("-g", "--geoip-file", type=str,
                        default="/usr/local/share/GeoIP/GeoIPCity.dat",
                        help = "Location of the GeoIP file.")

    parser.add_argument("file", nargs="+", help="The files to analyse.  "
                                                "Every file must contain one "
                                                "IP address per line.")

    return parser.parse_args()


def map_location(addresses, geoip_file):

    geoip = GeoIP.open(geoip_file, GeoIP.GEOIP_STANDARD)
    locations = {}
    failed = 0

    for address in addresses:
        record = geoip.record_by_addr(address)
        if not record:
            failed += 1
            continue
        locations[address] = (record["latitude"], record["longitude"])

    print >> sys.stderr, "[*] Failed to resolve %d records." % failed

    return locations


def load_addresses(file_name):

    addresses = []

    with open(file_name, "r") as fd:
        for line in fd:
            line = line.strip()
            addresses.append(line)

    return addresses


def main():

    args = parse_cmd_args()

    my_map = pygmaps.maps(0, 0, 2)
    colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#00ffff", "#ff00ff",
              "#000000", "#ffffff", "#770000", "#007700", "#000077", "#777700",
              "#007777", "#770077"]

    # Iterate over all files provided over the command line and plot its IP
    # addresses on a map in different colours.
    for file_name in args.file:

        color = colors.pop(0)
        locations = map_location(load_addresses(file_name), args.geoip_file)

        for address in locations.keys():
            latitude, longitude = locations[address]
            my_map.addpoint(latitude, longitude, color=color, title=file_name)

    # Write the resulting map to disk.
    output_file = tempfile.mktemp(prefix="map_", suffix=".html")
    my_map.draw(output_file)
    print >> sys.stderr, "[*] Wrote output to: %s" % output_file

    return 0

if __name__ == "__main__":
    sys.exit(main())
