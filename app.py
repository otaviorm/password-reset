from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    success = None

    if request.method == "POST":
        # pega os campos vindos do formulário
        email = (request.form.get("email") or "").strip()
        # por enquanto o código é ignorado, mas mantemos o campo na tela
        recovery_code = (request.form.get("recovery_code") or "").strip()

        new_password = (request.form.get("new_password") or "").strip()
        confirm_password = (request.form.get("confirm_password") or "").strip()

        # 1. validação básica
        if not email or not new_password or not confirm_password:
            error = "Preencha todos os campos obrigatórios."
            return render_template("index.html", error=error, success=None, email=email)

        # 2. confere se as senhas são iguais
        if new_password != confirm_password:
            error = "As senhas não coincidem!"
            return render_template("index.html", error=error, success=None, email=email)

        # 3. AQUI entraria a chamada real ao Supabase para trocar a senha
        #    (no nosso protótipo simplificado vamos só simular sucesso)
        # -----------------------------------------------------------------
        # Exemplo (quando você quiser ligar de verdade ao Supabase):
        # from supabase import create_client
        # SUPABASE_URL = "https://...supabase.co"
        # SUPABASE_ANON_KEY = "chave..."
        # supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        # resp = supabase.auth.admin.update_user_by_email(email, {"password": new_password})
        # if "error" em resp:
        #     error = "Não foi possível alterar a senha. Tente novamente mais tarde."
        # else:
        #     success = "Senha alterada com sucesso!"
        # -----------------------------------------------------------------

        success = "Senha alterada com sucesso! Agora você já pode voltar para o app e fazer login com a nova senha."
        return render_template("index.html", error=None, success=success, email=email)

    # GET: mostra o formulário vazio
    return render_template("index.html", error=error, success=success, email="")
