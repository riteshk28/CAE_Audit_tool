from flask import Flask, render_template, request
#from werkzeug import secure_filename

#from dash import Dash, html, Input, Output, dash_table
import pandas as pd
import PyPDF2
from utils import read_file, parse_course_name, rule_1, rule_2_cd, rule_2_pd, rule_2_ad, page_len

app = Flask(__name__)

@app.route("/")
def hello():
    
    return render_template('index.html')


@app.route("/uploader", methods=["POST", "GET"])
def upload_file():
    '''
    this will upload file, POST method will be used to call http://localhost:8080/uploader, 
    when we click on SUBMIT button.
    
    '''

    if request.method=="POST":
        fName=request.files["file"]
        fName.save("static/" + fName.filename)

        output=read_file("static/" +fName.filename)
        course_name=parse_course_name(output)
        asmt_weight = rule_1(output)
        rg = page_len(output)
        
        df1_c, df2_c, df3_c, df4_c, clo1_title_c, clo2_title_c, clo3_title_c, clo4_title_c = rule_2_cd(output)
        df1_p, df2_p, df3_p, df4_p, clo1_title_p, clo2_title_p, clo3_title_p, clo4_title_p = rule_2_pd(output)
        df1_a, df2_a, df3_a, df4_a, clo1_title_a, clo2_title_a, clo3_title_a, clo4_title_a = rule_2_ad(output)

    return render_template('index.html', message=course_name, tables=[asmt_weight.to_html(classes='data')],
    tables1 = [clo1_title_c ,df1_c.to_html(classes='data'), clo2_title_c, df2_c.to_html(classes='data'), clo3_title_c, df3_c.to_html(classes='data'), clo4_title_c, df4_c.to_html(classes='data')],
    tables2 = [clo1_title_p ,df1_p.to_html(classes='data'), clo2_title_p, df2_p.to_html(classes='data'), clo3_title_p, df3_p.to_html(classes='data'), clo4_title_p, df4_p.to_html(classes='data')],
    tables3 = [clo1_title_a ,df1_a.to_html(classes='data'), clo2_title_a, df2_a.to_html(classes='data'), clo3_title_a, df3_a.to_html(classes='data'), clo4_title_a, df4_a.to_html(classes='data')],
    titles=df1_c.columns.values)

#fName.filename
if __name__ == '__main__':
    DEFAULT_PORT = "8080"
    app.run(debug=True, port=DEFAULT_PORT)
