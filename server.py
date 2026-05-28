from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 1. ضع رابط قاعدة بيانات Firebase الخاصة بك هنا (تأكد من إضافة /chat_history.json في آخره)
# مثال: https://your-project-id.firebaseio.com/chat_history.json
FIREBASE_URL = "https://domplex-ai-default-rtdb.asia-southeast1.firebasedatabase.app/chat_history.json"

# 2. مفتاح OpenRouter الخاص بك
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"reply": "الرسالة فارغة!"}), 400

    # [Firebase]: حفظ رسالة المستخدم بخطوة خفيفة وبدون مكتبات ضخمة
    try:
        requests.post(FIREBASE_URL, json={'sender': 'user', 'message': user_message})
    except Exception as e:
        print(f"تنبيه: تعذر الحفظ المؤقت في Firebase: {e}")

    # إعداد طلب الذكاء الاصطناعي
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openrouter/free", 
        "messages": [
            {
                "role": "system",
                "content": "أنت العقل المدبر لشركة Bood Tech. مهمتك صناعة الألعاب والمواقع."
            },
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # [Firebase]: حفظ رد الذكاء الاصطناعي
            requests.post(FIREBASE_URL, json={'sender': 'ai', 'message': ai_response})
            
            return jsonify({"reply": ai_response})
        else:
            return jsonify({"reply": f"خطأ من OpenRouter: {response.text}"}), 500
    except Exception as e:
        return jsonify({"reply": f"حدث خطأ في الاتصال: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 السيرفر الخفيف يعمل الآن ومربوط بـ Firebase مباشرة!")
    app.run(host='127.0.0.1', port=5000, debug=True)
