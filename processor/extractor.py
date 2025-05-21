import jieba
import jieba.posseg as pseg
import re
from pyhanlp import *
from ltp import LTP

# 初始化LTP
ltp = LTP()

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

def get_hanlp_ner(text):
    """
    使用HanLP进行命名实体识别
    """
    NerLexicon = JClass("com.hankcs.hanlp.dictionary.CoreDictionary")
    ner_result = HanLP.segment(text)
    persons = []
    for term in ner_result:
        if term.nature == 'nr':  # nr表示人名
            persons.append(term.word)
    return persons

def get_ltp_ner(text):
    """
    使用LTP进行命名实体识别
    """
    seg, hidden = ltp.seg([text])
    ner = ltp.ner(hidden)
    persons = []
    for i, (word, tag) in enumerate(zip(seg[0], ner[0])):
        if tag == 'Nh':  # Nh表示人名
            persons.append(word)
    return persons

def get_ltp_dependency(text):
    """
    使用LTP进行依存句法分析
    """
    seg, hidden = ltp.seg([text])
    dep = ltp.dep(hidden)
    return seg[0], dep[0]

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
    
    # 4. 使用HanLP的命名实体识别
    if word in get_hanlp_ner(word):
        return True
    
    # 5. 使用LTP的命名实体识别
    if word in get_ltp_ner(word):
        return True
    
    # 6. 使用jieba的词性标注
    words = pseg.cut(word)
    for w, flag in words:
        if flag == 'nr':  # nr表示人名
            return True
    
    # 7. 检查词长度（2-4个字）且不包含数字
    if 2 <= len(word) <= 4 and not any(c.isdigit() for c in word):
        # 排除一些常见的非人名词
        if not (word.endswith('公司') or word.endswith('大学') or 
                word.endswith('学院') or word.endswith('中心') or
                word.endswith('部门') or word.endswith('单位') or
                word.endswith('系统') or word.endswith('平台') or
                word.endswith('项目') or word.endswith('工程')):
            # 8. 如果有上下文，检查上下文中的职务词
            if context:
                context_words = jieba.cut(context)
                for ctx_word in context_words:
                    if any(pos in ctx_word for pos in POSITIONS):
                        return True
            return True
    
    return False

def extract_info(text):
    # 分句
    sentences = HanLP.extractSummary(text, 100)  # 使用HanLP进行分句
    
    # 地点（使用HanLP的命名实体识别）
    locations = []
    for sentence in sentences:
        ner_result = HanLP.segment(sentence)
        for term in ner_result:
            if term.nature == 'ns':  # ns表示地名
                locations.append(term.word)
    
    # 人物（使用改进的规则）
    persons = []
    # 1. 使用HanLP的命名实体识别
    persons.extend(get_hanlp_ner(text))
    # 2. 使用LTP的命名实体识别
    persons.extend(get_ltp_ner(text))
    # 3. 使用自定义规则
    words = list(jieba.cut(text))
    for i, word in enumerate(words):
        # 获取上下文（前后各5个词）
        start = max(0, i - 5)
        end = min(len(words), i + 6)
        context = ' '.join(words[start:end])
        
        if is_person(word, context):
            persons.append(word)
    
    # 时间（使用HanLP的命名实体识别和正则匹配）
    times = []
    # 1. 使用HanLP识别时间
    for sentence in sentences:
        ner_result = HanLP.segment(sentence)
        for term in ner_result:
            if term.nature == 't':  # t表示时间
                times.append(term.word)
    # 2. 使用正则匹配
    times.extend(re.findall(r'\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}', text))

    # 事件名称（使用依存句法分析）
    event_names = []
    seg, dep = get_ltp_dependency(text)
    for i, (word, tag) in enumerate(zip(seg, dep)):
        if word.endswith(('大会', '活动', '论坛', '峰会', '展览', '仪式', '比赛', '讲座', '研讨会', '发布会')):
            event_names.append(word)

    # 事件动作（使用依存句法分析）
    actions = []
    for i, (word, tag) in enumerate(zip(seg, dep)):
        if tag == 'HED':  # HED表示核心谓语
            actions.append(word)

    return {
        '地点': list(set(locations)),
        '人物': list(set(persons)),
        '时间': list(set(times)),
        '事件名称': list(set(event_names)),
        '事件动作': list(set(actions)),
    } 