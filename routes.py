import datetime
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, current_app


pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")


@pages.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        entry_content = request.form.get("content")
        formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
        current_app.db.entries.insert_one({"content": entry_content, "date": formatted_date})

    entries_with_date = [
        (
            entry["content"],
            entry["date"],
            datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%b %d"),
        )
        for entry in current_app.db.entries.find({})
    ]

    return render_template("home.html", entries=reversed(entries_with_date))


@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"date_range": date_range}


def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)


@pages.route("/habit/")
def habit():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date}})
    completions = [
        habit_id["habit"] for habit_id in current_app.db.completions.find({"date": selected_date})
        ]

    return render_template(
        "habit.html",
        habits=habits_on_date,
        title="Habit Tracker",
        selected_date=selected_date,
        completions=completions,
        )


@pages.route("/habit/add/", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()

    if request.form:
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit")}
        )

    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=today
    )


@pages.route("/habit/complete/", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    date = datetime.datetime.fromisoformat(date_string)
    habit_name = request.form.get("habitId")
    current_app.db.completions.insert_one({"date": date, "habit": habit_name})

    return redirect(url_for("habits.habit", date=date_string))
