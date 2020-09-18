import pickle
import time
from itertools import islice
from multiprocessing.pool import ThreadPool

import get_date_times
import schedule_extractor
import school_cache


class School:
    def __init__(self, name):
        self.name = name
        self.rooms = self.read_rooms_file()
        self.update_room_schedules()

    def empty_rooms(self, current_time):
        """Returns all the empty rooms at the time and for how long"""

        empty_rooms_list = []

        for each in self.rooms:
            time_until_occupied = each.time_until_occupied(get_date_times.day_of_week(), current_time)

            if time_until_occupied > 0:
                empty_rooms_list.append((each, time_until_occupied))

        return empty_rooms_list

    def update_room_schedules(self):
        """Sets all schedules to current"""

        print("started schedule update for", self.name)

        threads = 8

        for rooms_chunk in chunk(self.rooms, threads):

            print("Starting", rooms_chunk[0].name, "->", rooms_chunk[-1].name)

            # This is left to catch which error occurs
            try:
                pool = ThreadPool(threads)

                paired_arguments = [(school_name, room_name) for school_name, room_name in
                                    zip([self.name for i in range(len(rooms_chunk))], rooms_chunk)]

                # Starmaps maps a list of arguments to a function
                results = pool.starmap(schedule_extractor.extract_schedule, paired_arguments)

                for room, result in zip(rooms_chunk, results):
                    room.schedule = result

                print("Finished", rooms_chunk[0].name, "->", rooms_chunk[-1].name)
            except:
                print("Failed", rooms_chunk[0].name, "->", rooms_chunk[-1].name)

    def read_rooms_file(self):
        with open("saved_files/rooms_by_school_file", "rb") as f:
            rooms_by_school_dict = pickle.load(f)

            room_names = rooms_by_school_dict[self.name]

            room_list = []

            for name in room_names:
                new_room = Room(self.name, name, None)
                room_list.append(new_room)
            return room_list

    def print_rooms_schedule(self):
        for room in self.rooms:
            print()
            print("Room:", room.name)
            for day, times in room.schedule.items():
                if len(times) == 0:
                    continue
                else:
                    print(day)
                    for time in times:
                        print("    ", time)


class Room:
    def __init__(self, school, name, schedule):
        self.school = school
        self.name = name
        self.url = schedule_extractor.create_url(school, name)
        self.schedule = schedule

    def time_until_occupied(self, day, current_time):
        """
        :param day: string, 0-4 index of day
        :param current_time: date and time string in hh:mm format
        :return: time in string hh:mm format
        """
        for time_stamp in self.schedule[day]:
            if not schedule_extractor.is_between(current_time, time_stamp):
                print(schedule_extractor.time_between(current_time, time_stamp[0]))
                return schedule_extractor.time_between(current_time, time_stamp[0])
            else:
                continue

        return 0


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def read_schools(rooms_school_file):
    with open(rooms_school_file, "rb") as file_handler:
        schools_dict = pickle.load(file_handler)

        schools_list = list(schools_dict.keys())

        return schools_list


def create_schedule_file():
    start_time = time.time()

    to_save = (read_schools("saved_files/rooms_by_school_file"))

    # Sets how many schools are calculated simultaneously
    my_pool = ThreadPool(1)

    # Creates school objects
    schools = my_pool.map(School, to_save)

    # Saves to cache
    cache = school_cache.SchoolCache("saved_files/saved_schools_week_" + str(get_date_times.get_week()))

    time_saving = time.time()
    cache.save_schools(schools)
    print("Saving took", round(time.time() - time_saving, 2), "seconds")

    # Count the rooms
    total_rooms = 0
    for school in cache.load_schools():
        for each in school.rooms:
            total_rooms += 1

    print()
    print("Schools updated:", len(schools))
    print("Rooms updated:", total_rooms)
    print()
    print("It took", round(time.time() - start_time), "seconds to complete update")
    print("Average room time:", round((time.time() - start_time) / total_rooms, 2), "seconds")


if __name__ == "__main__":
    create_schedule_file()
