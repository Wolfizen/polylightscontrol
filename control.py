#!/usr/bin/env python

import requests
import sys
import time

from colour import Color


def verbose_color(c):
    if str(c.web) != c.hex:
        return "'{}' ({})".format(c.hex_l, c.web)
    else:
        return "'{}'".format(c)


def get_color():
    response = requests.get("https://poly.rpi.edu/lights/color")
    response.raise_for_status()

    json = response.json()
    return Color(rgb=(float(json["R"])/255, float(json["G"])/255, float(json["B"])/255))


def get_stats():
    response = requests.get("https://poly.rpi.edu/lights/stats")
    response.raise_for_status()

    json = response.json()
    return json


def set_color(c):
    request_data = {"R": int(c.red*255), "G": int(c.green*255), "B": int(c.blue*255)}

    response = requests.post("https://poly.rpi.edu/lights/submit", params=request_data)
    response.raise_for_status()


def main():

    if len(sys.argv) >= 2:
        command = sys.argv[1]
    else:
        command = "help"

    # Handle interactions with the underlying action functions
    if command == "get" or command == "query":
        try:
            c = get_color()
            print("Current light color is {}".format(verbose_color(c)))

        except requests.HTTPError as ex:
            print("HTTP failure", file=sys.stderr)
            print(ex, file=sys.stderr)

    elif command == "stats":
        try:
            stats_object = get_stats()
            print("Statistics:")
            print(stats_object)

        except requests.HTTPError as ex:
            print("HTTP failure", file=sys.stderr)
            print(ex, file=sys.stderr)

    elif command == "set":
        try:
            c = Color(sys.argv[2])
            set_color(c)
            print("Light color is now {}".format(verbose_color(c)))

        except IndexError:
            print("Color argument is required.", file=sys.stderr)
        except ValueError as ex:
            print(ex, file=sys.stderr)  # Invalid color!
        except requests.HTTPError as ex:
            print("HTTP failure", file=sys.stderr)
            print(ex, file=sys.stderr)

    elif command == "cycle" or command == "rainbow":
        try:
            if command == "rainbow":
                spectrum = [Color("red"), Color("orange"), Color("yellow"), Color("green"), Color("blue"), Color("purple"), Color("magenta")]
            else:
                spectrum = [Color(x) for x in sys.argv[2::]]

            color_index = -1
            while True:
                color_index += 1
                if color_index >= len(spectrum):
                    color_index = 0
                set_color(spectrum[color_index])
                print("Rainbow is at {}".format(verbose_color(spectrum[color_index])))
                time.sleep(1)

        except KeyboardInterrupt:
            print("Effect stopped")
        except ValueError as ex:
            print(ex, file=sys.stderr)  # Invalid color!
        except requests.HTTPError as ex:
            print("HTTP failure", file=sys.stderr)
            print(ex, file=sys.stderr)

    elif command == "help" or command == "-h" or command == "--help":
        print("Usage: control.py COMMAND [ARGS]...\n"
              "Execute a command with the given arguments."
              ""
              "Commands:\n"
              "  get                Get the currently displayed color.\n"
              "  stats              Get the server-reported statistics.\n"
              "  set COLOR          Set the displayed color. Argument can be any web-compatible color spec.\n"
              "  cycle COLOR...     Iterate through the given colors continuously.\n"
              "  rainbow            A continuous effect that cycles through the color spectrum.\n"
              "\n"
              "The Polytechnic - Lights Control\n"
              "(c) 2017 Wolfizen <wolfizen@wolfizen.net>")
    else:
        print("Unknown command. Run 'control.py help'.")


if __name__ == "__main__":
    main()
