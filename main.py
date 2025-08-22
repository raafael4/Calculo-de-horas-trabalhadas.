import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ---------- BANCO DE DADOS ----------

def conectar():
    return sqlite3.connect("horas.db")

def criar_tabelas():
    with conectar() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS horas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                cliente TEXT,
                tarefa TEXT,
                horas REAL,
                data TEXT,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        """)
        conn.commit()

criar_tabelas()

# ---------- TELA DE LOGIN ----------

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Controle de Horas")
        self.root.geometry("300x250")

        ttk.Label(root, text="CPF:").pack(pady=5)
        self.cpf_entry = ttk.Entry(root)
        self.cpf_entry.pack()

        ttk.Label(root, text="Senha:").pack(pady=5)
        self.senha_entry = ttk.Entry(root, show="*")
        self.senha_entry.pack()

        ttk.Button(root, text="Entrar", command=self.login).pack(pady=10)
        ttk.Button(root, text="Cadastrar", command=self.cadastrar).pack()

    def login(self):
        cpf = self.cpf_entry.get()
        senha = self.senha_entry.get()

        with conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT id, nome FROM usuarios WHERE cpf=? AND senha=?", (cpf, senha))
            resultado = c.fetchone()

        if resultado:
            messagebox.showinfo("Sucesso", f"Bem-vindo, {resultado[1]}!")
            self.root.destroy()
            main_app(resultado[0], resultado[1])  # ID e nome do usuário
        else:
            messagebox.showerror("Erro", "CPF ou senha inválidos.")

    def cadastrar(self):
        CadastroWindow()

# ---------- TELA DE CADASTRO ----------

class CadastroWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Cadastro de Usuário")
        self.window.geometry("300x300")

        ttk.Label(self.window, text="Nome:").pack(pady=5)
        self.nome_entry = ttk.Entry(self.window)
        self.nome_entry.pack()

        ttk.Label(self.window, text="CPF:").pack(pady=5)
        self.cpf_entry = ttk.Entry(self.window)
        self.cpf_entry.pack()

        ttk.Label(self.window, text="Senha:").pack(pady=5)
        self.senha_entry = ttk.Entry(self.window, show="*")
        self.senha_entry.pack()

        ttk.Button(self.window, text="Cadastrar", command=self.salvar_usuario).pack(pady=10)

    def salvar_usuario(self):
        nome = self.nome_entry.get()
        cpf = self.cpf_entry.get()
        senha = self.senha_entry.get()

        if not nome or not cpf or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        try:
            with conectar() as conn:
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (nome, cpf, senha) VALUES (?, ?, ?)", (nome, cpf, senha))
                conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso.")
            self.window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "CPF já cadastrado.")

# ---------- TELA PRINCIPAL ----------

class AppHoras:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name

        self.root = tk.Tk()
        self.root.title(f"Controle de Horas - Usuário: {user_name}")
        self.root.geometry("800x500")

        # Formulário
        frame_form = ttk.LabelFrame(self.root, text="Novo Registro")
        frame_form.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_form, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.cliente = ttk.Entry(frame_form)
        self.cliente.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Tarefa:").grid(row=1, column=0, padx=5, pady=5)
        self.tarefa = ttk.Entry(frame_form)
        self.tarefa.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Horas:").grid(row=2, column=0, padx=5, pady=5)
        self.horas = ttk.Entry(frame_form)
        self.horas.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Data (AAAA-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
        self.data = ttk.Entry(frame_form)
        self.data.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(frame_form, text="Adicionar", command=self.adicionar).grid(row=4, column=0, padx=5, pady=10)
        ttk.Button(frame_form, text="Excluir Selecionado", command=self.excluir).grid(row=4, column=1, padx=5, pady=10)
        ttk.Button(frame_form, text="Gerar Relatório", command=self.gerar_relatorio).grid(row=4, column=2, padx=5, pady=10)

        # Tabela
        frame_tabela = ttk.LabelFrame(self.root, text="Registros")
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)

        colunas = ("ID", "Cliente", "Tarefa", "Horas", "Data")
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

        self.carregar_registros()
        self.root.mainloop()

    def adicionar(self):
        cliente = self.cliente.get()
        tarefa = self.tarefa.get()
        horas = self.horas.get()
        data = self.data.get()

        if not cliente or not tarefa or not horas or not data:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return

        try:
            horas = float(horas)
        except:
            messagebox.showerror("Erro", "Horas deve ser um número.")
            return

        with conectar() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO horas (usuario_id, cliente, tarefa, horas, data) VALUES (?,?,?,?,?)",
                      (self.user_id, cliente, tarefa, horas, data))
            conn.commit()

        self.carregar_registros()
        self.limpar_formulario()

    def excluir(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um item.")
            return

        item = self.tree.item(selecionado[0])
        id_registro = item["values"][0]

        with conectar() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM horas WHERE id=? AND usuario_id=?", (id_registro, self.user_id))
            conn.commit()

        self.carregar_registros()

    def carregar_registros(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        with conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT id, cliente, tarefa, horas, data FROM horas WHERE usuario_id=?", (self.user_id,))
            for linha in c.fetchall():
                self.tree.insert("", "end", values=linha)

    def gerar_relatorio(self):
        with conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT SUM(horas) FROM horas WHERE usuario_id=?", (self.user_id,))
            total = c.fetchone()[0] or 0
        messagebox.showinfo("Relatório", f"Total de horas registradas: {total:.2f}")

    def limpar_formulario(self):
        self.cliente.delete(0, tk.END)
        self.tarefa.delete(0, tk.END)
        self.horas.delete(0, tk.END)
        self.data.delete(0, tk.END)

# ---------- RODAR LOGIN ----------

def main_app(user_id, nome):
    AppHoras(user_id, nome)

if __name__ == "__main__":
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()
