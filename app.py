from flask import Flask, render_template
from flask_cors import CORS

from routes.courses import courses_bp
from routes.teachers import teachers_bp
from routes.rooms import rooms_bp
from routes.sections import sections_bp
from routes.schedule import schedule_bp

app = Flask(__name__, template_folder="Frontend")
CORS(app)

app.register_blueprint(courses_bp)
app.register_blueprint(teachers_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(sections_bp)
app.register_blueprint(schedule_bp)


@app.get("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
