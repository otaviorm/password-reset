import os
import textwrap
from flask import Flask, request, render_template_string
import requests
from dotenv import load_dotenv

# Carrega variáveis do .env local (boa para rodar em dev)
load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ljfuvqeeovcursooprzx.supabase.co")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxqZnV2cWVlb3ZjdXJzb29wcnp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1MDg0ODQsImV4cCI6MjA3NDA4NDQ4NH0.P_xmFyvkuHiBcqbfeT67CN6OzgMXZNjC-oF4Mw6l-zQ")

# ---------- HTML DO FORMULÁRIO (msm layout) ----------
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>Redefinir Senha</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #f2f4f8, #e5ebf5);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 16px;
    }

    .card {
      width: 100%;
      max-width: 480px;
      background: #ffffff;
      border-radius: 18px;
      box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
      padding: 20px 20px 24px;
    }

    @media (min-width: 420px) {
      .card {
        padding: 28px 28px 30px;
      }
    }

    .title {
      font-size: 26px;
      font-weight: 800;
      margin-bottom: 8px;
      color: #0f172a;
      text-align: center;
    }

    .subtitle {
      font-size: 14px;
      color: #4b5563;
      margin-bottom: 20px;
      text-align: center;
      line-height: 1.4;
    }

    .field {
      margin-bottom: 14px;
    }

    label {
      display: block;
      font-size: 14px;
      font-weight: 600;
      color: #111827;
      margin-bottom: 4px;
    }

    input {
      width: 100%;
      padding: 11px 12px;
      border-radius: 10px;
      border: 1px solid #d1d5db;
      font-size: 15px;
      outline: none;
      transition: box-shadow 0.15s ease, border-color 0.15s ease;
    }

    input:focus {
      border-color: #2563eb;
      box-shadow: 0 0 0 1px #2563eb33;
    }

    .hint {
      font-size: 11px;
      color: #6b7280;
      margin-top: 2px;
    }

    .button {
      width: 100%;
      margin-top: 14px;
      padding: 12px 14px;
      border-radius: 999px;
      border: none;
      background: #2563eb;
      color: #ffffff;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 12px 30px rgba(37, 99, 235, 0.55);
      transition: transform 0.1s ease, box-shadow 0.1s ease, background 0.1s ease;
    }

    .button:active {
      transform: translateY(1px);
      box-shadow: 0 6px 18px rgba(37, 99, 235, 0.6);
      background: #1d4ed8;
    }

    .msg {
      margin-bottom: 10px;
      padding: 8px 10px;
      border-radius: 8px;
      font-size: 13px;
      line-height: 1.3;
    }

    .msg-error {
      background: #fee2e2;
      color: #b91c1c;
      border: 1px solid #fecaca;
    }

    .msg-success {
      background: #dcfce7;
      color: #166534;
      border: 1px solid #bbf7d0;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1 class="title">Redefinir Senha</h1>
    <p class="subtitle">
      Digite seu e-mail, o código de recuperação (quando houver) e sua nova senha.
    </p>

    {% if message %}
      <div class="msg {{ 'msg-error' if error else 'msg-success' }}">
        {{ message }}
      </div>
    {% endif %}

    <form method="post" action="/">
      <div class="field">
        <label for="email">E-mail</label>
        <input
          id="email"
          name="email"
          type="email"
          placeholder="seuemail@exemplo.com"
          required
          value="{{ form_email or '' }}"
        />
      </div>

      <div class="field">
        <label for="code">Código de Recuperação</label>
        <input
          id="code"
          name="code"
          type="text"
          inputmode="numeric"
          placeholder="(opcional) código recebido por e-mail"
        />
        <div class="hint">
          Este campo é apenas informativo no momento, o backend usa o e-mail para localizar o usuário.
        </div>
      </div>

      <div class="field">
        <label for="password">Nova Senha</label>
        <input
          id="password"
          name="password"
          type="password"
          placeholder="Nova senha"
          required
        />
      </div>

      <div class="field">
        <label for="confirm_password">Confirme a Nova Senha</label>
        <input
          id="confirm_password"
          name="confirm_password"
          type="password"
          placeholder="Repita a nova senha"
          required
        />
      </div>

      <button class="button" type="submit">Alterar Senha</button>
    </form>
  </div>
</body>
</html>
"""

# ---------- Funções auxiliares para falar com o Supabase Admin API ----------

def _supabase_headers():
  return {
      "apikey": SERVICE_ROLE_KEY,
      "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
      "Content-Type": "application/json",
  }

def find_user_by_email(email: str):
  """Busca usuário pelo e-mail usando Admin API."""
  url = f"{SUPABASE_URL}/auth/v1/admin/users"
  resp = requests.get(url, headers=_supabase_headers(), params={"email": email})
  if resp.status_code != 200:
    app.logger.error("Erro ao buscar usuário: %s %s", resp.status_code, resp.text)
    return None
  data = resp.json()
  # Resposta pode ser lista ou dict, dependendo da versão; tratamos os dois.
  if isinstance(data, list):
    return data[0] if data else None
  return data

def update_user_password(user_id: str, new_password: str):
  """Atualiza a senha de um usuário pelo id."""
  url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
  resp = requests.put(
      url,
      headers=_supabase_headers(),
      json={"password": new_password},
  )
  return resp


# --------------------- ROTAS FLASK ---------------------

@app.route("/", methods=["GET", "POST"])
def index():
  message = None
  error = False
  form_email = ""

  if request.method == "POST":
    email = (request.form.get("email") or "").strip().lower()
    code = (request.form.get("code") or "").strip()  # ainda não usamos, só exibimos
    password = request.form.get("password") or ""
    confirm = request.form.get("confirm_password") or ""

    form_email = email  # para manter no input se der erro

    # 1) validação básica das senhas
    if password != confirm:
      message = "As senhas não coincidem!"
      error = True
    elif len(password) < 6:
      message = "A senha deve ter pelo menos 6 caracteres."
      error = True
    elif not email:
      message = "Informe um e-mail válido."
      error = True
    else:
      try:
        # 2) busca usuário pelo e-mail
        user = find_user_by_email(email)
        if not user or "id" not in user:
          message = "Usuário não encontrado para este e-mail."
          error = True
        else:
          user_id = user["id"]
          # 3) atualiza a senha via Admin API
          resp = update_user_password(user_id, password)
          if resp.status_code not in (200, 201):
            app.logger.error("Erro ao atualizar senha: %s %s", resp.status_code, resp.text)
            message = "Não foi possível alterar a senha. Tente novamente mais tarde."
            error = True
          else:
            message = "Senha alterada com sucesso! Você já pode voltar ao app e fazer login."
            error = False
      except Exception as e:
        app.logger.exception("Erro inesperado ao redefinir senha")
        message = "Ocorreu um erro interno ao tentar alterar a senha."
        error = True

  return render_template_string(
      PAGE_TEMPLATE,
      message=message,
      error=error,
      form_email=form_email,
  )

# Vercel olha para a variável 'app'
if __name__ == "__main__":
  app.run(debug=True)
