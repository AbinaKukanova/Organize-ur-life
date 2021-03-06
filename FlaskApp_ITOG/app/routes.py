import os, random, pathlib
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request
from flask import send_file
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import current_user, login_user
from app.models import User, Todo
from flask_login import login_user, current_user, logout_user, login_required
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import date
import collections

# 1 страница - домашняя
@app.route('/', methods=["POST", "GET"])
def home():
    complete_today = Todo.query.filter_by(complete=True).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.created_on).all()
    incomplete_today = []
    incomplete_old = []
    now_date = str(datetime.now().date())
    for stroka in list(Todo.query.filter_by(complete=False).order_by(Todo.created_on).all()):
        if now_date in str(stroka.created_on):
            incomplete_today.append(stroka)
        else:
            incomplete_old.append(stroka)
    now_date = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
    with open('app/templates/quotes.txt', encoding="UTF-8") as f:
        if request.method == 'GET':
            n = random.randint(0, 11)
            n *= 2
            k = 0
            for line in f:
                if k == n:
                    line1 = line
                elif k == n + 1:
                    return render_template('home.html', incomplete=incomplete_today, complete=complete_today,
                                           incomplete_old=incomplete_old, line1=line1, line=line, now_date=now_date)
                k += 1

@app.route('/sort_incomplete/<type_sort>', methods=["POST", "GET"])
def sort_incomplete(type_sort):
    t_s = str(type_sort)
    incomplete_old = []
    for stroka in list(Todo.query.filter_by(complete=False).order_by(Todo.created_on).all()):
        if str(datetime.now().date()) not in str(stroka.created_on):
            incomplete_old.append(stroka)
    if t_s == "date":
        incomplete_today = Todo.query.filter_by(complete=False).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.created_on).all()
    elif t_s == "importance":
        incomplete_today = Todo.query.filter_by(complete=False).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.important.desc()).all()
    elif t_s == "deadline":
        incomplete_today = Todo.query.filter_by(complete=False).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.deadline).all()
    
    complete_today = Todo.query.filter_by(complete=True).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.created_on).all()
    now_date = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
    with open('app/templates/quotes.txt', encoding="UTF-8") as f:
        if request.method == 'GET':
            n = random.randint(0, 11)
            n *= 2
            k = 0
            for line in f:
                if k == n:
                    line1 = line
                elif k == n + 1:
                    return render_template('home.html', incomplete=incomplete_today, complete=complete_today, 
                    incomplete_old=incomplete_old, line1=line1, line=line, now_date=now_date)
                k += 1

@app.route('/sort_complete/<type_sort>', methods=["POST", "GET"])
def sort_complete(type_sort):
    t_s = str(type_sort)
    incomplete_old = []
    for stroka in list(Todo.query.filter_by(complete=True).order_by(Todo.created_on).all()):
        if str(datetime.now().date()) not in str(stroka.created_on):
            incomplete_old.append(stroka)
    if t_s == "date":
        complete_today = Todo.query.filter_by(complete=True).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.created_on).all()
    elif t_s == "importance":
        complete_today = Todo.query.filter_by(complete=True).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.important.desc()).all()
    elif t_s == "deadline":
        complete_today = Todo.query.filter_by(complete=True).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.deadline).all()
    
    incomplete_today = Todo.query.filter_by(complete=False).filter(Todo.created_on.contains(str(datetime.now().date()))).order_by(Todo.created_on).all()    
    now_date = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
    with open('app/templates/quotes.txt', encoding="UTF-8") as f:
        if request.method == 'GET':
            n = random.randint(0, 11)
            n *= 2
            k = 0
            for line in f:
                if k == n:
                    line1 = line
                elif k == n + 1:
                    return render_template('home.html', incomplete=incomplete_today, complete=complete_today, 
                    incomplete_old=incomplete_old, line1=line1, line=line, now_date=now_date)
                k += 1


@app.route('/add', methods=["POST", "GET"])
def add():
    if request.method == "POST":
        if request.form['deadline'] != "":
            todo = Todo(text=request.form['todoitem'], deadline=datetime.strptime(request.form['deadline'], "%Y-%m-%dT%H:%M"),
                        important=request.form['important'], complete=False)
        else:
            todo = Todo(text=request.form['todoitem'], important=request.form['important'], complete=False)
        db.session.add(todo)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/complete/<id>')
def complete(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    todo.complete = True
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/incomplete/<id>')
def incomplete(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    todo.complete = False
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete/<id>')
def delete(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/update/<id>', methods=['POST'])
def update(id):
    quer = Todo.query
    filtr = quer.filter_by(id=int(id))
    form_name = "todo_" + str(id)
    todo_text = request.form.get(form_name, "")
    upd_dict = {"text": todo_text}
    deadline_name = "deadline_" + str(id)
    todo_deadline = request.form.get(deadline_name, None)
    if todo_deadline is not None:
        upd_dict["deadline"] = datetime.fromisoformat(todo_deadline)
    filtr.update(upd_dict)
    db.session.commit()
    return redirect(url_for('home'))

# 2 страница - О проекте
@app.route("/about")
def about():
    return render_template('about.html', title='О проекте')

# 3,4 страницы - регистрация/вход
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not bcrypt.check_password_hash(user.password, form.password.data):
            flash('Что-то пошло не так. Пожалуйста, проверьте правильность введённых данных')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('account'))
    return render_template('login.html', title='Вход', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


# 5 страница - аккаунт
def user_pic(form_picture):
    chisla = [random.randint(0, 11) for i in range(8)]
    future_name = ''
    for a in chisla:
        a = str(a)
        future_name += a
    _, extension = os.path.splitext(form_picture.filename)
    profile_picture = future_name + extension
    profile_picture_path = os.path.join(app.root_path, 'static/profile', profile_picture)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(profile_picture_path)
    return profile_picture


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = user_pic(form.picture.data)
            current_user.image_file = picture_file
            image_file = url_for('static', filename='/profile/' + current_user.image_file)
        current_user.username = form.username.data
        current_user.email = form.email.data
        flash('Изменения успешно сохранены')
        db.session.commit()
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='/profile/' + current_user.image_file)
    count_all = len(Todo.query.all())
    count_complete_today = int()
    count_incomplete_today = int()
    count_all_today = int()
    if count_all != 0:
        for stroka in list(Todo.query.filter_by(complete=True).all()):
            now_date = str(datetime.now().date())
            if now_date in str(stroka.created_on):
                count_complete_today += 1
        for stroka2 in list(Todo.query.all()):
            now_date = str(datetime.now().date())
            if now_date in str(stroka2.created_on):
                count_all_today += 1
        if count_all_today != 0:
            count_incomplete_today = count_all_today - count_complete_today
            percentage_1 = round(count_complete_today / count_all_today, 2)
            percentage_2 = round(1 - percentage_1, 2)
            values = [percentage_1, percentage_2]
            labels = ['завершено', 'не завершено']
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
            fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            colors = ['#637cfb', '#bebebe']
            fig.update_traces(textfont_size=28, marker=dict(colors=colors, line=dict(color='#000000', width=2)))
            fig.write_image(str(pathlib.Path('app/static/images/op.svg')), format='svg')

    else:
        values = [1, 0]
        labels = ['завершено', 'не завершено']
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo="none", hole=.5)])
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        colors = ['#637cfb', '#bebebe']
        fig.update_traces(textfont_size=28, marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.write_image(str(pathlib.Path('app/static/images/op.svg')), format='svg')

    return render_template('account.html', title='Личный кабинет',
                           image_file=image_file, form=form, count_complete=count_complete_today,
                           count_incomplete=count_incomplete_today)


@app.route("/account/page2", methods=['GET', 'POST'])
@login_required
def countdown():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = user_pic(form.picture.data)
            current_user.image_file = picture_file
            image_file = url_for('static', filename='/profile/' + current_user.image_file)
        current_user.username = form.username.data
        current_user.email = form.email.data
        flash('Изменения успешно сохранены')
        db.session.commit()
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='/profile/' + current_user.image_file)

    count_all = len(Todo.query.all())
    count_complete_today = int()
    count_incomplete_today = int()
    count_all_today = int()
    if count_all != 0:
        for stroka in list(Todo.query.filter_by(complete=True).all()):
            now_date = str(datetime.now().date())
            if now_date in str(stroka.created_on):
                count_complete_today += 1
        for stroka2 in list(Todo.query.all()):
            now_date = str(datetime.now().date())
            if now_date in str(stroka2.created_on):
                count_all_today += 1
        if count_all_today != 0:
            count_incomplete_today = count_all_today - count_complete_today
            percentage_1 = round(count_complete_today / count_all_today, 2)
            percentage_2 = round(1 - percentage_1, 2)
            values = [percentage_1, percentage_2]
            labels = ['завершено', 'не завершено']
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
            fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            colors = ['#637cfb', '#bebebe']
            fig.update_traces(textfont_size=28, marker=dict(colors=colors, line=dict(color='#000000', width=2)))
            fig.write_image(str(pathlib.Path('app/static/images/op.svg')), format='svg')

    else:
        values = [1, 0]
        labels = ['завершено', 'не завершено']
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo="none", hole=.5)])
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        colors = ['#637cfb', '#bebebe']
        fig.update_traces(textfont_size=28, marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.write_image(str(pathlib.Path('app/static/images/op.svg')), format='svg')

    if request.method == 'POST':
        if request.form.get('t'):
            if 't' in request.form:
                t = request.form['t']
                t = int(t)
                uved = 'Время вышло'
                timer = str()
                list6 = []
                while t >= 0:
                    mins, secs = divmod(t, 60)
                    timer = '{:02d}:{:02d}'.format(mins, secs)
                    t -= 1
                    list6.append(timer)
                return render_template('account_page2.html', title='Личный кабинет',
                                       image_file=image_file, form=form, count_complete=count_complete_today,
                                       count_incomplete=count_incomplete_today, uved=uved, list6=list6)
            else:
                uved = 'Некорректный запрос'
                return render_template('account_page2.html', title='Личный кабинет',
                                       image_file=image_file, form=form, count_complete=count_complete_today,
                                       count_incomplete=count_incomplete_today, uved=uved)

    return render_template('account_page2.html', title='Личный кабинет',
                           image_file=image_file, form=form, count_complete=count_complete_today,
                           count_incomplete=count_incomplete_today)


@app.route("/account/chart1")
def chart1():
    path_chart1 = os.path.join(app.config['UPLOAD_FOLDER'], 'op.svg')
    return send_file(path_chart1)


@app.route("/account/chart2")
def chart2():
    dict = {
        'Пн': 0,
        'Вт': 1,
        'Ср': 2,
        'Чт': 3,
        'Пт': 4,
        'Сб': 5,
        'Вс': 6,
    }
    dict2 = {
        'Пн': 0,
        'Вт': 0,
        'Ср': 0,
        'Чт': 0,
        'Пт': 0,
        'Сб': 0,
        'Вс': 0,
    }
    plt.plot()
    stroki = Todo.query.filter_by(complete=True).order_by(Todo.created_on).all()
    last_monday = int()
    for r in range(0, len(stroki)):
        if stroki[r].created_on.weekday() == 0:
            last_monday = r
    for rr in range(last_monday, len(stroki)):
        for b in dict.keys():
            if stroki[rr].created_on.weekday() == dict[b]:
                dict2[b] += 1
    x = [str(x) for x in dict2.keys()]
    y = [int(y) for y in dict2.values()]
    fig, ax = plt.subplots()
    ax.bar(x, y)
    plt.grid()
    buf2 = BytesIO()
    plt.savefig(buf2)
    buf2.seek(0)
    return send_file(buf2, mimetype='img/png')


@app.route("/account/image1")
def image1():
    path_image1 = os.path.join(app.config['UPLOAD_FOLDER'], 'кот1.gif')
    return send_file(path_image1)


@app.route("/account/image2")
def image2():
    path_image2 = os.path.join(app.config['UPLOAD_FOLDER'], 'кот2.png')
    return send_file(path_image2)

# 6 страница - календарь
@app.route("/calendar", defaults={'yr': None, 'mn': None})
@app.route("/calendar/<yr>/<mn>")
def calendar(yr, mn):
    if yr is None and mn is None:
        today_dt = datetime.today()
        yr = today_dt.year
        mn = today_dt.month
    mn = int(mn)
    start_dt = datetime(year=int(yr), month=mn, day=1)
    end_dt = datetime(year=int(yr), month=(mn + 1 if mn < 12 else 1), day=1)
    month_tasks = collections.defaultdict(list)
    for task_todo in list(Todo.query.filter((Todo.created_on >= start_dt) & (Todo.created_on < end_dt)).all()):
        day_key = task_todo.created_on.day
        month_tasks[day_key].append([task_todo.text, task_todo.complete, task_todo.created_on, task_todo.deadline, task_todo.important])

    month_deadlines = []
    for task_todo in list(Todo.query.filter((Todo.deadline >= start_dt) & (Todo.deadline < end_dt)).order_by(Todo.deadline).all()):
        month_deadlines.append(task_todo)

    return render_template('calendar.html', title='Календарь', c_year=yr, c_month=mn, mn_tasks=month_tasks, mn_deadlines=month_deadlines)
