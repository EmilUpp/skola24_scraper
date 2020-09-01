import os
import pickle
import stat
import time


def difference_schools_room(original_file, new_file):
    # Unpickle the files
    original_dict = pickle.load(open(original_file, "rb"))
    new_dict = pickle.load(open(new_file, "rb"))

    removed_schools = 0
    removed_rooms = 0

    added_schools = 0
    added_rooms = 0

    # Checks which schools and rooms that have been removed
    for school, rooms in original_dict.items():
        if school not in new_dict.keys():
            print(school, "was removed")
            removed_schools += 1
            continue

        for room in rooms:
            if room not in new_dict[school]:
                removed_rooms += 1

    # Checks which schools and rooms that have been added
    for school, rooms in new_dict.items():
        if school not in original_dict.keys():
            print(school, "was added")
            added_schools += 1

            # If school is new all rooms are new
            for room in rooms:
                added_rooms += 1
        else:
            for room in rooms:
                if room not in original_dict[school]:
                    added_rooms += 1

    print("Comparing difference between files:")
    print()
    print(original_file, " " * abs(len(original_file) - len(new_file) + 1), "    last modified",
          last_modified(original_file))
    print(new_file, "    last modified", last_modified(new_file))
    print()
    print()
    print(added_schools, "schools has been added")
    print(removed_schools, "schools has been removed")
    print()
    print(added_rooms, "rooms has been added")
    print(removed_rooms, "rooms has been removed")
    print()


def last_modified(file_path):
    file_stats_obj = os.stat(file_path)
    modification_time = time.ctime(file_stats_obj[stat.ST_MTIME])

    return modification_time


if __name__ == "__main__":
    difference_schools_room("rooms_by_school_file", "rooms_by_school_file_test")
