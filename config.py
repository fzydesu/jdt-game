# 技能配置 - 想加新技能就在这里加
ACTION_TYPES = {
    'J': {
        'name': '攒J',
        'cost': 0,
        'gain': 1,
        'damage': 0,
        'defense': 0,
        'description': '积蓄1点J气'
    },
    '挡': {
        'name': '挡',
        'cost': 0,
        'gain': 0,
        'damage': 0,
        'defense': 2,
        'description': '抵挡2点伤害'
    },
    '掏': {
        'name': '掏',
        'cost': 1,
        'gain': 0,
        'damage': 1,
        'defense': 0,
        'description': '消耗1J，造成1点伤害'
    },
    '戳': {
        'name': '戳',
        'cost': 2,
        'gain': 0,
        'damage': 2,
        'defense': 0,
        'description': '消耗2J，造成2点伤害'
    },
    '爆': {
        'name': '爆/拍',
        'cost': 3,
        'gain': 0,
        'damage': 3,
        'defense': 0,
        'description': '消耗3J，造成3点伤害'
    },
    '剪': {
        'name': '剪',
        'cost': 4,
        'gain': 0,
        'damage': 4,
        'defense': 0,
        'description': '消耗4J，造成4点伤害'
    },
    '捏': {
        'name': '捏',
        'cost': 5,
        'gain': 0,
        'damage': 5,
        'defense': 0,
        'description': '消耗5J，造成5点伤害'
    },
    '砍': {
        'name': '砍/阿西吧！',
        'cost': 6,
        'gain': 0,
        'damage': 6,
        'defense': 0,
        'description': '消耗6J，造成6点伤害'
    },
    '吃': {
        'name': '吃',
        'cost': 7,
        'gain': 0,
        'damage': 7,
        'defense': 0,
        'description': '消耗7J，造成7点伤害'
    },#以下为格挡
    '铛！': {
        'name': '铛！',
        'cost': 1,
        'gain': 0,
        'damage': 0,
        'defense': 5,
        'description': '消耗1J，抵挡5点伤害'
    },
    '护板': {
        'name': '护板',
        'cost': 2,
        'gain': 0,
        'damage': 0,
        'defense': 8,
        'description': '消耗2J，抵挡8点伤害'
    }
}

INITIAL_STATE = {
    'j_energy': 0,
    'hp': 5,
    'max_hp': 999
}