from config import ACTION_TYPES, INITIAL_STATE
from resolver import ActionResolver

class GameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}
        self.actions = {}
        self.game_over = False
        self.turn = 0
        
    def add_player(self, sid):
        if len(self.players) >= 2:
            return False
        self.players[sid] = INITIAL_STATE.copy()
        self.actions[sid] = None
        return True
        
    def set_action(self, sid, action):
        if action not in ACTION_TYPES:
            return False, "无效的行动"
        if ACTION_TYPES[action]['cost'] > self.players[sid]['j_energy']:
            return False, f"J气不足！需要{ACTION_TYPES[action]['cost']}J"
        self.actions[sid] = action
        return True, "行动已提交"
        
    def is_ready(self):
        if len(self.players) != 2:
            return False
        return all(a is not None for a in self.actions.values())
        
    def resolve_turn(self):
        if not self.is_ready():
            return None
            
        self.turn += 1
        sids = list(self.players.keys())
        
        # 获取双方招式
        action1 = self.actions[sids[0]]
        action2 = self.actions[sids[1]]
        
        result = ActionResolver.resolve(
            action1, action2,
            self.players[sids[0]], self.players[sids[1]]
        )
        
        self.players[sids[0]] = result['new_state1']
        self.players[sids[1]] = result['new_state2']
        
        # ⭐ 创建一个全新的字典，确保数据独立
        turn_result = {
            'result1': result.get('result1'),
            'result2': result.get('result2'),
            'damage_to_1': result.get('damage_to_1', 0),
            'damage_to_2': result.get('damage_to_2', 0),
            'new_state1': result.get('new_state1'),
            'new_state2': result.get('new_state2'),
            'detail': result.get('detail', ''),
            'action1': str(action1),  # 强制转字符串
            'action2': str(action2),
            'sid1': sids[0],
            'sid2': sids[1],
            'turn': self.turn
        }
        
        # 清空行动记录
        self.actions = {sid: None for sid in sids}
        
        # 检查游戏是否结束
        if self.players[sids[0]]['hp'] <= 0 or self.players[sids[1]]['hp'] <= 0:
            self.game_over = True
            winner = sids[1] if self.players[sids[0]]['hp'] <= 0 else sids[0]
            turn_result['game_over'] = True
            turn_result['winner'] = winner
        
        return turn_result
        
    def get_player_state(self, sid):
        return self.players.get(sid, {})
        
    def get_available_actions(self, sid):
        if sid not in self.players:
            return []
        j_energy = self.players[sid]['j_energy']
        return [{'id': aid, 'name': cfg['name'], 'cost': cfg['cost'], 'description': cfg['description']} 
                for aid, cfg in ACTION_TYPES.items() if cfg['cost'] <= j_energy]