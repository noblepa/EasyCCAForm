from flask import Flask, render_template, request, send_file
import os
import tempfile

from formatter import process_file

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/download-template')
def download_template():
    path = os.path.join('static', 'marks_template.xlsx')
    return send_file(path, as_attachment=True)


# Process File (NO RETENTION)
@app.route("/process", methods=["POST"])
def process():
    temp_path = None  # track temp file for cleanup

    try:
        # Form data
        form_data = {
            "college": request.form["college"],
            "course_code": request.form["course_code"],
            "course_name": request.form["course_name"],
            "year": request.form["year"],
            "semester": request.form["semester"],
            "category": request.form["category"]
        }

        file = request.files.get("marks_file")

        if not file or file.filename == "":
            return "<h3>No file uploaded</h3>"

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp:
            file.save(temp.name)
            temp_path = temp.name

        # Process file
        result = process_file(temp_path)

        return render_template(
            "preview.html",
            table1=result["table1"].to_html(index=False),
            table2=result["table2"],
            co_columns=result["co_columns"],
            max_marks=result["max_marks"],
            eval_list=result["eval_list"],
            total_cca_max=result["total_cca_max"],
            num_cos=len(result["co_columns"]),
            num_students=result["num_students"],
            form=form_data
        )

    except Exception as e:
        return f"<h3>Error:</h3><pre>{str(e)}</pre>"

    finally:
        # DELETE FILE IMMEDIATELY
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
