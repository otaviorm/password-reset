from flask import Flask, render_template, request
import requests

# ============================
# CONFIGURAÇÕES DO SUPABASE
# ============================

# Coloca aqui a URL do seu projeto Supabase (sem /auth no final)
SUPABASE_URL = "https://ljfuvqeeovcursooprzx.supabase.co"  # <- troque se for diferente
# Coloca aqui a CHAVE PÚBLICA (anon) do seu Supabase
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqZnV2cWVlb3ZjdXJzb29wcnp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1MDg0ODQsImV4cCI6MjA3NDA4NDQ4NH0.P_xmFyvkuHiBcqbfeT67CN6OzgMXZNjC-oF4Mw6l-zQ"

app = Flask(
    _name_,
    template_folder="templates",
    static_folder="static",
)


@app.route("/", methods=["GET"])
def form():
    """
    Mostra o formulário de redefinição de senha.
    Se vierem email e code na URL (?email=...&code=...),
    a gente já pré-preenche os campos.
    """
    email = request.args.get("email", "")
    code = request.args.get("code", "")
    message = request.args.get("message", "")

    return render_template(
        "reset_password.html",
        email=email,
        code=code,
        message=message,
        error=False,
    )


@app.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Recebe o formulário, valida os dados e fala com o Supabase:
      1) verifyOtp (type=recovery) usando email + código
      2) se der certo, atualiza a senha do usuário
    """

    email = request.form.get("email", "").strip()
    code = request.form.get("code", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    # ============================
    # 1. Validações básicas
    # ============================
    if not email or not code or not password or not confirm:
        return render_template(
            "reset_password.html",
            email=email,
            code=code,
            message="Preencha todos os campos.",
            error=True,
        )

    if password != confirm:
        return render_template(
            "reset_password.html",
            email=email,
            code=code,
            message="As senhas não coincidem.",
            error=True,
        )

    if len(password) < 6:
        return render_template(
            "reset_password.html",
            email=email,
            code=code,
            message="A nova senha deve ter pelo menos 6 caracteres.",
            error=True,
        )

    # ============================
    # 2. Chama verifyOtp no Supabase
    # ============================

    verify_url = f"{SUPABASE_URL}/auth/v1/verify"
    verify_payload = {
        "type": "recovery",
        "email": email,
        "token": code,
    }
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }

    try:
        verify_resp = requests.post(verify_url, json=verify_payload, headers=headers)
    except Exception as e:
        # Erro de rede, timeout, etc
        return render_template(
            "reset_password.html",
            email=email,
            code=code,
            message=f"Erro ao falar com o Supabase (verifyOtp): {e}",
            error=True,
        )

    if not verify_resp.ok:
        # Tentamos puxar mensagem amigável da resposta
        try:
            data = verify_resp.json()
            supabase_msg = data.get("msg") or data.get("message") or str(data)
        except Exception:
            supabase_msg = verify_resp.text

        return render_template(
            "reset_password.html",
            email=email,
            code=code,
            message=f"Código inválido ou expirado. Detalhes: {supabase_msg}",
            error=True,
        )

    # A resposta normalmente contém session/access_token
    try:
        data = verify_resp.json()
        # Alguns clients retornam {"access_token": "..."}
        # outros retornam {"session": {"access_token": "..."}}
        access_token = data.get("access_token")
        if not access_token and isinstance(data.get("session"), dict):
            access_token = data["session"].get("access_token")
    except Exception:
        access_token = None

    if not access_token:
        return render_template(
            "reset_password.html",
            email=email,
            code=code,
            message=(
                "Não foi possível obter o token de sessão após verificar o código. "
                "Verifique a configuração do Supabase."
            ),
            error=True,
        )

    # ============================
    # 3. Atualiza a senha do usuário
    # ============================

    update_url = f"{SUPABASE_URL}/auth/v1/user"
    update_payload = {"password": password}
    update_headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        up_resp = requests.put(update_url, json=update_payload, headers=update_headers)
    except Exception as e:
        return render_template(
            "reset_password.html",
            email=email,
            code=code,
            message=f"Erro ao atualizar a senha no Supabase: {e}",
            error=True,
        )

    if not up_resp.ok:
        try:
            data = up_resp.json()
            supabase_msg = data.get("msg") or data.get("message") or str(data)
        except Exception:
            supabase_msg = up_resp.text

        return render_template(
            "reset_password.html",
            email=email,
            code=code,
            message=f"Falha ao atualizar a senha. Detalhes: {supabase_msg}",
            error=True,
        )

    # Sucesso!
    return render_template(
        "reset_password.html",
        email="",
        code="",
        message="Senha alterada com sucesso! Você já pode voltar ao app e fazer login.",
        error=False,
    )


# Para rodar localmente (opcional, pra testar no navegador)
if _name_ == "_main_":
    app.run(debug=True)