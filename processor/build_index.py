import json
from indexer import Indexer

def main():
    # 读取分词后的新闻数据
    print("正在读取新闻数据...")
    with open('data/news_tokenized.json', 'r', encoding='utf-8') as f:
        processed_news = json.load(f)
    
    # 创建索引器实例
    print("正在构建索引...")
    indexer = Indexer()
    indexer.build_index(processed_news)
    
    # 保存索引
    print("正在保存索引...")
    indexer.save_index('data/index.json')
    print("索引构建完成！")

if __name__ == '__main__':
    main() 