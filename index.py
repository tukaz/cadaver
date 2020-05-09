from flask import Flask,session, render_template,redirect,url_for, request,jsonify
from datetime import timedelta
from flask_socketio import SocketIO, emit, join_room, leave_room,disconnect
from uuid import uuid4

app = Flask(__name__)
    
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socketio = SocketIO(app,ping_timeout=10,ping_interval=5)
app.permanent_session_lifetime = timedelta(minutes=5)

users = {}

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'


@socketio.on("send_msg", namespace="/send")
def broadcastText(data):
    print('sid del send')
    print(request.sid)
    uid = session['uid']
    recieverId = users[users[uid]['partnerId']]['sid']
    msg = data["msg"]
    emit("broadcasting_text", {"selection": msg}, room=request.sid)
    emit("broadcasting_text", {"selection": msg}, room=recieverId)
    emit("change_turn", {}, room=recieverId)
    emit("finish_texting", {}, room=request.sid)


@socketio.on("username", namespace="/adduser")
def recieve_username(username):
    # check if the user already logged in
    print('sid del username')
    print(request.sid)
    if 'user_sid' not in session.keys():
        uid = session['uid']
        users[uid] = {
            'name':username,
            'sid': request.sid,
            'partnerId':''
        }
        
        # search for single users
        for k in users.keys():
            if k != uid and users[k]['partnerId'] == '':
                users[uid]['partnerId'] = k
                users[k]['partnerId'] = uid          

        print(users)

        if users[uid]['partnerId']  != '':
            emit("partnerOK", {"newPartner": users[users[uid]['partnerId']]['name'] }, room=request.sid)
            emit("startTexting", {"newPartner": username }, room=users[users[uid]['partnerId']]['sid'])
        else:
            emit("waitingForPartner", {}, room=request.sid)


@socketio.on("connect")
def connect():
    print(f"{bcolors.OKBLUE}CONEXION")
    print(request.sid)
    print(session['uid'])

@socketio.on('disconnect', namespace="/adduser")
def disconnect():
    print(f"{bcolors.OKBLUE}Disconnection{bcolors.OKBLUE}")

    uid = session['uid']
    # if the user is in the system 
    if uid in users:
        # i get his partner registry
        partnerId = users[uid]['partnerId']
        print('partnerId', partnerId)
        if(partnerId != ''):
            partnerSid = users[users[uid]['partnerId']]['sid']
            print('partnerSid', partnerSid)
            # if he has a partner remove his connection 
            del users[partnerId]
            # notify the partner
            emit("partnerLeft", {}, room=partnerSid)
        # remove user from the system
        del users[uid]
    # remove user session
    session.clear()
    
@app.route('/')
def main():
    print(users)
    if 'uid' not in session.keys():
        print(f"{bcolors.OKBLUE}LOL{bcolors.OKBLUE}")
        session['uid'] = str(uuid4())
    else:
        print(f"{bcolors.OKGREEN}Im here{bcolors.OKGREEN}")
        print(session.values())
        print(session.keys())
    return render_template(
        "index.html"
    )
