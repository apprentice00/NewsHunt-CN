# 中文新闻信息检索系统（NewsHunt-CN）

基于新华网数据的中文新闻信息检索系统，使用 Vue3 + Flask + Python 实现。

## 项目结构

```
NewsHunt-CN/
├── crawler/               # Scrapy 爬虫模块
│   └── xinhuanet_spider.py
├── data/
│   └── news.json          # 原始数据
│   └── index.json         # 倒排索引文件
├── processor/
│   └── tokenizer.py       # THULAC 分词
│   └── indexer.py         # 倒排索引构建
│   └── vsm.py             # 向量空间模型检索算法
├── evaluator/
│   └── evaluation.py      # 准确率评估模块
├── frontend/              # Vue3 前端项目
├── backend/
│   └── app.py             # Flask 后端接口
└── README.md              # 项目说明
```

## 功能特点

1. 数据采集：自动爬取新华网新闻数据
2. 中文分词：使用 THULAC 进行精确分词
3. 倒排索引：高效的信息检索基础
4. 向量空间模型：基于 TF-IDF 的相关度计算
5. 自然语言查询：支持中文自然语言输入
6. 相关度排序：智能排序展示最相关结果
7. 评估系统：支持人工评价和准确率计算

## 安装说明

### 后端环境配置

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 前端环境配置

```bash
cd frontend
npm install
```

## 运行说明

1. 启动爬虫采集数据：
```bash
cd crawler
scrapy crawl xinhuanet
```

2. 启动后端服务：
```bash
cd backend
python app.py
```

3. 启动前端服务：
```bash
cd frontend
npm run dev
```

## 使用说明

1. 访问 http://localhost:5173 打开前端界面
2. 在搜索框输入查询内容
3. 系统会返回相关度排序的新闻列表
4. 点击新闻标题可查看详细内容

## 技术栈

- 前端：Vue3 + Element Plus
- 后端：Flask
- 爬虫：Scrapy
- 分词：THULAC
- 检索：TF-IDF + VSM

## 注意事项

1. 首次运行需要先执行爬虫采集数据
2. 确保已安装所有必要的依赖包
3. 建议使用 Python 3.10+ 版本 