from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Database URL configuration for both development and production
database_url = os.getenv('DATABASE_URL', 'sqlite:///career_reflections.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)

# Configure Dify API
DIFY_API_KEY = os.getenv('DIFY_API_KEY')
DIFY_API_ENDPOINT = os.getenv('DIFY_API_ENDPOINT')

if not DIFY_API_KEY or not DIFY_API_ENDPOINT:
    raise ValueError("DIFY_API_KEY and DIFY_API_ENDPOINT must be set in .env file")

# Create tables if they don't exist
with app.app_context():
    db.create_all()

class Reflection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

def generate_career_question():
    try:
        # 過去の履歴を取得
        reflections = Reflection.query.order_by(Reflection.date.desc()).all()
        reflection_history = "\n".join([
            f"質問: {r.question}\n回答: {r.answer}"
            for r in reflections[:5]  # 直近5件の履歴を使用
        ])

        # 履歴の有無で異なるプロンプトを使用
        if reflection_history:
            prompt = f"""以下は、このユーザーの過去のキャリアに関する質問と回答の履歴です：

{reflection_history}

この履歴を踏まえて、ユーザーのキャリア開発により深い洞察を与えられる、新しい質問を1つ生成してください。
以下の点を考慮してください：
1. 過去の回答から見えてきたユーザーの興味・関心
2. まだ十分に掘り下げられていない観点
3. 前回の回答を更に深めるような質問
4. キャリア開発の次のステップを促す質問

質問は具体的で、内省を促すものにしてください。
回答は質問文のみを返してください。"""
        else:
            prompt = """キャリアに関する深い自己分析のための質問を1つ生成してください。
            以下のようなテーマに関する質問を考えてください：
            - スキルと能力の成長
            - 価値観とやりがい
            - 将来のキャリアビジョン
            - 仕事での課題と克服
            質問は具体的で、内省を促すものにしてください。
            回答は質問文のみを返してください。"""

        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": {},
            "query": prompt,
            "response_mode": "blocking",
            "conversation_id": "",
            "user": "user"
        }
        
        print("Sending request to Dify API...")
        response = requests.post(DIFY_API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        
        print("Response received from Dify API")
        result = response.json()
        return result.get('answer', 'エラー: 質問を生成できませんでした')
    except Exception as e:
        print(f"Error in generate_career_question: {str(e)}")
        raise

def generate_career_advice(reflections):
    try:
        reflection_text = "\n".join([f"質問: {r.question}\n回答: {r.answer}" for r in reflections])
        
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": {},
            "query": f"""以下の過去の自己分析の記録を基に、総合的なキャリアアドバイスを提供してください：

{reflection_text}

以下の観点から分析してアドバイスをしてください：
1. 強みと成長ポイント
2. キャリアにおける価値観の傾向
3. 今後の成長に向けた具体的なアクション""",
            "response_mode": "blocking",
            "conversation_id": "",
            "user": "user"
        }
        
        response = requests.post(DIFY_API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get('answer', 'エラー: アドバイスを生成できませんでした')
    except Exception as e:
        print(f"Error in generate_career_advice: {str(e)}")
        raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/question', methods=['GET'])
def get_question():
    try:
        question = generate_career_question()
        return jsonify({'status': 'success', 'question': question})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reflection', methods=['POST'])
def save_reflection():
    try:
        data = request.json
        reflection = Reflection(
            question=data['question'],
            answer=data['answer']
        )
        db.session.add(reflection)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reflections', methods=['GET'])
def get_reflections():
    try:
        reflections = Reflection.query.order_by(Reflection.date.desc()).all()
        return jsonify({
            'status': 'success',
            'reflections': [{
                'id': r.id,
                'date': r.date.strftime('%Y-%m-%d %H:%M'),
                'question': r.question,
                'answer': r.answer
            } for r in reflections]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/advice', methods=['GET'])
def get_advice():
    try:
        reflections = Reflection.query.order_by(Reflection.date.desc()).all()
        advice = generate_career_advice(reflections)
        return jsonify({'status': 'success', 'advice': advice})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
