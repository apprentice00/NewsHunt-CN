import spacy
import re

# 加载中文模型
nlp = spacy.load("zh_core_web_sm")

# 职务词列表
POSITIONS = {
    '教授', '校长', '主任', '院长', '总工程师', '副总', '总裁', '董事长', '总经理',
    '部长', '局长', '处长', '科长', '书记', '常委', '委员', '代表', '主席', '副主席',
    '秘书长', '副秘书长', '研究员', '工程师', '设计师', '总监', '经理', '主管',
    '党委书记', '党委副书记', '副院长', '副处长', '副科长', '副研究员', '副工程师',
    '副总监', '副经理', '副主管'
}

# 称谓词列表
TITLES = {
    '先生', '女士', '老师', '博士', '硕士', '同学', '同志'
}

# 非人物词列表
NON_PERSON_WORDS = {
    # 抽象概念
    '合理性', '效果', '作用', '竞争力', '方式', '方法', '理念', '主题', '内容',
    '知识', '素质', '能力', '水平', '质量', '效率', '效益', '成果', '成绩', '成就',
    '贡献', '价值', '意义', '影响', '作用', '效果', '目标', '任务', '工作', '事业',
    '项目', '工程', '计划', '规划', '方案', '措施', '办法', '手段', '工具', '设备',
    '设施', '系统', '平台', '网络', '数据', '信息', '资料', '文件', '报告', '论文',
    '文章', '作品', '产品', '服务', '技术', '科学', '艺术', '文化', '教育', '医疗',
    '卫生', '体育', '娱乐', '旅游', '交通', '通信', '能源', '环境', '生态', '资源',
    '材料',
    # 动作词
    '与时俱进', '学会', '探讨', '提出', '跟踪', '打造', '重新', '灵活运用', '展示',
    '进行', '摆在', '评估', '打破', '适应', '指出', '论述', '传授', '解决', '交流',
    '强调', '运用', '注重', '扩充', '创新', '完善', '维护',
    # 时间词
    '11', '12', '上午', '下午', '晚上', '今天', '明天', '昨天',
    # 代词
    '他们', '我们', '你们', '它', '它们', '这个', '那个', '这些', '那些',
    # 数量词
    '一个', '多个', '一些', '多名', '各种',
    # 其他
    '更应', '解决方案', '角度', '帮助', '就业', '教材', '迅速', '典型',
    '教学要求', '北邮', '过程', '虚拟', '以便', '心理健康', '知识结构', '相符',
    '高等教育', '思维能力', '教学质量', '方向', '营造', '隔阂', '核心', '心理',
    '情况', '阶段', '出发', '传统', '管理', '编辑', '跨专业', '全过程', '北京',
    '借助', '文科', '所授', '自身', '有机', '背景', '更大', '数字化', '能否',
    '自主', '论坛', '得力助手', '机会', '至关重要', '重要', '根据', '实时', '数字',
    '对此', '圆桌', '只能', '特点', '教学方法', '依然'
}

# 非人名后缀和排除词
NON_PERSON_SUFFIX = ["时代", "论坛", "峰会", "活动", "AI", "发布会", "讲座"]
# 非时间表达排除词
NON_TIME_WORDS = ["AI时代", "人工智能时代"]

# 事件动作优先词典（可扩展）
EVENT_ACTION_DICT = set([
    '制定政策', '深化改革', '完善机制', '健全体系', '协调关系', '建立平台',
    '推动发展', '促进融合', '增强能力', '提升水平', '加强管理', '转型升级',
    '创新发展', '开展对话', '举办会议', '表示支持', '主持工作', '成立机构',
    '构建生态', '引入资源', '开放合作', '解决问题', '应对挑战', '精准施策',
    '产教融合', '培养人才', '教育育人', '学习经验', '探索路径', '研究方案',
    '传播理念', '识变求变', '激发活力', '承担责任', '规范操作', '分析形势',
    '洞察趋势', '抓住机遇', '入手落实', '面对困难', '适应环境', '转变思路'
])
# 停用动词
STOP_VERBS = set(['能', '要', '为', '是', '有', '在', '与', '和', '及', '将', '被', '让', '使', '于', '对', '以', '把', '到', '等', '并', '或', '及其', '及其'])

def split_sentences(text):
    """
    分句函数
    """
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def is_person(word, context=None):
    """
    判断一个词是否可能是人物
    :param word: 待判断的词
    :param context: 上下文文本（可选）
    :return: 是否是人物
    """
    # 1. 检查是否在非人物词列表中
    if word in NON_PERSON_WORDS:
        return False
    
    # 2. 检查是否包含职务词
    if any(pos in word for pos in POSITIONS):
        return True
    
    # 3. 检查是否包含称谓词
    if any(title in word for title in TITLES):
        return True
    
    # 4. 使用spacy的命名实体识别
    if context:
        doc = nlp(context)
        for ent in doc.ents:
            if ent.text == word and ent.label_ == 'PERSON':
                return True
    
    # 5. 检查词长度（2-4个字）且不包含数字
    if 2 <= len(word) <= 4 and not any(c.isdigit() for c in word):
        # 排除一些常见的非人名词
        if not (word.endswith('公司') or word.endswith('大学') or 
                word.endswith('学院') or word.endswith('中心') or
                word.endswith('部门') or word.endswith('单位') or
                word.endswith('系统') or word.endswith('平台') or
                word.endswith('项目') or word.endswith('工程')):
            return True
    
    return False

def extract_info(text):
    doc = nlp(text)
    
    # 地点
    locations = []
    # 人物
    persons = []
    
    for ent in doc.ents:
        # 地点
        if ent.label_ == 'GPE' or ent.label_ == 'LOC':
            locations.append(ent.text)
        # 人物，2-4字，排除非人名后缀和排除词
        elif ent.label_ == 'PERSON':
            if 2 <= len(ent.text) <= 4 and not any(ent.text.endswith(suf) for suf in NON_PERSON_SUFFIX):
                persons.append(ent.text)
    
    # 时间
    times = []
    for ent in doc.ents:
        if ent.label_ == 'DATE' or ent.label_ == 'TIME':
            # 排除非时间表达
            if ent.text not in NON_TIME_WORDS and not ent.text.endswith("时代") and not ent.text.endswith("AI"):
                times.append(ent.text)
    # 正则补充标准时间表达式
    times.extend(re.findall(r'\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}', text))

    # 事件名称（使用关键词匹配）
    event_names = []
    for token in doc:
        if token.text.endswith(('大会', '活动', '论坛', '峰会', '展览', '仪式', '比赛', '讲座', '研讨会', '发布会')):
            event_names.append(token.text)

    # 事件动作（动词短语抽取+词典优先+停用动词过滤）
    actions = set()
    # 1. 词典优先：只要原文中出现词典短语就收录
    for phrase in EVENT_ACTION_DICT:
        if phrase in text:
            actions.add(phrase)
    # 2. 依存句法分析：动词+名词短语
    for token in doc:
        # 只考虑动词且非停用动词
        if token.pos_ == 'VERB' and token.text not in STOP_VERBS:
            # 动词+直接宾语
            for child in token.children:
                if child.dep_ in ('dobj', 'obj') and child.pos_ in ('NOUN', 'PROPN'):
                    phrase = token.text + child.text
                    actions.add(phrase)
            # 动词+补语/定语
            for child in token.children:
                if child.dep_ in ('attr', 'acomp', 'ccomp', 'xcomp') and child.pos_ in ('NOUN', 'PROPN', 'ADJ'):
                    phrase = token.text + child.text
                    actions.add(phrase)
    # 3. 过滤单字动词、停用动词、无实际意义的词
    actions = {a for a in actions if len(a) > 2 and not any(stop in a for stop in STOP_VERBS)}

    return {
        '地点': list(set(locations)),
        '人物': list(set(persons)),
        '时间': list(set(times)),
        '事件名称': list(set(event_names)),
        '事件动作': list(actions),
    } 