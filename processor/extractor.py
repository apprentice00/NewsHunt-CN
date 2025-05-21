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
    '时代', '更应', '解决方案', '角度', '帮助', '就业', '教材', '迅速', '典型',
    '教学要求', '北邮', '过程', '虚拟', '以便', '心理健康', '知识结构', '相符',
    '高等教育', '思维能力', '教学质量', '方向', '营造', '隔阂', '核心', '心理',
    '情况', '阶段', '出发', '传统', '管理', '编辑', '跨专业', '全过程', '北京',
    '借助', '文科', '所授', '自身', '有机', '背景', '更大', '数字化', '能否',
    '自主', '论坛', '得力助手', '机会', '至关重要', '重要', '根据', '实时', '数字',
    '对此', '圆桌', '只能', '特点', '教学方法', '依然'
}

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
    # 使用spacy处理文本
    doc = nlp(text)
    
    # 地点
    locations = []
    # 人物
    persons = []
    
    # 使用spacy的命名实体识别
    for ent in doc.ents:
        if ent.label_ == 'GPE' or ent.label_ == 'LOC':  # GPE表示地理政治实体，LOC表示位置
            locations.append(ent.text)
        elif ent.label_ == 'PERSON':
            persons.append(ent.text)
    
    # 时间（使用spacy的时间识别和正则匹配）
    times = []
    # 1. 使用spacy识别时间
    for ent in doc.ents:
        if ent.label_ == 'DATE' or ent.label_ == 'TIME':
            times.append(ent.text)
    # 2. 使用正则匹配
    times.extend(re.findall(r'\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}', text))

    # 事件名称（使用关键词匹配）
    event_names = []
    for token in doc:
        if token.text.endswith(('大会', '活动', '论坛', '峰会', '展览', '仪式', '比赛', '讲座', '研讨会', '发布会')):
            event_names.append(token.text)

    # 事件动作（使用spacy的词性标注）
    actions = []
    for token in doc:
        if token.pos_ == 'VERB':  # spacy中VERB表示动词
            actions.append(token.text)

    return {
        '地点': list(set(locations)),
        '人物': list(set(persons)),
        '时间': list(set(times)),
        '事件名称': list(set(event_names)),
        '事件动作': list(set(actions)),
    } 