from flask import Flask, render_template, request, redirect, session
import socket
import reading_cache_test

app = Flask(__name__)
app.secret_key = 'test_password'

@app.route('/school/<school>', methods=['GET', "POST"])
def print_rooms(school=None, set_time="Current Time"):
    if request.method == "POST":
        if request.form.get("current_time_button"):
            selected_time = request.form["current_time_button"]
            session["set_time"] = selected_time
        else:
            selected_time = str(request.form["select_hour"]) + ":" + str(request.form["select_minute"])
            session["set_time"] = selected_time

    try:
        set_time = session["set_time"]
    except KeyError:
        app.logger.info("error no set time")

    if school is not None:
        if set_time != "Current Time":
            app.logger.info("set: " + session["set_time"])
            empty_rooms_to_print, occupied_rooms = reading_cache_test.empty_rooms_in_school(school, set_time)
        else:
            app.logger.info("Current time")
            empty_rooms_to_print, occupied_rooms = reading_cache_test.empty_rooms_in_school(school)
    else:
        empty_rooms_to_print = []
        occupied_rooms = []

    return render_template("show_rooms.html", school=school, room_list=empty_rooms_to_print,
                           occupied_rooms=len(occupied_rooms), occupied_room_list=occupied_rooms)


@app.route("/", methods=["GET","POST"])
def select_school():
    school = None
    if request.method == "POST":
        try:
            school = str(request.form["school"])
        except KeyError:
            pass

    if school is not None:
        if school not in [x.name for x in reading_cache_test.cache.load_schools()]:
            return render_template("enter_school_dropdown_extended.html", error_message=school)

        return redirect("/school/"+school)

    return render_template("enter_school_dropdown_extended.html", schools=[x.name for x in reading_cache_test.cache.load_schools()])

@app.route("/about", methods=["GET","POST"])
def load_about():
    return render_template("about.html")

@app.route("/contact", methods=["GET","POST"])
def load_contact():
    return render_template("contact.html")

@app.route("/base", methods=["GET","POST"])
def load_base():
    return render_template("base.html")


socket.getaddrinfo('localhost', 8080)
app.run('127.0.0.1', debug=True)