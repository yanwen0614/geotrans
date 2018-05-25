

from flask import Flask, make_response, request
import os
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'
    
@app.route('/translation', methods=['POST'])
def Translation():
    if request.form.get('source') or request.args.get('source'):
        from Translation import translation
        import json
        translationSerive = translation()
        if request.form.get('source'):
            datax = request.form.to_dict()['source']
        else:
            datax = request.args.to_dict()['source']
        transContext, tag, log = translationSerive.phrasetrans(datax)
        Context = json.dumps({"transContext":transContext,"tag":tag,"log":log},ensure_ascii=False) # 音译 意译tag  未译 -1 音 0 照搬 1  意 2
        resp = make_response(Context)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        content = "error_code"
        resp = make_response(content)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'uploads', f.filename)
        f.save(upload_path)
        resp = make_response(True)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return True
    

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    basepath = os.path.dirname(__file__)  # 假设在当前目录
    return send_from_directory(directory, filename, as_attachment=True)