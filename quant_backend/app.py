from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from quant_backend.api.market_data_routes import market_data_bp
from quant_backend.api.strategy_routes import strategy_bp

# 初始化 Flask 应用
app = Flask(__name__)

# 配置 CORS
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",  # Vite 默认端口
            "http://localhost:5174",  # 可能的备用端口
            "http://localhost:5175",  # 可能的备用端口
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://192.168.1.*:*",   # 局域网
            "*"                        # 允许所有源（生产环境应替换为特定域名）
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "supports_credentials": True
    }
})

# 注册市场数据蓝图
app.register_blueprint(market_data_bp)
# 注册策略蓝图
app.register_blueprint(strategy_bp)

# 初始化 SocketIO，支持跨域
socketio = SocketIO(app, cors_allowed_origins=[
    "http://localhost:5173", 
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174", 
    "http://127.0.0.1:5175",
    "http://192.168.1.*",
    "*"  # 允许所有源（生产环境应替换为特定域名）
])

@app.route('/')
def index():
    return "Flask Backend is Running"

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('server_response', {'data': 'Connected to WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('client_event')
def handle_client_event(json_data):
    print('Received client_event with data: ' + str(json_data))
    emit('server_response', {'data': 'Server received your event', 'original_payload': json_data})

if __name__ == '__main__':
    # 启动开发服务器
    socketio.run(app, debug=True, host='0.0.0.0', port=5002) 