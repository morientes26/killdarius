import logging
from datetime import datetime
from pony.orm import Database, Required, Set, PrimaryKey, db_session, Optional, select, desc

db = Database()


# logging.basicConfig(filename='pony.log', level=logging.INFO)


class Progress(db.Entity):
    id = PrimaryKey(int, auto=True)
    done = Optional(bool)
    task = Optional("Task")


class Task(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 126)
    created_at = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    progress = Set(Progress, cascade_delete=True)
    count = Required(int, default=0)
    reset = Required(bool, default=True)
    group = Optional("Group")


class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 126, default='bez mena')
    tasks = Set(Task, cascade_delete=True)
    key = Required(str, 32)


def connect_db():
    db.bind('sqlite', '../data/killdarius.sqlite', create_db=False)
    db.generate_mapping(create_tables=False)


def create_db():
    db.bind('sqlite', '../data/killdarius.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def create_new_task(name, key, count, reset=False, group_id=None, progress=None):
    task = Task(name=name, count=count, reset=reset)
    if progress:
        pr = []
        for p in progress:
            pt = Progress()
            pt.task = task
            pt.done = p
            pr.append(pt)
        task.progress = pr
    if group_id:
        group = Group.get(id=group_id)
    else:
        group = Group(tasks=[task], key=key)

    task.group = group
    return task


@db_session
def create_new_group(name, key):
    return Group(name=name, tasks=[], key=key)


@db_session
def done_task(task):
    p = Progress()
    p.done = True
    p.task = task


@db_session
def fail_task(task):
    list_progress = Progress.select(lambda p: p.task == task).order_by(lambda p: desc(p.id))[:]

    # remove all progress if 2x fail
    if list_progress.__len__() > 0 and not list_progress[0].done and task.reset:
        for prog in list_progress:
            prog.delete()
    else:
        p = Progress()
        p.done = False
        p.task = task


@db_session
def find_one_task(id):
    return Task.get(id=id)


@db_session
def find_all_task():
    tasks = select(t for t in Task)[:]
    return tasks


@db_session
def find_all_groups(key):
    groups = select(g for g in Group if g.key==key)[:]
    return groups


@db_session
def delete_task(id):
    task = find_one_task(id)
    if task.progress:
        for progress in task.progress:
            progress.delete()
    task.delete()


@db_session
def delete_group(id):
    group = Group.get(id=id)
    group.delete()


@db_session
def delete_tasks():
    for task in find_all_task():
        delete_task(task.id)


#create_db()
# with db_session:
#     for task in find_all_task():
#         delete_task(task.id)
#
#     p1 = Progress()
#     p1.done = True
#     p2 = Progress()
#     p2.done = False
#     task = create_task("Goldenhruska", [True, True])

# done_task(task)
# fail_task(task)
# fail_task(task)
# fail_task(task)
# print(task)
# find_task = find_one_task(1)
# print(find_task)
# find_task = Task.get(name="Behat2")
# print(find_task)
