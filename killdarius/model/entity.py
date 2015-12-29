import logging
import uuid
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
    user = Required("User")
    count = Required(int, default=0)
    reset = Required(bool, default=True)
    label = Optional(str, 32, nullable=True)
    group = Optional("Group")


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 32)
    password = Required(str, 32)
    task = Set(Task, cascade_delete=True)


class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 126, default='bez mena')
    tasks = Set(Task, cascade_delete=True)
    key = Required(str, 32)
    label = Optional(str, 32, nullable=True)
    description = Optional(str, 256, nullable=True)


def connect_db():
    db.bind('sqlite', '../data/killdarius.sqlite', create_db=False)
    db.generate_mapping(create_tables=False)


def create_db():
    db.bind('sqlite', '../data/killdarius.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)


def generate_key():
    return uuid.uuid4().hex[:8]


@db_session
def create_new_task(name, key, count, user_id, reset=False, group_id=None, progress=None):
    user = User[user_id]
    task = Task(name=name, user=user, count=count, reset=reset)
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
def create_new_group(name, description, key):
    return Group(name=name, description=description, tasks=[], key=key)


@db_session
def rename_group(name, description, id):
    group = Group.get(id=id)
    group.name = name
    group.description = description
    return group


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
    return select(g for g in Group if g.key==key).order_by(desc(Group.id))[:]


@db_session
def find_all_user_in_timeline(key):
    return select(u for u in User for t in Task if t.group.key==key).order_by(User.id)[:]


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


@db_session
def is_valid_login_user(username, password):
    if username and password:
        user = User.get(name=username, password=password)
        if user:
            return True
    return False


@db_session
def find_user_by_name(username):
    return User.get(name=username)


def get_last_created_key_by_username(name):
    tasks = select(t for t in Task if t.user.name==name).order_by(desc(Task.group))[:]
    if tasks:
        return tasks[0].group.key
    else:
        return generate_key()


@db_session
def create_test_data():
    key = '0000'
    person = User(name='mori', password='mori')
    task = Task(name='chodievat plavat kazdy den', count=7, reset=True, user=person)

    prog1 = Progress(task=task)

    person2 = User(name='lucia', password='lucia')
    task2 = Task(name='chodievat plavat kazdy den', count=7, reset=True, user=person2)

    prog2 = Progress(task=task2)

    Group(name='Skupina 1', tasks=[task, task2], key=key, label="11.10.2015 - 11.01.2016")
    Group(name='Skupina 2', tasks=[task], key=key, description="Lorem ipsum dolor sit amet, consectetur adipisicing elit. Autem dolorem quibusdam, tenetur commodi provident cumque magni voluptatem libero, quis rerum. Fugiat esse debitis optio, tempore. Animi officiis alias, officia repellendus.")

#create_db()
#create_test_data()

