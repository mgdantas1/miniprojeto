from flask import Flask, request, redirect, url_for, render_template, flash
from sqlalchemy import create_engine, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from flask_login import UserMixin, login_manager, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os

login_manager = LoginManager()
app = Flask(__name__)
login_manager.__init__(app)
app.secret_key = 'Esconda-me'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'pro_imagens')


engine = create_engine('sqlite:///banco.db')

sessao = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass


class Usuario(UserMixin, Base):
    __tablename__ = 'tb_usuario'

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usu_nome:Mapped[str] = mapped_column(String(100))
    usu_email:Mapped[str] = mapped_column(String(100))
    usu_senha:Mapped[str] = mapped_column(String(130))
    
    def get_id(self):
        return str(self.id)
    
    produtos = relationship('Produto', back_populates='usuario')

class Produto(Base):
    __tablename__ = 'tb_produto'

    pro_id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pro_nome:Mapped[str] = mapped_column(String(100))
    pro_preco:Mapped[float] = mapped_column()
    pro_descricao:Mapped[str] = mapped_column()
    pro_imagem_url:Mapped[str] = mapped_column(String())
    pro_usu_id:Mapped[int] = mapped_column(ForeignKey('tb_usuario.id'))

    usuario = relationship('Usuario', back_populates='produtos')


Base.metadata.create_all(engine)


@login_manager.user_loader
def load_user(user_id):
    with sessao() as session:
        return session.get(Usuario, int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        with sessao() as session:
            exist_usuario = session.query(Usuario).filter_by(usu_email=email).first()
            print(exist_usuario)
            
            if not exist_usuario:
                senha_crip = generate_password_hash(senha)                
                usuario_novo = Usuario(
                    usu_nome=nome, 
                    usu_email=email, 
                    usu_senha=senha_crip
                    )
                
                session.add(usuario_novo)
                session.commit()
                login_user(usuario_novo)

                flash('Usuário cadastrado!', category='sucesso')
                return redirect(url_for('index')) # return temporário
            
            flash('Já existe usuário cadastrado com esses dados!', category='erro')
    return render_template('cadastro_usuario.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        with sessao() as session:
            exist_usuario = session.query(Usuario).filter_by(usu_email=email).first()
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
    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        imagem = request.files['imagem']

        if imagem and imagem.filename != '':
            filename = secure_filename(imagem.filename)
            caminho_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            caminho = os.path.join(filename)
            imagem.save(caminho_save)
            imagem_url = caminho
        else:
            imagem_url = ''

        descricao = request.form['descricao']

        usu_id = current_user.id

        with sessao() as session:
            verificar = session.query(Produto).filter_by(pro_nome=nome).first()
            if not verificar:
                novo_prod = Produto(
                    pro_nome=nome, 
                    pro_preco=preco, 
                    pro_descricao=descricao, 
                    pro_imagem_url=imagem_url, 
                    pro_usu_id=usu_id
                    )
                
                session.add(novo_prod)
                session.commit()

                flash('Produto cadastrado com sucesso!', category='sucesso')
                return redirect(url_for('listar_produto'))
            
            flash('Produto não pode ser cadastrado!', category='erro')
            return redirect(url_for('cadastro_produto'))
            
    return render_template('cadastrar_produto.html')


@app.route('/listar_produto')
@login_required
def listar_produto():
    with sessao() as session:
        produtos = session.query(Produto).all()
    return render_template('produtos.html', produtos=produtos)


@app.route('/editar_produto', methods=['GET', 'POST'])
@login_required
def editar_produto():
    id = request.args.get('pro_id')

    with sessao() as session:
        produto_editar = session.query(Produto).filter_by(pro_id=id).first()
        if not produto_editar:
            flash('Produto não encontrado!', category='erro')
            return redirect(url_for('listar_produto')) 
        if produto_editar.pro_usu_id != current_user.id:
            flash('O produto não pode ser editado!', category='erro')
            return redirect(url_for('listar_produto')) 
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        preco = request.form.get('preco')

        descricao = request.form.get('descricao')
        
        with sessao() as session:
            produto = session.query(Produto).filter_by(pro_id=id).first()
            produto.pro_nome = nome
            produto.pro_preco = preco
            produto.pro_descricao = descricao
            session.commit()
        flash('Produto editado com sucesso!', category='sucesso')
        return redirect(url_for('listar_produto'))
    return render_template('editar_produto.html', produto_editar = produto_editar)


@app.route('/excluir_produto')
@login_required
def excluir_produto():
    with sessao() as session:
        id = request.args.get('pro_id')
        prod = session.query(Produto).filter_by(pro_id=id).first()
        if prod.pro_usu_id == current_user.id:
            session.delete(prod)
            session.commit()
            flash('Produto removido com sucesso!', category='sucesso')
            return redirect(url_for('listar_produto'))
        flash('O produto não pode ser removido!', category='erro')
        return redirect(url_for('listar_produto'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)