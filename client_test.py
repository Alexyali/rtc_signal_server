#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python 客户端测试脚本
用于测试 RTC 信令服务器
"""

import socketio
import time
import argparse
import threading
from datetime import datetime


class SignalingClient:
    """信令客户端"""

    def __init__(self, server_url='http://localhost:5000'):
        self.sio = socketio.Client()
        self.server_url = server_url
        self.connected = False
        self.user_id = None
        self.room_id = None

        # 注册事件处理器
        self._register_handlers()

    def _register_handlers(self):
        """注册事件处理器"""

        @self.sio.on('connect')
        def on_connect():
            self.connected = True
            self._log('✅ 已连接到服务器')

        @self.sio.on('disconnect')
        def on_disconnect():
            self.connected = False
            self._log('❌ 与服务器断开连接')

        @self.sio.on('joined')
        def on_joined(data):
            self._log(f'✅ 成功加入房间 {data["roomId"]}')
            self._log(f'   房间内用户: {", ".join(data["users"])}')

        @self.sio.on('user-joined')
        def on_user_joined(data):
            self._log(f'👤 {data["userId"]} 加入了房间 {data["roomId"]}')

        @self.sio.on('leaved')
        def on_leaved(data):
            self._log(f'✅ 已离开房间 {data["roomId"]}')

        @self.sio.on('user-left')
        def on_user_left(data):
            self._log(f'👋 {data["userId"]} 离开了房间 {data["roomId"]}')

        @self.sio.on('error')
        def on_error(data):
            self._log(f'❌ 错误: {data["message"]}')

    def connect(self):
        """连接到服务器"""
        try:
            self.sio.connect(self.server_url)
            time.sleep(0.5)  # 等待连接建立
            return True
        except Exception as e:
            self._log(f'连接失败: {e}')
            return False

    def disconnect(self):
        """断开连接"""
        if self.connected:
            self.sio.disconnect()

    def join_room(self, user_id, room_id):
        """加入房间"""
        self.user_id = user_id
        self.room_id = room_id
        self.sio.emit('join', {'userId': user_id, 'roomId': room_id})
        self._log(f'发送加入房间信令: userId={user_id}, roomId={room_id}')

    def leave_room(self):
        """离开房间"""
        if self.user_id and self.room_id:
            self.sio.emit('leave', {'userId': self.user_id, 'roomId': self.room_id})
            self._log(f'发送离开房间信令: userId={self.user_id}, roomId={self.room_id}')

    def _log(self, message):
        """输出日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f'[{timestamp}] [{self.user_id or "Client"}] {message}')


def interactive_test():
    """交互式测试"""
    print('=' * 60)
    print('RTC 信令服务器 - Python 客户端测试')
    print('=' * 60)

    client = SignalingClient()

    if not client.connect():
        print('无法连接到服务器，请确保服务器正在运行')
        return

    print('\n命令列表:')
    print('  join <userId> <roomId>  - 加入房间')
    print('  leave                   - 离开房间')
    print('  quit                    - 退出程序')
    print()

    try:
        while True:
            cmd = input('> ').strip().split()

            if not cmd:
                continue

            if cmd[0] == 'quit':
                break

            elif cmd[0] == 'join':
                if len(cmd) != 3:
                    print('用法: join <userId> <roomId>')
                    continue
                client.join_room(cmd[1], cmd[2])
                time.sleep(0.5)

            elif cmd[0] == 'leave':
                client.leave_room()
                time.sleep(0.5)

            else:
                print(f'未知命令: {cmd[0]}')

    except KeyboardInterrupt:
        print('\n\n程序被中断')

    finally:
        client.disconnect()
        print('已断开连接')


def auto_test(num_users=2, room_id='test-room'):
    """自动化测试"""
    print('=' * 60)
    print(f'自动化测试: {num_users} 个用户加入房间 {room_id}')
    print('=' * 60)

    clients = []

    # 创建并连接客户端
    for i in range(num_users):
        user_id = f'user{i+1}'
        client = SignalingClient()

        if client.connect():
            clients.append(client)
            time.sleep(0.5)
        else:
            print(f'客户端 {user_id} 连接失败')

    if not clients:
        print('没有客户端成功连接')
        return

    print(f'\n✅ {len(clients)} 个客户端已连接\n')

    # 测试场景1: 依次加入房间
    print('📝 场景1: 用户依次加入房间')
    for i, client in enumerate(clients):
        user_id = f'user{i+1}'
        client.join_room(user_id, room_id)
        time.sleep(1)

    time.sleep(2)

    # 测试场景2: 第一个用户离开
    print('\n📝 场景2: 第一个用户离开房间')
    clients[0].leave_room()
    time.sleep(2)

    # 测试场景3: 剩余用户离开
    print('\n📝 场景3: 剩余用户离开房间')
    for client in clients[1:]:
        client.leave_room()
        time.sleep(1)

    time.sleep(2)

    # 断开所有连接
    print('\n清理连接...')
    for client in clients:
        client.disconnect()

    print('✅ 测试完成')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RTC 信令服务器客户端测试')
    parser.add_argument('--auto', action='store_true', help='运行自动化测试')
    parser.add_argument('--users', type=int, default=2, help='自动化测试的用户数量')
    parser.add_argument('--room', type=str, default='test-room', help='测试房间ID')

    args = parser.parse_args()

    if args.auto:
        auto_test(args.users, args.room)
    else:
        interactive_test()
