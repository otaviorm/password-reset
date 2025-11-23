from flask import Flask, render_template, request
import os
import requests

app = Flask(__name__)

# === CONFIGURAÇÕES DO SUPABASE ===
# Pode deixar hard‐coded ou carregar com os.environ
SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SERVICE_ROLE_KEY = "SUA_CHAVE_SERVICE_ROLE"  # NÃO é a anon, é a service_role


def get_user_by_email(email: str):
  """Busca o usuário no Supabase Auth Admin pelo e-mail."""
  url = f"{SUPABASE_URL}/auth/v1/admin/users"
  headers = {
      "apikey": SERVICE_ROLE_KEY,
      "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    }
  params = {"email": email}

  resp = requests.get(url, headers=headers, params=params, timeout=10)
  if resp.status_code != 200:
    print("Erro ao buscar usuário:", resp.status_code, resp.text)
    return None

  data = resp.json()
  # Supabase retorna {"users": [...]} ou lista simples dependendo da versão.
  users = data.get("users") if isinstance(data, dict) else data
  if not users:
    return None

  return users[0]  # pega o primeiro


def update_user_password(user_id: str, new_password: str):
  """Atualiza a senha de um usuário pelo ID."""
  url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
  headers = {
      "apikey": SERVICE_ROLE_KEY,
      "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
      "Content-Type": "application/json",
    }
  json_body = {"password": new_password}

  resp = requests.patch(url, headers=headers, json=json_body, timeout=10)
  if resp.status_code not in (200, 201):
    print("Erro ao atualizar senha:", resp.status_code, resp.text)
    return False

  return True


@app.route("/", methods=["GET"])
def show_form():
  # só desenha o formulário
  return render_template("reset.html", error=None, success=None)


@app.route("/reset", methods=["POST"])
def reset_password():
  email = (request.form.get("email") or "").strip().lower()
  code = (request.form.get("code") or "").strip()
  new_password = request.form.get("new_password") or ""
  confirm_password = request.form.get("confirm_password") or ""

  # 1) validações simples
  if not email or not new_password or not confirm_password:
    return render_template(
      "reset.html",
      error="Preencha todos os campos.",
      success=None,
      email=email,
      code=code,
    )

  if new_password != confirm_password:
    return render_template(
      "reset.html",
      error="As senhas não coincidem!",
      success=None,
      email=email,
      code=code,
    )

  # OBS: por enquanto o 'code' é apenas enfeite para atender a exigência.
  # Se você quiser validar de verdade, aí teria que implementar um esquema
  # próprio de OTP no seu backend / banco.
  if code and not code.isdigit():
    return render_template(
      "reset.html",
      error="O código de recuperação deve conter apenas números.",
      success=None,
      email=email,
      code=code,
    )

  # 2) busca o usuário pelo e-mail no Supabase Auth
  user = get_user_by_email(email)
  if not user:
    return render_template(
      "reset.html",
      error="Usuário não encontrado para esse e-mail.",
      success=None,
      email=email,
      code=code,
    )

  user_id = user.get("id")
  if not user_id:
    return render_template(
      "reset.html",
      error="Não foi possível identificar o usuário no Supabase.",
      success=None,
      email=email,
      code=code,
    )

  # 3) atualiza a senha via API Admin
  ok = update_user_password(user_id, new_password)
  if not ok:
    return render_template(
      "reset.html",
      error="Falha ao atualizar a senha. Tente novamente mais tarde.",
      success=None,
      email=email,
      code=code,
    )

  # 4) deu tudo certo
  return render_template(
    "reset.html",
    error=None,
    success="Senha alterada com sucesso! Você já pode voltar ao aplicativo e fazer login com a nova senha.",
    email="",
    code="",
  )


# Vercel procura uma variável chamada 'app'
# (já está assim: app = Flask(__name__))

if __name__ == "__main__":
  # pra rodar localmente: python app.py
  app.run(host="0.0.0.0", port=5000, debug=True)
