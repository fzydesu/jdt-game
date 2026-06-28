# 技能配置 - 想加新技能就在这里加
ACTION_TYPES = {
    'J': {
        'name': '聚气',
        'cost': 0,
        'gain': 1,
        'damage': 0,
        'defense': 0,
        'description': '积蓄1点J气'
    },
    'D': {
        'name': '防御',
        'cost': 0,
        'gain': 0,
        'damage': 0,
        'defense': 2,
        'description': '抵挡2点伤害'
    },
    'T': {
        'name': '进攻',
        'cost': 1,
        'gain': 0,
        'damage': 2,
        'defense': 0,
        'description': '消耗1J，造成2点伤害'
    },
    'X': {
        'name': '必杀技',
        'cost': 3,
        'gain': 0,
        'damage': 5,
        'defense': 0,
        'description': '消耗3J，造成5点伤害'
    },
    'Y': {
        'name': '必杀技',
        'cost': 3,
        'gain': 0,
        'damage': 5,
        'defense': 0,
        'description': '消耗3J，造成5点伤害'
    },
    'Z': {
        'name': '必杀技',
        'cost': 3,
        'gain': 0,
        'damage': 5,
        'defense': 0,
        'description': '消耗3J，造成5点伤害'
    }
}

INITIAL_STATE = {
    'j_energy': 0,
    'hp': 10,
    'max_hp': 10
}