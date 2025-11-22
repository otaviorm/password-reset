from flask import Flask, request, render_template, redirect
from supabase import create_client, Client

app = Flask(__name__)

# 🔗 Coloque sua URL e chave ANON aqui:
SUPABASE_URL = "https://ljfuvqeeovcursooprzx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqZnV2cWVlb3ZjdXJzb29wcnp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1MDg0ODQsImV4cCI6MjA3NDA4NDQ4NH0.P_xmFyvkuHiBcqbfeT67CN6OzgMXZNjC-oF4Mw6l-zQ"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/", methods=["GET"])
def index():
    # só redireciona para a página de reset
    return redirect("/reset")


@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template("reset.html")

    email = request.form.get("email")
    code = request.form.get("code")  # código numérico de 8 dígitos
    new_password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    # validações simples
    if not email or not code or not new_password:
        return "Preencha todos os campos!"

    if new_password != confirm_password:
        return "As senhas não coincidem!"

    if len(code) != 8 or not code.isdigit():
        return "Código inválido! Deve ter 8 dígitos numéricos."

    # 🔥 SUPABASE: confirmar token de recuperação
    try:
        response = supabase.auth.verify_otp({
            "email": email,
            "token": code,
            "type": "recovery"
        })

        if response.get("session") is None:
            return "Código inválido ou expirado!"

        # trocar senha
        update_response = supabase.auth.update_user({"password": new_password})

        return "Senha alterada com sucesso! Agora você já pode voltar ao app."

    except Exception as e:
        return f"Erro ao redefinir a senha: {str(e)}"


# necessário para rodar localmente
if __name__ == "__main__":
    app.run(debug=True)
