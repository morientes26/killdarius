"""
    Models class for created task
"""


class Task:
    def __init__(self, name):
        self.__name = name
        self.__progress = []

    @property
    def progress(self):
        return self.__progress

    @progress.setter
    def progress(self, progress):
        self.__progress = progress

    def add_progress(self, progress):
        assert type(progress) == bool, "progress has to be boolean"
        self.__progress.append(progress)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        assert name is not None, "name has to be set"
        if name == "":
            self.__name = "no value"
            return
        self.__name = name

    def __str__(self):
        progress = self.__process()
        return self.__class__.__name__ + "(" + self.__name + ") " + progress

    def __process(self):
        result = ""
        idx = 0
        for i in self.__progress:
            if i is False:
                idx += 1
            result += 'x' if i is True else '-'
            if idx == 2:
                result += '|'
                idx = 0
        return result
