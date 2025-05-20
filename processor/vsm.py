import sys
import os
# 将项目根目录添加到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
from collections import defaultdict
import numpy as np
from datetime import datetime
from processor.tokenizer import Tokenizer

class VSM:
    def __init__(self, indexer):
        self.indexer = indexer
        self.tokenizer = Tokenizer()
        # BM25参数
        self.k1 = 1.5  # 词频饱和参数
        self.b = 0.75  # 文档长度归一化参数
        # 确保doc_lengths存在且不为空
        if not hasattr(self.indexer, 'doc_lengths') or not self.indexer.doc_lengths:
            self.indexer.doc_lengths = {doc_id: 1 for doc_id in range(self.indexer.doc_count)}
        self.avg_doc_length = sum(self.indexer.doc_lengths.values()) / len(self.indexer.doc_lengths) if self.indexer.doc_lengths else 1
        self.doc_vectors = {}  # 用于多样性评分
    
    def _calculate_query_vector(self, query):
        """
        计算查询向量，加入查询词权重调整
        :param query: 查询文本
        :return: 查询向量（词到权重的映射）
        """
        # 对查询进行分词
        query_tokens = self.tokenizer.tokenize(query)
        
        # 计算查询向量
        query_vector = defaultdict(float)
        for token in query_tokens:
            if token in self.indexer.inverted_index:
                # 使用改进的TF-IDF计算权重
                tf = query_tokens.count(token) / len(query_tokens)
                idf = math.log((self.indexer.doc_count - self.indexer.doc_freq[token] + 0.5) / 
                             (self.indexer.doc_freq[token] + 0.5) + 1)
                # 加入查询词权重调整
                query_vector[token] = tf * idf * 1.5  # 提高查询词权重
        
        return query_vector
    
    def _calculate_bm25_score(self, query_vector, doc_id, doc_vector):
        """
        计算BM25分数
        :param query_vector: 查询向量
        :param doc_id: 文档ID
        :param doc_vector: 文档向量
        :return: BM25分数
        """
        score = 0.0
        doc_length = self.indexer.doc_lengths[doc_id]
        
        for term, weight in query_vector.items():
            if term in doc_vector:
                # 计算词频
                tf = doc_vector[term]
                # 计算IDF
                idf = math.log((self.indexer.doc_count - self.indexer.doc_freq[term] + 0.5) / 
                             (self.indexer.doc_freq[term] + 0.5) + 1)
                # 计算文档长度归一化
                length_norm = 1 - self.b + self.b * (doc_length / self.avg_doc_length)
                # 计算BM25分数
                score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * length_norm)
        
        return score
    
    def _calculate_time_decay(self, doc_date):
        """
        计算时间衰减因子
        :param doc_date: 文档日期
        :return: 时间衰减分数
        """
        current_date = datetime.now()
        doc_datetime = datetime.strptime(doc_date, "%Y-%m-%d")
        days_diff = (current_date - doc_datetime).days
        return math.exp(-days_diff / 365)  # 使用指数衰减
    
    def _calculate_diversity_score(self, results, doc_id, doc_vector):
        """
        计算多样性分数
        :param results: 当前结果列表
        :param doc_id: 待评估文档ID
        :param doc_vector: 文档向量
        :return: 多样性分数
        """
        if not results:
            return 1.0
        
        # 计算与已有结果的相似度
        max_similarity = 0.0
        for result in results:
            if result['doc_id'] in self.doc_vectors:
                similarity = self._calculate_cosine_similarity(
                    doc_vector, 
                    self.doc_vectors[result['doc_id']]
                )
                max_similarity = max(max_similarity, similarity)
        
        return 1.0 - max_similarity
    
    def _calculate_cosine_similarity(self, vec1, vec2):
        """
        计算两个向量的余弦相似度，仅用于多样性评分
        :param vec1: 向量1
        :param vec2: 向量2
        :return: 相似度分数
        """
        dot_product = sum(vec1[term] * vec2.get(term, 0.0) for term in vec1)
        norm1 = math.sqrt(sum(w * w for w in vec1.values()))
        norm2 = math.sqrt(sum(w * w for w in vec2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
    
    def search(self, query, top_k=10):
        """
        搜索相关文档，使用改进的排序策略
        :param query: 查询文本
        :param top_k: 返回结果数量
        :return: 排序后的文档列表
        """
        # 计算查询向量
        query_vector = self._calculate_query_vector(query)
        
        # 收集相关文档
        doc_scores = defaultdict(float)
        doc_vectors = defaultdict(dict)
        
        # 遍历查询词
        for term, weight in query_vector.items():
            if term in self.indexer.inverted_index:
                for doc_info in self.indexer.inverted_index[term]:
                    doc_id = doc_info['doc_id']
                    doc_vectors[doc_id][term] = doc_info['weight']
        
        # 保存到实例属性，供多样性评分用
        self.doc_vectors = doc_vectors
        
        # 计算综合分数并排序
        results = []
        for doc_id, doc_vector in doc_vectors.items():
            # 计算BM25分数
            bm25_score = self._calculate_bm25_score(query_vector, doc_id, doc_vector)
            
            # 获取文档信息
            doc_info = None
            for term in query_vector:
                if term in self.indexer.inverted_index:
                    for info in self.indexer.inverted_index[term]:
                        if info['doc_id'] == doc_id:
                            doc_info = info
                            break
                    if doc_info:
                        break
            
            if doc_info:
                # 计算时间衰减分数
                time_score = self._calculate_time_decay(doc_info['date'])
                
                # 计算多样性分数
                diversity_score = self._calculate_diversity_score(results, doc_id, doc_vector)
                
                # 计算综合分数
                final_score = (bm25_score * 0.5 +  # BM25分数权重
                             time_score * 0.3 +    # 时间衰减权重
                             diversity_score * 0.2)  # 多样性权重
                
                results.append({
                    'doc_id': doc_id,
                    'title': doc_info['title'],
                    'url': doc_info['url'],
                    'date': doc_info['date'],
                    'score': final_score
                })
        
        # 按综合分数降序排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]

if __name__ == '__main__':
    # 测试检索
    from processor.indexer import Indexer
    
    # 加载索引
    indexer = Indexer()
    indexer.load_index('data/index.json')
    
    # 创建检索器
    vsm = VSM(indexer)
    
    # 测试查询
    query = "人工智能"
    results = vsm.search(query)
    
    # 打印结果
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']} (相关度: {result['score']:.4f})")
        print(f"   链接: {result['url']}")
        print(f"   日期: {result['date']}")
        print() 