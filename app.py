from flask import Flask, request, redirect, url_for, render_template
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column

engine =create_engine('sqlite:///banco.db')

sessao = Session(bind=engine)

class Base(DeclarativeBase):
    pass

class Produto(Base):
    __tablename__ = 'tb_produto'
    pro_id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pro_nome:Mapped[str] = mapped_column(String(100))
    pro_preco:Mapped[float] = mapped_column()
    pro_descricao:Mapped[str] = mapped_column(String(150))

class Usuario(Base):
    __tablename__ = 'tb_usuario'
    pro_id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pro_nome:Mapped[str] = mapped_column(String(100))
    pro_email:Mapped[str] = mapped_column(String(100))
    pro_senha:Mapped[str] = mapped_column(String(100))

Base.metadata.create_all(bind=engine)

app = Flask()
app.secret_key = 'Esconda-me'

@app.route('/')
def index():
    pass

@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    pass

@app.route('/cadastro_produto', methods=['GET', 'POST'])
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






