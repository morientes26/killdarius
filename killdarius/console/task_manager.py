"""
    Manager of tasks
"""


class TaskManager:

    def __init__(self, tasks):
        self.__tasks = tasks
        self.__count_of_fail = 0

    @property
    def tasks(self):
        return self.__tasks

    def add_task(self, task):
        self.__tasks.append(task)

    def pass_task(self, task):
        task.progress.append(True)

    def fail_task(self, task):
        task.progress.append(False)
        self.__count_of_fail += 1


    def show_tasks(self):
        for idx, task in enumerate(self.__tasks):
            print(idx, "->", task)
