import string
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import get_date_times

# The relative position of each day
# Values are hard coded from experimenting with their positions
# TODO Non hardcoded values
pos_to_day = {
    "0": 0.0,
    "1": 0.2,
    "2": 0.4,
    "3": 0.6,
    "4": 0.8
}


def create_url(school, room):
    root = "https://web.skola24.se/timetable/timetable-viewer/uppsala.skola24.se/"

    return root + school + "/room/" + room + "/"


def extract_schedule(school, room, week=get_date_times.get_week(), headless=True):
    """

    :param school: str, name of the school
    :param room: Room Object
    :param week: int, current week
    :param headless: bool, whether it opens chrome in the background or not
    :return:
    """

    # Installs the driver
    try:
        # Makes the window headless
        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')  # Last I checked this was necessary.

        executable_path = r"E:\HämtadeFiler\chromedriver_win32_84\chromedriver.exe"

        # Innit he driver
        driver = webdriver.Chrome(executable_path, options=options)
    except PermissionError:
        print("Permission Error at:", school, room.name)
        return False

    room_name = room.name
    driver.get(create_url(school, room_name))

    # Select the room
    try:
        # Enters the room name in the field and waits until load
        button = WebDriverWait(driver, 10).until(ec.presence_of_element_located(
            (By.XPATH, '/html/body/div[3]/div[2]/div/div[2]/div[1]/div[1]/div[5]/div/div/input')))
        button.click()
        time.sleep(3)
        button.send_keys(room_name)
        time.sleep(3)
        button.send_keys(Keys.ENTER)
    except TimeoutException:
        print("Button timed out", room_name)
        empty_split_list = {'0': [], '1': [], '2': [], '3': [], '4': []}
        driver.quit()
        return empty_split_list

    # Sets week if not current
    if week != get_date_times.get_week():
        week_button_xpath = '/html/body/div[3]/div[2]/div/div[2]/div[1]/div[1]/div[2]/div/div/input'
        driver.find_element_by_xpath(week_button_xpath).clear()  # Presses enter to the field
        time.sleep(2)
        # Enters the room name in the field
        driver.find_element_by_xpath(week_button_xpath).send_keys("v." + str(week) + ", 2020")
        time.sleep(2)
        # Presses enter to the field
        driver.find_element_by_xpath(week_button_xpath).send_keys(Keys.ENTER)
        time.sleep(2)

    try:
        results = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, "svg")))
    except NoSuchElementException:
        print("Found no svg at:", room_name)
        empty_split_list = {'0': [], '1': [], '2': [], '3': [], '4': []}
        driver.quit()
        return empty_split_list
    except TimeoutException:
        # driver.save_screenshot(room_name + "_svg_test_save_screen_shot.png")
        print("Sessions timed out", room_name)
        empty_split_list = {'0': [], '1': [], '2': [], '3': [], '4': []}
        driver.quit()
        return empty_split_list

    raw_timestamps = []

    # Gets the width and height in pixels of the schedule image
    width, height = results.get_attribute("width"), results.get_attribute("height")

    # Finds all timestamps on the schedule image
    for item in results.find_elements_by_tag_name('text'):
        if is_timestamp(item.text):
            # Calculates the relative horizontal position on the schedule image
            pos = round(int(item.get_attribute("x")) / int(width), 1)

            raw_timestamps.append((pos, item.text))

    # Splits the timestamps by day
    split_by_day_schedule = split_days(raw_timestamps)

    # Pairs all times where the room in occupied
    split_by_day_paired = pair_occupied_times(split_by_day_schedule)

    driver.quit()

    return split_by_day_paired


def split_days(raw_time_stamps):
    """
    Splits a list of timestamp into the respective days
    :param raw_time_stamps: list of tuples, (int, str) with the position and timestamp
    :return: array, list of list, each representing a day containing it's timestamps
    """

    split_list = [[],
                  [],
                  [],
                  [],
                  []]

    if len(raw_time_stamps) == 0:
        return split_list

    current_day_times = []
    current_day_number = raw_time_stamps[0][0]

    prior_time = "00:00"
    prior_pos = None

    # Goes through all pair of pos and times
    for pos_and_time in raw_time_stamps:
        # Pos is the relative position horizontally on the schedule image
        pos, time_stamp = pos_and_time

        # If it's the same day
        if is_before(prior_time, time_stamp) and pos != prior_pos:
            current_day_times.append(time_stamp)

            prior_time = time_stamp
            prior_pos = pos

        # If it's a new day
        else:
            # See if it's actually a day or the sidebar
            if current_day_number in pos_to_day.values():
                # Add the time to corresponding day
                split_list[int(get_key(pos_to_day, current_day_number))].extend(current_day_times)

            # The position of this new day
            current_day_number = pos

            # Start the next day
            current_day_times = [time_stamp]
            prior_time = "00:00"

    # Adds the last day
    try:
        split_list[int(get_key(pos_to_day, current_day_number))].extend(current_day_times)
    except TypeError:
        print("Error with last day")

    return split_list


def get_key(d, val):
    """Returns key from dict given value"""
    for key, value in d.items():
        if val == value:
            return key


def pair_occupied_times(split_by_day):
    """
    Pairs times to get the lessons and thus occupied times for a room

    :param split_by_day: 2D list with the different times for the different days
    :return: a dictonary with each day containing the respective times paired
    """

    schedule_dict = dict()

    for day_index, day in enumerate(split_by_day):
        paired_times = []
        for time in day[::2]:
            try:
                paired_times.append((time, day[day.index(time) + 1]))
            except IndexError:
                pass
        schedule_dict[str(day_index)] = paired_times
    return schedule_dict


def is_timestamp(entry):
    """
    Checks whether a string is a timestamp of format 'hh:mm'
    :param entry: a string
    :return: bool, true if it's a timestamp
    """

    has_colon = False

    for char in entry:
        if char.lower() in string.ascii_lowercase + "åäö":
            return False
        if char == ":":
            has_colon = True

    # no letters and colon means it's a timestamp
    return has_colon


def is_before(time1, time2):
    """Checks whether time1 is before time2"""

    hour1, minute1 = time1.split(":")
    hour2, minute2 = time2.split(":")

    if int(hour1) < int(hour2):
        return True
    if int(hour1) == int(hour2):
        if int(minute1) < int(minute2):
            return True
        if minute1 == minute2:
            return True

    return False


def is_between(current_time, time_stamps):
    """
    Checks whether a timestamp is between the two other
    :param current_time: str, hh:mm
    :param time_stamps: tuple, 2 timestamps, hh:mm
    :return: bool, true if it's between
    """

    if is_before(current_time, time_stamps[1]) and not is_before(current_time, time_stamps[0]):
        return True

    return False


def time_between(time1, time2):
    """Returns the time between 2 timestamps"""
    hour1, minute1 = time1.split(":")
    hour2, minute2 = time2.split(":")

    hour_difference = (int(hour2) - (int(hour1)) + divmod(int(minute2) - int(minute1), 60)[0])
    minute_difference = (int(minute2) - int(minute1)) - divmod(int(minute2) - int(minute1), 60)[0] * 60

    return str(hour_difference) + ":" + str(minute_difference)


class RoomDebugTest:
    def __init__(self, school, name, schedule):
        self.school = school
        self.name = name
        self.url = create_url(school, name)
        self.schedule = schedule


if __name__ == "__main__":
    start_time = time.time()
    schedule = extract_schedule("Rosendalsgymnasiet", RoomDebugTest("Rosendalsgymnasiet", "B408", None), 36)

    # driver.quit()

    # for day, times in schedule.items():
    #    print(day)
    #    for each_time in times:
    #        print("    ", each_time)

    print("Program took ", round(time.time() - start_time, 1), "seconds to run")
