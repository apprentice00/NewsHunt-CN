import thulac
import json
import os
import time

# 添加补丁以修复 time.clock() 问题
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter

class Tokenizer:
    def __init__(self):
        # 初始化 THULAC 分词器
        self.thu = thulac.thulac(seg_only=True)
        
        # 加载停用词
        self.stopwords = set()
        self._load_stopwords()
    
    def _load_stopwords(self):
        """加载停用词表"""
        stopwords_path = os.path.join(os.path.dirname(__file__), 'stopwords.txt')
        if os.path.exists(stopwords_path):
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                self.stopwords = set(line.strip() for line in f)
    
    def tokenize(self, text):
        """
        对文本进行分词
        :param text: 输入文本
        :return: 分词后的词列表
        """
        # 使用 THULAC 进行分词
        words = self.thu.cut(text, text=True).split()
        
        # 去除停用词
        words = [word for word in words if word not in self.stopwords]
        
        return words
    
    def process_news(self, news_file, output_file):
        """
        处理新闻文件，对每篇新闻进行分词
        :param news_file: 新闻数据文件路径
        :param output_file: 输出文件路径
        """
        # 读取新闻数据
        with open(news_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        # 对每篇新闻进行分词
        processed_news = []
        for news in news_data:
            processed_news.append({
                'title': news['title'],
                'content': news['content'],
                'url': news['url'],
                'date': news['date'],
                'title_tokens': self.tokenize(news['title']),
                'content_tokens': self.tokenize(news['content'])
            })
        
        # 保存处理后的数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_news, f, ensure_ascii=False, indent=2)
        
        return processed_news

if __name__ == '__main__':
    # 初始化分词器
    tokenizer = Tokenizer()
    
    # 设置输入输出文件路径
    news_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawler', 'data', 'news.json')
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawler', 'data', 'news_tokenized.json')
    
    # 处理新闻文件
    print(f"Processing news file: {news_file}")
    processed_news = tokenizer.process_news(news_file, output_file)
    print(f"Processed {len(processed_news)} news articles")
    print(f"Results saved to: {output_file}") 