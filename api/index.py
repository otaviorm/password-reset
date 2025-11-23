from flask import Flask, render_template, request

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

@app.route("/", methods=["GET", "POST"])
def reset_password():
    message = None
    message_type = "info"

    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        otp = (request.form.get("otp") or "").strip()
        password = (request.form.get("password") or "").strip()
        confirm = (request.form.get("confirm_password") or "").strip()

        # Validações simples
        if not email or not password or not confirm:
            message = "Preencha todos os campos obrigatórios."
            message_type = "error"
        elif password != confirm:
            message = "As senhas não coincidem!"
            message_type = "error"
        else:
            # Aqui depois você pluga a chamada real pro Supabase
            # (por enquanto vamos só simular sucesso)
            message = "Senha alterada com sucesso! Agora você já pode voltar ao app."
            message_type = "success"

    return render_template(
        "reset_password.html",
        message=message,
        message_type=message_type
    )

# Vercel procura a variável 'app'
