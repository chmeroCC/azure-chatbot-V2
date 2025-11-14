# app.py - Version corrigée - Réponses naturelles pour tous les sujets
from flask import Flask, request, jsonify, render_template
import os
import openai
import logging
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration Azure OpenAI avec ANCIENNE syntaxe
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("AZURE_OPENAI_VERSION", "2024-02-01")

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Vérification des variables critiques
required_configs = {
    "AZURE_OPENAI_KEY": openai.api_key,
    "AZURE_OPENAI_ENDPOINT": openai.api_base,
    "AZURE_OPENAI_DEPLOYMENT": deployment_name
}

missing_configs = [key for key, value in required_configs.items() if not value]

if missing_configs:
    logger.error("Configuration manquante: %s", missing_configs)
    raise ValueError(f"Configuration Azure OpenAI manquante: {missing_configs}")

logger.info("Azure Chatbot V2 - Initialisation reussie")
logger.info("Endpoint: %s", openai.api_base)
logger.info("Deploiement: %s", deployment_name)
logger.info("Cle API: [SECURISEE]")

@app.route('/')
def home():
    """Page d'accueil du chatbot"""
    logger.info("Acces page d'accueil")
    return render_template('chat.html')

@app.route('/health')
def health_check():
    """Endpoint de sante pour les monitors"""
    return jsonify({
        "status": "healthy",
        "service": "azure-chatbot-v2",
        "version": "2.0.0"
    })

@app.route('/api/info')
def api_info():
    """Information sur l'API (sans secrets)"""
    return jsonify({
        "service": "AI Chatbot Assistant",
        "version": "2.1.0",
        "deployment": deployment_name,
        "status": "operational",
        "capabilities": "Réponses générales et expertise Yu-Gi-Oh!"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint principal pour le chat - Version corrigée"""
    try:
        # Validation de la requête
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "status": "error"
            }), 400
            
        user_input = request.json.get("message")
        
        if not user_input or not user_input.strip():
            return jsonify({
                "error": "Le message ne peut pas etre vide",
                "status": "error"
            }), 400
        
        # Nettoyage de l'input
        user_input = user_input.strip()
        logger.info("Question: %s", user_input)
        
        # Appel à Azure OpenAI avec instruction corrigée
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {
                    "role": "system", 
                    "content": """Tu es un assistant IA utile et polyvalent. Tu réponds à tous types de questions de manière naturelle et utile.

Tu as une expertise en Yu-Gi-Oh! que tu peux utiliser quand c'est pertinent, mais tu aides sur tous les sujets.

RÈGLES IMPORTANTES :
1. RÉPONDS TOUJOURS de manière utile, quelle que soit la question
2. NE DIS JAMAIS "ce n'est pas lié à Yu-Gi-Oh!" ou "je ne peux pas répondre"
3. Sois naturel et adapte ton style au sujet
4. Réponses concises : 1-2 phrases maximum
5. Pour Yu-Gi-Oh! : sois technique et passionné
6. Pour autres sujets : sois informatif et clair

Exemples de bonnes réponses :
- "Qu'est-ce que Linux?" → "Linux est un système d'exploitation open-source très populaire pour les serveurs et les développeurs."
- "Explique les règles de Yu-Gi-Oh!" → "Yu-Gi-Oh! est un jeu de cartes où chaque joueur commence avec 8000 points de vie. Le but est de réduire les points de l'adversaire à zéro."
- "Quel temps fait-il?" → "Je ne peux pas accéder aux données météo en temps réel, mais je te conseille de consulter une application météo!"
"""
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ],
            max_tokens=120,
            temperature=0.6,
            top_p=0.9
        )
        
        bot_response = response.choices[0].message.content.strip()
        logger.info("Reponse: %s", bot_response)
        
        return jsonify({
            "response": bot_response,
            "status": "success",
            "tokens_used": response.usage.total_tokens if response.usage else None
        })
        
    except Exception as e:
        logger.error("Erreur endpoint /api/chat: %s", str(e))
        return jsonify({
            "error": "Erreur interne du service",
            "status": "error"
        }), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning("Route non trouvee")
    return jsonify({
        "error": "Endpoint non trouve",
        "status": "error"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error("Erreur interne du serveur")
    return jsonify({
        "error": "Erreur interne du serveur",
        "status": "error"
    }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
    
    logger.info("Demarrage sur le port %s (debug: %s)", port, debug_mode)
    
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=port
    )