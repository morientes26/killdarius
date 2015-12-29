import logging
import uuid
from pony.orm import db_session, select, desc

from killdarius.ext.send_email import EmailNotification
from killdarius.model.entities import Progress, User, Group, Timeline, Task


def generate_key():
    return uuid.uuid4().hex[:8]


def authorize(key, session):
    if not 'user_id' in session:
        return False

    timeline = Timeline.get(key=key)
    user = User.get(id=session['user_id'])
    if user in timeline.user:
        return True
    else:
        return False


@db_session
def create_new_task(name, key, count, user_id, reset=False, group_id=None, progress=None):
    logging.debug("Create new task")
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

    timeline = Timeline.get(key=key)
    if not timeline:
        Timeline(key=key, owner=user, user=user)

    task.group = group
    return task


@db_session
def create_new_group(name, description, key):
    return Group(name=name, description=description, tasks=[], key=key)


@db_session
def create_new_timeline(key, user_id, name):
    user = User[user_id]
    # create default group
    create_new_group("skupina úloh č.1", "Predgenerovaná skupina úloh. V prípade potreby editujte popis a názov skupiny.", key)
    return Timeline(name=name, key=key, owner=user, user=user)


@db_session
def add_user_to_db(username, key):
    user = find_user_by_name(username)
    if not user:
        user = User(name=username, password="..empty..")
    timeline = Timeline.get(key=key)
    if user not in timeline.user:
        add_user_to_timeline(user, timeline)
    return user


@db_session
def set_user_password(user_id, password):
    user = User.get(id=user_id)
    user.password = password


@db_session
def share_timeline_to_email(from_user, emails, key):
    timeline = Timeline.get(key=key)
    e_notify = EmailNotification()

    for email in emails:
        user = User.get(name=email)
        if user:
            add_user_to_timeline(user, timeline)
        text = prepare_text(from_user, email, key)
        e_notify.send(email, text[0], text[1])


def add_user_to_timeline(user, timeline):
    users = [user]
    for u in timeline.user:
        users.append(u)
    timeline.user = users


def prepare_text(from_user, email, key):
    token = "?key="+key+"&user="+email
    share_url = "http://localhost:5000/timeline/share/"+token
    text = "Ahoj!\nBola ti poslaná notifikácia o zdielani timelinu v projekte KillDarius od používateľa <b>"+from_user.name+"</br>\nNotifikáciu si mǒžeš pozrieť kliknutím na link\n"+share_url
    html = "<html><head></head><body><p>Ahoj!<br>Bola ti poslaná notifikácia o zdielaní timelinu v projekte KillDarius od používateľa <b>"+from_user.name+"</b><br>Notifikáciu si mǒžeš pozrieť kliknutím na link <a href="+share_url+">link</a></p></body></html>"
    return [text, html]


@db_session
def count_progression(groups):
    progression = {}
    for group in groups:
        nn = 0
        i = 0
        for task in group.tasks:
            n = task.progress.__len__()
            n = (n / task.count) * 100
            nn += n
            i += 1
        if i > 0:
            progression[group.id] = int(nn / i)
        else:
            progression[group.id] = 0

    return progression


@db_session
def rename_group(name, description, id):
    group = Group.get(id=id)
    group.name = name
    group.description = description
    return group


@db_session
def has_access_to_task(user, task_id):
    task = find_one_task(task_id)
    if task in user.task:
        return True
    else:
        return False


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
def find_all_user_timeline(user_id):
    user = User.get(id=user_id)
    return select(t for t in Timeline if user in t.user)

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


