from flask import Flask, request, redirect, url_for, render_template, flash
from sqlalchemy import create_engine, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship
from flask_login import UserMixin, login_manager, LoginManager, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

login_manager = LoginManager()
app = Flask(__name__)
login_manager.__init__(app)
app.secret_key = 'Esconda-me'

engine =create_engine('sqlite:///banco.db')

sessao = Session(bind=engine)

class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = 'tb_usuario'

    usu_id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usu_nome:Mapped[str] = mapped_column(String(100))
    usu_email:Mapped[str] = mapped_column(String(100))
    usu_senha:Mapped[str] = mapped_column(String(130))

    produtos = relationship('Produto', back_populates='usuario')

class Produto(Base):
    __tablename__ = 'tb_produto'

    pro_id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pro_nome:Mapped[str] = mapped_column(String(100))
    pro_preco:Mapped[float] = mapped_column()
    pro_descricao:Mapped[str] = mapped_column()
    pro_usu_id:Mapped[int] = mapped_column(ForeignKey('tb_usuario.usu_id'))

    usuario = relationship('Usuario', back_populates='produtos')


    def get_id(self):
        return str(self.id)
Base.metadata.create_all(bind=engine)


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(Usuario).get(int(user_id))
    session.close()
    return user


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        with Session(engine) as sessao:
            exist_usuario = sessao.query(Usuario).filter_by(usu_email=email).first()
            print(exist_usuario)
            if not exist_usuario:
                senha_crip = generate_password_hash(senha)
                usuario_novo = Usuario(usu_nome=nome, usu_email=email, usu_senha=senha_crip)
                sessao.add(usuario_novo)
                sessao.commit()
                flash('Usuário cadastrado!', category='sucesso')
                return redirect(url_for('index')) # return temporário
            flash('Já existe usuário cadastrado com esses dados!', category='erro')
    return render_template('cadastro_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        with Session(engine) as sessao:
            exist_usuario = sessao.query(Usuario).filter_by(usu_email=email).first()
            print(exist_usuario)
            if exist_usuario and check_password_hash(exist_usuario.usu_senha, senha):
                login_user(exist_usuario)
                flash('Usuário logado com sucesso!', category='sucesso')
                return redirect(url_for('index')) # return temporário
            flash('Usuário não encontrado!', category='erro')
    return render_template('login.html')

@app.route('/cadastro_produto', methods=['GET', 'POST'])
@login_required
def cadastro_produto():
    pass

@app.route('/listar_produto', methods=['GET', 'POST'])
def listar_produto():
    pass


@app.route('/editar_produto', methods=['GET', 'POST'])
def editar_produto():
    pass

@app.route('/excluir_produto', methods=['GET', 'POST'])
def excluir_produto():
    pass

@app.route('/logout')
def logout():
    pass






