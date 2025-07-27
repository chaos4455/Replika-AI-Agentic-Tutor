# -*- coding: utf-8 -*-
# NOME DO ARQUIVO: duolingo_on_demand_app_v7.py

import sys
import os
import logging
import re
import yaml
import sqlite3
import json
import random
from flask import Flask, request, jsonify, render_template_string
from waitress import serve

# --- Configuration Constants ---
APP_VERSION = "7.0-AI-Explanations"
CONFIG = {
    "API_KEY": 'SUA-CHAVE-API',
    "MODEL_NAME": "gemini-1.5-flash-latest",
    "API_TIMEOUT_SECONDS": 180, # Aumentado para dar mais tempo à IA para gerar explicações
    "WEB_PORT": 8999,
    "LOG_FILENAME": "duolingo_app.log",
    "DATABASE_FILENAME": "quiz-database.db"
}

# --- PROMPT ### MUDANÇA ### (Adicionada a chave 'explanation' e instrução) ---
GEMINI_PROMPT_LINES = [
    "Você é um Designer Instrucional Sênior. Sua tarefa é criar um quiz interativo sobre um tópico específico.",
    "Gere um conjunto de 20 a 30 perguntas e respostas sobre o tópico '{topic}'.",
    "A saída DEVE ser um bloco de código YAML único e bem formatado, nada mais.",
    "A estrutura YAML deve ser uma lista, onde cada item tem as chaves: 'question' (string), 'options' (lista de 4 strings), 'answer' (string), e 'explanation' (string).",
    "A chave 'explanation' DEVE conter uma explicação técnica, didática e concisa do porquê a resposta correta está certa. A explicação deve ser útil e agregar conhecimento.",
    "EXEMPLO DE ESTRUTURA YAML:",
    "```yaml",
    "- question: \"Qual planeta é conhecido como o 'Planeta Vermelho'?\"",
    "  options:",
    "    - \"Vênus\"",
    "    - \"Marte\"",
    "    - \"Júpiter\"",
    "    - \"Saturno\"",
    "  answer: \"Marte\"",
    "  explanation: \"Marte possui uma alta concentração de óxido de ferro (ferrugem) em sua superfície e atmosfera, o que lhe confere a característica aparência avermelhada.\"",
    "```",
    "Agora, gere o quiz para o seguinte tópico: '{topic}'"
]

# --- TEMPLATES (HTML, CSS) - Sem alterações necessárias ---

HTML_LINES = [
    '<!DOCTYPE html><html lang="pt-br"><head>',
    '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '<title>Estudo On-Demand v7</title>',
    '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">',
    '<style>{css_styles}</style></head><body><div id="app-wrapper">',
    '<!-- Tela de Início -->',
    '<div id="start-screen" class="screen active"><div class="logo">🎓</div><h1>Estudo On-Demand</h1>',
    '<div class="settings-container"><div class="toggle-switch">',
    '  <input type="checkbox" id="infinite-lives-toggle" class="toggle-switch-checkbox">',
    '  <label class="toggle-switch-label" for="infinite-lives-toggle">',
    '    <span class="toggle-switch-inner"></span><span class="toggle-switch-switch"></span>',
    '  </label><span class="toggle-label-text">Vidas Infinitas</span>',
    '</div></div>',
    '<div class="start-section"><p>Crie uma nova aula interativa do zero.</p>',
    '<input type="text" id="topic-input" placeholder="Digite um tópico aqui...">',
    '<button id="generate-btn">Gerar com IA</button></div>',
    '<div class="separator">OU</div>',
    '<div class="start-section">',
    '<p>Escolha uma aula que você já criou.</p>',
    '<div id="existing-quizzes-list-container"><div id="existing-quizzes-list">Carregando quizzes...</div></div>',
    '</div></div>',
    '<!-- Outras Telas (Loading, Quiz, Final) -->',
    '<div id="loading-screen" class="screen">',
    '<div class="spinner"></div><h2>Criando sua aula...</h2><p>Aguarde, a IA está trabalhando.</p></div>',
    '<div id="quiz-screen" class="screen">',
    '<div id="quiz-header"><div id="lives-container"></div><div id="question-counter"></div></div>',
    '<div id="progress-bar-container"><div id="progress-bar"></div></div>',
    '<div id="question-container"><h2 id="question-text"></h2></div><div id="options-container"></div></div>',
    '<div id="final-screen" class="screen"><div id="final-icon"></div><h2 id="final-title"></h2>',
    '<p id="final-message"></p><div class="score-card"><h3>Sua Pontuação</h3><div id="final-score-value"></div></div>',
    '<button id="restart-btn">Voltar ao Início</button></div></div>',
    '<!-- Painel de Feedback -->',
    '<div id="feedback-container"><div id="feedback-content"><div id="feedback-icon"></div>',
    '<div id="feedback-text"><h3 id="feedback-title"></h3><p id="feedback-details"></p></div></div>',
    '<button id="next-btn">Continuar</button></div>',
    '<script>{js_code}</script></body></html>'
]

CSS_LINES = [
    ':root { --blue: #007aff; --blue-dark: #005bb5; --green: #34c759; --green-dark: #28a449; --red: #ff3b30; --red-dark: #d92c23; --text-primary: #1d1d1f; --text-secondary: #6e6e73; --bg-light-1: #f9fafb; --bg-light-2: #f0f2f5; --bg-white: #ffffff; --border-light: #e5e5e5; --font-family: "Poppins", sans-serif; }',
    'body { font-family: var(--font-family); background-image: radial-gradient(circle at top left, var(--bg-light-1), var(--bg-light-2)); color: var(--text-primary); display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; margin: 0; padding: 2rem; box-sizing: border-box; }',
    '#app-wrapper { width: 100%; max-width: 600px; background: var(--bg-white); border-radius: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); padding: 2rem; box-sizing: border-box; }',
    '.screen { display: none; flex-direction: column; align-items: center; text-align: center; } .screen.active { display: flex; }',
    'h1 { font-size: 2.5rem; margin-bottom: 8px; color: var(--text-primary); } p { color: var(--text-secondary); line-height: 1.6; } .logo { font-size: 4rem; margin-bottom: 1rem; }',
    '#start-screen .start-section { background: transparent; padding: 0; border-radius: 0; width: 100%; box-shadow: none; }',
    '#start-screen .start-section p { font-weight: 600; margin-bottom: 1rem; }',
    '#start-screen .separator { font-weight: 700; color: var(--border-light); margin: 1.5rem 0; }',
    '#topic-input { width: 100%; padding: 16px; font-size: 1.1rem; border: 2px solid var(--border-light); border-radius: 12px; margin-top: 0; box-sizing: border-box; text-align: center; transition: all 0.2s; }',
    '#topic-input:focus { border-color: var(--blue); outline: none; box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2); }',
    'button { width: 100%; padding: 16px; font-size: 1.1rem; font-weight: 700; color: var(--bg-white); background-color: var(--blue); border: none; border-radius: 12px; cursor: pointer; margin-top: 1rem; transition: background-color 0.2s; text-transform: uppercase; }',
    'button:hover { background-color: var(--blue-dark); }',
    '#existing-quizzes-list-container { max-height: 200px; overflow-y: auto; padding-right: 10px; }',
    '#existing-quizzes-list .existing-quiz-btn { width: 100%; background-color: var(--bg-light-2); color: var(--text-primary); text-transform: none; font-weight: 600; }',
    '#existing-quizzes-list .existing-quiz-btn:hover { background-color: #e8eaed; }',
    '.settings-container { display: flex; justify-content: center; align-items: center; margin-bottom: 1.5rem; }',
    '.toggle-switch { position: relative; display: inline-block; width: 50px; height: 28px; margin-right: 10px; } .toggle-switch-checkbox { opacity: 0; width: 0; height: 0; }',
    '.toggle-label-text { font-weight: 600; color: var(--text-secondary); }',
    '.toggle-switch-label { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }',
    '.toggle-switch-label:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }',
    '.toggle-switch-checkbox:checked + .toggle-switch-label { background-color: var(--green); }',
    '.toggle-switch-checkbox:checked + .toggle-switch-label:before { transform: translateX(22px); }',
    '#quiz-header { width: 100%; display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }',
    '#lives-container { display: flex; gap: 8px; font-size: 1.5rem; align-items: center; } #question-counter { font-weight: 600; color: var(--text-secondary); }',
    '#progress-bar-container { width: 100%; height: 12px; background-color: var(--border-light); border-radius: 6px; overflow: hidden; margin-bottom: 2rem; }',
    '#progress-bar { width: 0%; height: 100%; background-color: var(--green); transition: width 0.3s ease-in-out; }',
    '#question-container h2 { font-size: 1.8rem; font-weight: 600; min-height: 100px; line-height: 1.4; }',
    '#options-container { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; width: 100%; }',
    '.option-btn { padding: 1.2rem; background-color: var(--bg-white); border: 2px solid var(--border-light); border-radius: 12px; font-size: 1.1rem; font-weight: 600; text-align: center; cursor: pointer; transition: all 0.2s; color: var(--text-primary); }',
    '.option-btn.neutral { background-color: var(--bg-light-2); border-color: var(--bg-light-2); color: var(--text-secondary); }',
    '.option-btn:hover:not(:disabled) { border-color: var(--blue); background-color: #f0f8ff; }',
    '.option-btn.correct { border-color: var(--green); background-color: #e5f9e9; color: var(--green-dark); font-weight: 700; }',
    '.option-btn.wrong { border-color: var(--red); background-color: #ffebee; color: var(--red-dark); font-weight: 700; }',
    '#feedback-container { position: fixed; bottom: 0; left: 0; right: 0; padding: 1.5rem 2rem; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-top: 1px solid rgba(0, 0, 0, 0.1); transform: translateY(100%); transition: transform 0.3s ease-in-out; z-index: 10; display: flex; align-items: center; }',
    '#feedback-container.show { transform: translateY(0); }',
    '#feedback-content { display: flex; align-items: center; gap: 1rem; flex-grow: 1; } #feedback-icon { font-size: 2rem; } #feedback-text h3 { margin: 0; font-size: 1.2rem; } #feedback-text p { margin: 4px 0 0; }',
    '#feedback-container.correct #feedback-text h3 { color: var(--green-dark); } #feedback-container.wrong #feedback-text h3 { color: var(--red-dark); }',
    '#feedback-container button { width: auto; min-width: 150px; flex-shrink: 0; }',
    '#feedback-container.correct button { background-color: var(--green); } #feedback-container.correct button:hover { background-color: var(--green-dark); }',
    '#feedback-container.wrong button { background-color: var(--red); } #feedback-container.wrong button:hover { background-color: var(--red-dark); }',
    '#final-screen #final-icon { font-size: 5rem; margin-bottom: 1rem; } .score-card { background: var(--bg-light-2); padding: 1.5rem; border-radius: 16px; margin: 1.5rem 0; width: 50%; }',
    '.score-card h3 { margin: 0 0 0.5rem 0; color: var(--text-secondary); font-size: 1rem; } #final-score-value { font-size: 3rem; font-weight: 700; color: var(--blue); }',
    '.spinner { border: 5px solid #f3f3f3; border-top: 5px solid var(--blue); border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; } @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }',
    '@media (max-width: 600px) { #app-wrapper { padding: 1rem; margin-top: 0; border-radius: 0; } #options-container { grid-template-columns: 1fr; } }'
]

# --- JAVASCRIPT ### MUDANÇA ### (Funções 'checkAnswer' e 'showFeedback' foram atualizadas) ---
JS_LINES = [
    'document.addEventListener("DOMContentLoaded", () => {',
    '    const state = { quizData: [], currentQuestionIndex: 0, score: 0, correctAnswer: "", lives: 5, maxLives: 5, infiniteLives: false };',
    '    const ui = {',
    '        screens: { start: document.getElementById("start-screen"), loading: document.getElementById("loading-screen"), quiz: document.getElementById("quiz-screen"), final: document.getElementById("final-screen") },',
    '        buttons: { generate: document.getElementById("generate-btn"), next: document.getElementById("next-btn"), restart: document.getElementById("restart-btn") },',
    '        topicInput: document.getElementById("topic-input"), optionsContainer: document.getElementById("options-container"), questionText: document.getElementById("question-text"),',
    '        livesContainer: document.getElementById("lives-container"), questionCounter: document.getElementById("question-counter"), progressBar: document.getElementById("progress-bar"),',
    '        existingQuizzesList: document.getElementById("existing-quizzes-list"),',
    '        infiniteLivesToggle: document.getElementById("infinite-lives-toggle"),',
    '        feedback: { container: document.getElementById("feedback-container"), icon: document.getElementById("feedback-icon"), title: document.getElementById("feedback-title"), details: document.getElementById("feedback-details") },',
    '        final: { icon: document.getElementById("final-icon"), title: document.getElementById("final-title"), message: document.getElementById("final-message"), scoreValue: document.getElementById("final-score-value") }',
    '    };',
    '    function shuffleArray(array) {',
    '        for (let i = array.length - 1; i > 0; i--) {',
    '            const j = Math.floor(Math.random() * (i + 1));',
    '            [array[i], array[j]] = [array[j], array[i]];',
    '        }',
    '    }',
    '    function showScreen(screenName) { Object.values(ui.screens).forEach(s => s.classList.remove("active")); ui.screens[screenName].classList.add("active"); }',
    '    async function generateQuiz() {',
    '        const topic = ui.topicInput.value.trim(); if (!topic) { alert("Por favor, insira um tópico."); return; }',
    '        showScreen("loading");',
    '        try {',
    '            const response = await fetch("/generate-quiz", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ topic: topic }) });',
    '            if (!response.ok) { const err = await response.json(); throw new Error(err.error); }',
    '            const data = await response.json();',
    '            if (!data.quiz || data.quiz.length < 5) { throw new Error("A IA não retornou um quiz válido."); }',
    '            state.quizData = data.quiz; startQuiz();',
    '        } catch (error) { alert("Erro: " + error.message); showScreen("start"); }',
    '    }',
    '    async function loadExistingQuizzes() {',
    '        try {',
    '            const response = await fetch("/get-quizzes"); const quizzes = await response.json();',
    '            ui.existingQuizzesList.innerHTML = "";',
    '            if (quizzes.length === 0) { ui.existingQuizzesList.innerHTML = "<p>Nenhuma aula salva ainda.</p>"; return; }',
    '            quizzes.forEach(quiz => {',
    '                const button = document.createElement("button"); button.innerText = quiz.topic;',
    '                button.className = "existing-quiz-btn"; button.dataset.id = quiz.id;',
    '                button.addEventListener("click", () => startExistingQuiz(quiz.id));',
    '                ui.existingQuizzesList.appendChild(button);',
    '            });',
    '        } catch (error) { ui.existingQuizzesList.innerHTML = "<p>Erro ao carregar aulas.</p>"; }',
    '    }',
    '    async function startExistingQuiz(quizId) {',
    '        showScreen("loading");',
    '        try {',
    '            const response = await fetch("/get-quiz/" + quizId);',
    '            if (!response.ok) throw new Error("Não foi possível carregar a aula.");',
    '            const data = await response.json(); state.quizData = data.quiz; startQuiz();',
    '        } catch (error) { alert("Erro: " + error.message); showScreen("start"); }',
    '    }',
    '    function startQuiz() {',
    '        state.currentQuestionIndex = 0; state.score = 0;',
    '        state.infiniteLives = ui.infiniteLivesToggle.checked;',
    '        state.lives = state.infiniteLives ? 999 : state.maxLives;',
    '        shuffleArray(state.quizData);',
    '        updateLivesDisplay(); showScreen("quiz"); displayQuestion();',
    '    }',
    '    function displayQuestion() {',
    '        hideFeedback(); const question = state.quizData[state.currentQuestionIndex];',
    '        state.correctAnswer = question.answer; ui.questionText.innerText = question.question; ui.optionsContainer.innerHTML = "";',
    '        shuffleArray(question.options);',
    '        question.options.forEach(optionText => {',
    '            const button = document.createElement("button"); button.className = "option-btn"; button.innerText = optionText;',
    '            button.addEventListener("click", () => checkAnswer(optionText, button)); ui.optionsContainer.appendChild(button);',
    '        });',
    '        updateProgressBar(); updateQuestionCounter();',
    '    }',
    '    function checkAnswer(selectedOption, clickedButton) {',
    '        const question = state.quizData[state.currentQuestionIndex];',
    '        const isCorrect = selectedOption === question.answer;',
    '        ui.optionsContainer.querySelectorAll(".option-btn").forEach(btn => {',
    '            btn.disabled = true;',
    '            if (btn.innerText === question.answer) { btn.classList.add("correct"); }',
    '            else { btn.classList.add("neutral"); }',
    '        });',
    '        if (isCorrect) {',
    '            state.score += 10;',
    '            showFeedback(true, question.explanation || "Ótimo trabalho!");',
    '        } else {',
    '            if (!state.infiniteLives) { state.lives--; updateLivesDisplay(); }',
    '            clickedButton.classList.add("wrong");',
    '            showFeedback(false, "A resposta certa era: " + question.answer);',
    '        }',
    '    }',
    '    function showFeedback(isCorrect, detailsText) {',
    '        ui.feedback.container.className = isCorrect ? "correct" : "wrong";',
    '        ui.feedback.icon.innerText = isCorrect ? "✅" : "❌";',
    '        ui.feedback.title.innerText = isCorrect ? "Resposta Certa!" : "Resposta Incorreta";',
    '        ui.feedback.details.innerText = detailsText;',
    '        ui.feedback.container.classList.add("show");',
    '    }',
    '    function hideFeedback() { ui.feedback.container.classList.remove("show"); }',
    '    function nextStep() {',
    '        if (state.lives <= 0 && !state.infiniteLives) { showFinalScreen(false); return; }',
    '        state.currentQuestionIndex++; if (state.currentQuestionIndex < state.quizData.length) { displayQuestion(); } else { showFinalScreen(true); }',
    '    }',
    '    function showFinalScreen(isWinner) {',
    '        showScreen("final"); hideFeedback();',
    '        if (isWinner) { ui.final.icon.innerText = "🏆"; ui.final.title.innerText = "Parabéns!"; ui.final.message.innerText = "Excelente trabalho! Você dominou o tópico."; }',
    '        else { ui.final.icon.innerText = "💔"; ui.final.title.innerText = "Fim de Jogo"; ui.final.message.innerText = "Não desanime! Tente novamente para melhorar."; }',
    '        ui.final.scoreValue.innerText = state.score;',
    '    }',
    '    function updateLivesDisplay() {',
    '        ui.livesContainer.innerHTML = "";',
    '        if (state.infiniteLives) {',
    '            ui.livesContainer.innerHTML = \'❤️ <span style="font-size: 1.5rem; font-weight: bold;">∞</span>\';',
    '            return;',
    '        }',
    '        for(let i = 0; i < state.maxLives; i++) { ui.livesContainer.innerHTML += (i < state.lives) ? "❤️" : "💀"; }',
    '    }',
    '    function updateQuestionCounter() { ui.questionCounter.innerText = "Questão " + (state.currentQuestionIndex + 1) + " / " + state.quizData.length; }',
    '    function updateProgressBar() { const progress = ((state.currentQuestionIndex) / state.quizData.length) * 100; ui.progressBar.style.width = progress + "%"; }',
    '    function restartApp() { showScreen("start"); loadExistingQuizzes(); }',
    '    ui.buttons.generate.addEventListener("click", generateQuiz);',
    '    ui.buttons.next.addEventListener("click", nextStep);',
    '    ui.buttons.restart.addEventListener("click", restartApp);',
    '    ui.topicInput.addEventListener("keyup", e => e.key === "Enter" && generateQuiz());',
    '    loadExistingQuizzes();',
    '});'
]

# --- Bloco de Código Python Principal (Backend) ---
# ### MUDANÇA ###: Adicionada validação para o campo 'explanation'.

def init_db():
    try:
        conn = sqlite3.connect(CONFIG["DATABASE_FILENAME"])
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL UNIQUE,
                quiz_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
        conn.commit()
        conn.close()
        print("Banco de dados '{0}' pronto.".format(CONFIG["DATABASE_FILENAME"]))
    except Exception as e:
        print("Erro ao inicializar o banco de dados: {0}".format(e))

GOOGLE_AI_AVAILABLE = False
try:
    import google.generativeai as genai
    genai.configure(api_key=CONFIG["API_KEY"])
    GOOGLE_AI_AVAILABLE = True
    print("Biblioteca google.generativeai carregada.")
except Exception as e:
    print("AVISO: IA desabilitada. Erro: {0}".format(e))

logging.basicConfig(filename=CONFIG["LOG_FILENAME"], level=logging.INFO, format='%(asctime)s - %(message)s')
app = Flask(__name__)

def send_prompt_to_gemini(prompt_content):
    if not GOOGLE_AI_AVAILABLE: return "Erro: Funcionalidade de IA indisponível."
    try:
        model = genai.GenerativeModel(CONFIG["MODEL_NAME"])
        response = model.generate_content(prompt_content, request_options={'timeout': CONFIG["API_TIMEOUT_SECONDS"]})
        return response.text
    except Exception as e: return "Erro: {0}".format(e)

def extract_yaml_from_response(raw_text):
    match = re.search(r"```yaml\s*([\s\S]+?)\s*```", raw_text, re.DOTALL)
    return match.group(1).strip() if match else raw_text.strip()

@app.route('/')
def index():
    html_content = '\n'.join(HTML_LINES).format(css_styles='\n'.join(CSS_LINES), js_code='\n'.join(JS_LINES))
    return render_template_string(html_content)

@app.route('/get-quizzes', methods=['GET'])
def get_quizzes():
    try:
        conn = sqlite3.connect(CONFIG["DATABASE_FILENAME"])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, topic FROM quizzes ORDER BY created_at DESC")
        quizzes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(quizzes)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/get-quiz/<int:quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    try:
        conn = sqlite3.connect(CONFIG["DATABASE_FILENAME"])
        cursor = conn.cursor()
        cursor.execute("SELECT quiz_data FROM quizzes WHERE id = ?", (quiz_id,))
        row = cursor.fetchone()
        conn.close()
        if row: return jsonify({"quiz": json.loads(row[0])})
        return jsonify({"error": "Quiz não encontrado"}), 404
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.get_json(); topic = data.get('topic')
        if not topic: return jsonify({'error': 'Nenhum tópico fornecido'}), 400

        prompt_content = '\n'.join(GEMINI_PROMPT_LINES).format(topic=topic)
        ai_response = send_prompt_to_gemini(prompt_content)
        if ai_response.startswith("Erro:"): raise ValueError(ai_response)

        yaml_content = extract_yaml_from_response(ai_response)
        quiz_data = yaml.safe_load(yaml_content)
        
        # ### MUDANÇA ###: Validação aprimorada para incluir 'explanation'
        if not isinstance(quiz_data, list) or not all('question' in item and 'explanation' in item for item in quiz_data):
            raise yaml.YAMLError("O formato YAML retornado pela IA é inválido ou não contém o campo 'explanation'.")

        random.shuffle(quiz_data)

        conn = sqlite3.connect(CONFIG["DATABASE_FILENAME"])
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO quizzes (topic, quiz_data) VALUES (?, ?)", (topic, json.dumps(quiz_data)))
        conn.commit()
        conn.close()
        logging.info("Quiz para '{0}' gerado com explicações e salvo no DB.".format(topic))
        return jsonify({'quiz': quiz_data})
    except Exception as e:
        logging.error("Erro em /generate-quiz: {0}".format(e), exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    init_db()
    print("="*60)
    print("  Estudo On-Demand v{0}".format(APP_VERSION))
    print("  >> Explicações Técnicas Geradas por IA Implementadas <<")
    print("  Servidor iniciado. Acesse em seu navegador:")
    print("  http://127.0.0.1:{0}".format(CONFIG["WEB_PORT"]))
    print("="*60)
    serve(app, host="0.0.0.0", port=CONFIG["WEB_PORT"])
