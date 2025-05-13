from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import random


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "dev-energy"

# Classic to-do list model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# YouTube learning schedule model
class ScheduleTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer)
    focus_area = db.Column(db.String(100))
    topic = db.Column(db.String(255))
    tutorial = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)


FLIRTY_MESSAGES = [
    "🔥 You just crushed that. Are you always this impressive?",
    "✨ One step closer to global domination… or maybe just being super cute and productive.",
    "💡 Task complete! Can’t believe brains AND looks — unfair.",
    "🚀 If you were a course, I’d binge-watch you.",
    "🌟 Impressive progress. Got a secret? Asking for a friend. (It’s me. I’m the friend.)",
    "🧠 Smart. Motivated. Attractive. You’re basically a startup founder now.",
    "💬 If productivity was attractive, you’d be off the charts.",
    "📈 At this rate, you’re gonna outshine the sun by week 3.",
    "🎯 Task complete! Bet your playlists are just as fire.",
    "🥇 You + discipline = unstoppable (also, maybe take me on a coffee date?)"
]

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    content = request.form.get('content')
    if content:
        new_task = Task(content=content)
        db.session.add(new_task)
        db.session.commit()
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

@app.route('/complete/<int:task_id>')
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect('/')

@app.route('/schedule')
def show_schedule():
    tasks = ScheduleTask.query.order_by(ScheduleTask.day).all()
    return render_template('schedule.html', tasks=tasks)

@app.route('/toggle_schedule/<int:task_id>')
def toggle_schedule(task_id):
    task = ScheduleTask.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()

    if task.completed:
        flirt = random.choice(FLIRTY_MESSAGES)
        flash(flirt)
    else:
        flash("Task marked incomplete — taking a break is still valid 😌")

    return redirect('/schedule')

@app.route('/import_schedule')
def import_schedule():
    df = pd.read_excel("./data/schedule.xlsx", header=1)
    df = df.rename(columns={
        df.columns[0]: "Day",
        df.columns[1]: "Focus Area",
        df.columns[2]: "Topic",
        df.columns[3]: "YouTube Tutorial"
    }).dropna(how='all')

    # Clean up: only import rows where Day is a number
    for _, row in df.iterrows():
        try:
            day = int(row['Day'])  # This will skip "Week X" rows
        except (ValueError, TypeError):
            continue  # Skip bad rows

        task = ScheduleTask(
            day=day,
            focus_area=row['Focus Area'],
            topic=row['Topic'],
            tutorial=row['YouTube Tutorial']
        )
        db.session.add(task)

    db.session.commit()
    return "Schedule imported!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
