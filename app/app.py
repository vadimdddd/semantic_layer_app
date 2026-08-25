from flask import Flask, request, jsonify, Response
import requests
import json
import os
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Загружаем конфигурацию из переменных окружения
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://ollama:11434/api/generate')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:0.5b')
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT', '')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# Метрики для Prometheus
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
LLM_REQUEST_COUNT = Counter('llm_requests_total', 'Total LLM requests', ['model', 'status'])
LLM_REQUEST_DURATION = Histogram('llm_request_duration_seconds', 'LLM request duration', ['model'])

@app.route('/ask', methods=['POST'])
@REQUEST_DURATION.labels(method='POST', endpoint='/ask').time()
def ask():
    """Основной эндпоинт - получает вопрос и возвращает ответ от LLM"""
    start_time = time.time()
    data = request.get_json()
    user_question = data.get('question', '')
    
    if not user_question:
        REQUEST_COUNT.labels(method='POST', endpoint='/ask', status='400').inc()
        return jsonify({"error": "Вопрос не может быть пустым"}), 400
    
    logger.info(f"Получен вопрос: {user_question[:50]}...")
    
    # Формируем промпт
    if SYSTEM_PROMPT:
        prompt = f"{SYSTEM_PROMPT}\n\nВопрос пользователя: {user_question}\nОтвет:"
    else:
        prompt = f"Ответь на вопрос: {user_question}"
    
    # Отправляем запрос к Ollama
    try:
        with LLM_REQUEST_DURATION.labels(model=OLLAMA_MODEL).time():
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 256
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            llm_response = response.json().get('response', 'Нет ответа от модели')
            LLM_REQUEST_COUNT.labels(model=OLLAMA_MODEL, status='success').inc()
        
        # Форматируем ответ
        result = {
            "answer": llm_response.strip(),
            "model_used": OLLAMA_MODEL,
            "source": "Семантический слой (on-premise, CPU)",
            "version": APP_VERSION,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "mode": "self-hosted",
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
        }
        REQUEST_COUNT.labels(method='POST', endpoint='/ask', status='200').inc()
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при обращении к LLM: {str(e)}")
        LLM_REQUEST_COUNT.labels(model=OLLAMA_MODEL, status='error').inc()
        REQUEST_COUNT.labels(method='POST', endpoint='/ask', status='500').inc()
        return jsonify({
            "error": f"Ошибка при обращении к LLM: {str(e)}",
            "model_used": OLLAMA_MODEL
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    try:
        requests.get('http://ollama:11434', timeout=2)
        ollama_status = "available"
    except:
        ollama_status = "unavailable"
    
    return jsonify({
        "status": "healthy" if ollama_status == "available" else "degraded",
        "ollama": ollama_status,
        "model": OLLAMA_MODEL,
        "version": APP_VERSION
    })

@app.route('/config', methods=['GET'])
def config():
    """Показывает текущую конфигурацию"""
    return jsonify({
        "model": OLLAMA_MODEL,
        "system_prompt": SYSTEM_PROMPT[:100] + "..." if len(SYSTEM_PROMPT) > 100 else SYSTEM_PROMPT,
        "ollama_url": OLLAMA_URL,
        "version": APP_VERSION
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    """Эндпоинт для Prometheus"""
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)from flask import Flask, request, jsonify, Response
import requests
import json
import os
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Загружаем конфигурацию из переменных окружения
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://ollama:11434/api/generate')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:0.5b')
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT', '')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# Метрики для Prometheus
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
LLM_REQUEST_COUNT = Counter('llm_requests_total', 'Total LLM requests', ['model', 'status'])
LLM_REQUEST_DURATION = Histogram('llm_request_duration_seconds', 'LLM request duration', ['model'])

@app.route('/ask', methods=['POST'])
@REQUEST_DURATION.labels(method='POST', endpoint='/ask').time()
def ask():
    """Основной эндпоинт - получает вопрос и возвращает ответ от LLM"""
    start_time = time.time()
    data = request.get_json()
    user_question = data.get('question', '')
    
    if not user_question:
        REQUEST_COUNT.labels(method='POST', endpoint='/ask', status='400').inc()
        return jsonify({"error": "Вопрос не может быть пустым"}), 400
    
    logger.info(f"Получен вопрос: {user_question[:50]}...")
    
    # Формируем промпт
    if SYSTEM_PROMPT:
        prompt = f"{SYSTEM_PROMPT}\n\nВопрос пользователя: {user_question}\nОтвет:"
    else:
        prompt = f"Ответь на вопрос: {user_question}"
    
    # Отправляем запрос к Ollama
    try:
        with LLM_REQUEST_DURATION.labels(model=OLLAMA_MODEL).time():
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 256
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            llm_response = response.json().get('response', 'Нет ответа от модели')
            LLM_REQUEST_COUNT.labels(model=OLLAMA_MODEL, status='success').inc()
        
        # Форматируем ответ
        result = {
            "answer": llm_response.strip(),
            "model_used": OLLAMA_MODEL,
            "source": "Семантический слой (on-premise, CPU)",
            "version": APP_VERSION,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "mode": "self-hosted",
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
        }
        REQUEST_COUNT.labels(method='POST', endpoint='/ask', status='200').inc()
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при обращении к LLM: {str(e)}")
        LLM_REQUEST_COUNT.labels(model=OLLAMA_MODEL, status='error').inc()
        REQUEST_COUNT.labels(method='POST', endpoint='/ask', status='500').inc()
        return jsonify({
            "error": f"Ошибка при обращении к LLM: {str(e)}",
            "model_used": OLLAMA_MODEL
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    try:
        requests.get('http://ollama:11434', timeout=2)
        ollama_status = "available"
    except:
        ollama_status = "unavailable"
    
    return jsonify({
        "status": "healthy" if ollama_status == "available" else "degraded",
        "ollama": ollama_status,
        "model": OLLAMA_MODEL,
        "version": APP_VERSION
    })

@app.route('/config', methods=['GET'])
def config():
    """Показывает текущую конфигурацию"""
    return jsonify({
        "model": OLLAMA_MODEL,
        "system_prompt": SYSTEM_PROMPT[:100] + "..." if len(SYSTEM_PROMPT) > 100 else SYSTEM_PROMPT,
        "ollama_url": OLLAMA_URL,
        "version": APP_VERSION
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    """Эндпоинт для Prometheus"""
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)# New feature
