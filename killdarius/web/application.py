import os


from flask import Flask, render_template, redirect, url_for, request, session, flash
#from flask.ext.pystmark import Pystmark, Message
#from pystmark import ResponseError
from killdarius.ext.flask_pystmark import Pystmark
from killdarius.model.api import *
from killdarius.model.entities import connect_db
from killdarius.web.filter import count_done_task, count_fail_task

application = Flask(__name__)
application.jinja_env.filters['count_done_task'] = count_done_task
application.jinja_env.filters['count_fail_task'] = count_fail_task
application.config['PYSTMARK_API_KEY'] = 'a7e112c2-2569-461f-9d17-ff3361e2553b'
application.config['PYSTMARK_DEFAULT_SENDER'] = 'morienstudio@gmail.com'
pystmark = Pystmark(application)

application.jinja_env.add_extension('jinja2.ext.loopcontrols')

if 'KILLDARIUS_MODE' in os.environ:
    application.config.from_pyfile('killdarius.'+os.environ['KILLDARIUS_MODE']+'_settings')
    print("Application running in "+os.environ['KILLDARIUS_MODE']+" mode")
else:
    application.config.from_pyfile('killdarius.settings')
    print("Application running in production mode")

logging.basicConfig(filename='killdarius.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

connect_db(application.config['DATABASE_URI'])


@application.route("/")
def index():
    return render_template('index.html')


@application.route('/anonym-login/')
@db_session
def generate():
    session['key'] = generate_key()
    return redirect("/timeline/" + session['key'])


@application.route('/login/', methods=['GET', 'POST'])
@db_session
def login():
    if request.method == 'POST':
        if not login_validation(request.form['username'], request.form['password']):
            flash('Nesprávne heslo', 'error')
            logging.error("Nesprávne heslo [%s]", request.form['username'])
        else:
            session['username'] = request.form['username']
            session['user_id'] = find_user_by_name(request.form['username']).id
            key = get_last_created_key_by_username(request.form['username'])
            session['key'] = key
            logging.info("login success [%s]", request.form['username'])
            return redirect("/timeline/" + key)
    return render_template('index.html')


def login_validation(username, password):
    return is_valid_login_user(username, password)


@application.route('/logout/')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('key', None)
    return redirect(url_for('index'))


@application.route('/user/password/', methods=['POST'])
def set_password():
    if request.form['password']!="" and request.form['password'] == request.form['password2']:
        set_user_password(session["user_id"], request.form['password'])
        flash("Heslo úspešne nastavené")
    else:
        return redirect('/timeline/' + session['key']+ "?promt=1&error=Zle zadané heslo!")

    return redirect('/timeline/' + session['key'])


@application.route('/user/profile/', methods=['POST'])
def set_profile():
    set_user_profile(session["user_id"], request.form['alias'], request.form['icon_color'])
    flash("Profil úspešne nastavený")

    return redirect('/timeline/' + session['key'])


@application.route('/timeline/<key>')
@db_session
def show_tasks(key=None):
    if key == "":
        redirect(url_for('index'))

    session['key'] = key

    if not authorize(key, session):
        flash("Nemate opravnenie vidiet obsah stranky")
        return redirect(url_for('index'))

    groups = find_all_groups(key)
    users = find_all_user_in_timeline(key)
    timelines = find_all_user_timeline(session['user_id'])
    progression = count_progression(groups)
    promt = request.args.get('promt')
    error = request.args.get('error')

    return render_template('timeline.html', groups=groups, key=key,
                                            users=users, timelines=timelines,
                                            progression=progression, promt=promt, error=error)


@application.route('/timeline/task/create/', methods=['POST'])
@db_session
def create_task():
    if request.form['taskname'] != "":
        reset = False
        once = False
        if 'reset' in request.form:
            reset = True
        if 'once' in request.form:
            once = True

        create_new_task(request.form['taskname'],
                        request.form['key'],
                        request.form['count'],
                        session['user_id'],
                        reset,
                        once,
                        request.form['group_id'])
    return redirect('/timeline/' + request.form['key'])


@application.route('/timeline/create/', methods=['POST'])
@db_session
def create_timeline():
    session['key'] = generate_key()
    create_new_timeline(session['key'], session['user_id'], request.form['name'])
    return redirect("/timeline/" + session['key'])


@application.route('/timeline/share/', methods=['POST', 'GET'])
@db_session
def share_timeline():
    if request.method == 'POST':
        key = session['key']
        from_user = find_user_by_name(session['username'])
        emails = request.values.getlist('emails')
        share_timeline_to_email(from_user, emails, key, pystmark, application)
        logging.info("share timeline : [%s]", key)
        flash("Kontaktom bola odoslaná požiadavka na zdielanie timelinu")
        return redirect("/timeline/" + key)
    else:
        username = request.args.get('user')
        key = request.args.get('key')
        user = add_user_to_db(username, key)
        session['username'] = username
        session['user_id'] = user.id
        session['key'] = key
        flash("Vitaj, "+user.name+" v zdielanom timeline")
        logging.info("share login : [%s]", user.name)
        promt = ""
        if user.password == "..empty..":
            promt = "?promt=1"

        return redirect("/timeline/" + key + promt)


@application.route('/timeline/group/create/', methods=['POST'])
@db_session
def create_group():
    if request.form['name'] != "":
        create_new_group(request.form['name'], request.form['description'], request.form['key'])
    return redirect('/timeline/' + request.form['key'])


@application.route('/timeline/group/rename/', methods=['POST'])
@db_session
def rename_selected_group():
    if request.form['name'] != "":
        rename_group(request.form['name'], request.form['description'], request.form['group_id'])
    return redirect('/timeline/' + request.form['key'])


@application.route('/timeline/task/pass/<int:id>', methods=['GET'])
@db_session
def pass_chosen_task(id=None):
    user = find_user_by_name(session['username'])
    if not has_access_to_task(user, id):
        flash("Nemáte oprávnenie manažovať túto úlohu. Nie ste vlastníkom úlohy", "error")
        return redirect('/timeline/' + session['key'])

    if not can_progress_task(id):
        flash("Dnes už bola vykonaná aktivita pre úlohu. Ďalšia aktivita povolená až zajtra", "error")
        return redirect('/timeline/' + session['key'])

    task = find_one_task(id)
    done_task(task)
    return redirect('/timeline/' + session['key'])


@application.route('/timeline/task/fail/<int:id>')
@db_session
def fail_chosen_task(id=None):
    user = find_user_by_name(session['username'])
    if not has_access_to_task(user, id):
        flash("Nemáte oprávnenie manažovať túto úlohu. Nie ste vlastníkom úlohy", "error")
        return redirect('/timeline/' + session['key'])
    task = find_one_task(id)
    fail_task(task)
    return redirect('/timeline/' + session['key'])


@application.route('/timeline/task/remove/<int:id>')
@db_session
def remove_chosen_task(id=None):
    user = find_user_by_name(session['username'])
    if not has_access_to_task(user, id):
        flash("Nemáte oprávnenie manažovať túto úlohu. Nie ste vlastníkom úlohy", "error")
        return redirect('/timeline/' + session['key'])
    delete_task(id)
    return redirect('/timeline/' + session['key'])


@application.route('/timeline/group/delete/<int:id>')
@db_session
def remove_chosen_group(id=None):
    delete_group(id)
    return redirect('/timeline/' + session['key'])


if __name__ == "__main__":
    application.run(debug=True)

