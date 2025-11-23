import os
import requests
from flask import Flask, render_template, request

# === CONFIGURAÇÕES DO SUPABASE ===
# Para seu projeto, pode deixar hardcoded (é um trabalho da faculdade).
# Se quiser, depois trocamos para variáveis de ambiente.
SUPABASE_URL = "https://ljfuvqeeovcursooprzx.supabase.co"  # <-- a sua URL
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqZnV2cWVlb3ZjdXJzb29wcnp4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODUwODQ4NCwiZXhwIjoyMDc0MDg0NDg0fQ.NRvJSeGSk5pWiLQUdbcoWW2-zjaLeNxHuwNkOvpjMws"        # <-- chave service_role

# IMPORTANTE:
# - precisa ser a SERVICE_ROLE_KEY (do Supabase) pra poder trocar senha
# - NÃO é a anon key

app = Flask(
    _name_,
    template_folder="templates",
    static_folder="static"
)


@app.route("/", methods=["GET"])
def index():
    """
    Mostra o formulário de redefinição de senha.
    Se der erro ao renderizar o template, o Flask iria dar 500,
    então é bom garantir que o arquivo reset_password.html existe
    dentro de templates/.
    """
    return render_template("reset_password.html")


@app.route("/reset", methods=["POST"])
def reset_password():
    """
    Processa o formulário:
      1. valida campos
      2. verifica o código (OTP) no Supabase
      3. altera a senha do usuário com a Admin API
    """
    try:
        email = request.form.get("email", "").strip().lower()
        code = request.form.get("code", "").strip()
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("password_confirm", "")

        # --- Validações básicas ---
        if not email or not code or not new_password or not confirm_password:
            return render_template("message.html", message="Preencha todos os campos."), 400

        if new_password != confirm_password:
            return render_template("message.html", message="As senhas não coincidem!"), 400

        # --- 1. Verificar o código (OTP) no Supabase ---
        verify_url = f"{SUPABASE_URL}/auth/v1/verify"
        verify_headers = {
            "apikey": SERVICE_ROLE_KEY,
            "Content-Type": "application/json"
        }
        verify_payload = {
            "email": email,
            "token": code,
            "type": "recovery"
        }

        verify_resp = requests.post(
            verify_url,
            json=verify_payload,
            headers=verify_headers,
            timeout=10
        )

        print("Verify status:", verify_resp.status_code)
        print("Verify body:", verify_resp.text)

        if verify_resp.status_code != 200:
            return render_template(
                "message.html",
                message="Código inválido ou expirado. Tente gerar um novo link."
            ), 400

        data = verify_resp.json()
        user = data.get("user")
        if not user:
            return render_template(
                "message.html",
                message="Usuário não encontrado após verificação."
            ), 400

        user_id = user.get("id")
        if not user_id:
            return render_template(
                "message.html",
                message="Não foi possível identificar o usuário."
            ), 400

        # --- 2. Alterar a senha usando a Admin API ---
        update_url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
        update_headers = {
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }
        update_payload = {
            "password": new_password
        }

        update_resp = requests.put(
            update_url,
            json=update_payload,
            headers=update_headers,
            timeout=10
        )

        print("Update status:", update_resp.status_code)
        print("Update body:", update_resp.text)

        if update_resp.status_code not in (200, 201):
            return render_template(
                "message.html",
                message="Erro ao atualizar a senha. Tente novamente ou fale com o responsável."
            ), 500

        return render_template(
            "message.html",
            message="Senha alterada com sucesso! Agora você já pode voltar ao app e entrar com a nova senha."
        )

    except Exception as e:
        # Isso aqui evita que o usuário veja um 500 seco.
        # E as prints aparecem nos logs do Vercel pra gente debugar.
        print("ERRO NO /reset:", repr(e))
        return render_template(
            "message.html",
            message="Ocorreu um erro inesperado ao tentar redefinir a senha."
        ), 500


# Vercel detecta o objeto 'app' automaticamente.
# Não precisa de nada além disso.
if _name_ == "_main_":
    # Apenas para rodar localmente, se você quiser:
    app.run(debug=True)