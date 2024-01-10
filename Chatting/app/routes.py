from flask import session, redirect, url_for, render_template, request, Blueprint

main = Blueprint('main', __name__)

@main.route('/moveroom', methods=['GET'])
def moveroom():
    print('moveroom')
    session['img'] = request.args.get('img')
    session['user1'] = request.args.get('user1')
    session['user2'] = request.args.get('user2')
    
    return redirect(url_for('.chatroom'))

@main.route('/chatting')
def chatroom():
    print("chatroom")
    user1 = session.get('user1', '')
    user2 = session.get('user2', '')
    img = session.get('img', '')
    
    if user1 == '' or user2 == '':
        return redirect(url_for('.moveroom')) # 라우트 함수이름
    return render_template('chatroom.html', user1=user1, user2=user2, img=img)
    
