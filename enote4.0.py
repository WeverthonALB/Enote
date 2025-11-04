import uuid
import json
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from functools import partial

class GerenciadorNotasApp:
    """
    ENOTE - Sistema de Notas Escolares com interface Tkinter e SQLite.
    Versão unificada com persistência de dados e interface dark mode aprimorada.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("ENOTE - SISTEMA DE NOTAS ESCOLARES")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)

        # --- Conexão com Banco ---
        try:
            self.conexao = sqlite3.connect("banco_completo.db")
            self.cursor = self.conexao.cursor()
            self.criar_tabelas()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível conectar ao SQLite: {e}")
            self.root.quit()
            return

        # --- Estruturas de Dados em Memória ---
        self.alunos = {}
        self.notas = {}
        self.carregar_dados()

        # --- Tema Dark ---
        self.BG_MAIN = '#0a0a0a'
        self.BG_CONTAINER = '#1e1e1e'
        self.TEXT_LIGHT = '#f0f0f0'
        self.ACCENT_COLOR = '#4A90E2'
        self.DANGER_COLOR = '#E74C3C'
        self.SUCCESS_COLOR = '#2ECC71'
        self.HEADER_BG = '#282828'
        self.DETAIL_BG = '#252525'

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.root.configure(bg=self.BG_MAIN)

        # --- Estilos Globais ---
        self.style.configure("TFrame", background=self.BG_MAIN)
        self.style.configure("Content.TFrame", background=self.BG_CONTAINER, borderwidth=1, relief="flat")
        self.style.configure("Detail.TFrame", background=self.DETAIL_BG, borderwidth=1, relief="solid")

        # Labels
        self.style.configure("TLabel", background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT, font=('Inter', 11))
        self.style.configure("Title.TLabel", font=('Inter', 36, 'bold'), background=self.BG_MAIN, foreground=self.ACCENT_COLOR, padding=15)
        self.style.configure("Header.TLabel", font=('Inter', 18, 'bold'), background=self.HEADER_BG, foreground=self.TEXT_LIGHT, padding=(20, 15))
        self.style.configure("Detail.TLabel", font=('Inter', 12, 'bold'), background=self.DETAIL_BG, foreground=self.TEXT_LIGHT)

        # Treeview (Tabela)
        self.style.configure("Treeview",
                             background=self.BG_CONTAINER,
                             foreground=self.TEXT_LIGHT,
                             fieldbackground=self.BG_CONTAINER,
                             rowheight=35,
                             borderwidth=0,
                             font=('Inter', 11))
        self.style.map("Treeview",
                       background=[('selected', self.ACCENT_COLOR)],
                       foreground=[('selected', 'white')])
        self.style.configure("Treeview.Heading",
                             font=('Inter', 12, 'bold'),
                             background=self.HEADER_BG,
                             foreground=self.TEXT_LIGHT,
                             relief="flat",
                             padding=12)
        
        # Botões
        self.style.configure("TButton", font=('Inter', 11, 'bold'), padding=(20, 10), relief="flat", background=self.ACCENT_COLOR, foreground="white")
        self.style.map("TButton",
            background=[('active', '#5aa0f2'), ('pressed', '#3a80d2')],
            foreground=[('active', 'white')]
        )
        
        # Entradas
        self.style.configure("TEntry", 
                             fieldbackground="#333", 
                             foreground=self.TEXT_LIGHT, 
                             bordercolor="#555", 
                             insertcolor=self.TEXT_LIGHT,
                             font=('Inter', 11),
                             padding=8)
        self.style.map("TEntry",
                       bordercolor=[('focus', self.ACCENT_COLOR)],
                       fieldbackground=[('focus', '#333')])


        self.current_frame = None
        self.show_main_menu()

    # ======================================================
    # BANCO DE DADOS (Unido do Script A)
    # ======================================================
    def criar_tabelas(self):
        """Cria as tabelas 'alunos' e 'notas' se não existirem."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            matricula TEXT,
            data_nascimento TEXT,
            turma TEXT NOT NULL,
            contato TEXT
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            componentes TEXT NOT NULL, -- Armazena a lista de componentes como JSON
            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
        )
        """)
        self.conexao.commit()

    def carregar_dados(self):
        """Carrega alunos e notas do SQLite para a memória."""
        self.alunos.clear()
        self.notas.clear()
        
        # Carregar Alunos
        self.cursor.execute("SELECT * FROM alunos")
        for row in self.cursor.fetchall():
            aluno_id, nome, matricula, nasc, turma, contato = row
            self.alunos[aluno_id] = {
                "nome": nome, "matricula": matricula,
                "data_nascimento": nasc, "turma": turma, "contato": contato
            }

        # Carregar Notas
        self.cursor.execute("SELECT aluno_id, disciplina, componentes FROM notas")
        for aluno_id, disciplina, comp_json in self.cursor.fetchall():
            try:
                comps = json.loads(comp_json)
                self.notas.setdefault(aluno_id, []).append(
                    {"disciplina": disciplina, "componentes": comps})
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON para o aluno {aluno_id}, disciplina {disciplina}")

    # ======================================================
    # INTERFACE GERAL (Do Script B)
    # ======================================================
    def clear_frame(self):
        """Destrói o frame atual para alternar entre telas."""
        if self.current_frame:
            self.current_frame.destroy()

    def formatar_numero(self, numero, casas=2):
        """Formata float para string com vírgula como separador decimal."""
        return f"{numero:.{casas}f}".replace('.', ',')

    def show_main_menu(self):
        """Cria e exibe a tela de menu principal."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="80", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        center_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=60)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(center_frame, text="📄",
                  font=('Inter', 64, 'bold'),
                  foreground=self.ACCENT_COLOR,
                  background=self.BG_CONTAINER).pack(pady=(10, 5))

        ttk.Label(center_frame, text="ENOTE",
                  font=('Inter', 48, 'bold'),
                  foreground=self.ACCENT_COLOR,
                  background=self.BG_CONTAINER).pack(pady=(0, 20))

        ttk.Label(center_frame, text="SISTEMA DE GESTÃO DE NOTAS ESCOLARES",
                  font=('Inter', 16),
                  background=self.BG_CONTAINER,
                  foreground=self.TEXT_LIGHT).pack(pady=(0, 40))

        ttk.Button(center_frame, text="🧑‍🏫 PROFESSOR/ADMIN", command=self.show_professor_menu, width=30).pack(pady=15)
        ttk.Button(center_frame, text="🎓 ALUNO", command=self.show_aluno_menu, width=30).pack(pady=15)
        ttk.Button(center_frame, text="❌ SAIR", command=self.root.quit, width=30).pack(pady=30)

    # ======================================================
    # PROFESSOR (Interface do Script B)
    # ======================================================
    def show_professor_menu(self):
        """Cria e exibe a tela de gestão do professor."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="20", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        self.current_frame.columnconfigure(0, weight=0)
        self.current_frame.columnconfigure(1, weight=1)
        self.current_frame.rowconfigure(0, weight=1)

        # Frame da Esquerda: Ações
        left_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=20)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=10)
        left_frame.grid_propagate(False)

        ttk.Label(left_frame, text="MENU DE AÇÕES", style="Header.TLabel", background=self.HEADER_BG, anchor="center").pack(pady=15, fill="x")

        actions_container = ttk.Frame(left_frame, style="Content.TFrame")
        actions_container.pack(expand=True, fill="both", pady=10)

        actions = [
            ("➕ ADICIONAR ALUNO", self.adicionar_aluno_gui),
            ("📝 ATRIBUIR NOTAS (DINÂMICO)", self.adicionar_notas_gui),
            ("📈 VISUALIZAR NOTAS", self.visualizar_notas_gui),
            ("🧮 CALCULAR MÉDIA GERAL", self.calcular_media_gui),
            ("🗑️ EXCLUIR ALUNO", self.excluir_aluno_gui),
        ]

        for text, command in actions:
            ttk.Button(actions_container, text=text, command=command).pack(pady=10, fill="x", padx=15)

        ttk.Button(left_frame, text="⬅️ VOLTAR AO MENU", command=self.show_main_menu).pack(side="bottom", pady=20, fill="x", padx=15)

        # Frame da Direita: Lista de Alunos
        list_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=20)
        list_frame.grid(row=0, column=1, sticky="nsew", pady=10, padx=(0, 10))

        ttk.Label(list_frame, text="ALUNOS CADASTRADOS", style="Header.TLabel", background=self.HEADER_BG, anchor="center").pack(pady=10, fill="x")

        cols = ('Nome', 'Turma', 'ID Único')
        self.tree = ttk.Treeview(list_frame, columns=cols, show='headings')
        self.tree.column('Nome', anchor='w', width=200)
        self.tree.column('Turma', anchor='center', width=100)
        self.tree.column('ID Único', anchor='center', width=150)

        for col in cols:
            self.tree.heading(col, text=col)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(expand=True, fill="both", pady=(10,0))
        self.atualizar_lista_alunos()

    def get_selected_aluno_id(self):
        """Retorna o ID do aluno selecionado na Treeview ou exibe um aviso."""
        try:
            selected_item = self.tree.selection()[0]
            aluno_id = self.tree.item(selected_item)['values'][2]
            return aluno_id
        except IndexError:
            messagebox.showwarning("AVISO", "Por favor, selecione um aluno na lista primeiro para realizar esta ação.")
            return None

    def atualizar_lista_alunos(self):
        """Limpa e preenche a Treeview com os dados dos alunos."""
        if not hasattr(self, 'tree'): return # Evita erro se a tree não foi criada
        
        self.tree.delete(*self.tree.get_children())
        for aluno_id, info in self.alunos.items():
            self.tree.insert("", "end", values=(info['nome'], info['turma'], aluno_id))

    # --- CRUD Aluno (Implementado com DB) ---

    def adicionar_aluno_gui(self):
        """Abre uma nova janela (Toplevel) para cadastrar um novo aluno."""
        top = tk.Toplevel(self.root)
        top.title("ENOTE: CADASTRO DE NOVO ALUNO")
        top.geometry("500x450") # Janela pode ser pequena, o scroll lidará com o excesso
        top.configure(bg=self.BG_MAIN)
        top.transient(self.root)
        top.grab_set()

        # --- Container principal que aplica o padding externo ---
        # Usamos Content.TFrame para o BG_CONTAINER
        main_padded_frame = ttk.Frame(top, style="Content.TFrame") 
        main_padded_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_padded_frame.rowconfigure(0, weight=1)
        main_padded_frame.columnconfigure(0, weight=1)

        # --- Canvas para scrolling ---
        canvas = tk.Canvas(main_padded_frame, background=self.BG_CONTAINER, borderwidth=0, highlightthickness=0)
        
        # --- Scrollbar ---
        scrollbar = ttk.Scrollbar(main_padded_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # --- Frame de conteúdo (vai dentro do canvas) ---
        # Este frame tem o padding interno
        form_frame = ttk.Frame(canvas, padding=30, style="Content.TFrame")
        
        # --- Adiciona o frame ao canvas ---
        form_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")

        # --- Layout do Canvas e Scrollbar ---
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Bindings para o scroll funcionar ---
        def on_frame_configure(event):
            # Atualiza o scrollregion para o tamanho do form_frame
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            # Força o form_frame a ter a largura do canvas
            canvas.itemconfig(form_window, width=event.width)

        form_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)


        campos = {
            "nome": "NOME COMPLETO",
            "matricula": "MATRÍCULA (opcional)",
            "data_nascimento": "DATA DE NASCIMENTO (opcional)",
            "turma": "TURMA/SÉRIE (obrigatório)",
            "contato": "TELEFONE/EMAIL (opcional)",
        }
        entradas = {}

        # Ajuste aqui: removido o 'background=self.BG_CONTAINER' para usar o estilo Header.TLabel
        ttk.Label(form_frame, text="PREENCHA OS DADOS DO NOVO ALUNO", style="Header.TLabel", anchor="center").grid(row=0, columnspan=2, sticky='ew', pady=(0, 20))

        row = 1
        for chave, label in campos.items():
            ttk.Label(form_frame, text=label + ":", font=('Inter', 11, 'bold'), background=self.BG_CONTAINER).grid(row=row, column=0, sticky="w", pady=8, padx=10)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=row, column=1, pady=8, padx=10, sticky="ew")
            entradas[chave] = entry
            row += 1

        ttk.Separator(form_frame, orient='horizontal').grid(row=row, columnspan=2, sticky='ew', pady=20)
        row += 1

        def salvar():
            dados = {chave: entrada.get().strip() for chave, entrada in entradas.items()}

            if not dados.get('nome') or not dados.get('turma'):
                messagebox.showerror("ERRO DE CADASTRO", "Os campos 'Nome Completo' e 'Turma/Série' são obrigatórios.", parent=top)
                return

            novo_id = str(uuid.uuid4()).split('-')[0].upper()
            
            try:
                # 1. Salvar no Banco de Dados
                self.cursor.execute("""
                    INSERT INTO alunos (id, nome, matricula, data_nascimento, turma, contato)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    novo_id, dados['nome'], dados['matricula'],
                    dados['data_nascimento'], dados['turma'], dados['contato']
                ))
                self.conexao.commit()

                # 2. Atualizar Memória
                self.alunos[novo_id] = dados
                self.notas[novo_id] = []

                # 3. Atualizar UI
                messagebox.showinfo("SUCESSO", f"Aluno '{dados['nome']}' cadastrado com sucesso!\n\nID DO ALUNO (ACESSO): {novo_id}", parent=top)
                self.atualizar_lista_alunos()
                top.destroy()
                
            except sqlite3.Error as e:
                messagebox.showerror("ERRO DE BANCO DE DADOS", f"Não foi possível salvar o aluno: {e}", parent=top)

        ttk.Button(form_frame, text="✅ SALVAR ALUNO E GERAR ID", command=salvar).grid(row=row, columnspan=2, pady=20, padx=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

    def excluir_aluno_gui(self):
        """Exclui um aluno e suas notas (via CASCADE) após confirmação."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id: return

        aluno_nome = self.alunos[aluno_id]['nome']
        confirm = messagebox.askyesno("CONFIRMAR EXCLUSÃO",
                                      f"Tem certeza que deseja excluir o aluno '{aluno_nome}' e todas as suas notas?\n\nEsta ação é irreversível!")

        if confirm:
            try:
                # 1. Excluir do Banco de Dados (CASCADE excluirá as notas)
                self.cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
                self.conexao.commit()

                # 2. Atualizar Memória
                del self.alunos[aluno_id]
                if aluno_id in self.notas:
                    del self.notas[aluno_id]

                # 3. Atualizar UI
                messagebox.showinfo("SUCESSO", f"Aluno '{aluno_nome}' foi excluído com sucesso.")
                self.atualizar_lista_alunos()
                
            except sqlite3.Error as e:
                messagebox.showerror("ERRO DE BANCO DE DADOS", f"Não foi possível excluir o aluno: {e}")

    # --- Adicionar Notas Dinâmico (Implementado com DB) ---

    def adicionar_notas_gui(self):
        """Abre uma nova janela para adicionar notas e pesos DINÂMICOS para um aluno."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id: return

        aluno_nome = self.alunos[aluno_id]['nome']

        top = tk.Toplevel(self.root)
        top.title(f"ENOTE: ATRIBUIR NOTAS E PESOS - {aluno_nome}")
        top.geometry("750x700")
        top.configure(bg=self.BG_MAIN)
        top.transient(self.root)
        top.grab_set()

        form_frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(3, weight=1) # Treeview expande

        # 1. Disciplina e Aluno
        ttk.Label(form_frame, text=f"DISCIPLINA PARA: {aluno_nome}", style="Header.TLabel", background=self.HEADER_BG, anchor="center").grid(row=0, column=0, sticky='ew', pady=(0, 15))

        disciplina_frame = ttk.Frame(form_frame, style="Content.TFrame")
        disciplina_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(disciplina_frame, text="NOME DA DISCIPLINA:", font=('Inter', 11, 'bold'), background=self.BG_CONTAINER).pack(side="left", padx=5, pady=5)
        disciplina_entry = ttk.Entry(disciplina_frame, width=40)
        disciplina_entry.pack(side="left", padx=5, expand=True, fill="x", ipady=3)

        # 2. Entrada de Componente (Nome, Nota, Peso)
        input_frame = ttk.Frame(form_frame, style="Content.TFrame", padding=15)
        input_frame.grid(row=2, column=0, sticky="new", pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(3, weight=1)

        ttk.Label(input_frame, text="ADICIONAR COMPONENTE DE AVALIAÇÃO:", font=('Inter', 13, 'bold'), background=self.BG_CONTAINER, foreground=self.ACCENT_COLOR).grid(row=0, columnspan=4, sticky="w", pady=(0, 10))
        ttk.Label(input_frame, text="NOME (Ex: Prova):", background=self.BG_CONTAINER).grid(row=1, column=0, sticky="w", padx=5)
        ttk.Label(input_frame, text="NOTA (0-10):", background=self.BG_CONTAINER).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(input_frame, text="PESO (1-5):", background=self.BG_CONTAINER).grid(row=1, column=2, sticky="w", padx=5)

        componente_entry = ttk.Entry(input_frame, width=20)
        componente_entry.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 10), ipady=3)
        nota_entry = ttk.Entry(input_frame, width=10)
        nota_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=(0, 10), ipady=3)
        peso_entry = ttk.Entry(input_frame, width=10)
        peso_entry.insert(0, "1")
        peso_entry.grid(row=2, column=2, sticky="ew", padx=5, pady=(0, 10), ipady=3)

        # 3. Treeview Temporário para Componentes
        tree_componentes_frame = ttk.Frame(form_frame, style="Content.TFrame", padding=(0, 10))
        tree_componentes_frame.grid(row=3, column=0, sticky="nsew", pady=10)

        ttk.Label(tree_componentes_frame, text="COMPONENTES INCLUÍDOS NESTA DISCIPLINA:", font=('Inter', 12, 'bold'), background=self.BG_CONTAINER).pack(anchor="w", padx=10, pady=(0, 10))
        cols = ('Nome', 'Nota', 'Peso')
        tree_componentes = ttk.Treeview(tree_componentes_frame, columns=cols, show='headings')
        tree_componentes.column('Nome', anchor='w', width=150)
        tree_componentes.column('Nota', anchor='center', width=100)
        tree_componentes.column('Peso', anchor='center', width=100)
        for col in cols: tree_componentes.heading(col, text=col)
        vsb = ttk.Scrollbar(tree_componentes_frame, orient="vertical", command=tree_componentes.yview)
        vsb.pack(side='right', fill='y')
        tree_componentes.configure(yscrollcommand=vsb.set)
        tree_componentes.pack(expand=True, fill="both", padx=10)

        # Funções internas
        def adicionar_componente():
            comp = componente_entry.get().strip()
            try:
                nota_val = float(nota_entry.get().replace(',', '.'))
                peso_val = int(peso_entry.get().strip())
                if not comp: raise ValueError("O nome do componente não pode ser vazio.")
                if not (0 <= nota_val <= 10): raise ValueError("Notas devem ser entre 0 e 10.")
                if not (1 <= peso_val <= 5): raise ValueError("Pesos devem ser entre 1 e 5.")
            except ValueError as e:
                messagebox.showerror("ERRO DE ENTRADA", f"Verifique as entradas: {e}", parent=top)
                return

            tree_componentes.insert("", "end", values=(comp, self.formatar_numero(nota_val, 1), peso_val))
            componente_entry.delete(0, tk.END)
            nota_entry.delete(0, tk.END)
            peso_entry.delete(0, tk.END)
            peso_entry.insert(0, "1")
            componente_entry.focus_set()

        ttk.Button(input_frame, text="➕ ADICIONAR", command=adicionar_componente, style="TButton").grid(row=2, column=3, sticky="ew", padx=5, pady=(0, 10), ipady=3)

        # 4. Botões de Controle e Submissão
        control_frame = ttk.Frame(form_frame, style="Content.TFrame")
        control_frame.grid(row=4, column=0, sticky="ew", pady=10)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)

        def remover_componente():
            selected = tree_componentes.selection()
            if selected:
                tree_componentes.delete(selected[0])
            else:
                messagebox.showwarning("AVISO", "Selecione um componente para remover.", parent=top)

        def limpar_componentes():
            if tree_componentes.get_children():
                if messagebox.askyesno("CONFIRMAR LIMPEZA", "Deseja remover TODOS os componentes?", parent=top):
                    tree_componentes.delete(*tree_componentes.get_children())
            else:
                messagebox.showinfo("AVISO", "Não há componentes para limpar.", parent=top)

        ttk.Button(control_frame, text="🗑️ REMOVER", command=remover_componente).grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Button(control_frame, text="🧹 LIMPAR TUDO", command=limpar_componentes).grid(row=0, column=1, sticky="ew", padx=5)

        def submit():
            disciplina = disciplina_entry.get().strip().upper()
            if not disciplina:
                messagebox.showerror("ERRO DE NOTA", "O NOME DA DISCIPLINA é obrigatório.", parent=top)
                return
            if not tree_componentes.get_children():
                messagebox.showerror("ERRO DE NOTA", "Adicione pelo menos um componente de avaliação.", parent=top)
                return

            for item in self.notas.get(aluno_id, []):
                if item['disciplina'] == disciplina:
                    messagebox.showwarning("AVISO", f"A disciplina '{disciplina}' já possui notas cadastradas.", parent=top)
                    return

            componentes_salvar = []
            for item_id in tree_componentes.get_children():
                comp_data = tree_componentes.item(item_id, 'values')
                nota_float = float(comp_data[1].replace(',', '.'))
                peso_int = int(comp_data[2])
                componentes_salvar.append({"nome": comp_data[0], "nota": nota_float, "peso": peso_int})

            # Converter para JSON para salvar no SQLite
            componentes_json = json.dumps(componentes_salvar)

            try:
                # 1. Salvar no Banco de Dados
                self.cursor.execute("""
                    INSERT INTO notas (aluno_id, disciplina, componentes)
                    VALUES (?, ?, ?)
                """, (aluno_id, disciplina, componentes_json))
                self.conexao.commit()

                # 2. Atualizar Memória
                self.notas.setdefault(aluno_id, []).append({
                    "disciplina": disciplina,
                    "componentes": componentes_salvar
                })
                
                # 3. Atualizar UI
                messagebox.showinfo("SUCESSO", f"Notas de '{disciplina}' para '{aluno_nome}' adicionadas.", parent=top)
                top.destroy()
                
            except sqlite3.Error as e:
                messagebox.showerror("ERRO DE BANCO DE DADOS", f"Não foi possível salvar as notas: {e}", parent=top)

        ttk.Button(control_frame, text="✅ SALVAR DISCIPLINA E COMPONENTES", command=submit).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(15, 5))

    # --- Métodos de Cálculo e Visualização (Implementados) ---

    def calcular_media_por_disciplina(self, nota_item):
        """Calcula a média PONDERADA de um item de nota específico."""
        if not nota_item or not nota_item.get('componentes'):
            return 0.0

        componentes = nota_item['componentes']
        soma_produtos = 0
        soma_pesos = 0

        for comp in componentes:
            soma_produtos += comp.get('nota', 0) * comp.get('peso', 1)
            soma_pesos += comp.get('peso', 1)

        media_ponderada = soma_produtos / soma_pesos if soma_pesos > 0 else 0.0
        return media_ponderada

    def calcular_media_gui(self, aluno_id=None, show_message=True):
        """Calcula a média PONDERADA geral de todas as disciplinas do aluno."""
        if not aluno_id:
            aluno_id = self.get_selected_aluno_id()
            if not aluno_id: return "0,00"

        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
            if show_message:
                messagebox.showerror("ERRO DE CÁLCULO", f"Nenhuma nota ponderada foi registrada para '{aluno_nome}'.")
            return "0,00"

        total_medias = 0
        total_disciplinas = len(notas_aluno)

        for nota_item in notas_aluno:
            total_medias += self.calcular_media_por_disciplina(nota_item)

        media_final = total_medias / total_disciplinas if total_disciplinas > 0 else 0
        media_str = self.formatar_numero(media_final, 2)

        if show_message:
            status = "APROVADO" if media_final >= 6.0 else "REPROVADO"
            emoji = "🎉" if status == "APROVADO" else "😔"
            messagebox.showinfo("MÉDIA GERAL FINAL",
                                f"A Média Geral Ponderada de '{aluno_nome}' é: {media_str}\n\nSTATUS FINAL: {status} {emoji}")
        return media_str
    
    def visualizar_notas_gui(self, aluno_id_param=None):
        """Abre o boletim detalhado do aluno. Usado pelo Professor e pelo Aluno."""
        aluno_id = aluno_id_param if aluno_id_param else self.get_selected_aluno_id()
        if not aluno_id: return
        
        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        top = tk.Toplevel(self.root)
        top.title(f"ENOTE: BOLETIM DE NOTAS - {aluno_nome}")
        top.geometry("900x650")
        top.configure(bg=self.BG_MAIN)
        top.transient(self.root)
        top.grab_set()

        main_frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.rowconfigure(2, weight=1) # Linha das tabelas
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text=f"BOLETIM DE NOTAS: {aluno_nome}", style="Header.TLabel", background=self.HEADER_BG, anchor="center").grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 15))

        # --- Coluna da Esquerda: Disciplinas ---
        left_frame = ttk.Frame(main_frame, style="Content.TFrame")
        left_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)

        ttk.Label(left_frame, text="DISCIPLINAS E MÉDIAS", style="TLabel", font=('Inter', 12, 'bold')).grid(row=0, column=0, sticky="w", pady=10, padx=10)
        
        cols_disciplinas = ('Disciplina', 'Média Ponderada')
        tree_disciplinas = ttk.Treeview(left_frame, columns=cols_disciplinas, show='headings')
        tree_disciplinas.column('Disciplina', anchor='w', width=180)
        tree_disciplinas.column('Média Ponderada', anchor='center', width=100)
        for col in cols_disciplinas: tree_disciplinas.heading(col, text=col)
        tree_disciplinas.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        if not notas_aluno:
            tree_disciplinas.insert("", "end", values=("Nenhuma nota registrada", ""))
        else:
            for nota_item in notas_aluno:
                media_disc = self.calcular_media_por_disciplina(nota_item)
                tree_disciplinas.insert("", "end", values=(nota_item['disciplina'], self.formatar_numero(media_disc)))

        # --- Coluna da Direita: Detalhes dos Componentes ---
        detail_frame = ttk.Frame(main_frame, style="Detail.TFrame", padding=15) # Use Detail style
        detail_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 0))
        detail_frame.rowconfigure(1, weight=1)
        detail_frame.columnconfigure(0, weight=1)

        ttk.Label(detail_frame, text="COMPONENTES (clique em uma disciplina)", style="Detail.TLabel", font=('Inter', 12, 'bold')).grid(row=0, column=0, sticky="w", pady=10, padx=10)

        # --- Média Geral ---
        media_geral = self.calcular_media_gui(aluno_id=aluno_id, show_message=False)
        media_float = float(media_geral.replace(',', '.'))
        status = "APROVADO" if media_float >= 6.0 else "REPROVADO"
        cor_status = self.SUCCESS_COLOR if status == "APROVADO" else self.DANGER_COLOR

        footer_frame = ttk.Frame(main_frame, style="Content.TFrame")
        footer_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Label(footer_frame, text=f"MÉDIA GERAL FINAL: {media_geral}", font=('Inter', 14, 'bold'), background=self.BG_CONTAINER).pack(side="left", padx=10, pady=10)
        ttk.Label(footer_frame, text=f"STATUS: {status}", font=('Inter', 14, 'bold'), foreground=cor_status, background=self.BG_CONTAINER).pack(side="right", padx=10, pady=10)

        # --- Bind ---
        tree_disciplinas.bind("<ButtonRelease-1>", 
            lambda event: self.atualizar_detalhes_disciplina(event, tree_disciplinas, aluno_id, detail_frame))

    def atualizar_detalhes_disciplina(self, event, tree_disciplinas, aluno_id, detail_frame):
        """Atualiza o painel de detalhes quando uma disciplina é selecionada na Treeview."""
        try:
            selected_item = tree_disciplinas.selection()[0]
        except IndexError:
            return # Nada selecionado

        disciplina_selecionada = tree_disciplinas.item(selected_item, 'values')[0]
        nota_item = next((item for item in self.notas[aluno_id] if item['disciplina'] == disciplina_selecionada), None)

        for widget in detail_frame.winfo_children():
            widget.destroy()

        if nota_item:
            ttk.Label(detail_frame, text=f"COMPONENTES DE: {disciplina_selecionada}", style="Detail.TLabel", font=('Inter', 12, 'bold')).grid(row=0, column=0, sticky="w", pady=10, padx=10)

            cols_comps = ('Componente', 'Nota', 'Peso')
            tree_comps = ttk.Treeview(detail_frame, columns=cols_comps, show='headings')
            tree_comps.column('Componente', anchor='w', width=120)
            tree_comps.column('Nota', anchor='center', width=80)
            tree_comps.column('Peso', anchor='center', width=80)
            for col in cols_comps: tree_comps.heading(col, text=col)
            tree_comps.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
            
            for comp in nota_item['componentes']:
                tree_comps.insert("", "end", values=(comp['nome'], self.formatar_numero(comp['nota'], 1), comp['peso']))
            
            detail_frame.rowconfigure(1, weight=1)
            detail_frame.columnconfigure(0, weight=1)
        else:
            ttk.Label(detail_frame, text="Erro: Detalhes não encontrados.", style="Detail.TLabel").grid(row=0, column=0, sticky="w", pady=10, padx=10)

    # ======================================================
    # MENU ALUNO (Adaptado do Script A com estilo do B)
    # ======================================================
    def show_aluno_menu(self):
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="80", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=50)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(frame, text="🎓", font=('Inter', 48, 'bold'),
                  foreground=self.ACCENT_COLOR, background=self.BG_CONTAINER).pack(pady=(10, 5))
        ttk.Label(frame, text="ÁREA DO ALUNO", font=('Inter', 24, 'bold'),
                  foreground=self.TEXT_LIGHT, background=self.BG_CONTAINER).pack(pady=(0, 20))
        
        ttk.Label(frame, text="Digite seu ID de Aluno:", background=self.BG_CONTAINER,
                  foreground=self.TEXT_LIGHT).pack(pady=10)

        entry = ttk.Entry(frame, width=30, justify="center")
        entry.pack(pady=5, ipady=5)

        def acessar():
            aluno_id = entry.get().strip().upper() # Nossos IDs são maiúsculos
            if aluno_id in self.alunos:
                # Reutiliza a função de visualização de notas
                self.visualizar_notas_gui(aluno_id_param=aluno_id)
            else:
                messagebox.showerror("Erro de Acesso", "ID de Aluno inválido ou não encontrado.")

        ttk.Button(frame, text="Acessar Boletim", command=acessar, width=30).pack(pady=15)
        ttk.Button(frame, text="⬅️ Voltar", command=self.show_main_menu, width=30).pack(pady=10)


# ======================================================
# EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorNotasApp(root)
    root.mainloop()

