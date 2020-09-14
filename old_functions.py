def split_days_back(raw_timestamps):
    split_list = []

    day = []

    prior_time = "00:00"
    for time_stamp in raw_timestamps:
        if is_before(prior_time, time_stamp):  # Checks to see if it's a new day
            day.append(time_stamp)
            prior_time = time_stamp
        else:
            split_list.append(day)
            prior_time = "00:00"
            day = [time_stamp]

    split_list.append(day)

    split_list = split_list[2:]  # Removes the 2 first since they're not actual days

    return split_list


def split_days_back(raw_timestamps):
    # TODO fix when no lessons, add empty days that gets filled
    split_list = []

    day = []
    last_day = 0

    prior_time = "00:00"
    for pos_and_time_stamp in raw_timestamps:
        pos, time_stamp = pos_and_time_stamp

        if is_before(prior_time, time_stamp):  # Checks to see if it's not a new day
            day.append(time_stamp)
            prior_time = time_stamp
        else:
            split_list.append(day)  # Adds the day to the list
            prior_time = "00:00"
            day = [time_stamp]

            day_number = get_key(pos_to_day, pos)

            if type(day_number) == str:
                day_number = int(day_number)
                print(day_number, last_day)
                if day_number != last_day + 1:
                    print("empty added")
                    split_list.append([])

                last_day = day_number

    split_list.append(day)

    split_list = split_list[2:]  # Removes the 2 first since they're not actual days
    print(split_list)

    return split_list


def pair_timestamps(split_by_day):
    """
    Pairs all times where the room is free between
    :param split_by_day:
    :return:
    """

    # TODO Pair occupied times

    schedule_dict = {}

    schedule_dict.setdefault(str(1), [])
    schedule_dict[str(1)].append(("8:00", split_by_day[0][0]))  # Fixes the first empty time monday morning

    for day in split_by_day:
        day_index = split_by_day.index(day)

        for time in (day[1::2]):  # Every other timetamp to get the one inbetween
            time_index = day.index(time)
            try:
                schedule_dict.setdefault(str(day_index + 1), [])
                schedule_dict[str(day_index + 1)].append((time, day[time_index + 1]))

                # pair_list.append((time, day[time_index + 1]))               # Appends the two times
            except:
                try:
                    # Sets empty from after the last lesson until 18:00
                    schedule_dict.setdefault(str(day_index + 1), [])
                    schedule_dict[str(day_index + 1)].append((time, "18:00"))

                    # Sets the room empty from morning until first lesson starts
                    schedule_dict.setdefault(str(day_index + 2), [])
                    schedule_dict[str(day_index + 2)].append(("8:00", split_by_day[day_index + 1][0]))

                    # pair_list.append((time, split_by_day[day_index + 1][0])) # Adds the first of the next day after the last lesson
                except IndexError:
                    continue
                    # Fixes edge case on the after the last lesson on friday
                    # schedule_dict.setdefault(str(day_index + 1), [])
                    # schedule_dict[str(day_index + 1)].append((split_by_day[-1][-1], "18:00"))

                    # pair_list.append((split_by_day[-1][-1], "23:59"))        # Fixes the last on the last day

    return schedule_dict


def save_rooms_by_school2():
    """
    Reads all the rooms from all the schools and saves them in a dict dumped to "rooms_by_school_file"
    :return:
    """

    school_list = get_schools()

    rooms_by_school_dict = dict()

    for school in school_list:
        rooms = get_rooms(school)

        if len(rooms) > 0:
            rooms_by_school_dict[school] = rooms
        else:
            continue

    total_rooms = sum([len(x) for x in rooms_by_school_dict.values()])

    print("Found", total_rooms, "different rooms at", len(rooms_by_school_dict), "schools")

    pickle.dump(rooms_by_school_dict, open("rooms_by_school_file_test", "wb"))  # Pickles the result

    return
