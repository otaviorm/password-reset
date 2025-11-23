from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# Variáveis do Supabase
SUPABASE_URL = os.environ.get("https://ljfuvqeeovcursooprzx.supabase.co")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqZnV2cWVlb3ZjdXJzb29wcnp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1MDg0ODQsImV4cCI6MjA3NDA4NDQ4NH0.P_xmFyvkuHiBcqbfeT67CN6OzgMXZNjC-oF4Mw6l-zQ")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ROTA PRINCIPAL → MOSTRA O FORM
@app.route("/", methods=["GET"])
def index():
    # Captura o token enviado no link do email (se existir)
    token = request.args.get("token_hash", "")
    email = request.args.get("email", "")

    return render_template("reset_password.html", token=token, email=email)


# ROTA PARA ALTERAR SENHA
@app.route("/change-password", methods=["POST"])
def change_password():
    data = request.json

    email = data.get("email")
    token = data.get("token")
    new_password = data.get("password")

    if not email or not token or not new_password:
        return jsonify({"error": "Dados incompletos"}), 400

    # Chamando a API do Supabase
    payload = {
        "email": email,
        "token_hash": token,
        "password": new_password,
        "type": "recovery",
    }

    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/recover",
        json=payload,
        headers=headers
    )

    if response.status_code >= 400:
        return jsonify({
            "error": "Falha ao redefinir senha",
            "details": response.text
        }), 400

    return jsonify({"message": "Senha redefinida com sucesso!"})


# Necessário para o Vercel
def handler(event, context):
    return app(event, context)
