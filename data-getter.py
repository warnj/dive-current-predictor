'''
This program is a
'''
import requests
import csv
import datetime
from datetime import datetime as dt
from astral import moon  # https://astral.readthedocs.io/en/latest

# https://www.programiz.com/python-programming/datetime/strftime
DATEFMT = '%Y-%m-%d' # example 2019/01/18
TIMEFMT = '%H:%M' # example 13:11, 5:01
DATETIMEFMTDASH = '%Y-%m-%d %H:%M' # combination of above but with dash

# https://api.tidesandcurrents.noaa.gov/api/prod/
URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&datum=MLLW&station=1615202&time_zone=LST&units=english&interval=hilo&format=json"

class Tide:
    time = None
    low = None
    height = 0.0

    def __str__(self):
        type = 'lo' if self.low else 'hi'
        return '{} {} @ {}'.format(type, self.height, dt.strftime(self.time, DATETIMEFMTDASH))

def parseTide(prediction):
    t = Tide()
    t.time = dt.strptime(prediction['t'], DATETIMEFMTDASH)
    t.low = prediction['type'] == 'L'
    t.height = float(prediction['v'])
    return t

def getDateTimeDash(date, time):
    return dt.strptime(date + " " + time, DATETIMEFMTDASH)

def getDayBefore(start):
    date = dt.strptime(start, DATEFMT)
    date -= datetime.timedelta(days=1)
    return date.strftime(DATEFMT)

def getDayAfter(start):
    date = dt.strptime(start, DATEFMT)
    date += datetime.timedelta(days=1)
    return date.strftime(DATEFMT)

def getDayUrl(baseUrl, start):
    return baseUrl + f'&begin_date={getDayBefore(start).replace("-", "")}&end_date={getDayAfter(start).replace("-", "")}'

def getTideBeforeAndAfter(midTime, predictions):
    pre = None
    index = 0
    for prediction in predictions:
        time = dt.strptime(prediction['t'], DATETIMEFMTDASH)
        if time < midTime:
            index += 1
            pre = parseTide(prediction)
        else:
            break
    if index >= len(predictions):
        raise Exception("no slack after the dive time, extend the URL request a day")
    post = parseTide(predictions[index])
    return pre, post

def checkTideInfo(date, time):
    urlFinal = getDayUrl(URL, date)
    response = requests.get(urlFinal)
    if response.status_code != 200:
        raise Exception('NOAA API is down')

    midTime = getDateTimeDash(date, time) + datetime.timedelta(minutes=30)
    print("middle of dive at", midTime)

    pre, post = getTideBeforeAndAfter(midTime, response.json()['predictions'])
    print("tide before dive:", pre)
    print("tide after dive:", post)
    type = "flood" if pre.low else "ebb"
    size = abs(pre.height - post.height)
    dur = (post.time - pre.time).total_seconds() / 60
    after = (midTime - pre.time).total_seconds() / 60
    before = (post.time - midTime).total_seconds() / 60
    print("exchange type:", type)
    print("exchange size:", size)
    print("exchange duration:", dur)
    print("time after tide slack (minutes):", after)
    print("time before tide slack (minutes):", before)
    print()
    return type, size, dur, after, before

# def getMoonPhase():
    # should probably just fill this in by hand
    # https://www.almanac.com/astronomy/moon/calendar/zipcode/96753/2022-12

def main():
    # consider using the water level api in Kahului to get real-time water level
    # url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&datum=MLLW&station=1615680&time_zone=LST&units=english&format=json"

    with open('data.csv', mode='r') as data_read:
        csv_reader = csv.DictReader(data_read, delimiter=',')

        with open('data-features.csv', mode='w', newline='') as data_write:
            csv_writer = None

            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print('Columns being read are:', row.keys())
                    new_keys = []
                    new_keys.extend(row.keys())
                    new_keys.extend(['moon', 'tide_type', 'tide_size', 'tide_duration', 'tide_after', 'tide_before'])
                    print('Columns being written are:', new_keys)
                    csv_writer = csv.DictWriter(data_write, delimiter=',', fieldnames=new_keys)
                    csv_writer.writeheader()

                date, time = row['date'], row['time']
                print('checking tide height for {} at {}'.format(date, time))
                type, size, dur, after, before = checkTideInfo(date, time)
                row['moon'] = moon.phase(getDateTimeDash(date, time)) / 28.0
                row['tide_type'] = type
                row['tide_size'] = size
                row['tide_duration'] = dur
                row['tide_after'] = after
                row['tide_before'] = before
                csv_writer.writerow(row)

                line_count += 1
            print(f'Processed {line_count} dives.')

if __name__ == '__main__':
    main()
