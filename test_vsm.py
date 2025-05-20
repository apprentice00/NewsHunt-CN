import sys
import os
from processor.indexer import Indexer
from processor.vsm import VSM
from datetime import datetime

def test_search(query, top_k=5):
    """
    测试单个查询的检索效果
    :param query: 查询文本
    :param top_k: 返回结果数量
    """
    print(f"\n测试查询: '{query}'")
    print("-" * 50)
    
    results = vsm.search(query, top_k=top_k)
    
    print(f"找到 {len(results)} 个结果:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   相关度分数: {result['score']:.4f}")
        print(f"   链接: {result['url']}")
        print(f"   日期: {result['date']}")

def test_multiple_queries():
    """
    测试多个查询的检索效果
    """
    test_queries = [
        "人工智能",
        "疫情防控",
        "经济发展",
        "科技创新",
        "教育改革"
    ]
    
    print("开始多查询测试...")
    print("=" * 50)
    
    for query in test_queries:
        test_search(query)
        print("\n" + "=" * 50)

def analyze_results(query, results):
    """
    分析检索结果
    :param query: 查询文本
    :param results: 检索结果列表
    """
    print(f"\n分析查询 '{query}' 的结果:")
    print("-" * 50)
    
    # 计算平均相关度分数
    avg_score = sum(r['score'] for r in results) / len(results) if results else 0
    print(f"平均相关度分数: {avg_score:.4f}")
    
    # 分析时间分布
    dates = [datetime.strptime(r['date'], "%Y-%m-%d") for r in results]
    oldest = min(dates)
    newest = max(dates)
    print(f"结果时间范围: {oldest.strftime('%Y-%m-%d')} 到 {newest.strftime('%Y-%m-%d')}")
    
    # 分析标题长度分布
    title_lengths = [len(r['title']) for r in results]
    avg_title_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0
    print(f"平均标题长度: {avg_title_length:.1f} 字符")

if __name__ == '__main__':
    # 加载索引
    indexer = Indexer()
    indexer.load_index('data/index.json')
    
    # 创建检索器
    vsm = VSM(indexer)
    
    # 运行测试
    print("开始向量空间检索模型测试...")
    print("=" * 50)
    
    # 测试单个查询
    test_search("人工智能", top_k=5)
    
    # 分析结果
    results = vsm.search("人工智能", top_k=5)
    analyze_results("人工智能", results)
    
    # 测试多个查询
    test_multiple_queries() 