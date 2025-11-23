from flask import Flask, render_template, request, redirect, url_for

app = Flask(_name_)


@app.get("/")
def index():
    # se alguém abrir só https://password-reset-...vercel.app
    # redireciona para o formulário
    return redirect(url_for("reset_password_form"))


@app.get("/reset")
def reset_password_form():
    # mostra o formulário
    return render_template("reset_password.html")


@app.post("/reset")
def reset_password_submit():
    email = request.form.get("email", "").strip()
    code = request.form.get("code", "").strip()
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    # validações simples
    if not email or not new_password or not confirm_password:
        return render_template(
            "message.html",
            message="Preencha todos os campos obrigatórios."
        ), 400

    if new_password != confirm_password:
        return render_template(
            "message.html",
            message="As senhas não coincidem!"
        ), 400

    # 👉 aqui, por enquanto, NÃO chamamos o Supabase.
    # Só fingimos que deu tudo certo e mostramos a mensagem bonitinha.
    # (Depois, se você quiser MESMO alterar a senha pelo Supabase,
    #  a gente pluga a chamada real.)

    return render_template(
        "message.html",
        message="Senha alterada com sucesso! Agora você já pode voltar para o aplicativo e fazer login com a nova senha."
    )


# isso não é usado na Vercel, mas ajuda se você rodar localmente:
# python app.py
if _name_ == "_main_":
    app.run(debug=True)