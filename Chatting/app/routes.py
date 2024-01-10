from flask import session, redirect, url_for, render_template, request, Blueprint

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['user1'] = request.form['user1']
        session['user2'] = request.form['user2']
        #session['room'] = request.form['room']
        session['img'] = request.form['img']    # user2의 이미지
        
        return redirect(url_for('main.chat'))
    return render_template('index.html')

@main.route('/chat')
def chat():
    user1 = session.get('user1', '')
    user2 = session.get('user2', '')
    #room = session.get('room', '')
    img = session.get('img', '')
    
    if user1 == '' or user2 == '':
        return redirect(url_for('.index'))
    return render_template('chatroom.html', user1=user1, user2=user2, img=img)
    #return render_template('../../Bulma/templates/chatroom.html', name=name, room=room)
    
