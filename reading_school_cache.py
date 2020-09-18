import get_date_times
import schedule_extractor
import school_cache

debug_set_time = get_date_times.current_time_to_time_stamp()


def time_until_occupied(room, day, current_time):
    """
    :param day: string, 0-4 index of day
    :param room: room object
    :param current_time: date and time string in hh:mm format
    :return: time in string hh:mm format
    """

    try:
        for index, time_stamp_pairs in enumerate(room.schedule[day]):
            if schedule_extractor.is_between(current_time, time_stamp_pairs):
                return -get_date_times.time_stamp_to_minutes(
                    schedule_extractor.time_between(current_time, time_stamp_pairs[1]))

            if schedule_extractor.is_before(current_time, time_stamp_pairs[0]):
                return get_date_times.time_stamp_to_minutes(
                    schedule_extractor.time_between(current_time, time_stamp_pairs[0]))

        if len(room.schedule[day]) == 0:
            return get_date_times.time_stamp_to_minutes(schedule_extractor.time_between(current_time, "17:00"))
        else:
            return -60
    except KeyError:
        return -60


def empty_rooms(school, set_time):
    """
    Returns all the empty rooms at the time and for how long

    :return: 2 lists of tuples
    """

    empty_rooms_list = []
    occupied_rooms_list = []

    for room in school.rooms:
        time_left = time_until_occupied(room, get_date_times.day_of_week(), set_time)
        if len(room.name) >= 10:
            room.name = room.name[:7] + ".."
        if time_left > 0:
            empty_rooms_list.append((time_left, room.name))
        elif time_left > -30:
            occupied_rooms_list.append((-time_left, room.name))
    return empty_rooms_list, occupied_rooms_list


def sort_tuples(list_of_tuple, reverse=True):
    list_of_tuple.sort(reverse=reverse)

    return list_of_tuple


cache = school_cache.SchoolCache("saved_files/saved_schools_week_" + str(get_date_times.get_week()))


def empty_rooms_in_school(school_name, set_time=get_date_times.current_time_to_time_stamp()):
    school = cache.get_school(school_name)

    # If school wasn't found
    if not school:
        return [], []

    # Gets and sorts all empty rooms
    empty, occupied = empty_rooms(school, set_time)
    empty, occupied = sort_tuples(empty), sort_tuples(occupied, False)

    result_result = []
    occupied_result = []

    # Returns if it's after 17:00
    if not schedule_extractor.is_before(set_time, "17:00"):
        return result_result, occupied_result

    # Sets the string to be shown on site
    for room in empty:
        if room[0] == get_date_times.time_stamp_to_minutes(schedule_extractor.time_between(set_time, "17:00")):
            result_result.append(str(room[1]) + " " * (10 - len(room[1])) + "obokad")
        else:
            result_result.append(
                str(room[1]) + " " * (10 - len(room[1])) + str(room[0]) + " " * (4 - len(str(room[0]))) + "minuter")

    for room in occupied:
        occupied_result.append(
            str(room[1]) + " " * (10 - len(room[1])) + str(room[0]) + " " * (4 - len(str(room[0]))) + " minuter")

    return result_result, occupied_result


if __name__ == "__main__":
    print(debug_set_time)
    test_school = cache.get_school("Rosendalsgymnasiet")
    print("Empty rooms at", test_school.name)
    print()
    test_empty, test_occupied = empty_rooms(test_school, debug_set_time)
    test_empty = sort_tuples(test_empty)
    print("Room:", " " * 4, "Time left:")
    for each in test_empty:
        print(each[1], " " * (9 - len(each[1])), each[0], "minutes")
