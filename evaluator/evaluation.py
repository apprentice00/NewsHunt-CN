import json
from collections import defaultdict
import numpy as np
from processor.vsm import VSM
from processor.indexer import Indexer

class Evaluator:
    def __init__(self, vsm):
        self.vsm = vsm
        self.relevance_judgments = {}  # 相关性判断结果
    
    def add_relevance_judgment(self, query, doc_url, is_relevant):
        """
        添加相关性判断
        :param query: 查询文本
        :param doc_url: 文档URL
        :param is_relevant: 是否相关
        """
        if query not in self.relevance_judgments:
            self.relevance_judgments[query] = {}
        self.relevance_judgments[query][doc_url] = is_relevant
    
    def calculate_precision_at_k(self, query, k=10):
        """
        计算前k个结果的准确率
        :param query: 查询文本
        :param k: 结果数量
        :return: 准确率
        """
        if query not in self.relevance_judgments:
            return 0.0
        
        # 获取检索结果
        results = self.vsm.search(query, top_k=k)
        
        # 计算相关文档数量
        relevant_count = 0
        for result in results:
            if result['url'] in self.relevance_judgments[query]:
                if self.relevance_judgments[query][result['url']]:
                    relevant_count += 1
        
        return relevant_count / k if k > 0 else 0.0
    
    def calculate_map(self, queries):
        """
        计算平均准确率均值（MAP）
        :param queries: 查询列表
        :return: MAP值
        """
        ap_values = []
        
        for query in queries:
            if query not in self.relevance_judgments:
                continue
            
            # 获取检索结果
            results = self.vsm.search(query)
            
            # 计算平均准确率
            relevant_count = 0
            precision_sum = 0.0
            
            for i, result in enumerate(results, 1):
                if result['url'] in self.relevance_judgments[query]:
                    if self.relevance_judgments[query][result['url']]:
                        relevant_count += 1
                        precision_sum += relevant_count / i
            
            if relevant_count > 0:
                ap_values.append(precision_sum / relevant_count)
        
        return np.mean(ap_values) if ap_values else 0.0
    
    def save_judgments(self, output_file):
        """
        保存相关性判断结果
        :param output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.relevance_judgments, f, ensure_ascii=False, indent=2)
    
    def load_judgments(self, input_file):
        """
        加载相关性判断结果
        :param input_file: 输入文件路径
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            self.relevance_judgments = json.load(f)

if __name__ == '__main__':
    # 测试评估
    indexer = Indexer()
    indexer.load_index('data/index.json')
    vsm = VSM(indexer)
    evaluator = Evaluator(vsm)
    
    # 添加一些测试数据
    test_queries = [
        "国务院常务会议",
        "疫情防控",
        "经济发展"
    ]
    
    # 模拟相关性判断
    for query in test_queries:
        results = vsm.search(query)
        for result in results[:5]:  # 只判断前5个结果
            # 随机判断相关性（实际应用中应该由人工判断）
            evaluator.add_relevance_judgment(query, result['url'], np.random.choice([True, False]))
    
    # 计算评估指标
    for query in test_queries:
        precision = evaluator.calculate_precision_at_k(query)
        print(f"查询 '{query}' 的 P@10: {precision:.4f}")
    
    map_score = evaluator.calculate_map(test_queries)
    print(f"\nMAP: {map_score:.4f}") 