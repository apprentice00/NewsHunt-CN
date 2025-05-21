import json
from collections import defaultdict
import math
import os

class Indexer:
    def __init__(self):
        self.inverted_index = defaultdict(list)
        self.doc_freq = defaultdict(int)  # 文档频率
        self.doc_count = 0  # 文档总数
        self.doc_lengths = {}  # 文档长度
        self.news_data = None  # 新增，存储原始新闻数据
    
    def build_index(self, processed_news):
        """
        构建倒排索引
        :param processed_news: 处理后的新闻数据列表
        """
        self.doc_count = len(processed_news)
        
        # 第一遍遍历：计算文档频率
        for doc_id, news in enumerate(processed_news):
            # 合并标题和内容的分词结果
            all_tokens = news['title_tokens'] + news['content_tokens']
            
            # 计算词频
            term_freq = defaultdict(int)
            for token in all_tokens:
                term_freq[token] += 1
            
            # 更新文档频率
            for term in term_freq:
                self.doc_freq[term] += 1
            
            # 记录文档长度
            self.doc_lengths[doc_id] = len(all_tokens)
        
        # 第二遍遍历：构建倒排索引
        for doc_id, news in enumerate(processed_news):
            # 合并标题和内容的分词结果
            all_tokens = news['title_tokens'] + news['content_tokens']
            
            # 计算词频
            term_freq = defaultdict(int)
            for token in all_tokens:
                term_freq[token] += 1
            
            # 构建倒排索引项
            for term, freq in term_freq.items():
                # 计算 TF-IDF 权重
                tf = freq / self.doc_lengths[doc_id]
                idf = math.log(self.doc_count / (self.doc_freq[term] + 1))
                weight = tf * idf
                
                # 添加到倒排索引
                self.inverted_index[term].append({
                    'doc_id': doc_id,
                    'weight': weight,
                    'title': news['title'],
                    'url': news['url'],
                    'date': news['date']
                })
    
    def save_index(self, output_file):
        """
        保存倒排索引到文件
        :param output_file: 输出文件路径
        """
        index_data = {
            'inverted_index': dict(self.inverted_index),
            'doc_freq': dict(self.doc_freq),
            'doc_count': self.doc_count,
            'doc_lengths': self.doc_lengths
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def load_index(self, input_file):
        """
        从文件加载倒排索引
        :param input_file: 输入文件路径
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        self.inverted_index = defaultdict(list, index_data['inverted_index'])
        self.doc_freq = defaultdict(int, index_data['doc_freq'])
        self.doc_count = index_data['doc_count']
        self.doc_lengths = index_data['doc_lengths']
        # 新增：加载原始新闻数据
        news_tokenized_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'news_tokenized.json')
        if os.path.exists(news_tokenized_path):
            with open(news_tokenized_path, 'r', encoding='utf-8') as f:
                self.news_data = json.load(f)
        else:
            self.news_data = None

if __name__ == '__main__':
    # 测试索引构建
    with open('data/processed_news.json', 'r', encoding='utf-8') as f:
        processed_news = json.load(f)
    
    indexer = Indexer()
    indexer.build_index(processed_news)
    indexer.save_index('data/index.json') 