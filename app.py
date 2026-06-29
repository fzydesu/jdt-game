from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit, join_room
from game import GameRoom

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}
waiting_room = None

# ========== 前端HTML页面 ==========
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>JDT对战</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #fff;
        }
        .container {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            width: 700px;
            max-width: 95%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.1);
        }
        h1 { text-align: center; font-size: 28px; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #888; font-size: 14px; margin-bottom: 30px; }
        .status-box {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: #aaa;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .status-box.ready { color: #4ecdc4; border-color: #4ecdc4; }
        .status-box.fight { color: #ff6b6b; border-color: #ff6b6b; font-weight: bold; }
        .stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            gap: 10px;
        }
        .stat-item {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 12px 16px;
            flex: 1;
            text-align: center;
        }
        .stat-item .label { font-size: 12px; color: #888; }
        .stat-item .value { font-size: 24px; font-weight: bold; margin-top: 4px; }
        .stat-item .value.hp { color: #ff6b6b; }
        .stat-item .value.j { color: #ffd93d; }
        .battle-display {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 15px 20px;
            margin: 15px 0;
            min-height: 80px;
        }
        .battle-display .side {
            text-align: center;
            flex: 1;
        }
        .battle-display .side .label {
            font-size: 12px;
            color: #888;
        }
        .battle-display .side .action {
            font-size: 36px;
            margin-top: 4px;
            transition: all 0.3s;
        }
        .battle-display .side .action.show {
            animation: pop 0.3s ease;
        }
        .battle-display .vs {
            font-size: 24px;
            color: #ff6b6b;
            padding: 0 10px;
        }
        @keyframes pop {
            0% { transform: scale(0.5); opacity: 0; }
            50% { transform: scale(1.3); }
            100% { transform: scale(1); opacity: 1; }
        }
        .actions {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        .action-btn {
            padding: 16px 10px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        .action-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            border-color: #4ecdc4;
            background: rgba(78,205,196,0.15);
        }
        .action-btn:disabled {
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }
        .action-btn .cost {
            font-size: 12px;
            font-weight: normal;
            color: #ffd93d;
            display: block;
            margin-top: 4px;
        }
        .action-btn .desc {
            font-size: 11px;
            font-weight: normal;
            color: #888;
            display: block;
            margin-top: 2px;
        }
        .match-btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #4ecdc4, #44b39d);
            color: #fff;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 10px;
        }
        .match-btn:hover { transform: scale(1.02); opacity: 0.9; }
        .match-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
        .log {
            margin-top: 20px;
            padding: 12px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            min-height: 40px;
            font-size: 14px;
            color: #aaa;
            max-height: 80px;
            overflow-y: auto;
        }
        .game-over {
            text-align: center;
            padding: 20px;
            background: rgba(255,107,107,0.1);
            border-radius: 12px;
            border: 2px solid #ff6b6b;
            margin-top: 15px;
        }
        .game-over .winner { font-size: 24px; color: #ffd93d; }
        .hidden { display: none; }
        /* 响应式：按钮数量多时自动换行 */
        .actions {
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
        }
    </style>
</head>
<body>
<div class="container">
    <h1>⚔️ JDT 对战</h1>
    <div class="subtitle">聚气 · 防御 · 进攻</div>
    
    <button class="match-btn" id="matchBtn" onclick="findMatch()">🎯 匹配对手</button>
    
    <div class="status-box" id="statusBox">等待开始...</div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="label">❤️ 生命值</div>
            <div class="value hp" id="hpDisplay">5</div>
        </div>
        <div class="stat-item">
            <div class="label">⚡ J气</div>
            <div class="value j" id="jDisplay">0</div>
        </div>
    </div>
    
    <!-- 双方出招显示 -->
    <div class="battle-display">
        <div class="side">
            <div class="label">你</div>
            <div class="action" id="myAction">❓</div>
        </div>
        <div class="vs">⚔️</div>
        <div class="side">
            <div class="label">对手</div>
            <div class="action" id="opponentAction">❓</div>
        </div>
    </div>
    
    <!-- 动态按钮容器 -->
    <div class="actions" id="actionsContainer"></div>
    
    <div class="log" id="logBox">💡 匹配对手开始游戏</div>
    <div class="game-over hidden" id="gameOverBox">
        <div class="winner" id="winnerText">🏆 玩家获胜！</div>
        <button class="match-btn" style="margin-top:10px;" onclick="location.reload()">🔄 重新开始</button>
    </div>
</div>

<script>
const socket = io();
let roomId = null;
let mySid = null;

// 招式图标映射（新增技能时在这里加图标）
const actionEmoji = {
    // ===== 进攻技能（攻击力递增） =====
    'J': '🌀',    // 攒J - 聚气
    '掏': '👊',    // 掏 - 消耗1J，造成1伤害（轻拳）
    '戳': '✊',    // 戳 - 消耗2J，造成2伤害（重拳）
    '爆': '💥',    // 爆/拍 - 消耗3J，造成3伤害（爆发）
    '剪': '✂️',    // 剪 - 消耗4J，造成4伤害（剪刀）
    '捏': '🤏',    // 捏 - 消耗5J，造成5伤害（捏碎）
    '砍': '🗡️',    // 砍/阿西吧！ - 消耗6J，造成6伤害（刀砍）
    '吃': '🍽️',    // 吃 - 消耗7J，造成7伤害（吃掉！）
    
    // ===== 防御技能 =====
    '挡': '🛡️',    // 挡 - 基础防御，抵挡2伤害
    '铛！': '🔊',    // 铛！ - 消耗1J，抵挡5伤害（金属碰撞声）
    '护板': '🏏',    // 护板 - 消耗2J，抵挡8伤害（护盾板）
};

// ===== 获取所有技能并渲染按钮 =====
socket.on('all_actions', (data) => {
    renderActionButtons(data.actions);
});

socket.on('connect', () => {
    mySid = socket.id;
    socket.emit('get_all_actions');
    console.log('已连接，SID:', mySid);
});

function renderActionButtons(actions) {
    const container = document.getElementById('actionsContainer');
    container.innerHTML = '';
    
    for (const [key, config] of Object.entries(actions)) {
        const btn = document.createElement('button');
        btn.className = 'action-btn';
        btn.dataset.action = key;
        btn.onclick = () => playAction(key);
        btn.disabled = true;
        
        const emoji = actionEmoji[key] || '⚔️';
        let costText = '';
        if (config.cost > 0) {
            costText = `⚡消耗${config.cost}J`;
        } else if (config.gain > 0) {
            costText = `+${config.gain}J`;
        }
        
        btn.innerHTML = `
            ${emoji} ${config.name}
            <span class="cost">${costText}</span>
            <span class="desc">${config.description || ''}</span>
        `;
        
        container.appendChild(btn);
    }
}

// ===== 匹配功能 =====
function findMatch() {
    document.getElementById('matchBtn').disabled = true;
    document.getElementById('matchBtn').textContent = '⏳ 匹配中...';
    socket.emit('find_match');
}

socket.on('waiting', (data) => {
    roomId = data.room_id;
    setStatus('⏳ 等待对手加入...', 'ready');
    addLog('等待对手加入...');
});

socket.on('match_found', (data) => {
    roomId = data.room_id;
    setStatus('✅ 匹配成功！请出招', 'ready');
    addLog('🔥 匹配成功！战斗开始！');
    document.getElementById('matchBtn').disabled = true;
    document.getElementById('matchBtn').textContent = '✅ 已匹配';
    document.querySelectorAll('.action-btn').forEach(btn => btn.disabled = false);
    updateActions();
});

// ===== 出招功能 =====
function playAction(action) {
    if (!roomId) {
        alert('请先匹配对手！');
        return;
    }
    socket.emit('play_action', { room_id: roomId, action: action });
}

socket.on('action_confirmed', (data) => {
    const emoji = actionEmoji[data.action] || '⚔️';
    addLog(`✅ 你出了 ${emoji} ${data.action}`);
    setStatus('⏳ 等待对手出招...', 'ready');
    document.querySelectorAll('.action-btn').forEach(btn => btn.disabled = true);
    // 显示自己出的招
    document.getElementById('myAction').textContent = `${emoji} ${data.action}`;
    document.getElementById('myAction').className = 'action show';
});

// ===== 回合结算 =====
socket.on('turn_result', (data) => {
    const isPlayer1 = mySid === data.sid1;
    
    const myAction = isPlayer1 ? data.action1 : data.action2;
    const opponentAction = isPlayer1 ? data.action2 : data.action1;
    
    const myEmoji = actionEmoji[myAction] || '⚔️';
    const oppEmoji = actionEmoji[opponentAction] || '⚔️';
    
    document.getElementById('myAction').textContent = `${myEmoji} ${myAction}`;
    document.getElementById('myAction').className = 'action show';
    document.getElementById('opponentAction').textContent = `${oppEmoji} ${opponentAction}`;
    document.getElementById('opponentAction').className = 'action show';
    
    addLog(`📊 ${data.detail}`);
    setStatus('👊 请出招', 'fight');
    document.querySelectorAll('.action-btn').forEach(btn => btn.disabled = false);
    updateActions();
    
    // 2.5秒后清空
    setTimeout(() => {
        if (!document.getElementById('gameOverBox').classList.contains('hidden')) {
            return;
        }
        document.getElementById('myAction').textContent = '❓';
        document.getElementById('myAction').className = 'action';
        document.getElementById('opponentAction').textContent = '❓';
        document.getElementById('opponentAction').className = 'action';
    }, 2500);
});

// ===== 更新状态 =====
socket.on('update_actions', (data) => {
    document.getElementById('jDisplay').textContent = data.j_energy || 0;
    document.getElementById('hpDisplay').textContent = data.hp || 10;
    
    const availableIds = (data.available_actions || []).map(a => a.id);
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.disabled = !availableIds.includes(btn.dataset.action);
    });
});

function updateActions() {
    if (roomId) {
        socket.emit('get_actions', { room_id: roomId });
    }
}

// 定时刷新
setInterval(() => {
    if (roomId) {
        socket.emit('get_actions', { room_id: roomId });
    }
}, 3000);

// ===== 游戏结束 =====
socket.on('game_over', (data) => {
    const isMe = data.winner === mySid;
    document.getElementById('gameOverBox').classList.remove('hidden');
    document.getElementById('winnerText').textContent = isMe ? '🏆 你赢了！' : '💀 你输了...';
    setStatus('游戏结束', 'fight');
    document.querySelectorAll('.action-btn').forEach(btn => btn.disabled = true);
    addLog(`🏁 游戏结束！${isMe ? '你赢了！' : '你输了'}`);
});

socket.on('action_error', (data) => {
    addLog(`❌ ${data.msg}`);
    setStatus(`❌ ${data.msg}`, 'fight');
    document.querySelectorAll('.action-btn').forEach(btn => btn.disabled = false);
});

// ===== 工具函数 =====
function setStatus(text, type) {
    const box = document.getElementById('statusBox');
    box.textContent = text;
    box.className = 'status-box' + (type ? ' ' + type : '');
}

function addLog(text) {
    const box = document.getElementById('logBox');
    box.innerHTML += '<br>' + text;
    box.scrollTop = box.scrollHeight;
}
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

# ========== SocketIO 事件处理 ==========
@socketio.on('connect')
def handle_connect():
    print(f'✅ 玩家 {request.sid} 已连接')

@socketio.on('get_all_actions')
def handle_get_all_actions():
    from config import ACTION_TYPES
    emit('all_actions', {'actions': ACTION_TYPES})

@socketio.on('find_match')
def handle_find_match():
    global waiting_room
    sid = request.sid
    
    if waiting_room is None:
        room_id = f"room_{sid}"
        room = GameRoom(room_id)
        room.add_player(sid)
        rooms[room_id] = room
        waiting_room = room_id
        join_room(room_id)
        emit('waiting', {'room_id': room_id, 'msg': '等待对手...'})
        print(f'📌 玩家 {sid} 创建房间 {room_id}，等待匹配')
    else:
        room = rooms[waiting_room]
        if room.add_player(sid):
            join_room(waiting_room)
            emit('match_found', {'room_id': waiting_room}, room=waiting_room)
            emit('match_found', {'room_id': waiting_room}, to=sid)
            print(f'✅ 匹配成功！房间 {waiting_room}')
            waiting_room = None
        else:
            emit('error', {'msg': '房间已满'})

@socketio.on('play_action')
def handle_play_action(data):
    room_id = data.get('room_id')
    action = data.get('action')
    sid = request.sid
    
    if room_id not in rooms:
        emit('action_error', {'msg': '房间不存在'})
        return
    
    room = rooms[room_id]
    success, msg = room.set_action(sid, action)
    
    if not success:
        emit('action_error', {'msg': msg})
        return
    
    emit('action_confirmed', {'action': action, 'msg': msg})
    print(f'📝 玩家 {sid} 出招: {action}')
    
    if room.is_ready():
        result = room.resolve_turn()
        print(f'⚔️ 回合 {result["turn"]} 结算: {result["detail"]}')
        print(f'🔍 发送前检查: action1={result.get("action1")}, action2={result.get("action2")}')
        emit('turn_result', result, room=room_id)
        
        if result.get('game_over'):
            emit('game_over', {
                'winner': result['winner'],
                'final_states': room.players
            }, room=room_id)
            print(f'🏁 游戏结束！胜者: {result["winner"]}')
            del rooms[room_id]

@socketio.on('get_actions')
def handle_get_actions(data):
    room_id = data.get('room_id')
    sid = request.sid
    
    if room_id not in rooms:
        return
    
    room = rooms[room_id]
    state = room.get_player_state(sid)
    actions = room.get_available_actions(sid)
    
    emit('update_actions', {
        'j_energy': state.get('j_energy', 0),
        'hp': state.get('hp', 0),
        'available_actions': actions
    })

@socketio.on('disconnect')
def handle_disconnect():
    print(f'❌ 玩家 {request.sid} 断开连接')
    for room_id, room in list(rooms.items()):
        if request.sid in room.players:
            del rooms[room_id]
            print(f'🗑️ 删除房间 {room_id}')

if __name__ == '__main__':
    print('''
    ╔═══════════════════════════════════════╗
    ║   🎮 JDT 对战服务器启动中...          ║
    ║   访问地址: http://localhost:5000     ║
    ║   局域网访问: http://你的IP:5000      ║
    ║                                       ║
    ║   💡 加新技能只需修改 config.py       ║
    ║   前端按钮会自动生成！                ║
    ╚═══════════════════════════════════════╝
    ''')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)