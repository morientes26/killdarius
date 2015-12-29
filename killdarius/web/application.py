from flask import Flask, render_template, redirect, url_for, request, session, flash

from killdarius.model.entity import *

application = Flask(__name__)
application.jinja_env.add_extension('jinja2.ext.loopcontrols')

# set the secret key.  keep this really secret:
application.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
application.config['TEST_USER'] = "anonym-224"
application.config['ADMIN_USER'] = "morientes"


connect_db()


@application.route("/")
def index():
    return render_template('index.html')


@application.route('/anonym-login/')
@db_session
def generate():
    session['key'] = generate_key()
    return redirect("/timeline/"+session['key'])


@application.route('/login/', methods=['GET', 'POST'])
@db_session
def login():
    if request.method == 'POST':
        if not login_validation(request.form['username'], request.form['password']):
            flash('Nesprávne heslo', 'error')
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['user_id'] = find_user_by_name(request.form['username']).id
            key = get_last_created_key_by_username(request.form['username'])
            session['key'] = key
            return redirect("/timeline/" + key)
    return render_template('index.html')


def login_validation(username, password):
    if username == application.config['TEST_USER']:
        return True
    else:
        return is_valid_login_user(username, password)


@application.route('/logout/')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('key', None)
    return redirect(url_for('index'))


@application.route('/timeline/<key>')
@db_session
def show_tasks(key=None):
    if key == "":
        redirect(url_for('index'))

    groups = find_all_groups(key)
    users = find_all_user_in_timeline(key)

    return render_template('timeline.html', groups=groups, key=key, users=users)


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
                        session['user_id'],
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
