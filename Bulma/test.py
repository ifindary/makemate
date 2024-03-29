from flask import Flask, render_template, jsonify, request
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from pymongo import MongoClient  
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_jwt_extended import get_jwt
from werkzeug.utils import secure_filename
from datetime import timedelta
import requests # TEST용 지우기
import os
import json #TEST용 지우기 


# 앱 설정
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "tarzan"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10) # 초 단위
jwt = JWTManager(app)

client = MongoClient('mongodb://minitest:minitest@3.39.231.115', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbminitest  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.

# 이미지를 저장할 경로 설정
UPLOAD_FOLDER = 'static'#여기에 웹서버 경로 설정
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/main')
def movemain():
    return render_template('main.html')

@app.route('/index')
def moveindex():
    return render_template('index.html')

@app.route('/list', methods=['GET'])
def movelist():
    genre = request.args.get('genre')
    print(genre)
    return render_template('list.html', genre=genre)

@app.route('/chatroom')
def movechatroom():
    return render_template('chatroom.html')


@app.route('/memo', methods=['POST'])
def signup():
    # 1. 클라이언트로부터 데이터를 받기
    id_receive = request.form['id_give']  # 클라이언트로부터 url을 받는 부분
    pw_receive = request.form['pw_give']  # 클라이언트로부터 comment를 받는 부분
    pw_check_receive = request.form['pw_check_give']  # 클라이언트로부터 comment를 받는 부분
    name_receive = request.form['name_give']  # 클라이언트로부터 comment를 받는 부분
    file_receive = request.files['file_give']  # 이미지 파일 받기
    
    # ID가 이미 존재하는지 확인
    if db.members.find_one({'id': id_receive}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 ID입니다.'})
    if pw_receive!=pw_check_receive:
        return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다.'})

    # 파일명 안전하게 처리
    filename = secure_filename(file_receive.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # 파일 저장
    file_receive.save(file_path)
    
    # 비밀번호 해시 생성
    pw_hash = generate_password_hash(pw_receive)

    member = {'id': id_receive, 'pw': pw_hash, 'name': name_receive,"image_path": file_path}

    # 3. mongoDB에 데이터를 넣기
    db.members.insert_one(member)

    return jsonify({'result': 'success','msg': '회원가입 성공!'})

@app.route('/login', methods=['POST'])
def login():
    # id_receive = request.form['id_give']
    # pw_receive = request.form['pw_give']

    # # 데이터베이스에서 해당 ID의 사용자 찾기
    # member = db.members.find_one({'id': id_receive}, {'_id': 0})

    # if member is not None and member['pw'] == pw_receive:
    #     # 비밀번호가 일치하는 경우
    #     return jsonify({'result': 'success', 'msg': '로그인 성공'})
    # else:
    #     # 로그인 실패
    #     return jsonify({'result': 'fail', 'msg': '로그인 실패'})
    
    id = request.json.get('id_give')
    password = request.json.get('pw_give')
    
    # MongoDB에서 사용자 검색
    member = db.members.find_one({"id": id})
    if not member:
        return jsonify({'result': 'fail', 'msg': '존재하지 않는 사용자입니다.'}), 200

    # 사용자 존재 여부 및 비밀번호 확인
    #print(check_password_hash(member['pw'], password))
    if member and check_password_hash(member['pw'], password):
        # JWT 토큰 생성
        access_token = create_access_token(identity=id)
        return jsonify({'result': 'success', 'msg': '로그인 성공','access_token': access_token}), 200
    else:
        return jsonify({'result': 'fail', 'msg': '로그인 실패'}), 200 #401에서 200 으로 변경하고
    
# @app.route('/loadprofileimg', methods=['POST'])
# def loadprofileimg():
    
#     id = request.json.get('id_give')
    
#     # MongoDB에서 사용자 검색
#     member = db.members.find_one({"id": id})
#     return jsonify({'result': 'success','img_url': member['image_path']}), 200 

@app.route('/protected', methods=['GET'])
@jwt_required() #로그인한 유저만이 이 API를 사용할 수 있다는 뜻
def protected():
    current_user = get_jwt_identity()
    member = db.members.find_one({"id": current_user})
    return jsonify({'logged_in_as':current_user, 'img_url' : member['image_path'], 'name' : member['name']}), 200

@app.route('/showimage', methods=['POST'])
def showimage():
    genre = request.json.get('genre_give')
    section = db.sections.find_one({"title": genre})
    return jsonify({'img_url' : section['image']}), 200

# blocklist 생성. 중복 방지 위해 set 자료형 사용
jwt_blocklist = set()

#로그아웃 처리 api
@app.route('/logout', methods=['GET'])
@jwt_required()
def user_logout():
    jti = get_jwt()['jti']
    jwt_blocklist.add(jti)
    return jsonify({"msg": "로그아웃 되었습니다."}), 200

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "로그인 시간이 만료되었습니다."}), 401

# 토큰이 블랙리스트에 있는지 확인하는 콜백 함수
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in jwt_blocklist

@app.route('/memo', methods=['GET'])
def read_members():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    result = list(db.members.find({}, {'_id': 0}))
    # 2. articles라는 키 값으로 article 정보 보내주기
    return jsonify({'result': 'success', 'members': result})

# main에서 분야 추가할 때 사용
@app.route('/collect', methods=['POST'])
def post_sections():
    # 클라이언트로부터 데이터를 받기
    image_receive = request.files['section_image']  # 클라이언트로부터 image를 받는 부분
    title_receive = request.form['section_title']  # 클라이언트로부터 title을 받는 부분

    # title이 이미 존재하는지 확인
    if db.sections.find_one({'title': title_receive}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 분야입니다.'}), 200

    # 파일명 안전하게 처리
    post_filename = secure_filename(image_receive.filename)
    post_file_path = os.path.join(app.config['UPLOAD_FOLDER'], post_filename)

    # 파일 저장
    image_receive.save(post_file_path)

    section = {'image': post_file_path, 'title': title_receive}

    # mongoDB에 데이터를 넣기
    db.sections.insert_one(section)
    return jsonify({'result':'success','msg': '추가 성공'}), 200

@app.route('/collectread', methods=['GET'])
def read_sections():
    # mongoDB에서 모든 데이터 조회해오기 (Read)
    result = list(db.sections.find({}, {'_id': 0}))
    # 2. articles라는 키 값으로 article 정보 보내주기
    return jsonify({'result': 'success', 'sections': result}), 200

#위 부분을 jinja2로 변경할 수 있음.
#def sections_route():
#    sections = list(db.sections.find({}, {'_id': 0}))
#    return render_template('main.html', sections=sections)

# main에서 분야 추가할 때 사용
@app.route('/listup', methods=['POST'])
@jwt_required() #로그인한 유저만이 이 API를 사용할 수 있다는 뜻
def post_lists():

    current_user = get_jwt_identity()
    member = db.members.find_one({"id": current_user})

    # 클라이언트로부터 데이터를 받기
    intro_receive = request.json.get('intro_give')  # 클라이언트로부터 intro를 받는 부분
    genre_receive = request.json.get('genre_give')  # Use get method to avoid KeyError

    if not genre_receive:
        return jsonify({'result': 'fail', 'msg': '분야가 전달되지 않았습니다.'}), 400

    # 이미 존재하는지 확인
    if db.lists.find_one({'id': current_user, 'genre': genre_receive}):
        return jsonify({'result': 'fail', 'msg': '이미 해당 분야에서 소개글을 작성하였습니다.'})
    list_data = {'id': current_user, 'name': member['name'], 'img_url' : member['image_path'], 'genre': genre_receive, 'intro': intro_receive}

    # mongoDB에 데이터를 넣기
    db.lists.insert_one(list_data)

    return jsonify({'result': 'success'})

@app.route('/listup', methods=['GET'])
def read_lists():
    genre_receive = request.args['genre_give']

    # mongoDB에서 조건에 맞는 데이터 조회해오기 (Read)
    result = list(db.lists.find({'genre': genre_receive}, {'_id': 0}))

    # 2. articles라는 키 값으로 article 정보 보내주기
    return jsonify({'result': 'success', 'lists': result})

#list 화면에서 사용
@app.route('/genre_route')
def genre_route():
    # genre를 어떻게 가져오는지에 따라 다름
    # 예: URL에서 쿼리 파라미터로 가져오기
    genre = request.args.get('genre')
    return render_template('list.html', genre=genre)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)