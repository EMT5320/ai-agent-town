from __future__ import annotations

LOCATIONS = [
    {"id": "home-north", "name": "北街住宅区", "type": "home", "x": 18, "y": 28, "color": "#7dd3fc", "description": "安静的家庭住宅区，适合休息、照顾家人和邻里闲聊。"},
    {"id": "plaza", "name": "中央广场", "type": "public", "x": 50, "y": 45, "color": "#facc15", "description": "小镇的公共中心，公告、庆典、争执和偶遇都常发生在这里。"},
    {"id": "shop", "name": "星露杂货铺", "type": "commerce", "x": 74, "y": 36, "color": "#fb7185", "description": "购买食物、药品和生活用品，也是居民交换消息的地方。"},
    {"id": "clinic", "name": "白桦诊所", "type": "service", "x": 32, "y": 66, "color": "#86efac", "description": "处理疾病、照护老人和人口事件后的心理安抚。"},
    {"id": "tavern", "name": "月猫酒馆", "type": "social", "x": 70, "y": 72, "color": "#c084fc", "description": "夜间社交地点，适合谈心、冲突调解和形成新关系。"},
]

AGENTS = [
    {"id": "mira", "name": "米拉", "age": 31, "lifeStage": "adult", "job": "杂货铺店主", "locationId": "shop", "homeId": "home-north", "personality": ["务实", "照顾型", "轻微焦虑"], "familyId": "family-mira", "spouseId": "tomas", "childrenIds": ["nina"], "longTermGoals": ["让杂货铺稳定盈利", "照顾刚出生的孩子"], "money": 72, "health": 84},
    {"id": "tomas", "name": "托马斯", "age": 34, "lifeStage": "adult", "job": "木匠", "locationId": "home-north", "homeId": "home-north", "personality": ["可靠", "沉默", "保护欲强"], "familyId": "family-mira", "spouseId": "mira", "childrenIds": ["nina"], "longTermGoals": ["修缮小镇公共设施", "成为更好的父亲"], "money": 51, "health": 88},
    {"id": "nina", "name": "妮娜", "age": 1, "lifeStage": "child", "job": "婴儿", "locationId": "home-north", "homeId": "home-north", "personality": ["好奇", "依赖"], "familyId": "family-mira", "parentsIds": ["mira", "tomas"], "childrenIds": [], "longTermGoals": ["健康成长"], "money": 0, "health": 76},
    {"id": "orren", "name": "奥伦", "age": 72, "lifeStage": "elder", "job": "退休教师", "locationId": "plaza", "homeId": "home-north", "personality": ["睿智", "固执", "爱讲故事"], "familyId": "family-orren", "childrenIds": [], "longTermGoals": ["留下小镇历史记录", "修复和年轻人的关系"], "money": 35, "health": 54},
    {"id": "lena", "name": "蕾娜", "age": 27, "lifeStage": "adult", "job": "医生", "locationId": "clinic", "homeId": "home-north", "personality": ["理性", "共情", "疲惫"], "familyId": "family-lena", "childrenIds": [], "longTermGoals": ["降低老人死亡风险", "建立公共健康档案"], "money": 64, "health": 82},
    {"id": "kai", "name": "凯", "age": 22, "lifeStage": "young_adult", "job": "酒馆乐手", "locationId": "tavern", "homeId": "home-north", "personality": ["外向", "冲动", "浪漫"], "familyId": "family-kai", "childrenIds": [], "longTermGoals": ["写出小镇之歌", "获得更多朋友认可"], "money": 24, "health": 79},
    {"id": "sana", "name": "萨娜", "age": 41, "lifeStage": "adult", "job": "镇长", "locationId": "plaza", "homeId": "home-north", "personality": ["组织者", "强势", "责任感"], "familyId": "family-sana", "childrenIds": ["rio"], "longTermGoals": ["维持小镇稳定", "处理迁入居民适应问题"], "money": 90, "health": 80},
    {"id": "rio", "name": "里奥", "age": 13, "lifeStage": "teen", "job": "学生", "locationId": "plaza", "homeId": "home-north", "personality": ["叛逆", "敏感", "好奇"], "familyId": "family-sana", "parentsIds": ["sana"], "childrenIds": [], "longTermGoals": ["证明自己能独立", "找到志同道合的朋友"], "money": 8, "health": 91},
    {"id": "ivy", "name": "艾薇", "age": 29, "lifeStage": "adult", "job": "外来研究员", "locationId": "plaza", "homeId": "home-north", "personality": ["观察型", "礼貌", "疏离"], "familyId": "family-ivy", "childrenIds": [], "longTermGoals": ["记录 Agent 社会实验", "融入本地社群"], "money": 58, "health": 86},
    {"id": "bram", "name": "布拉姆", "age": 46, "lifeStage": "adult", "job": "农夫", "locationId": "shop", "homeId": "home-north", "personality": ["勤劳", "直率", "记仇"], "familyId": "family-bram", "childrenIds": [], "longTermGoals": ["扩大农田供应", "化解和酒馆的欠账冲突"], "money": 44, "health": 74},
]

INITIAL_RELATIONS = [
    ("mira", "tomas", 82, 79, 8, "spouse"), ("mira", "nina", 96, 92, 0, "parent"), ("tomas", "nina", 94, 90, 0, "parent"),
    ("sana", "rio", 68, 61, 22, "parent"), ("lena", "orren", 74, 80, 6, "doctor_patient"), ("kai", "bram", 34, 35, 44, "debt_conflict"),
    ("ivy", "sana", 52, 48, 4, "newcomer"), ("mira", "bram", 57, 63, 12, "supplier"), ("kai", "rio", 70, 46, 10, "mentor"),
]
