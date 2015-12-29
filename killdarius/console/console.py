from pony.orm import commit, db_session

from killdarius.console.task import Task
from killdarius.console.task_manager import TaskManager
from killdarius.model.api import find_all_task, delete_tasks, create_db, create_new_task


class Application(object):
    @staticmethod
    def run():
        print("Application 'KillDarius' is starting\n")

        manager = TaskManager(Application().load_tasks())

        print("List of tasks:")
        manager.show_tasks()

        action = input("Choose action [0 - exit, 1 - Add progress to task, 2 - Create new task, 3 - Remove task]: ")
        assert action == "0" or action == "1" or action == "2" or action == "3", "action is not number 0,1,2 or 3"

        if action == "0":
            return

        # switcher for action
        {'1': lambda x: Application().set_progress(manager),
         '2': lambda x: Application().create_new_task(manager),
         '3': lambda x: Application().remove_task(manager),
         }[action](action)

        Application().save_resource(manager)

    @staticmethod
    def set_progress(manager):
        task_number = input("Choose number of task: ")
        assert len(manager.tasks) >= int(task_number), "number is bigger than number of task"

        pass_task = input("1 - pass task, 0 - fail task: ")
        assert pass_task == "0" or pass_task == "1", "action is not number 0 or 1"

        if pass_task == "1":
            manager.pass_task(manager.tasks[int(task_number)])
        else:
            manager.fail_task(manager.tasks[int(task_number)])

    @staticmethod
    def create_new_task(manager):
        name = input("Choose name of task: ")
        manager.tasks.append(Task(name))

    @staticmethod
    def remove_task(manager):
        task_number = input("Choose number of task: ")
        assert len(manager.tasks) >= int(task_number), "number is bigger than number of task"
        manager.tasks.remove(manager.tasks[int(task_number)])

    @staticmethod
    @db_session
    def load_tasks():
        tasks = []
        for task in find_all_task():
            task_tmp = Task(task.name)
            prog = []
            for d in sorted(task.progress):
                prog.append(d.done)

            task_tmp.progress = prog
            tasks.append(task_tmp)

        return tasks

    @staticmethod
    @db_session
    def save_resource(manager):
        delete_tasks()
        commit()
        for task in manager.tasks:
            create_new_task(task.name, "xxx", 7, False)


if __name__ == '__main__':
    Application().run()
