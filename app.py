from flask import Flask, render_template, request
import os
import requests

# ==========================
# CONFIGURAÇÃO DO SUPABASE
# ==========================
SUPABASE_URL = "https://ljfuvqeeovcursooprzx.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqZnV2cWVlb3ZjdXJzb29wcnp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1MDg0ODQsImV4cCI6MjA3NDA4NDQ4NH0.P_xmFyvkuHiBcqbfeT67CN6OzgMXZNjC-oF4Mw6l-zQ"

# Endpoints da API de autenticação
SUPABASE_VERIFY_OTP_URL = f"{SUPABASE_URL}/auth/v1/verify"
SUPABASE_USER_URL = f"{SUPABASE_URL}/auth/v1/user"

# App Flask que o Vercel vai usar
app = Flask(__name__, static_folder="static", template_folder="templates")


# ==========================
# ROTAS
# ==========================

# Rota principal: mostra o formulário
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
        return (
            render_template(
                "message.html",
                title="Erro",
                message="Preencha todos os campos.",
            ),
            400,
        )

    if new_password != confirm_password:
        return (
            render_template(
                "message.html",
                title="Erro",
                message="As senhas não coincidem.",
            ),
            400,
        )

    # 2. Verificar o código (OTP) com o Supabase
    try:
        verify_payload = {
            "type": "recovery",  # fluxo de recuperação de senha
            "email": email,
            "token": code,
        }
        verify_headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
        }

        verify_resp = requests.post(
            SUPABASE_VERIFY_OTP_URL,
            json=verify_payload,
            headers=verify_headers,
            timeout=10,
        )
    except Exception as e:
        print("[DEBUG] Erro ao chamar /verify:", e)
        return (
            render_template(
                "message.html",
                title="Erro",
                message="Não foi possível conectar ao servidor de autenticação. Tente novamente em alguns instantes.",
            ),
            500,
        )

    if verify_resp.status_code != 200:
        print("[DEBUG] /verify status:", verify_resp.status_code, verify_resp.text)
        # mensagem amigável
        msg = "Código inválido ou expirado. Solicite um novo e-mail de recuperação."
        try:
            data = verify_resp.json()
            if "msg" in data:
                msg = data["msg"]
            elif "error_description" in data:
                msg = data["error_description"]
        except Exception:
            pass

        return (
            render_template(
                "message.html",
                title="Erro",
                message=msg,
            ),
            400,
        )

    verify_data = verify_resp.json()
    access_token = verify_data.get("access_token")

    if not access_token:
        print("[DEBUG] /verify sem access_token:", verify_data)
        return (
            render_template(
                "message.html",
                title="Erro",
                message="Resposta inesperada do servidor de autenticação. Tente novamente.",
            ),
            500,
        )

    # 3. Atualizar a senha do usuário usando o access_token retornado
    try:
        update_headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        update_payload = {
            "password": new_password,
        }

        update_resp = requests.put(
            SUPABASE_USER_URL,
            json=update_payload,
            headers=update_headers,
            timeout=10,
        )
    except Exception as e:
        print("[DEBUG] Erro ao chamar /user:", e)
        return (
            render_template(
                "message.html",
                title="Erro",
                message="Não foi possível atualizar a senha. Tente novamente.",
            ),
            500,
        )

    if update_resp.status_code != 200:
        print("[DEBUG] /user status:", update_resp.status_code, update_resp.text)
        return (
            render_template(
                "message.html",
                title="Erro",
                message="Não foi possível atualizar a senha. Verifique o código e tente novamente.",
            ),
            500,
        )

    # 4. Sucesso 🎉
    return (
        render_template(
            "message.html",
            title="Sucesso",
            message="Senha alterada com sucesso! Agora você já pode voltar ao app e fazer login com a nova senha.",
        ),
        200,
    )


# Para rodar localmente (não usado no Vercel)
if __name__ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)