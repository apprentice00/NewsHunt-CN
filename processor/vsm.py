import math
from collections import defaultdict
import numpy as np
from .tokenizer import Tokenizer

class VSM:
    def __init__(self, indexer):
        self.indexer = indexer
        self.tokenizer = Tokenizer()
    
    def _calculate_query_vector(self, query):
        """
        计算查询向量
        :param query: 查询文本
        :return: 查询向量（词到权重的映射）
        """
        # 对查询进行分词
        query_tokens = self.tokenizer.tokenize(query)
        
        # 计算查询向量
        query_vector = defaultdict(float)
        for token in query_tokens:
            if token in self.indexer.inverted_index:
                # 使用 TF-IDF 计算权重
                tf = query_tokens.count(token) / len(query_tokens)
                idf = math.log(self.indexer.doc_count / (self.indexer.doc_freq[token] + 1))
                query_vector[token] = tf * idf
        
        return query_vector
    
    def _calculate_cosine_similarity(self, query_vector, doc_vector):
        """
        计算余弦相似度
        :param query_vector: 查询向量
        :param doc_vector: 文档向量
        :return: 相似度分数
        """
        # 计算点积
        dot_product = sum(query_vector[term] * doc_vector[term] 
                         for term in set(query_vector) & set(doc_vector))
        
        # 计算模长
        query_norm = math.sqrt(sum(w * w for w in query_vector.values()))
        doc_norm = math.sqrt(sum(w * w for w in doc_vector.values()))
        
        # 避免除以零
        if query_norm == 0 or doc_norm == 0:
            return 0
        
        return dot_product / (query_norm * doc_norm)
    
    def search(self, query, top_k=10):
        """
        搜索相关文档
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
        
        # 计算相似度并排序
        results = []
        for doc_id, doc_vector in doc_vectors.items():
            similarity = self._calculate_cosine_similarity(query_vector, doc_vector)
            if similarity > 0:
                # 获取文档信息
                doc_info = next(info for info in self.indexer.inverted_index[term] 
                              if info['doc_id'] == doc_id)
                results.append({
                    'title': doc_info['title'],
                    'url': doc_info['url'],
                    'date': doc_info['date'],
                    'score': similarity
                })
        
        # 按相似度降序排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]

if __name__ == '__main__':
    # 测试检索
    from indexer import Indexer
    
    # 加载索引
    indexer = Indexer()
    indexer.load_index('data/index.json')
    
    # 创建检索器
    vsm = VSM(indexer)
    
    # 测试查询
    query = "国务院常务会议"
    results = vsm.search(query)
    
    # 打印结果
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']} (相关度: {result['score']:.4f})")
        print(f"   链接: {result['url']}")
        print(f"   日期: {result['date']}")
        print() 