from __future__ import annotations

DAY1_LOCATION_IDS = ["farm", "plaza", "tavern"]
DAY1_NPC_IDS = ["mira", "tomas", "orren", "lena", "kai", "bram"]
DAY1_EVENT_ID = "starlight_festival_shortage"
NPC_PRESENCE_SOURCES = ["habit", "director_spotlight", "event_skill", "relationship_pull"]

LOCATIONS = [
    {
        "id": "farm",
        "name": "晨露农场",
        "type": "player_home",
        "x": 18,
        "y": 76,
        "color": "#a7f3d0",
        "defaultEntryAnchorId": "farm_house_door",
        "description": "玩家刚搬入的小农场，后续会承载作物、仓库和房屋升级。",
    },
    {
        "id": "home-north",
        "name": "北街住宅区",
        "type": "home",
        "x": 18,
        "y": 28,
        "color": "#7dd3fc",
        "defaultEntryAnchorId": "home_north_lane",
        "description": "安静的家庭住宅区，适合休息、照顾家人和邻里闲聊。",
    },
    {
        "id": "plaza",
        "name": "中央广场",
        "type": "public",
        "x": 50,
        "y": 45,
        "color": "#facc15",
        "defaultEntryAnchorId": "plaza_gate",
        "description": "小镇的公共中心，公告、庆典、争执和偶遇都常发生在这里。",
    },
    {
        "id": "shop",
        "name": "星露杂货铺",
        "type": "commerce",
        "x": 74,
        "y": 36,
        "color": "#fb7185",
        "defaultEntryAnchorId": "shop_counter",
        "description": "购买食物、药品和生活用品，也是居民交换消息的地方。",
    },
    {
        "id": "clinic",
        "name": "白桦诊所",
        "type": "service",
        "x": 32,
        "y": 66,
        "color": "#86efac",
        "defaultEntryAnchorId": "clinic_front_desk",
        "description": "处理疾病、照护老人和人口事件后的心理安抚。",
    },
    {
        "id": "tavern",
        "name": "月猫酒馆",
        "type": "social",
        "x": 70,
        "y": 72,
        "color": "#c084fc",
        "defaultEntryAnchorId": "tavern_door",
        "description": "夜间社交地点，适合谈心、冲突调解和形成新关系。",
    },
]

ANCHORS = [
    {"id": "farm_house_door", "locationId": "farm", "kind": "entry", "screenPosition": {"x": 0.26, "y": 0.68}, "capacity": 1, "tags": ["home", "rest"]},
    {"id": "farm_field", "locationId": "farm", "kind": "farm_field", "screenPosition": {"x": 0.58, "y": 0.72}, "capacity": 4, "tags": ["farm", "crop", "tutorial"]},
    {"id": "plaza_gate", "locationId": "plaza", "kind": "entry", "screenPosition": {"x": 0.18, "y": 0.76}, "capacity": 2, "tags": ["entry", "public"]},
    {"id": "plaza_fountain", "locationId": "plaza", "kind": "social_spot", "screenPosition": {"x": 0.54, "y": 0.62}, "capacity": 3, "tags": ["chat", "public", "festival_view"]},
    {"id": "market_stall", "locationId": "plaza", "kind": "market_spot", "screenPosition": {"x": 0.72, "y": 0.58}, "capacity": 2, "tags": ["market", "errand"]},
    {"id": "tavern_door", "locationId": "tavern", "kind": "entry", "screenPosition": {"x": 0.22, "y": 0.74}, "capacity": 2, "tags": ["entry", "evening"]},
    {"id": "tavern_stage", "locationId": "tavern", "kind": "event_spot", "screenPosition": {"x": 0.62, "y": 0.56}, "capacity": 3, "tags": ["music", "festival", "event"]},
    {"id": "home_north_lane", "locationId": "home-north", "kind": "entry", "screenPosition": {"x": 0.48, "y": 0.70}, "capacity": 2, "tags": ["home", "street"]},
    {"id": "shop_counter", "locationId": "shop", "kind": "service_spot", "screenPosition": {"x": 0.54, "y": 0.60}, "capacity": 2, "tags": ["shop", "trade"]},
    {"id": "clinic_front_desk", "locationId": "clinic", "kind": "service_spot", "screenPosition": {"x": 0.46, "y": 0.64}, "capacity": 2, "tags": ["clinic", "care"]},
]

FARM_PLOTS = [
    {
        "id": "farm_plot_01",
        "locationId": "farm",
        "anchorId": "farm_field",
        "cropId": None,
        "stage": "empty",
        "seedItemId": "starlight_turnip_seed",
        "outputItem": {"id": "fresh_turnip", "name": "新鲜芜菁", "tags": ["crop", "gift", "event_item"]},
    },
    {
        "id": "farm_plot_02",
        "locationId": "farm",
        "anchorId": "farm_field",
        "cropId": None,
        "stage": "empty",
        "seedItemId": "starlight_turnip_seed",
        "outputItem": {"id": "fresh_turnip", "name": "新鲜芜菁", "tags": ["crop", "gift", "event_item"]},
    },
]

INTERACTABLES = [
    {"id": "farm_plot_01", "locationId": "farm", "anchorId": "farm_field", "kind": "farm_plot", "actions": ["plant", "water", "harvest"], "state": {"farmPlotId": "farm_plot_01", "stage": "empty"}},
    {"id": "farm_plot_02", "locationId": "farm", "anchorId": "farm_field", "kind": "farm_plot", "actions": ["plant", "water", "harvest"], "state": {"farmPlotId": "farm_plot_02", "stage": "empty"}},
    {"id": "plaza_notice_board", "locationId": "plaza", "anchorId": "plaza_fountain", "kind": "notice_board", "actions": ["inspect"], "state": {"topic": "town_news"}},
    {"id": "tavern_event_marker", "locationId": "tavern", "anchorId": "tavern_stage", "kind": "event_marker", "actions": ["inspect", "attend_event"], "state": {"eventId": DAY1_EVENT_ID}},
]

NPC_SOFT_PRESENCE = {
    "mira": {"anchorId": "market_stall", "intent": "整理杂货铺临时摊位，并观察星灯祭供应是否还够。"},
    "tomas": {"anchorId": "plaza_fountain", "intent": "检查广场木制摊架，顺手照看米娅附近的动线。"},
    "orren": {"anchorId": "plaza_fountain", "intent": "在喷泉旁记录小镇历史，等待年轻人主动来问旧故事。"},
    "lena": {"anchorId": "plaza_fountain", "intent": "留意广场居民的疲惫状态，准备提供轻量健康建议。"},
    "kai": {"anchorId": "tavern_stage", "intent": "试着维持月猫酒馆的节日气氛，同时担心食材短缺影响演出。"},
    "bram": {"anchorId": "farm_field", "intent": "检查农场作物供应，心里仍被酒馆欠账和节日供货拉扯。"},
}

AGENTS = [
    {"id": "mira", "name": "米娅", "genderIdentity": "female", "age": 31, "lifeStage": "adult", "job": "杂货铺店主", "locationId": "plaza", "homeId": "home-north", "personality": ["务实", "照顾型", "轻微焦虑"], "familyId": "family-mira", "spouseId": "tomas", "childrenIds": ["nina"], "longTermGoals": ["让杂货铺稳定盈利", "照顾刚出生的孩子"], "money": 72, "health": 84},
    {"id": "tomas", "name": "托玛", "genderIdentity": "male", "age": 34, "lifeStage": "adult", "job": "木匠", "locationId": "plaza", "homeId": "home-north", "personality": ["可靠", "沉默", "保护欲强"], "familyId": "family-mira", "spouseId": "mira", "childrenIds": ["nina"], "longTermGoals": ["修缮小镇公共设施", "成为更好的父亲"], "money": 51, "health": 88},
    {"id": "nina", "name": "妮娜", "genderIdentity": "female", "age": 1, "lifeStage": "child", "job": "婴儿", "locationId": "home-north", "homeId": "home-north", "personality": ["好奇", "依赖"], "familyId": "family-mira", "parentsIds": ["mira", "tomas"], "childrenIds": [], "longTermGoals": ["健康成长"], "money": 0, "health": 76},
    {"id": "orren", "name": "奥蕾娅", "genderIdentity": "female", "age": 72, "lifeStage": "elder", "job": "退休教师", "locationId": "plaza", "homeId": "home-north", "personality": ["睿智", "固执", "爱讲故事"], "familyId": "family-orren", "childrenIds": [], "longTermGoals": ["留下小镇历史记录", "修复和年轻人的关系"], "money": 35, "health": 54},
    {"id": "lena", "name": "莉娜", "genderIdentity": "female", "age": 27, "lifeStage": "adult", "job": "医生", "locationId": "plaza", "homeId": "home-north", "personality": ["理性", "共情", "疲惫"], "familyId": "family-lena", "childrenIds": [], "longTermGoals": ["降低老人死亡风险", "建立公共健康档案"], "money": 64, "health": 82},
    {"id": "kai", "name": "凯娅", "genderIdentity": "female", "age": 22, "lifeStage": "young_adult", "job": "酒馆乐手", "locationId": "tavern", "homeId": "home-north", "personality": ["外向", "冲动", "浪漫"], "familyId": "family-kai", "childrenIds": [], "longTermGoals": ["写出小镇之歌", "获得更多朋友认可"], "money": 24, "health": 79},
    {"id": "sana", "name": "萨娜", "genderIdentity": "female", "age": 41, "lifeStage": "adult", "job": "镇长", "locationId": "plaza", "homeId": "home-north", "personality": ["组织者", "强势", "责任感"], "familyId": "family-sana", "childrenIds": ["rio"], "longTermGoals": ["维持小镇稳定", "处理迁入居民适应问题"], "money": 90, "health": 80},
    {"id": "rio", "name": "里奥", "genderIdentity": "male", "age": 13, "lifeStage": "teen", "job": "学生", "locationId": "plaza", "homeId": "home-north", "personality": ["叛逆", "敏感", "好奇"], "familyId": "family-sana", "parentsIds": ["sana"], "childrenIds": [], "longTermGoals": ["证明自己能独立", "找到志同道合的朋友"], "money": 8, "health": 91},
    {"id": "ivy", "name": "艾薇", "genderIdentity": "female", "age": 29, "lifeStage": "adult", "job": "外来研究员", "locationId": "plaza", "homeId": "home-north", "personality": ["观察型", "礼貌", "疏离"], "familyId": "family-ivy", "childrenIds": [], "longTermGoals": ["记录 Agent 社会实验", "融入本地社群"], "money": 58, "health": 86},
    {"id": "bram", "name": "布兰娜", "genderIdentity": "female", "age": 36, "lifeStage": "adult", "job": "农场主", "locationId": "farm", "homeId": "home-north", "personality": ["勤劳", "直率", "记仇", "强势"], "familyId": "family-bram", "childrenIds": [], "longTermGoals": ["稳定农田供应", "化解和酒馆的欠账冲突"], "money": 44, "health": 78},
]

INITIAL_RELATIONS = [
    ("mira", "tomas", 82, 79, 8, "spouse"), ("mira", "nina", 96, 92, 0, "parent"), ("tomas", "nina", 94, 90, 0, "parent"),
    ("sana", "rio", 68, 61, 22, "parent"), ("lena", "orren", 74, 80, 6, "doctor_patient"), ("kai", "bram", 34, 35, 44, "debt_conflict"),
    ("ivy", "sana", 52, 48, 4, "newcomer"), ("mira", "bram", 57, 63, 12, "supplier"), ("kai", "rio", 70, 46, 10, "mentor"),
]

DAY1_EVENTS = [
    {
        "id": DAY1_EVENT_ID,
        "title": "星灯祭供应短缺",
        "locationId": "tavern",
        "phase": "evening",
        "status": "available",
        "summary": "月猫酒馆准备星灯祭前夜小聚，但节日食材不足，凯娅和布兰娜因为欠账与供货压力起了争执。",
        "participants": ["player", "kai", "bram", "mira", "lena", "orren", "tomas"],
        "choices": [
            {"id": "donate_crop", "label": "拿出新鲜芜菁帮酒馆渡过今晚"},
            {"id": "mediate", "label": "调解凯娅和布兰娜的欠账冲突"},
            {"id": "support_kai", "label": "优先支持凯娅维持节日气氛"},
            {"id": "support_bram", "label": "优先支持布兰娜守住供货底线"},
            {"id": "observe", "label": "先旁观并记录大家的反应"},
        ],
    }
]
