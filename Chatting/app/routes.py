from flask import session, redirect, url_for, render_template, request, Blueprint

main = Blueprint('main', __name__)

@main.route('/moveroom', methods=['GET'])
def moveroom():
    session['img'] = request.args.get('img')
    session['user1'] = request.args.get('user1')
    #session['user2'] = request.args.get('user2')
    session['genre'] = request.args.get('genre')
    session['room_id'] = request.args.get('room_id')
    
    return redirect(url_for('.chatroom'))

@main.route('/chatting')
def chatroom():
    user1 = session.get('user1', '')
    #user2 = session.get('user2', '')
    genre = session.get('genre', '')
    img = session.get('img', '')
    room_id = session.get('room_id', '')
    
    #print(user1 + ' & ' + user2 + ' & ' +img)
    if user1 == '':
        return redirect(url_for('.moveroom')) # 라우트 함수이름
    return render_template('chatroom.html', user1=user1, genre=genre, img=img, room_id=room_id)#, 200, {'Content-Type': 'text/html; charset=utf-8'}
