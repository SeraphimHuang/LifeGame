from typing import List, Dict, Optional
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from apps.config.models import AttributeMapping
from .services import llm_json


ACTION_KEYWORDS = ["整理", "清理", "打扫", "垃圾", "做饭", "煮", "洗", "购物", "出门", "通勤", "运动", "跑步", "俯卧撑", "哑铃", "飞鸟", "快走", "热身", "睡", "起床", "早餐", "吃早", "收纳"]
STUDY_KEYWORDS = ["学习", "作业", "作题", "题目", "复习", "阅读", "读书", "论文", "面试准备", "笔试", "LeetCode", "课程", "上课"]


def is_study(title: str) -> bool:
    return any(k in title for k in STUDY_KEYWORDS)


def generate_action_subtasks(title: str) -> List[Dict]:
    t = title
    subtasks: List[Dict] = []
    lower = t.lower()
    # 求职/投简历类：强制第一步为启动动作
    if any(k in t for k in ["简历", "投递", "求职"]):
        subtasks = [
            {"title": "坐到桌前，花10秒打开电脑并接上电源。", "estimate_seconds": 10},
            {"title": "整备投递装备，花1分钟打开浏览器与简历文件夹。", "estimate_seconds": 60},
            {"title": "像踏入公会榜单，花5分钟定位本次目标岗位清单。", "estimate_seconds": 300},
            {"title": "投出第一封试探之矢，花3分钟完成一次提交。", "estimate_seconds": 180},
        ]
        return subtasks
    if "早餐" in t or "吃早" in t:
        subtasks = [
            {"title": "最重要的一步是，花10秒从床上坐起来穿上拖鞋。", "estimate_seconds": 10},
            {"title": "进入厨房，花3分钟准备餐具与简单食材。", "estimate_seconds": 180},
            {"title": "点火开局，花5分钟完成主食或加热。", "estimate_seconds": 300},
            {"title": "收尾结算，花1分钟整理台面与餐具。", "estimate_seconds": 60},
        ]
    elif any(k in t for k in ["整理", "清理", "打扫", "垃圾"]):
        subtasks = [
            {"title": "作为寻宝环节，花5分钟找到房间里所有需要清洗的衣物。", "estimate_seconds": 300},
            {"title": "装备垃圾袋，花3分钟收集可见垃圾。", "estimate_seconds": 180},
            {"title": "集中清点，花2分钟把散落物归位到固定位置。", "estimate_seconds": 120},
        ]
    elif any(k in t for k in ["运动", "跑步", "快走", "哑铃", "俯卧撑", "飞鸟"]):
        subtasks = [
            {"title": "进入训练副本，花3分钟做关节热身。", "estimate_seconds": 180},
            {"title": "主线动作，花12分钟完成一组核心训练。", "estimate_seconds": 720},
            {"title": "收招拉伸，花3分钟舒缓心率。", "estimate_seconds": 180},
        ]
    elif any(k in t for k in ["出门", "通勤", "上课"]):
        subtasks = [
            {"title": "出门打怪前置补给，花2分钟打包手机、充电宝、雨伞、水、纸巾。", "estimate_seconds": 120},
            {"title": "钥匙与卡，花30秒确认入口装备。", "estimate_seconds": 30},
        ]
    else:
        # 通用行动模板
        subtasks = [
            {"title": "开场与定位，花1分钟圈定目标地点或物品。", "estimate_seconds": 60},
            {"title": "推进主目标，花8分钟完成关键一步。", "estimate_seconds": 480},
            {"title": "收尾检查，花1分钟把成果放到位。", "estimate_seconds": 60},
        ]
    return subtasks


def generate_study_subtasks(title: str) -> List[Dict]:
    # 学习类默认不带估时（用户可手动添加），第一条为启动动作
    return [
        {"title": "就位与开局：坐到桌前，打开资料与题目。"},
        {"title": "拆页推进：完成一个最小可交付的片段。"},
        {"title": "收束提交：记录卡点，存档本次进展。"},
    ]


def infer_attribute_weights(title: str):
    # 粗略推断：学习/体力/魅力/技艺 各给 0/1 值，再做软化
    w = {"learning": 0.0, "stamina": 0.0, "charisma": 0.0, "craft": 0.0, "inspiration": 0.0}
    if is_study(title):
        w["learning"] = 1.0
    if any(k in title for k in ["面试", "会面", "沟通", "交流"]):
        w["charisma"] = 1.0
    if any(k in title for k in ["跑步", "运动", "快走", "俯卧撑", "哑铃", "飞鸟"]):
        w["stamina"] = 1.0
    if any(k in title for k in ["做饭", "整理", "清理", "打扫", "修理", "写作", "创作"]):
        w["craft"] = 1.0
    if any(k in title for k in ["写作", "创作", "灵感", "构思", "点子"]):
        w["inspiration"] = 1.0
    # 若全为0，则给一个均匀轻权
    if sum(w.values()) == 0:
        for k in w:
            w[k] = 0.2
    return w


KEY_MAP = {
    "学习": "learning",
    "体力": "stamina",
    "魅力": "charisma",
    "技艺": "craft",
    "灵感": "inspiration",
    "learning": "learning",
    "stamina": "stamina",
    "charisma": "charisma",
    "craft": "craft",
    "inspiration": "inspiration",
}


def normalize_weights(weights: Dict, prior: Optional[Dict] = None, alpha: float = 0.7) -> Dict[str, float]:
    if not isinstance(weights, dict):
        weights = {}
    # map keys to english and clamp
    w: Dict[str, float] = {k: 0.0 for k in ["learning", "stamina", "charisma", "craft", "inspiration"]}
    for k, v in weights.items():
        ek = KEY_MAP.get(k, None)
        if not ek:
            continue
        try:
            fv = float(v)
        except Exception:
            continue
        w[ek] = max(0.0, min(1.0, fv))
    # blend with prior if provided
    if prior and isinstance(prior, dict):
        for k in w.keys():
            try:
                pv = float(prior.get(k, 0))
            except Exception:
                pv = 0.0
            w[k] = alpha * max(0.0, min(1.0, pv)) + (1 - alpha) * w[k]
    # normalize optional（使总量不至于过大）
    total = sum(w.values())
    if total > 0:
        w = {k: round(v / total, 2) for k, v in w.items()}
    return w


def classify_label(title: str) -> Optional[str]:
    t = title
    if any(k in t for k in ["简历", "投递", "求职"]):
        return "求职-简历投递"
    if any(k in t for k in ["笔试", "面试", "模拟面试", "沟通", "交流"]):
        return "笔试/面试"
    if any(k in t for k in ["上课", "作业", "复习", "课程", "题"]):
        return "学业-上课/作业"
    if any(k in t for k in ["跑步", "运动", "快走", "俯卧撑", "哑铃", "飞鸟", "热身", "健身"]):
        return "运动训练"
    if any(k in t for k in ["早睡", "早起", "作息"]):
        return "作息-早睡早起"
    if any(k in t for k in ["做饭", "家务", "清理", "整理", "打扫"]):
        return "家务/做饭"
    if any(k in t for k in ["社交", "会友", "聚会"]):
        return "社交/会友"
    if any(k in t for k in ["创作", "写作", "灵感", "构思", "点子"]):
        return "创作/写作"
    if any(k in t for k in ["工具", "技能", "学习"]):
        return "工具/技能学习"
    if any(k in t for k in ["玩耍", "休闲", "游戏"]):
        return "玩耍/休闲"
    return None


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def decompose(request):
    title = (request.data.get("title") or "").strip()
    if not title:
        return Response({"detail": "title required"}, status=status.HTTP_400_BAD_REQUEST)
    # 先尝试 LLM
    label = classify_label(title)
    prior = None
    if label:
        row = AttributeMapping.objects.filter(label=label).first()
        if row:
            prior = row.weights
    schema = '{"subtasks":[{"title":"string","estimate_seconds":120}],"attribute_weights":{"learning":0.5,"stamina":0.1,"charisma":0.1,"craft":0.3,"inspiration":0.0}}'
    prompt = (
        "你是一个奇幻冒险的小说家，你正在写一本小说将现实世界的任务转换成奇幻世界的冒险。\n"
        "将用户的大任务标题拆解为 3–6 条子任务，并输出 JSON：subtasks 与 attribute_weights。\n"
        "- 语气与风格：奇幻冒险隐喻、RPG 风，第三人称；句子短；鼓励化；避免“必须/一定”等压力词。\n"
        "- 题材指引：优先采用「城市/行会/告示板/邮亭/印蜡章」等城市日常意象；学习/研究场景可用「书卷/抄写室/学徒/符文」；健身可用「训练场/器械/印记」。\n"
        "- 学习类不估时；家务/作息/运动/出门/整理/投递等行动型可给 estimate_seconds（单位只用“秒”）。\n"
        "- 第一条子任务必须是“启动动作”，估时 10–60 秒，如：坐到案台点亮台灯、展开卷轴、推开窗等。\n"
        "- 子任务标题需“可立刻执行”，拒绝空泛措辞（如“继续完成任务”）；必要时用具体动作词（打开/写下/封缄/投递/抄录）。\n"
        "- attribute_weights 为 学习/体力/魅力/技艺/灵感 的权重，范围 0–1；若提供了先验权重 prior，请尽量贴近并做归一化。\n\n"
        f"标题：{title}\n"
        f"先验权重（可无）：{prior or '无'}\n\n"
        "仅返回 JSON。例如：\n"
        "{\n"
        '  "subtasks": [\n'
        '    { "title": "（动词开头的启动动作…）", "estimate_seconds": 40 },\n'
        '    { "title": "（…）", "estimate_seconds": 180 },\n'
        '    { "title": "（学习类则不含 estimate_seconds）" }\n'
        "  ],\n"
        '  "attribute_weights": {\n'
        '    "学习": 0.40, "体力": 0.10, "魅力": 0.15, "技艺": 0.20, "灵感": 0.15\n'
        "  }\n"
        "}\n"
    )
    data = llm_json(prompt, schema)
    if data and "subtasks" in data:
        # 归一化权重键名与范围
        weights = data.get("attribute_weights") or {}
        weights = normalize_weights(weights, prior)
        data["attribute_weights"] = weights
        return Response(data)
    # 回退到本地生成
    if is_study(title):
        subtasks = generate_study_subtasks(title)
    else:
        subtasks = generate_action_subtasks(title)
    # 优先用设置页里的默认映射；命中不到再用本地推断
    label = classify_label(title)
    attr_w = None
    if label:
        row = AttributeMapping.objects.filter(label=label).first()
        if row:
            attr_w = row.weights
    if not attr_w:
        attr_w = infer_attribute_weights(title)
    return Response({"subtasks": subtasks, "attribute_weights": attr_w})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def score(request):
    title = (request.data.get("title") or "").strip()
    subtasks = request.data.get("subtasks", [])
    schema = '{"score": 25}'
    prompt = (
        "给出该任务的整数分值（5–50）。只返回JSON。\n"
        f"标题：{title}\n子任务数量：{len(subtasks)}"
    )
    data = llm_json(prompt, schema)
    if data and isinstance(data.get("score"), int):
        s = max(5, min(50, int(data["score"])))
        return Response({"score": s})
    # fallback：按子任务数给出一个粗略分
    base = 5 + min(45, len(subtasks) * 5)
    return Response({"score": base})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reward(request):
    dominant = request.data.get("dominant_attribute", "learning")
    summary = request.data.get("task_summary", "")
    schema = '{"name":"回声指环","description":"……"}'
    prompt = (
        "生成一件奇幻风但不带数值的物品，用于任务奖励。返回JSON包含 name 与 description。"
        f"主导属性：{dominant}；任务摘要：{summary}。"
    )
    data = llm_json(prompt, schema)
    if data and data.get("name") and data.get("description"):
        return Response({"name": data["name"], "description": data["description"]})
    # fallback
    return Response({"name": "无名纹章", "description": "其表面在夜里泛起微光，像在默默记下你的努力。"})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def level_story(request):
    display_name = request.data.get("display_name", "旅者")
    level = int(request.data.get("level", 1))
    recent = request.data.get("recentTasks", [])
    total_score = sum(int(t.get("score", 0)) for t in recent)
    target_len = 200 + total_score * 3
    schema = '{"title":"等级X的边界","content":"……"}'
    prompt = (
        "用中性第三人称写一段奇幻冒险短文，称呼固定为“勇者{display_name}”。"
        f"长度约{target_len}字；允许出现在荒野与城市之间往来。任务线索：{recent}"
    )
    data = llm_json(prompt, schema)
    if data and data.get("title") and data.get("content"):
        return Response({"title": data["title"], "content": data["content"]})
    # fallback
    return Response({"title": f"等级 {level} 的边界", "content": f"在新的旅程里，勇者{display_name}整备行囊……"})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def narrative(request):
    title = (request.data.get("title") or "").strip()
    if not title:
        return Response({"detail": "title required"}, status=status.HTTP_400_BAD_REQUEST)
    # 读取映射作为先验
    label = classify_label(title)
    prior = None
    if label:
        row = AttributeMapping.objects.filter(label=label).first()
        if row:
            prior = row.weights
    schema = '{"narrative":"……","attribute_weights":{"learning":0.4,"stamina":0.1,"charisma":0.15,"craft":0.2,"inspiration":0.15}}'
    prompt = (
        "你是“奇幻城邦的吟游诗人兼文书官”。根据任务标题，创作一段 120–220 字的奇幻式鼓励文案，让读者立刻想开始。\n"
        "- 题材与隐喻：城市/行会/告示板/邮亭/印蜡章/金色封缄/名册/案台/信笺/徽记 等；可加少量自然场景（灯火/风/晨雾）。\n"
        "- 叙事要求：第三人称；句子短；鼓励化；避免“必须/一定”等压力词。\n"
        "- 画面元素（尽量包含）：①一个「启动仪式」镜头（例如点亮案台灯或系好行囊）；②一个「核心动作」隐喻（如把 5 道题映射为“五枚试题碑”或“五只小魔偶”）；③一个「回执或印记」结尾（如盖章、铭刻、路标）。\n"
        "- 若标题包含数量（如“5 道/3 篇/2 小时”），在文案里做对应的奇幻意象（如“五枚封缄的金色信封投入行会投递匣”）。\n"
        "- attribute_weights 为 学习/体力/魅力/技艺/灵感 的权重，范围 0–1；若提供了先验权重 prior，请尽量贴近并做归一化。\n"
        "- 不要输出子任务或步骤；不出现项目符号和列表；只给一段文案。\n\n"
        f"标题：{title}\n先验权重（可无）：{prior or '无'}\n\n"
        "仅返回 JSON，格式如下：\n"
        "{\n"
        '  "narrative": "（120–220 字的奇幻鼓励文案。含启动仪式、核心动作隐喻、回执/印记收束。城市/行会氛围，第三人称，句子短，无压力词。）",\n'
        '  "attribute_weights": {\n'
        '    "学习": 0.45, "体力": 0.10, "魅力": 0.15, "技艺": 0.20, "灵感": 0.10\n'
        "  }\n"
        "}\n"
    )
    data = llm_json(prompt, schema)
    if data and isinstance(data.get("narrative"), str):
        weights = normalize_weights(data.get("attribute_weights") or {}, prior)
        return Response({"narrative": data["narrative"], "attribute_weights": weights})
    # fallback 文案
    fallback = (
        "他在案台前点亮小灯，像为一段旅程点燃火种。面前的任务被刻成几枚小碑，"
        "每推倒一枚，路标上的徽记便多亮一分。收束时，他把今日的印章按在名册上，"
        "像把犹豫钉进夜色的边缘。"
    )
    return Response({"narrative": fallback, "attribute_weights": normalize_weights(infer_attribute_weights(title), prior)})

