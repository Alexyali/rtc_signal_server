# RTC 信令服务器

基于 Python Flask-SocketIO 实现的 WebRTC 信令服务器，支持用户加入/离开房间的信令管理。

## 功能特性

- ✅ 用户加入房间（自动创建房间）
- ✅ 用户离开房间（自动销毁空房间）
- ✅ 房间内用户广播
- ✅ 断线自动清理
- ✅ 多房间隔离
- ✅ CORS 跨域支持

## 信令格式

### 客户端 → 服务器

**加入房间**
```json
{
  "type": "join",
  "userId": "user123",
  "roomId": "room456"
}
```

**离开房间**
```json
{
  "type": "leave",
  "userId": "user123",
  "roomId": "room456"
}
```

### 服务器 → 客户端

**加入成功**
```json
{
  "type": "joined",
  "userId": "user123",
  "roomId": "room456",
  "users": ["user123", "user456"]
}
```

**新用户加入（广播给其他用户）**
```json
{
  "type": "user-joined",
  "userId": "user123",
  "roomId": "room456"
}
```

**离开成功**
```json
{
  "type": "leaved",
  "userId": "user123",
  "roomId": "room456"
}
```

**用户离开（广播给其他用户）**
```json
{
  "type": "user-left",
  "userId": "user123",
  "roomId": "room456"
}
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务器

```bash
python server.py
```

服务器将运行在 `http://localhost:5000`

## 测试方法

### 方法1: Web 浏览器测试

1. 启动服务器后，打开浏览器访问 `http://localhost:5000`
2. 打开多个浏览器标签页模拟多用户
3. 输入用户ID和房间ID，点击"加入房间"
4. 在不同标签页观察信令交互

### 方法2: Python 客户端测试

**交互式测试**
```bash
python client_test.py
```

命令示例：
```
> join user1 room1
> leave
> quit
```

**自动化测试**
```bash
# 模拟2个用户加入同一房间
python client_test.py --auto --users 2 --room test-room

# 模拟5个用户
python client_test.py --auto --users 5 --room my-room
```

## 项目结构

```
rtc-signaling-server/
├── server.py              # 信令服务器主程序
├── templates/
│   └── client_test.html   # Web 测试客户端
├── client_test.py         # Python 测试客户端
├── requirements.txt       # Python 依赖
├── README.md             # 使用说明
└── server.log            # 服务器日志（运行后生成）
```

## 技术栈

- **Flask**: Web 框架
- **Flask-SocketIO**: WebSocket 支持
- **Flask-CORS**: 跨域支持
- **python-socketio**: Python 客户端库
- **eventlet**: 异步支持

## 注意事项

1. 如果不需要跨域支持，可以在 `server.py` 中移除 `CORS(app)` 和 `flask-cors` 依赖
2. 默认端口为 5000，可在 `server.py` 中修改
3. 日志文件保存在 `server.log`
4. 支持多房间并发，房间之间完全隔离

## 测试场景

### 场景1: 基本加入/离开
1. 用户A加入房间1 → 收到 `joined` 信令
2. 用户B加入房间1 → 用户A收到 `user-joined`，用户B收到 `joined`
3. 用户A离开房间1 → 用户B收到 `user-left`，用户A收到 `leaved`

### 场景2: 多房间隔离
1. 用户A加入房间1
2. 用户B加入房间2
3. 验证用户A和B互不干扰

### 场景3: 断线重连
1. 用户A加入房间
2. 断开连接
3. 房间内其他用户收到离开通知

## License

MIT
