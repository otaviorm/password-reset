from flask import Flask, render_template, request
import requests
import urllib.parse

# =====================================================================
#  CONFIGURAÇÕES DO SUPABASE
#  (pode deixar hard-coded aqui mesmo pro trabalho da faculdade)
# =====================================================================
SUPABASE_URL = "https://ljfuvqeeovcursooprzx.supabase.co"  # <-- sua URL
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqZnV2cWVlb3ZjdXJzb29wcnp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1MDg0ODQsImV4cCI6MjA3NDA4NDQ4NH0.P_xmFyvkuHiBcqbfeT67CN6OzgMXZNjC-oF4Mw6l-zQ"    # <-- troque

# Cabeçalhos para chamar a API de admin do Supabase
ADMIN_HEADERS = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
}

app = Flask(_name_)


@app.route("/", methods=["GET", "POST"])
def reset_password():
    """
    Rota principal:
    - GET: mostra o formulário de redefinição de senha.
    - POST: recebe email + código + nova senha, troca a senha no Supabase
            e mostra mensagem de sucesso/erro.
    """
    error = None
    success = None

    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        code = (request.form.get("code") or "").strip()
        new_password = request.form.get("new_password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        # 1) validações simples
        if not email or not new_password or not confirm_password:
            error = "Preencha todos os campos obrigatórios."
        elif new_password != confirm_password:
            error = "As senhas não coincidem!"
        elif len(new_password) < 6:
            error = "A nova senha deve ter pelo menos 6 caracteres."
        elif not code.isdigit() or len(code) != 8:
            # Não vamos usar o código de verdade, mas validamos o formato
            error = "O código de recuperação deve ter 8 dígitos numéricos."
        else:
            try:
                # 2) Buscar usuário pelo e-mail na API de admin
                user_id = find_user_id_by_email(email)
                if not user_id:
                    error = "Não foi encontrado um usuário com esse e-mail."
                else:
                    # 3) Atualizar senha desse usuário
                    ok, msg = update_user_password(user_id, new_password)
                    if ok:
                        success = "Senha alterada com sucesso! Você já pode voltar ao app e entrar com a nova senha."
                    else:
                        error = msg or "Não foi possível alterar a senha. Tente novamente mais tarde."
            except Exception as e:
                print("Erro inesperado:", e)
                error = "Ocorreu um erro interno ao tentar alterar a senha."

    return render_template("reset_password.html", error=error, success=success)


# =====================================================================
# Funções auxiliares para chamar a API de admin do Supabase
# =====================================================================

def find_user_id_by_email(email: str):
    """
    Usa a API de admin do Supabase para buscar um usuário pelo e-mail.
    GET /auth/v1/admin/users?email=...
    Retorna o id do usuário ou None.
    """
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    params = {"email": email}

    resp = requests.get(url, headers=ADMIN_HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        print("Erro ao buscar usuário:", resp.status_code, resp.text)
        return None

    data = resp.json()
    # A API pode retornar lista ou um objeto, dependendo da versão.
    if isinstance(data, list) and data:
        return data[0].get("id")
    if isinstance(data, dict) and data.get("id"):
        return data.get("id")

    return None


def update_user_password(user_id: str, new_password: str):
    """
    Usa a API de admin pra atualizar a senha de um usuário específico.
    PATCH /auth/v1/admin/users/{id}
    """
    url = f"{SUPABASE_URL}/auth/v1/admin/users/{urllib.parse.quote(user_id)}"
    payload = {"password": new_password}

    resp = requests.patch(url, headers=ADMIN_HEADERS, json=payload, timeout=15)
    if resp.status_code in (200, 201):
        return True, None

    print("Erro ao atualizar senha:", resp.status_code, resp.text)
    try:
        data = resp.json()
        msg = data.get("message") or data.get("error_description")
    except Exception:
        msg = None

    return False, msg


# =====================================================================
# Ponto de entrada para o Vercel/@vercel/python
# =====================================================================
# O Vercel espera uma variável "app" no módulo indicado.
# Já definimos app = Flask(_name_) lá em cima.
# =====================================================================

if _name_ == "_main_":
    # Para testar localmente:
    #   python app.py
    # Depois abrir http://localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)