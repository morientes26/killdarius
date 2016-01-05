import os
from datetime import datetime

from pony.orm import PrimaryKey, Required, Set, Optional, Database, db_session

db = Database()


class Progress(db.Entity):
    id = PrimaryKey(int, auto=True)
    done = Optional(bool)
    task = Optional(lambda: Task)
    created_at = Required(datetime, sql_default='CURRENT_TIMESTAMP')


class Task(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 126)
    created_at = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    progress = Set(Progress, cascade_delete=True)
    user = Required(lambda: User)
    count = Required(int, default=0)
    reset = Required(bool, default=True)
    once = Optional(bool, default=True)
    group = Optional(lambda: Group)


class Timeline(db.Entity):
    key = PrimaryKey(str)
    created_at = Required(datetime, sql_default='CURRENT_TIMESTAMP')
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
    nickname = Optional(str, 32)
    icon_color = Optional(str, 20, default="primary")


class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, 126, default='bez mena')
    tasks = Set(Task, cascade_delete=True)
    key = Required(str, 32)
    label = Optional(str, 32, nullable=True)
    description = Optional(str, 256, nullable=True)


def connect_db(db_uri):
    db_type = 'sqlite'
    #db.bind(db_type, db_uri, create_db=False)
    db.bind('postgres', user='kmtuhklmcrudbw', password='9kQ2PawPQ4FwRMbqj0OvbDyuN2', host='ec2-54-204-12-25.compute-1.amazonaws.com', database='dac4ur43v1c3od')
    db.generate_mapping(create_tables=False)


def create_db(db_uri):
    db_type = 'sqlite'
    db.bind('postgres', user='kmtuhklmcrudbw', password='9kQ2PawPQ4FwRMbqj0OvbDyuN2', host='ec2-54-204-12-25.compute-1.amazonaws.com', database='dac4ur43v1c3od')
    #db.bind(db_type, db_uri, create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def create_test_data():
    key = '0000'
    person = User(name='mori', password='mori')
    timeline = Timeline(name='test timeline', owner=person, user=person, key=key)
    person.timeline = timeline
    task = Task(name='chodievat plavat kazdy den', count=7, reset=True, user=person, created_at='2015-01-01 00:00:00')

    Progress(task=task, created_at='2015-01-01 00:00:00')

    person2 = User(name='lucia', password='lucia')
    task2 = Task(name='chodievat plavat kazdy den', count=7, reset=True, user=person2, created_at='2015-01-01 00:00:00')

    Progress(task=task2, created_at='2015-01-01 00:00:00')

    Group(name='Skupina 1', tasks=[task, task2], key=key, label="11.10.2015 - 11.01.2016")
    Group(name='Skupina 2', tasks=[task], key=key, description="Lorem ipsum dolor sit amet, consectetur adipisicing elit. Autem dolorem quibusdam, tenetur commodi provident cumque magni voluptatem libero, quis rerum. Fugiat esse debitis optio, tempore. Animi officiis alias, officia repellendus.")


def initialize_db_environment():
    uri = 'postgres://kmtuhklmcrudbw:9kQ2PawPQ4FwRMbqj0OvbDyuN2@ec2-54-204-12-25.compute-1.amazonaws.com:5432/dac4ur43v1c3od'
    #create_db('../data/killdarius.sqlite')
    create_db(uri)
    create_test_data()

if 'IMPORT_DB' in os.environ:
    print('creating DB and importing test data')
    initialize_db_environment()
