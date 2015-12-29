import os
from datetime import datetime

from pony.orm import PrimaryKey, Required, Set, Optional, Database, db_session

db = Database()


class Progress(db.Entity):
    id = PrimaryKey(int, auto=True)
    done = Optional(bool)
    task = Optional(lambda: Task)


class Task(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 126)
    created_at = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    progress = Set(Progress, cascade_delete=True)
    user = Required(lambda: User)
    count = Required(int, default=0)
    reset = Required(bool, default=True)
    label = Optional(str, 32, nullable=True)
    group = Optional(lambda: Group)


class Timeline(db.Entity):
    key = PrimaryKey(str)
    name = Required(str, 126, default='timeline')
    user = Set(lambda: User)
    owner = Required(lambda: User)


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 32)
    password = Required(str, 32)
    task = Set(Task, cascade_delete=True)
    timeline = Set(Timeline)
    own_timeline = Set(Timeline, reverse="owner")


class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 126, default='bez mena')
    tasks = Set(Task, cascade_delete=True)
    key = Required(str, 32)
    label = Optional(str, 32, nullable=True)
    description = Optional(str, 256, nullable=True)


def connect_db(db_uri):
    db.bind('sqlite', db_uri, create_db=False)
    db.generate_mapping(create_tables=False)


def create_db(db_uri):
    db.bind('sqlite', db_uri, create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def create_test_data():
    key = '0000'
    person = User(name='mori', password='mori')
    timeline = Timeline(name='test timeline', owner=person, user=person, key=key)
    person.timeline = timeline
    task = Task(name='chodievat plavat kazdy den', count=7, reset=True, user=person)

    Progress(task=task)

    person2 = User(name='lucia', password='lucia')
    task2 = Task(name='chodievat plavat kazdy den', count=7, reset=True, user=person2)

    Progress(task=task2)

    Group(name='Skupina 1', tasks=[task, task2], key=key, label="11.10.2015 - 11.01.2016")
    Group(name='Skupina 2', tasks=[task], key=key, description="Lorem ipsum dolor sit amet, consectetur adipisicing elit. Autem dolorem quibusdam, tenetur commodi provident cumque magni voluptatem libero, quis rerum. Fugiat esse debitis optio, tempore. Animi officiis alias, officia repellendus.")


def initialize_db_environment():
    create_db('../data/killdarius.sqlite')
    create_test_data()

if 'IMPORT_DB' in os.environ:
    print('creating DB and importing test data')
    initialize_db_environment()
