from flask import Flask, render_template, jsonify, request
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from pymongo import MongoClient  
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_jwt_extended import get_jwt
import requests # TEST용 지우기
import json #TEST용 지우기 


# 앱 설정
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "tarzan"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 20 # 초 단위
jwt = JWTManager(app)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsignuptest  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/main')
def movemain():
    return render_template('main.html')

@app.route('/index')
def moveindex():
    return render_template('index.html')


@app.route('/memo', methods=['POST'])
def signup():
    # 1. 클라이언트로부터 데이터를 받기
    id_receive = request.form['id_give']  # 클라이언트로부터 url을 받는 부분
    pw_receive = request.form['pw_give']  # 클라이언트로부터 comment를 받는 부분
    pw_check_receive = request.form['pw_check_give']  # 클라이언트로부터 comment를 받는 부분
    name_receive = request.form['name_give']  # 클라이언트로부터 comment를 받는 부분
    
    # ID가 이미 존재하는지 확인
    if db.members.find_one({'id': id_receive}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 ID입니다.'})
    if pw_receive!=pw_check_receive:
        return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다.'})

    # 비밀번호 해시 생성
    pw_hash = generate_password_hash(pw_receive)

    member = {'id': id_receive, 'pw': pw_hash, 'name': name_receive}

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

@app.route('/protected', methods=['GET'])
@jwt_required() #로그인한 유저만이 이 API를 사용할 수 있다는 뜻
def protected():
    current_user = get_jwt_identity()
    return jsonify({'logged_in_as':current_user}), 200

# blocklist 생성. 중복 방지 위해 set 자료형 사용
jwt_blocklist = set()

#로그아웃 처리 api
@app.route('/logout', methods=['GET'])
@jwt_required()
def user_logout():
    jti = get_jwt()['jti']
    jwt_blocklist.add(jti)
    return jsonify({"msg": "로그아웃 되었습니다."}), 200

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



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)