#!flask/bin/python
import json, sqlite3, time, datetime

def get_latest_temperatures():
    query = """SELECT ID, TEMPERATURE, TIMESTAMP FROM TEMPERATURE ORDER BY TIMESTAMP DESC LIMIT 100;""";
    conn = sqlite3.connect('temperature.db')
    cur = conn.cursor()
    cur.execute(query)

    ts_list = []
    temp_list = []

    for row in cur:
        id, temp, timestamp = row
        # print type(timestamp)
        # timestamp = time.mktime(timestamp.timetuple())
        epochmills = time.mktime(datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").timetuple())
        print epochmills
        temp_list += [temp, ]
        ts_list += [epochmills, ]

    cur.close()
    conn.close()

    response = {'ts_list' : ts_list, 'temp_list' : temp_list}

    return response


def get_oven_temperature():
    """Get oven temperature (celsius) through hardware magic

    @return: float
    """
    past_temp = get_latest_temperatures()
    latest_temp = past_temp['temp_list'][0]
    return latest_temp

def get_oven_state():
    """Get state of oven

    @return: One of ["on", "off", "error"]
    """
    return "error"


def main():
    print get_oven_temperature()
    print get_latest_temperatures()

if __name__ == '__main__':
    main()
