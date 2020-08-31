from selenium import webdriver
import time
import pickle, os
import check_differences
from itertools import islice
from multiprocessing.pool import ThreadPool

root = "https://web.skola24.se/timetable/timetable-viewer/uppsala.skola24.se/"


def get_schools(headless=True):
    """
    Reads all schools from the skola24 website
    :return: list of the schools
    """

    # Installs the driver
    try:
        # Makes the window headless
        options = webdriver.ChromeOptions()

        if (headless):
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        executable_path = r"E:\HämtadeFiler\chromedriver_win32_84\chromedriver.exe"

        # Innit he driver
        driver = webdriver.Chrome(executable_path, options=options)
    except PermissionError:
        return False

    # get web page
    url_page = root + "Rosendalsgymnasiet/"
    driver.get(url_page)
    time.sleep(8)

    # The menu bar
    results = driver.find_elements_by_class_name("w-row")
    school_list = list()

    for item in results:
        # Returns the different menu object
        options = item.find_elements_by_tag_name("div")

        for option in options:
            # checks if it's the correct menu
            if option.get_attribute("data-identifier") == "unitSelection":
                # listed objects
                rooms = option.find_elements_by_tag_name('li')
                for room in rooms:
                    # Gets the text on the object
                    school_list.append(room.get_attribute('data-text'))

    print("")
    print("Found:", len(school_list), "schools")
    print("")

    driver.quit()

    return school_list


def get_rooms(school_name, headless=True):
    """
    Reads all the rooms int the given school from the the skola24 website
    :param school_name: string with school name
    :return: list of all the rooms
    """

    # Installs the driver
    try:
        # Makes the window headless
        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        executable_path = r"E:\HämtadeFiler\chromedriver_win32_84\chromedriver.exe"

        # Innit he driver
        driver = webdriver.Chrome(executable_path, options=options)
    except PermissionError:
        return False

    # get web page
    url_page = root + school_name + "/"
    driver.get(url_page)
    time.sleep(10)  # Sleeps to make sure the site loads

    # The path to the menu bar
    x_path_menu_bar = "/html/body/div[3]/div[2]/div/div[2]/div[1]/div[1]"
    results = driver.find_elements_by_xpath(x_path_menu_bar)
    room_list = list()

    # Iterates the different menu options
    for item in results:
        # Returns the different menu object
        options = item.find_elements_by_tag_name("div")

        for option in options:
            try:
                # checks if it's the correct menu
                if option.get_attribute("data-identifier") == "SalSelection":
                    x_path_sal_button = "/html/body/div[3]/div[2]/div/div[2]/div[1]/div[1]/div[5]/div/div/button"
                    option.find_element_by_xpath(x_path_sal_button).click()
                    time.sleep(1)
                    rooms = option.find_elements_by_tag_name('li')
                    for room in rooms:
                        # Gets the text on the object
                        room_list.append(room.get_attribute('data-text'))
            except:
                pass

    print("")
    print("Found:", len(room_list), "rooms at", school_name)
    print("")

    driver.quit()

    return school_name, room_list


def save_rooms_by_school(threads=8):
    """
    Reads all the rooms from all the schools and saves them in a dict dumped to "rooms_by_school_file"
    Uses multiple threads
    :param threads: int, the amount of threads to be run parallel
    :return: Boolean
    """

    start_time = time.time()

    # Fetches all the school names as strings
    school_list = get_schools()
    rooms_by_school_dict = dict()

    # Pool for multithreading
    pool = ThreadPool(threads)

    # Split the list into chunks for the threads
    for school_chunk in chunk(school_list, threads):
        # Uses multiple threads to extract the rooms
        school_rooms = pool.map(get_rooms, school_chunk)

        for school, rooms in school_rooms:
            # Catch error where the room is None
            if len(rooms) == 1 and rooms[0] is None:
                continue
            if len(rooms) > 0:
                rooms_by_school_dict[school] = rooms
            else:
                continue

    total_rooms = sum([len(x) for x in rooms_by_school_dict.values()])

    print("Found", total_rooms, "different rooms at", len(rooms_by_school_dict), "schools")
    print()
    print("---It took", round(time.time() - start_time, 1), "seconds to search and find all schools---")
    print()

    if True:
        pickle.dump(rooms_by_school_dict, open("temp_rooms_by_school_file", "wb"))

        check_differences.difference_schools_room("rooms_by_school_file", "temp_rooms_by_school_file")
        os.remove("temp_rooms_by_school_file")

        pickle.dump(rooms_by_school_dict, open("rooms_by_school_file", "wb"))
        return True
    else:
        return False


def chunk(it, size):
    """Splits a list into chunks of length size"""
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


if __name__ == "__main__":
    if save_rooms_by_school():
        print("Saving schools succeeded")
    else:
        print("Saving schools failed")
