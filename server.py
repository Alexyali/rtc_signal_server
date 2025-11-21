#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RTC 信令服务器
支持用户加入/离开房间的信令转发
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rtc-signaling-secret'

# 启用 CORS（如果不需要跨域，可以移除这行和 flask_cors 依赖）
CORS(app)

# 创建 SocketIO 实例
socketio = SocketIO(app, cors_allowed_origins="*")

# 房间管理：{roomId: {userId: sid}}
rooms = {}

# 用户到房间的映射：{sid: {userId, roomId}}
user_rooms = {}


@app.route('/')
def index():
    """提供测试页面"""
    return render_template('client_test.html')


@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    logger.info(f'Client connected: {request.sid}')
    emit('connected', {'sid': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接，自动清理房间"""
    sid = request.sid
    logger.info(f'Client disconnected: {sid}')

    if sid in user_rooms:
        user_info = user_rooms[sid]
        user_id = user_info['userId']
        room_id = user_info['roomId']

        # 清理房间数据
        _remove_user_from_room(sid, user_id, room_id)

        # 通知房间内其他用户
        emit('user-left', {
            'userId': user_id,
            'roomId': room_id
        }, room=room_id, skip_sid=sid)

        logger.info(f'Auto cleaned user {user_id} from room {room_id}')


@socketio.on('join')
def handle_join(data):
    """处理加入房间信令"""
    user_id = data.get('userId')
    room_id = data.get('roomId')
    sid = request.sid

    if not user_id or not room_id:
        emit('error', {'message': 'userId and roomId are required'})
        return

    logger.info(f'User {user_id} joining room {room_id}')

    # 如果房间不存在，创建房间
    if room_id not in rooms:
        rooms[room_id] = {}
        logger.info(f'Created new room: {room_id}')

    # 将用户加入房间
    rooms[room_id][user_id] = sid
    user_rooms[sid] = {'userId': user_id, 'roomId': room_id}

    # 加入 SocketIO 房间
    join_room(room_id)

    # 获取房间内所有用户
    users_in_room = list(rooms[room_id].keys())

    # 向用户发送加入成功信令
    emit('joined', {
        'userId': user_id,
        'roomId': room_id,
        'users': users_in_room
    })

    # 向房间内其他用户广播新用户加入
    emit('user-joined', {
        'userId': user_id,
        'roomId': room_id
    }, room=room_id, skip_sid=sid)

    logger.info(f'User {user_id} joined room {room_id}, total users: {len(users_in_room)}')


@socketio.on('leave')
def handle_leave(data):
    """处理离开房间信令"""
    user_id = data.get('userId')
    room_id = data.get('roomId')
    sid = request.sid

    if not user_id or not room_id:
        emit('error', {'message': 'userId and roomId are required'})
        return

    logger.info(f'User {user_id} leaving room {room_id}')

    # 清理房间数据
    _remove_user_from_room(sid, user_id, room_id)

    # 离开 SocketIO 房间
    leave_room(room_id)

    # 向用户发送离开成功信令
    emit('leaved', {
        'userId': user_id,
        'roomId': room_id
    })

    # 向房间内其他用户广播用户离开
    emit('user-left', {
        'userId': user_id,
        'roomId': room_id
    }, room=room_id)

    logger.info(f'User {user_id} left room {room_id}')


def _remove_user_from_room(sid, user_id, room_id):
    """从房间中移除用户"""
    # 从房间中移除用户
    if room_id in rooms and user_id in rooms[room_id]:
        del rooms[room_id][user_id]

        # 如果房间为空，销毁房间
        if not rooms[room_id]:
            del rooms[room_id]
            logger.info(f'Room {room_id} destroyed (empty)')

    # 从用户映射中移除
    if sid in user_rooms:
        del user_rooms[sid]


@socketio.on('message')
def handle_message(data):
    """中转消息（用于 WebRTC 信令交换）"""
    room_id = data.get('roomId')
    if room_id:
        logger.debug(f'Relaying message to room {room_id}')
        emit('message', data, room=room_id, skip_sid=request.sid)


if __name__ == '__main__':
    logger.info('Starting RTC Signaling Server...')
    logger.info('Server running at http://localhost:5000')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
