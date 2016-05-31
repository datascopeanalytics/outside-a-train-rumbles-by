"""Create a json with current train passing results from CTA API.

"""
from __future__ import print_function

import collections
import datetime
import json
import logging
import time

import ctaapi
import settings

# the CTA station IDs for Randolph and Adams stations in the loop
RANDOLPH = 40200
ADAMS = 40680

# used for looking up colors / directions
COLORS = {
    'Brn': 'brown',
    'G': 'green',
    'Org': 'orange',
    'P': 'purple',
    'Pink': 'pink',
}

# Green line has two directions which will be determined on the fly
DIRECTIONS = {
    'brown': 'northbound',
    'orange': 'southbound',
    'purple': 'northbound',
    'pink': 'southbound',
}


def unix_time(a_datetime):
    """Take a datetime as input, and return milliseconds since the
    epoch.

    """
    return int(time.mktime(a_datetime.timetuple())) * 1000


class TrainTracker(ctaapi.TrainTracker):
    """Subclass the TrainTracker object so that we can add the
    `run_number` to the result (don't know why that wasn't in
    there).

    """
    @classmethod
    def _build_eta_dict(cls, eta):
        result = super(TrainTracker, cls)._build_eta_dict(eta)
        result.update({
            'run_number': eta.find('rn').text,
        })
        return result


def get_color(info_list):
    """Takes a list of arrival results from the API for the same run
    number and returns the color of the train.

    """
    for station, info in info_list:

        # if this color code from the API hasn't been seen before,
        # throw an error so we can add it to the dictionary
        try:
            color = COLORS[info['route_name']]
        except KeyError:
            logging.error(str(info))
            msg = 'Need to add route name "%s" to the COLORS dictionary' % \
                info['route_name']
            raise KeyError(msg)

        # return the color of the first result in the list
        return color


def get_direction(info_list, color):
    """Use the results from the API to get the direction this train is
    going.

    """

    try:
        if color == 'green':
            station, info = info_list[0]
            """ trDr = 1: northbound, 5: southbound
            Assume no other numbers will be given, but if other show up, just make the train southbound.

            """
            if info['direction'] == '1':
                direction = 'northbound'
            else:
                direction = 'southbound'
        else:
            direction = DIRECTIONS[color]
    except KeyError:
        logging.error(str(color))
        logging.error(str(info_list))
        msg = 'Need to add color "%s" to the DIRECTIONS dictionary' % color
        raise KeyError(msg)
    return direction


def get_pass_time(info_list, color, direction):
    """Using the arrival times, estimate when the train is going to pass
    the Datascope office. Returns the result as a "milliseconds since
    epoch" timestamp so that it's easy to deal with in javascript.

    """
    result = None

    # the list has one element if it's either already passed on of the
    # stations, or if it's really far away and only shows up for one
    # of the stations.
    if len(info_list) == 1:
        station, info = info_list[0]
        if station == RANDOLPH and direction == 'northbound':
            pass_time = info['arrival_time'] - datetime.timedelta(minutes=1)
            result = unix_time(pass_time)
        elif station == ADAMS and direction == 'southbound':
            pass_time = info['arrival_time'] - datetime.timedelta(minutes=1)
            result = unix_time(pass_time)

    # most will probably have two: assume Datascope is halfway between
    # RANDOLPH and ADAMS stations
    elif len(info_list) == 2:
        (station_a, info_a), (station_b, info_b) = info_list
        arrive_a = unix_time(info_a['arrival_time'])
        arrive_b = unix_time(info_b['arrival_time'])
        result = (arrive_a + arrive_b) / 2

    # never seen this before, but warning just in case
    else:
        msg = 'unknown case with %i elements in info list' % len(info_list)
        logging.warning(msg)

    # just to be safe, fall back to "now" for any results that don't
    # make sense.
    if not result:
        result = unix_time(datetime.datetime.now())

    return result


def main():
    """Find estimated pass-by times/direction/color for all trains that
    will pass by in the next 10 minutes or so. return the result as a
    JSON string.

    """
    api = TrainTracker(settings.CTA_API_KEY)

    # group trains by run number
    grouped_by_run = collections.defaultdict(list)
    for arrival in api.arrivals(map_id=RANDOLPH):
        grouped_by_run[arrival['run_number']].append(
            (arrival['station_id'], arrival))
    for arrival in api.arrivals(map_id=ADAMS):
        grouped_by_run[arrival['run_number']].append(
            (arrival['station_id'], arrival))


    # "decorate" by when the train will pass so that it's easy to sort
    decorated = []
    for run_number, info_list in grouped_by_run.iteritems():
        color = get_color(info_list)
        direction = get_direction(info_list,color)
        pass_time = get_pass_time(info_list, color, direction)
        decorated.append((pass_time, {
            'pass_time': pass_time,
            'color': color,
            'direction': direction,
        }))

    # make a list of the results, sorted by when the trains will pass
    # our office.
    result = [info for (pass_time, info) in sorted(decorated)]

    return json.dumps(result)

if __name__ == '__main__':

    json_string = main()
    with open('web/data/train-times.json', 'w') as outfile:
        outfile.write(json_string)
