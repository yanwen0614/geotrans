

import json
import os
import xlrd
from flask import (Flask, make_response, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__, static_url_path='')
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/translation', methods=['POST'])
def Translation():
    if request.form.get('source') or request.args.get('source'):
        from Translation import translation
        translationSerive = translation()
        if request.form.get('source'):
            datax = request.form.to_dict()['source']
        else:
            datax = request.args.to_dict()['source']
        transContext, tag, log = translationSerive.phrasetrans(datax)
        Context = json.dumps({"transContext":transContext,"tag":tag,"log":log},ensure_ascii=False) # 音译 意译tag  未译 -1 音 0 照搬 1  意 2
        resp = make_response(Context)
        return resp
    else:
        content = "error_code"
        resp = make_response(content)

        return resp

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['Filedata']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'static/file/upload', f.filename)
        f.save(upload_path)
        from Translation import translation
        translationSerive = translation(f.filename)
        translationSerive.filetrans(f.filename)
        resp = make_response("True")
        return resp
    

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    basepath = os.path.dirname(__file__)  # 假设在当前目录
    upload_path = os.path.join(basepath, 'static/file/trans_result')
    #return app.send_static_file(upload_path+"/"+filename)
    return send_from_directory(upload_path, filename, as_attachment=True)

@app.route("/transfile", methods=['POST'])
def filetrans():
    if request.form.get('filename') or request.args.get('filename'):
        if request.form.get('source'):
            datax = request.form.to_dict()['source']
        else:
            datax = request.args.to_dict()['source']
    from Translation import translation
    translationSerive = translation(datax)
    translationSerive.filetrans(datax)
    resp = make_response("翻译完毕")
    return resp
    
@app.route("/getInstance", methods=['POST'])
def LoadInstance():
    if request.form.get('start') and request.form.get('end'):
        start = int(request.form.to_dict()['start'])
        end = int(request.form.to_dict()['end'])
        table = xlrd.open_workbook("rule\罗马文1-100第5版.xls").sheets()[0]
        field = ['ck','id','romanname','deputy1','deputy2','chinesename',
                'chinesenamedeputy','countries','long','lat',
                ]

        res = list()
        for i in range(start, end+1):
            inst = {k:v for k,v in zip(field,[False,]+ table.row_values(i))}
            res.append(inst)
        resjs = json.dumps(res)
        resp = make_response(resjs)
        return resp
