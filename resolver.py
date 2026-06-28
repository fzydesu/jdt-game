from config import ACTION_TYPES

class ActionResolver:
    @staticmethod
    def resolve(action1, action2, state1, state2):
        new_state1 = state1.copy()
        new_state2 = state2.copy()
        
        config1 = ACTION_TYPES.get(action1)
        config2 = ACTION_TYPES.get(action2)
        
        # 处理能量变化
        new_state1['j_energy'] += config1['gain'] - config1['cost']
        new_state2['j_energy'] += config2['gain'] - config2['cost']
        
        damage_to_1 = 0
        damage_to_2 = 0
        detail = "双方行动结束"
        
        # 玩家1进攻 vs 玩家2防御
        if config1['damage'] > 0:
            effective = max(0, config1['damage'] - config2['defense'])
            if effective > 0:
                damage_to_2 = effective
                detail = f"玩家1造成{effective}点伤害"
            else:
                detail = "玩家2成功防御！"
        
        # 玩家2进攻 vs 玩家1防御
        if config2['damage'] > 0:
            effective = max(0, config2['damage'] - config1['defense'])
            if effective > 0:
                damage_to_1 = effective
                detail = f"玩家2造成{effective}点伤害"
            else:
                detail = "玩家1成功防御！"
        
        # 双方都进攻
        if config1['damage'] > 0 and config2['damage'] > 0:
            if config1['damage'] > config2['damage']:
                damage_to_2 = config1['damage'] - config2['damage']
                detail = f"玩家1攻击力更强！造成{damage_to_2}点伤害"
            elif config2['damage'] > config1['damage']:
                damage_to_1 = config2['damage'] - config1['damage']
                detail = f"玩家2攻击力更强！造成{damage_to_1}点伤害"
            else:
                detail = "双方攻击互相抵消！"
        
        new_state1['hp'] -= damage_to_1
        new_state2['hp'] -= damage_to_2
        
        return {
            'result1': 'win' if damage_to_2 > damage_to_1 else 'lose' if damage_to_1 > damage_to_2 else 'draw',
            'result2': 'win' if damage_to_1 > damage_to_2 else 'lose' if damage_to_2 > damage_to_1 else 'draw',
            'damage_to_1': damage_to_1,
            'damage_to_2': damage_to_2,
            'new_state1': new_state1,
            'new_state2': new_state2,
            'detail': detail
        }