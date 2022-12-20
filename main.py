'''
This program is a ML classifier used to identify the features with greatest influence on currents off
Red Hill / Puu Olai, Maui
'''
import csv
import datetime
from astral import moon  # https://astral.readthedocs.io/en/latest

def getMoonPhase(date):
    return moon.phase(date)

def getDatetime(dateStr):
    return datetime.datetime.strptime(dateStr, '%m/%d/%Y')

def main():
    with open('data.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')

            print(f'checking moon phase for {row["date"]}')
            phase = getMoonPhase(getDatetime(row['date']))
            print(phase)

            print(f'checking tide height for {row["date"]} at {row["time"]}')



            line_count += 1

        print(f'Processed {line_count} dives.')


if __name__ == '__main__':
    main()
