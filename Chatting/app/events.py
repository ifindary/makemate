from flask import session
from flask_socketio import emit, join_room, leave_room, Namespace

import datetime
import random

from pymongo import MongoClient

room_client = MongoClient('localhost', 27017)
db = room_client.save_chat #테이블 이름 - 컬렉션 상위
#room 정보 - room_data 컬렉션
#chat 정보 - room_msg 컬렉션

'''바꿀 점
    1 - 동시입장한다면 수정 필요
    2 - 혼자 입장 후 상대가 수락 후 입장한다면
        -> 입장 이벤트는 그대로 - 초대 이벤트 생성 필요 - (초대 -> 입장)'''
def socketio_init(socketio):
    @socketio.on('joined', namespace='/chat')
    def joined(message):
        user = session.get('name')
        
        user_img = message['img']
        user1 = message['user1']
        genre = message['genre']
        room_id = message['room_id']
        
        print(genre)
        
        #is_room = db.room_data.find_one({  })
        
        # 재입장 고려하지 않음
        
        # 생성이 되어있는지 확인
        result = db.room_data.find_one({'room_id': room_id})
            
        # 중복되지 않으면 null 반환
        if result is None:
            print("room create!")
        
        join_room(room_id)
        session['room'] = room_id
        
        data = {
            'room_id': room_id,
            'user1': user1,
            'genre': genre,
        }
        db.room_data.insert_one(data)
        
        emit('status', {'msg':user1 + '님이 입장하셧습니다'}, room=room_id)
          
    @socketio.on('text', namespace='/chat')
    def text(message):
        room = session.get('room_id')
        sender = session.get('user1')
        date = datetime.datetime.now()
        
        data = {
            'room_id': room,
            'date': date, #type=datetime.datetime 스트링 아님
            'sender': sender,
            'text': message['msg'],
        }
        db.room_msg.insert_one(data)
        
        print(date, ': ', message['msg']) # -------------- 여기까지 됨
        
        emit('message', {'msg' : sender + ':' + message['msg']}, room=room)
        
    #@socketio.on('connect', namespace='/')
    #def connect_handler(data):
    #    print(data)
        
        
    @socketio.on('left', namespace='/chat')
    def left(message):
        room = session.get('room_id')
        leave_room(room)
        emit('status', {'msg':session.get('name') + '님이 퇴장'}, room=room)
        
        