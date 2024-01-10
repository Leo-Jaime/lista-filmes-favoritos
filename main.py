from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length ,NumberRange
import requests
import pprint
CHAVE_API = "minha_chave_aqui"
FILME_DB_PESQUISAR = "https://api.themoviedb.org/3/search/movie"
FILME_DB_DETALHES = "https://api.themoviedb.org/3/movie/"
FILME_DB_IMAGENS = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///meus-filmes.db"
db = SQLAlchemy()
db.init_app(app)


class Filme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(250), unique=True)
    ano = db.Column(db.Integer)
    descricao = db.Column(db.String(250), nullable=True)
    avaliacao = db.Column(db.Float(250), nullable=True)
    classificacao = db.Column(db.Integer, nullable=True)
    analise = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()


########Adicionar filme
class AdicionarFilme(FlaskForm):
    titulo = StringField(label="Titulo do filme")
    adicionar = SubmitField(label="Adicionar filme")



#########modelando o formulario de editar o filme
class AvaliarFilmeForm(FlaskForm):
    avaliacao = FloatField(label="Você pode avaliar 10 ou por exemplo 7.3", validators=[DataRequired()])
    analise = StringField(label="Me conte oque você achou do filme", validators=[DataRequired()])
    enviar = SubmitField(label="Enviar")



####Aqui comeca as rotas
@app.route("/")
def home():
    with app.app_context():
        buscar_filmes = db.session.execute(db.select(Filme).order_by(Filme.titulo))
        todos_filmes = buscar_filmes.scalars().all()
    return render_template("index.html", filmes=todos_filmes)

@app.route("/procurar", methods=["GET", "POST"])
def procurar_filme():
    filme_id = request.args.get("id")
    filme_api_url = f"{FILME_DB_DETALHES}/{filme_id}"
    parametros = {
        "api_key": "3700279c3a18be03e2d40318c5e35550",

        "language": "pt-BR"
    }
    resposta = requests.get(url=filme_api_url, params=parametros)
    dados = resposta.json()
    novo_filme = Filme(
        titulo=dados['title'],
        ano=dados['release_date'][:4],
        descricao=dados['overview'],
        avaliacao=dados['vote_average'],
        img_url=f"{FILME_DB_IMAGENS}/{dados['poster_path']}"
    )
    db.session.add(novo_filme)
    db.session.commit()
    return redirect(url_for("edit", id=novo_filme.id))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AdicionarFilme()
    if form.validate_on_submit():
        titulo_filme = form.titulo.data
        parametros = {
            "api_key":"3700279c3a18be03e2d40318c5e35550",
            "query": titulo_filme,
            "language": "pt-BR",
            "page": "1"
        }

        reposta = requests.get(FILME_DB_PESQUISAR, params=parametros)
        lista_filmes = reposta.json()["results"]

        return render_template("select.html", filmes=lista_filmes)
    return render_template("add.html", form=form)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = AvaliarFilmeForm()
    filme_id = request.args.get('id')
    filme_selecionado = db.get_or_404(Filme, filme_id)
    if form.validate():
        filme_selecionado.avaliacao = float(form.avaliacao.data)
        filme_selecionado.analise = str(form.analise.data)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", form=form, filme=filme_selecionado)


@app.route("/delete", methods=["GET"])
def delete():
    filme_id = request.args.get('id')
    filme_selecionado = db.get_or_404(Filme, filme_id)
    db.session.delete(filme_selecionado)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
