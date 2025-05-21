from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import hashlib
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor.indexer import Indexer
from processor.vsm import VSM
from processor.extractor import extract_info

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 初始化检索系统
indexer = Indexer()
indexer.load_index('data/index.json')
vsm = VSM(indexer)

@app.route('/api/search', methods=['POST'])
def search():
    """
    搜索接口
    请求体格式：
    {
        "query": "搜索关键词",
        "top_k": 10  // 可选，默认10
    }
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': '缺少查询参数'}), 400
    
    query = data['query']
    top_k = data.get('top_k', 10)
    
    try:
        results = vsm.search(query, top_k=top_k)
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """
    评估接口
    请求体格式：
    {
        "query": "搜索关键词",
        "doc_url": "文档URL",
        "is_relevant": true/false
    }
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ['query', 'doc_url', 'is_relevant']):
        return jsonify({'error': '缺少必要参数'}), 400
    
    try:
        from evaluator.evaluation import Evaluator
        evaluator = Evaluator(vsm)
        
        # 加载已有的判断结果
        if os.path.exists('data/judgments.json'):
            evaluator.load_judgments('data/judgments.json')
        
        # 添加新的判断
        evaluator.add_relevance_judgment(
            data['query'],
            data['doc_url'],
            data['is_relevant']
        )
        
        # 保存更新后的判断结果
        evaluator.save_judgments('data/judgments.json')
        
        return jsonify({
            'status': 'success',
            'message': '评估结果已保存'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    获取系统统计信息
    """
    try:
        return jsonify({
            'status': 'success',
            'stats': {
                'doc_count': indexer.doc_count,
                'term_count': len(indexer.inverted_index),
                'avg_doc_length': sum(indexer.doc_lengths.values()) / len(indexer.doc_lengths)
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/extract_info', methods=['POST'])
def extract_info_api():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': '缺少正文'}), 400
    info = extract_info(text)
    return jsonify({'status': 'success', 'info': info})

@app.route('/api/evaluate_extraction', methods=['POST'])
def evaluate_extraction():
    """
    评价信息抽取结果
    请求体格式：
    {
        "doc_url": "文档URL",
        "accuracy": 80,  # 准确率评分（0-100）
        "extracted_info": {
            "地点": [...],
            "人物": [...],
            "时间": [...],
            "事件名称": [...],
            "事件动作": [...]
        }
    }
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ['doc_url', 'accuracy', 'extracted_info']):
        return jsonify({'error': '缺少必要参数'}), 400
    
    try:
        # 确保评价数据目录存在
        os.makedirs('data/evaluations', exist_ok=True)
        
        # 构建评价数据
        evaluation = {
            'doc_url': data['doc_url'],
            'accuracy': data['accuracy'],
            'extracted_info': data['extracted_info'],
            'timestamp': datetime.now().isoformat()
        }
        
        # 生成唯一的评价ID
        evaluation_id = hashlib.md5(
            f"{data['doc_url']}_{datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        # 保存评价结果
        evaluation_file = f'data/evaluations/{evaluation_id}.json'
        with open(evaluation_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': '评价结果已保存',
            'evaluation_id': evaluation_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 