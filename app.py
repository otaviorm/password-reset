from flask import Flask, render_template, request, redirect, url_for
import os

# O Vercel procura por um objeto chamado "app" aqui
app = Flask(__name__, static_folder="static", template_folder="templates")


# Rota principal: mostra o formulário de redefinição
@app.route("/", methods=["GET"])
def index():
    return render_template("reset_password.html")


# Rota que recebe o POST do formulário
@app.route("/reset_password", methods=["POST"])
def reset_password():
    email = request.form.get("email", "").strip()
    code = request.form.get("code", "").strip()
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    # 1. validações básicas
    if not email or not code or not new_password or not confirm_password:
        return render_template(
            "message.html",
            title="Erro",
            message="Preencha todos os campos."
        ), 400

    if new_password != confirm_password:
        return render_template(
            "message.html",
            title="Erro",
            message="As senhas não coincidem."
        ), 400

    # 2. (FUTURO) Aqui você faria a chamada para a API do Supabase
    # usando o e-mail + código + nova senha.
    #
    # Por enquanto, vamos apenas simular que deu certo,
    # pra tela funcionar bonitinho no Vercel:

    print(f"[DEBUG] Pedido de reset: email={email}, code={code}")  # aparece nos logs do Vercel

    return render_template(
        "message.html",
        title="Sucesso",
        message="Senha alterada com sucesso! Agora você já pode voltar ao app e fazer login com a nova senha."
    ), 200


# Apenas para rodar localmente se você quiser testar com python app.py
if __name__ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)