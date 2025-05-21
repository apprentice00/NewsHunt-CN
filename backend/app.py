from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor.indexer import Indexer
from processor.vsm import VSM

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
        import traceback
        traceback.print_exc()  # 打印详细堆栈到控制台，便于调试
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

@app.route('/api/eval_stats', methods=['POST'])
def eval_stats():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': '缺少查询参数'}), 400

    try:
        from evaluator.evaluation import Evaluator
        evaluator = Evaluator(vsm)
        if os.path.exists('data/judgments.json'):
            evaluator.load_judgments('data/judgments.json')
        precision = evaluator.calculate_precision_at_k(data['query'], k=10)
        return jsonify({
            'status': 'success',
            'precision_at_10': precision
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 