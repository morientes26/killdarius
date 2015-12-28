import uuid

from flask import Flask, render_template, redirect, url_for, request, session, flash

from killdarius.model.entity import *

application = Flask(__name__)

# set the secret key.  keep this really secret:
application.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

connect_db()


@application.route("/")
def index(key=""):
    if 'key' in session:
        key = session['key']

    return render_template('index.html', key=key)


@application.route('/generate/')
@db_session
def generate():
    session['key'] = uuid.uuid4().hex[:8]
    return redirect("/timeline/"+session['key'])


@application.route('/login/', methods=['POST'])
@db_session
def login():
    if validate_login_key(request.form['key']):
        session['key'] = request.form['key']
    else:
        flash('Kľúč neexistuje', 'error')
        return redirect("/")

    return redirect("/timeline/"+request.form['key'])


def validate_login_key(key):
    check = find_all_groups(key)
    if check:
        return True
    else:
        return False


@application.route('/timeline/<key>')
@db_session
def show_tasks(key=None):
    if key == "":
        redirect(url_for('index'))

    groups = find_all_groups(key)

    return render_template('timeline.html', groups=groups, key=key)


@application.route('/timeline/task/create/', methods=['POST'])
@db_session
def create_task():
    if request.form['taskname'] != "":
        if 'reset' in request.form:
            reset = True
        else:
            reset = False
        create_new_task(request.form['taskname'],
                        request.form['key'],
                        request.form['count'],
                        reset,
                        request.form['group_id'])
    return redirect('/timeline/'+request.form['key'])


@application.route('/timeline/group/create/', methods=['POST'])
@db_session
def create_group():
    if request.form['name'] != "":
        create_new_group(request.form['name'], request.form['description'], request.form['key'])
    return redirect('/timeline/'+request.form['key'])


@application.route('/timeline/group/rename/', methods=['POST'])
@db_session
def rename_selected_group():
    if request.form['name'] != "":
        rename_group(request.form['name'], request.form['description'], request.form['group_id'])
    return redirect('/timeline/'+request.form['key'])


@application.route('/timeline/task/pass/<int:id>', methods=['GET'])
@db_session
def pass_chosen_task(id=None):
    task = find_one_task(id)
    done_task(task)
    return redirect('/timeline/'+session['key'])


@application.route('/timeline/task/fail/<int:id>')
@db_session
def fail_chosen_task(id=None):
    task = find_one_task(id)
    fail_task(task)
    return redirect('/timeline/'+session['key'])


@application.route('/timeline/task/remove/<int:id>')
@db_session
def remove_chosen_task(id=None):
    delete_task(id)
    return redirect('/timeline/'+session['key'])


@application.route('/timeline/group/delete/<int:id>')
@db_session
def remove_chosen_group(id=None):
    delete_group(id)
    return redirect('/timeline/'+session['key'])

if __name__ == "__main__":
    application.run(debug=True)
