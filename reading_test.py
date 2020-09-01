import pickle


def write_to_text_file(d, file_path):
    """
    Writes the dict to a file in a more readable format (debug mostly)
    :param file_path: filepath, where to write
    :param d: dictonary
    :return:
    """
    with open(file_path, "w") as file_handler:
        for key, rooms in d.items():
            file_handler.write(key + ": " + str(len(rooms)) + " rooms\n")
            for room in rooms:
                if type(room) != str:
                    continue
                file_handler.write("    " + room + "\n")
            file_handler.write("\n")

    return True


if __name__ == "__main__":
    to_pickle_file = open("rooms_by_school_file", "rb")
    rooms_by_school_dict = pickle.load(to_pickle_file)

    for test_key, test_rooms in rooms_by_school_dict.items():
        print(test_key + ":", len(test_rooms), "rooms")
        for test_room in test_rooms:
            print("    ", test_room)
        print()

    write_to_text_file(rooms_by_school_dict, "rooms_by_school_pretty")
