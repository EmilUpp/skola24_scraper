import datetime
import time


def today_to_date():
    """Converts todays date to a tuple"""
    return datetime.date.today().year, datetime.date.today().month, datetime.date.today().day


def get_week(date=today_to_date()):
    """Returns the weeknumber for the given date, defaults to today"""
    year, week, day = datetime.date(date[0], date[1], date[2]).isocalendar()
    return week


def day_of_week():
    return str(datetime.date.today().weekday())


def current_time_to_time_stamp():
    t = time.localtime()
    time_stamped = time.strftime("%H:%M", t)
    return time_stamped


def time_stamp_to_minutes(time_stamp):
    hour, minute = time_stamp.split(":")
    return int(hour) * 60 + int(minute)


if __name__ == "__main__":
    current_time_to_time_stamp()
    # day_of_week()
    # print(today_to_date())
    # print(get_week(today_to_date()))
