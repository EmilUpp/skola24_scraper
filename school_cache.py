import dill


class SchoolCache:
    """
    A class for saving and loading schools and their associated rooms and schedule
    """

    def __init__(self, save_file_name):
        self.save_file_name = save_file_name
        self.already_saved = self.get_already_saved()

    def get_already_saved(self):
        """Loads already saved"""
        try:
            return [school.name for school in self.load_schools()]
        except EOFError:
            return []

    def save_schools(self, school_list):
        """
        Reads in new schools and pickles them to file
        :param school_list: list, schools to save
        :return: None
        """

        already_pickled = self.load_schools()

        with open(self.save_file_name, "wb") as file_handler:

            to_pickle = []

            for school in school_list:
                if school.name not in self.already_saved:
                    self.already_saved.append(school.name)

                    to_pickle.append(school)

                else:
                    continue

            already_pickled.extend(to_pickle)

            dill.dump(already_pickled, file_handler)

    def load_schools(self):
        """loads all schools"""
        try:
            with open(self.save_file_name, "rb") as file_handler:
                try:
                    unpickled = dill.load(file_handler)
                    return unpickled
                except EOFError:
                    return []
        except FileNotFoundError:
            return []

    def get_school(self, name):
        """return the school object with the given name from the saved schools"""
        with open(self.save_file_name, "rb") as file_handler:
            unpickled = dill.load(file_handler)

            for school in unpickled:
                if school.name == name:
                    return school
                else:
                    continue

            return False
