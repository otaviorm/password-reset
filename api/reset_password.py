from flask import Flask, render_template, request
import os
import requests

app = Flask(_name_, template_folder="../templates")

# >>>> COLOCA A SUA URL E CHAVE AQUI <<<<
SUPABASE_URL = "https://ljfuvqeeovcursooprzx.supabase.co"
SUPABASE_SERVICE_ROLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqZnV2cWVlb3ZjdXJzb29wcnp4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODUwODQ4NCwiZXhwIjoyMDc0MDg0NDg0fQ.NRvJSeGSk5pWiLQUdbcoWW2-zjaLeNxHuwNkOvpjMws"  # pode usar anon por enquanto se quiser

# --------- ROTAS ---------

@app.route("/", methods=["GET"])
def home():
    # Só pra ver se o app está vivo
    return render_template("message.html", message="Página de reset carregada com sucesso!")

@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        # Mostrar o formulário
        return render_template("reset_password.html")

    # POST – processar o formulário
    email = request.form.get("email", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    # validações simples
    if not email or not new_password or not confirm_password:
        return render_template("message.html", message="Preencha todos os campos.")

    if new_password != confirm_password:
        return render_template("message.html", message="As senhas não coincidem!")

    # aqui fazemos a chamada à API do Supabase para atualizar a senha
    try:
        # Endpoint de admin do Supabase Auth para atualizar usuário
        url = f"{SUPABASE_URL}/auth/v1/admin/users"

        # 1) pegar o usuário pelo e-mail
        params = {"email": email}
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE}",
        }

        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return render_template("message.html", message="Usuário não encontrado.")

        user_id = data[0]["id"]

        # 2) atualizar a senha do usuário
        update_url = f"{url}/{user_id}"
        payload = {"password": new_password}

        update_resp = requests.put(update_url, headers=headers, json=payload, timeout=10)
        update_resp.raise_for_status()

        return render_template("message.html", message="Senha alterada com sucesso!")

    except requests.HTTPError as e:
        return render_template("message.html", message=f"Erro HTTP ao falar com o Supabase: {e}")
    except Exception as e:
        return render_template("message.html", message=f"Erro interno: {e}")


# Vercel procura por uma variável chamada "app"
# então não precisa de nada além disso.