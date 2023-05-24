import datetime
import os
from flask import Flask, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    client = MongoClient(os.getenv("MONGO_URI"))
    app.db = client.microblog

    habits = ['Test habit', 'Test habit 2']

    @app.route('/', methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            entry_content = request.form.get("content")
            formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
            app.db.entries.insert_one({"content": entry_content, "date": formatted_date})

        entries_with_date = [
            (
                entry["content"],
                entry["date"],
                datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%b %d"),
            )
            for entry in app.db.entries.find({})
        ]

        return render_template("home.html", entries=reversed(entries_with_date))

    @app.context_processor
    def add_calc_date_range():
        def date_range(start: datetime.date):
            dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
            return dates

        return {"date_range": date_range}

    @app.route("/habit/")
    def habit():
        date_str = request.args.get("date")
        if date_str:
            selected_date = datetime.date.fromisoformat(date_str)
        else:
            selected_date = datetime.date.today()
        return render_template(
            "habit.html",
            habits=habits,
            title="Habit Tracker",
            selected_date=selected_date
            )

    @app.route("/habit/add/", methods=["GET", "POST"])
    def add_habit():
        if request.method == "POST":
            habits.append(request.form.get("habit"))
        return render_template(
            "add_habit.html",
            title="Habit Tracker - Add Habit",
            selected_date=datetime.date.today()
        )

    return app


# if __name__ == '__main__':
#     create_app().run(debug=True)
