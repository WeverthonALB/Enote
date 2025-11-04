import uuid
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class GerenciadorNotasApp:
    """
    Aplicação eNote para gerenciamento de notas escolares usando Tkinter.
    Agora suporta cálculo de Média Ponderada (com Pesos).
    """
    def __init__(self, root):
        self.root = root
        self.root.title("eNote - Sistema de Notas Inteligente (v3.0)")
        self.root.geometry("900x700") # Tamanho maior para melhor visualização
        self.root.minsize(800, 600)

        # --- Esquema de Cores e Estilos Dark Mode (eNote Pro Style) ---
        self.BG_MAIN = '#0c0c0c'        # Fundo principal (quase preto, mais profundo)
        self.BG_CONTAINER = '#1a1a1a'   # Fundo dos painéis e caixas (cinza escuro)
        self.TEXT_LIGHT = '#ebebeb'     # Cor principal do texto (branco suave)
        self.ACCENT_COLOR = '#00c3ff'   # Cor de destaque (Ciano vibrante)
        self.DANGER_COLOR = '#ff6b6b'   # Vermelho suave para reprovado/erro
        self.SUCCESS_COLOR = '#50e3c2'  # Verde água suave para aprovado/sucesso
        self.HEADER_BG = '#282828'      # Fundo para cabeçalhos e separadores
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuração do Fundo da Janela Principal
        self.root.configure(bg=self.BG_MAIN)
        
        # Estilos Gerais de Frames
        self.style.configure("TFrame", background=self.BG_MAIN)
        self.style.configure("Content.TFrame", background=self.BG_CONTAINER, borderwidth=0, relief="flat") # Sem borda explícita

        # Estilos de Títulos e Headers
        self.style.configure("Title.TLabel", font=('Inter', 32, 'bold'), background=self.BG_MAIN, foreground=self.ACCENT_COLOR, padding=15)
        self.style.configure("Header.TLabel", font=('Inter', 18, 'bold'), background=self.HEADER_BG, foreground=self.TEXT_LIGHT, padding=(20, 15))
        
        # Estilos de Botões (Mais contraste e padding)
        self.style.configure("TButton", 
            padding=(15, 10), 
            relief="flat", 
            background=self.ACCENT_COLOR, 
            foreground=self.BG_CONTAINER, 
            font=('Inter', 12, 'bold'),
            focuscolor=self.ACCENT_COLOR
        )
        self.style.map("TButton", 
            background=[('active', '#0097c2')], 
            foreground=[('active', self.BG_MAIN)]
        )

        # Estilos para Entradas (Entry) - Mais escuro para contraste
        self.style.configure("TEntry", fieldbackground='#303030', foreground=self.TEXT_LIGHT, borderwidth=0, relief="flat", padding=10)

        # Estilo Treeview (Tabela de Dados)
        self.style.configure("Treeview", 
            background=self.BG_CONTAINER, 
            foreground=self.TEXT_LIGHT, 
            fieldbackground=self.BG_CONTAINER,
            rowheight=35,
            borderwidth=0
        )
        self.style.map("Treeview", background=[('selected', self.ACCENT_COLOR)], foreground=[('selected', self.BG_CONTAINER)])
        self.style.configure("Treeview.Heading", 
            font=('Inter', 12, 'bold'), 
            background=self.HEADER_BG, 
            foreground=self.TEXT_LIGHT,
            relief="flat",
            padding=12
        )
        
        # Dados armazenados em memória. O objeto nota agora inclui 'pesos'
        self.alunos = {}
        self.notas = {}

        self.current_frame = None
        
        self.show_main_menu()

    def clear_frame(self):
        """Destrói o frame atual para alternar entre telas."""
        if self.current_frame:
            self.current_frame.destroy()

    def show_main_menu(self):
        """Cria e exibe a tela de menu principal (Login/Seleção de Perfil)."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="80", style="TFrame") # Mais padding
        self.current_frame.pack(expand=True, fill="both")
        
        center_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=60)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Ícone/Marca eNote (Refinado)
        logo_icon = ttk.Label(center_frame, text="📄✔️", 
                  font=('Inter', 64, 'bold'), 
                  foreground=self.ACCENT_COLOR, 
                  background=self.BG_CONTAINER)
        logo_icon.pack(pady=(10, 5))
        
        logo_text = ttk.Label(center_frame, text="eNOTE", 
                  font=('Inter', 48, 'bold'), 
                  foreground=self.ACCENT_COLOR, 
                  background=self.BG_CONTAINER)
        logo_text.pack(pady=(0, 20))

        title_label = ttk.Label(center_frame, text="Sistema de Gestão de Notas Ponderadas", 
                                font=('Inter', 16), 
                                background=self.BG_CONTAINER, 
                                foreground=self.TEXT_LIGHT)
        title_label.pack(pady=(0, 40))

        # Botões de acesso com visual aprimorado
        professor_button = ttk.Button(center_frame, text="🧑‍🏫 Professor/Admin", command=self.show_professor_menu, width=30)
        professor_button.pack(pady=15)

        aluno_button = ttk.Button(center_frame, text="🎓 Aluno", command=self.show_aluno_menu, width=30)
        aluno_button.pack(pady=15)

        sair_button = ttk.Button(center_frame, text="❌ Sair", command=self.root.quit, width=30)
        sair_button.pack(pady=30)

    # --- Métodos do Professor ---

    def show_professor_menu(self):
        """Cria e exibe a tela de gestão do professor (mantendo o layout)."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="20", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        self.current_frame.columnconfigure(0, weight=0) 
        self.current_frame.columnconfigure(1, weight=1) 
        self.current_frame.rowconfigure(0, weight=1)

        # Frame da Esquerda: Ações
        left_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=20)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=10)

        ttk.Label(left_frame, text="Menu de Ações", style="Header.TLabel", background=self.HEADER_BG).pack(pady=15, fill="x")

        # Botões de Ação
        actions = [
            ("➕ Adicionar Aluno", self.adicionar_aluno_gui),
            ("📝 Atribuir Notas (c/ Pesos)", self.adicionar_notas_gui),
            ("📈 Visualizar Notas", self.visualizar_notas_gui),
            ("🧮 Calcular Média Geral", self.calcular_media_gui),
            ("🗑️ Excluir Aluno", self.excluir_aluno_gui),
        ]

        for text, command in actions:
            ttk.Button(left_frame, text=text, command=command).pack(pady=10, fill="x", padx=15)
            
        ttk.Button(left_frame, text="⬅️ Voltar ao Menu", command=self.show_main_menu).pack(side="bottom", pady=20, fill="x", padx=15)

        # Frame da Direita: Lista de Alunos (TreeView)
        list_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=20)
        list_frame.grid(row=0, column=1, sticky="nsew", pady=10, padx=(0, 10))

        ttk.Label(list_frame, text="Alunos Cadastrados no Sistema", style="Header.TLabel", background=self.HEADER_BG).pack(pady=10, fill="x")

        # Treeview (Tabela)
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
        
        self.tree.pack(expand=True, fill="both")
        self.atualizar_lista_alunos()

    def atualizar_lista_alunos(self):
        """Limpa e preenche a Treeview com os dados dos alunos."""
        self.tree.delete(*self.tree.get_children())
        
        for aluno_id, info in self.alunos.items():
            self.tree.insert("", "end", values=(info['nome'], info['turma'], aluno_id))

    def adicionar_aluno_gui(self):
        """Abre uma nova janela (Toplevel) para cadastrar um novo aluno."""
        top = tk.Toplevel(self.root)
        top.title("eNote: Cadastro de Novo Aluno")
        top.geometry("500x550")
        top.configure(bg=self.BG_MAIN) 
        top.transient(self.root)
        top.grab_set()

        campos = {
            "nome": "Nome Completo",
            "matricula": "Matrícula (opcional)",
            "data_nascimento": "Data de Nascimento (opcional)",
            "turma": "Turma/Série (obrigatório)",
            "contato": "Telefone/Email (opcional)",
        }

        entradas = {}

        form_frame = ttk.Frame(top, padding=30, style="Content.TFrame") 
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Título do Formulário
        ttk.Label(form_frame, text="Preencha os dados do novo aluno", style="Header.TLabel", background=self.BG_CONTAINER).grid(row=0, columnspan=2, sticky='ew', pady=(0, 20))
        
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
            """Função interna para salvar os dados do novo aluno."""
            dados = {chave: entrada.get().strip() for chave, entrada in entradas.items()}
            
            if not dados.get('nome') or not dados.get('turma'):
                messagebox.showerror("Erro de Cadastro", "Os campos 'Nome Completo' e 'Turma/Série' são obrigatórios.", parent=top)
                return

            novo_id = str(uuid.uuid4()).split('-')[0] # ID mais curto e amigável
            self.alunos[novo_id] = dados
            self.notas[novo_id] = []
            
            messagebox.showinfo("Sucesso", f"Aluno '{dados['nome']}' cadastrado com sucesso!\n\nID do Aluno (Acesso): {novo_id}", parent=top)
            
            self.atualizar_lista_alunos()
            top.destroy()

        ttk.Button(form_frame, text="✅ Salvar Aluno e Gerar ID", command=salvar).grid(row=row, columnspan=2, pady=20, padx=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

    def get_selected_aluno_id(self):
        """Retorna o ID do aluno selecionado na Treeview ou exibe um aviso."""
        try:
            selected_item = self.tree.selection()[0]
            # O ID Único é a terceira coluna (índice 2) na Treeview
            aluno_id = self.tree.item(selected_item)['values'][2] 
            return aluno_id
        except IndexError:
            messagebox.showwarning("Aviso", "Por favor, selecione um aluno na lista primeiro para realizar esta ação.")
            return None

    def adicionar_notas_gui(self):
        """Abre uma nova janela para adicionar notas e pesos para um aluno."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id:
            return

        aluno_nome = self.alunos[aluno_id]['nome']

        top = tk.Toplevel(self.root)
        top.title(f"eNote: Atribuir Notas e Pesos para {aluno_nome}")
        top.geometry("550x450")
        top.configure(bg=self.BG_MAIN)
        top.transient(self.root)
        top.grab_set()

        form_frame = ttk.Frame(top, padding=30, style="Content.TFrame")
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(2, weight=1)

        ttk.Label(form_frame, text="Disciplina:", font=('Inter', 11, 'bold'), background=self.BG_CONTAINER).grid(row=0, column=0, sticky="w", pady=10, padx=5)
        disciplina_entry = ttk.Entry(form_frame, width=40)
        disciplina_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=10, padx=5)
        
        ttk.Separator(form_frame, orient='horizontal').grid(row=1, columnspan=3, sticky='ew', pady=10)

        # Cabeçalhos para Notas e Pesos
        ttk.Label(form_frame, text="COMPONENTE", font=('Inter', 10, 'bold'), background=self.BG_CONTAINER, foreground=self.ACCENT_COLOR).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        ttk.Label(form_frame, text="NOTA (0-10)", font=('Inter', 10, 'bold'), background=self.BG_CONTAINER, foreground=self.ACCENT_COLOR).grid(row=2, column=1, sticky="w", pady=5, padx=5)
        ttk.Label(form_frame, text="PESO (1-5)", font=('Inter', 10, 'bold'), background=self.BG_CONTAINER, foreground=self.ACCENT_COLOR).grid(row=2, column=2, sticky="w", pady=5, padx=5)

        # Dados
        componentes = ["Trabalho", "Teste", "Prova"]
        entradas_notas = {}
        entradas_pesos = {}
        
        for i, comp in enumerate(componentes):
            row_num = i + 3
            ttk.Label(form_frame, text=f"{comp}:", background=self.BG_CONTAINER).grid(row=row_num, column=0, sticky="w", pady=8, padx=5)
            
            # Entry para Nota
            nota_entry = ttk.Entry(form_frame, width=15)
            nota_entry.grid(row=row_num, column=1, sticky="ew", pady=8, padx=5)
            entradas_notas[comp.lower()] = nota_entry
            
            # Entry para Peso (Default 1)
            peso_entry = ttk.Entry(form_frame, width=15)
            peso_entry.insert(0, "1") # Valor padrão
            peso_entry.grid(row=row_num, column=2, sticky="ew", pady=8, padx=5)
            entradas_pesos[comp.lower()] = peso_entry


        def submit():
            """Função interna para validar, ponderar e salvar as notas."""
            disciplina = disciplina_entry.get().strip()
            
            if not disciplina:
                messagebox.showerror("Erro de Nota", "O nome da disciplina não pode ser vazio.", parent=top)
                return

            # Validação e conversão das notas e pesos
            notas_data = {}
            pesos_data = {}
            try:
                for comp in componentes:
                    comp_key = comp.lower()
                    
                    # Nota
                    nota_val = float(entradas_notas[comp_key].get().replace(',', '.'))
                    if not (0 <= nota_val <= 10):
                         raise ValueError("Notas devem ser entre 0 e 10.")
                    notas_data[comp_key] = nota_val
                    
                    # Peso
                    peso_val = int(entradas_pesos[comp_key].get().strip())
                    if not (1 <= peso_val <= 5):
                        raise ValueError("Pesos devem ser entre 1 e 5.")
                    pesos_data[comp_key] = peso_val
                    
            except ValueError as e:
                messagebox.showerror("Erro de Entrada", f"Verifique as entradas: {e}", parent=top)
                return
            
            # Verifica se a disciplina já foi cadastrada (evita duplicidade)
            for item in self.notas[aluno_id]:
                if item['disciplina'].lower() == disciplina.lower():
                    messagebox.showwarning("Aviso", f"A disciplina '{disciplina}' já possui notas cadastradas.", parent=top)
                    return

            self.notas[aluno_id].append({
                "disciplina": disciplina,
                "notas": notas_data,
                "pesos": pesos_data # Novo campo para pesos
            })
            messagebox.showinfo("Sucesso", f"Notas de '{disciplina}' para '{aluno_nome}' adicionadas e ponderadas.", parent=top)
            top.destroy()

        submit_button = ttk.Button(form_frame, text="✅ Adicionar Notas Ponderadas", command=submit)
        submit_button.grid(row=len(componentes) + 4, columnspan=3, pady=30, padx=5, sticky="ew")

    def calcular_media_por_disciplina(self, nota_item):
        """Calcula a média PONDERADA de um item de nota específico."""
        if not nota_item or not nota_item.get('notas') or not nota_item.get('pesos'):
             return 0.0
        
        notas = nota_item['notas']
        pesos = nota_item['pesos']
        
        soma_produtos = 0
        soma_pesos = 0
        
        for chave in notas.keys():
            soma_produtos += notas[chave] * pesos[chave]
            soma_pesos += pesos[chave]

        media_ponderada = soma_produtos / soma_pesos if soma_pesos > 0 else 0.0
        return media_ponderada

    def visualizar_notas_gui(self, aluno_id=None):
        """Abre uma janela para visualizar todas as notas e médias de um aluno."""
        if not aluno_id:
            aluno_id = self.get_selected_aluno_id()
            if not aluno_id:
                return

        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
            messagebox.showinfo("Informação", f"Nenhuma nota ponderada encontrada para {aluno_nome}.")
            return

        top = tk.Toplevel(self.root)
        top.title(f"eNote: Histórico de Notas Ponderadas de {aluno_nome}")
        top.geometry("800x600")
        top.configure(bg=self.BG_MAIN)
        top.transient(self.root)
        top.grab_set()

        list_frame = ttk.Frame(top, padding=15, style="Content.TFrame")
        list_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ttk.Label(list_frame, text=f"Histórico Detalhado - {aluno_nome}", style="Header.TLabel", background=self.HEADER_BG).pack(pady=(0, 15), fill="x")

        # Treeview para exibir a tabela de notas
        cols = ('Disciplina', 'T-Nota', 'T-Peso', 'S-Nota', 'S-Peso', 'P-Nota', 'P-Peso', 'Média Ponderada', 'Status')
        tree_notas = ttk.Treeview(list_frame, columns=cols, show='headings')
        
        # Ajuste de Larguras
        tree_notas.column('Disciplina', anchor='w', width=120)
        tree_notas.column('T-Nota', anchor='center', width=60); tree_notas.column('T-Peso', anchor='center', width=60)
        tree_notas.column('S-Nota', anchor='center', width=60); tree_notas.column('S-Peso', anchor='center', width=60)
        tree_notas.column('P-Nota', anchor='center', width=60); tree_notas.column('P-Peso', anchor='center', width=60)
        tree_notas.column('Média Ponderada', anchor='center', width=100)
        tree_notas.column('Status', anchor='center', width=90)
        
        for col in cols:
            tree_notas.heading(col, text=col)
            
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=tree_notas.yview)
        vsb.pack(side='right', fill='y')
        tree_notas.configure(yscrollcommand=vsb.set)
        tree_notas.pack(expand=True, fill="both")
        
        # Preenche a Treeview
        for nota_item in notas_aluno:
            media_disciplina = self.calcular_media_por_disciplina(nota_item)
            media_corte = 6.0
            status = "APROVADO" if media_disciplina >= media_corte else "REPROVADO"
            
            tag = "aprovado" if status == "APROVADO" else "reprovado"
            tree_notas.tag_configure("aprovado", foreground=self.SUCCESS_COLOR)
            tree_notas.tag_configure("reprovado", foreground=self.DANGER_COLOR)
            
            # Formatação de string para exibição
            T_Nota = f"{nota_item['notas']['trabalho']:.1f}".replace('.', ',')
            S_Nota = f"{nota_item['notas']['teste']:.1f}".replace('.', ',')
            P_Nota = f"{nota_item['notas']['prova']:.1f}".replace('.', ',')
            
            T_Peso = nota_item['pesos']['trabalho']
            S_Peso = nota_item['pesos']['teste']
            P_Peso = nota_item['pesos']['prova']
            
            media_str = f"{media_disciplina:.2f}".replace('.', ',')

            tree_notas.insert("", "end", values=(
                nota_item['disciplina'],
                T_Nota, T_Peso,
                S_Nota, S_Peso,
                P_Nota, P_Peso,
                media_str,
                status
            ), tags=(tag,))
        
        ttk.Button(list_frame, text="Fechar", command=top.destroy).pack(pady=15)

    def calcular_media_gui(self, aluno_id=None, show_message=True):
        """Calcula a média PONDERADA geral de todas as disciplinas do aluno."""
        if not aluno_id:
            aluno_id = self.get_selected_aluno_id()
            if not aluno_id:
                return "0,00"

        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
            if show_message:
                messagebox.showerror("Erro de Cálculo", f"Nenhuma nota ponderada foi registrada para '{aluno_nome}'.")
            return "0,00"

        total_medias = 0
        total_disciplinas = len(notas_aluno)
        
        for nota_item in notas_aluno:
            total_medias += self.calcular_media_por_disciplina(nota_item)

        media_final = total_medias / total_disciplinas if total_disciplinas > 0 else 0

        media_str = f"{media_final:.2f}".replace('.', ',')
        
        if show_message:
            status = "APROVADO" if media_final >= 6.0 else "REPROVADO"
            emoji = "🎉" if status == "APROVADO" else "😔"
            messagebox.showinfo("Média Geral Final", 
                                f"A Média Geral Ponderada de '{aluno_nome}' é: {media_str}\n\nStatus Final: {status} {emoji}")

        return media_str

    def excluir_aluno_gui(self):
        """Exclui um aluno e suas notas após confirmação."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id:
            return

        aluno_nome = self.alunos[aluno_id]['nome']
        confirm = messagebox.askyesno("Confirmar Exclusão",
                                      f"Tem certeza que deseja excluir o aluno '{aluno_nome}' e todas as suas notas?\n\nEsta ação é irreversível!")

        if confirm:
            del self.alunos[aluno_id]
            if aluno_id in self.notas:
                del self.notas[aluno_id]
            messagebox.showinfo("Sucesso", f"Aluno '{aluno_nome}' foi excluído com sucesso.")
            self.atualizar_lista_alunos() 

    # --- Métodos do Aluno ---

    def show_aluno_menu(self):
        """Tela inicial para o aluno (login por ID)."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="80", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        center_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=50)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(center_frame, text="🔑 Área de Acesso do Aluno", style="Header.TLabel", background=self.HEADER_BG).pack(pady=(0, 20), fill="x")
        ttk.Label(center_frame, text="Insira seu ID Único para acessar suas notas:", background=self.BG_CONTAINER).pack(pady=10)

        id_entry = ttk.Entry(center_frame, width=30)
        id_entry.pack(pady=5, padx=10)

        def on_submit():
            aluno_id = id_entry.get().strip()
            if aluno_id in self.alunos:
                self.show_aluno_dashboard(aluno_id)
            else:
                messagebox.showerror("Erro de Acesso", "ID de aluno não encontrado. Verifique se o ID está correto.")

        submit_button = ttk.Button(center_frame, text="🔐 Acessar Dashboard", command=on_submit, width=30)
        submit_button.pack(pady=20)

        back_button = ttk.Button(center_frame, text="⬅️ Voltar ao Menu Principal", command=self.show_main_menu)
        back_button.pack(pady=10)

    def show_aluno_dashboard(self, aluno_id):
        """Dashboard com as informações e notas do aluno logado."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="40", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        aluno_nome = self.alunos[aluno_id]['nome']

        ttk.Label(self.current_frame, text=f"Bem-vindo(a), {aluno_nome}!", style="Title.TLabel", background=self.BG_MAIN).pack(pady=(0, 20))

        # Estrutura com duas colunas (Info Pessoal | Média Principal)
        top_row_frame = ttk.Frame(self.current_frame, style="TFrame")
        top_row_frame.pack(pady=10, fill="x")
        top_row_frame.columnconfigure(0, weight=1)
        top_row_frame.columnconfigure(1, weight=1)

        # 1. Box de Informações Pessoais
        info_box = ttk.Frame(top_row_frame, style="Content.TFrame", padding=30)
        info_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ttk.Label(info_box, text="👤 DADOS PESSOAIS", font=('Inter', 12, 'bold'), background=self.BG_CONTAINER, foreground=self.ACCENT_COLOR).pack(anchor="w", pady=(0, 10))
        
        for key, label in [("turma", "Turma"), ("matricula", "Matrícula"), ("data_nascimento", "Nascimento"), ("contato", "Contato")]:
            value = self.alunos[aluno_id].get(key, "Não Informado")
            ttk.Label(info_box, text=f"• {label}: {value}", background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT).pack(anchor="w", padx=10)


        # 2. Box de Média Principal
        media_box = ttk.Frame(top_row_frame, style="Content.TFrame", padding=30)
        media_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        media_str = self.calcular_media_gui(aluno_id, show_message=False)
        media_float = float(media_str.replace(',', '.')) 
        status = "APROVADO" if media_float >= 6.0 else "REPROVADO"
        status_color = self.SUCCESS_COLOR if status == "APROVADO" else self.DANGER_COLOR

        ttk.Label(media_box, text="📈 MÉDIA GERAL PONDERADA", font=('Inter', 12, 'bold'), background=self.BG_CONTAINER, foreground=self.ACCENT_COLOR).pack(anchor="w")
        ttk.Label(media_box, text=media_str, font=('Inter', 48, 'bold'), foreground=self.TEXT_LIGHT, background=self.BG_CONTAINER).pack(anchor="center", pady=10)
        
        status_label = ttk.Label(media_box, text=f"Status Final: {status}", font=('Inter', 16, 'bold'), foreground=status_color, background=self.BG_CONTAINER)
        status_label.pack(anchor="center", pady=5)


        # Botão Ação Principal
        ttk.Button(self.current_frame, text="📊 Visualizar DETALHES DAS NOTAS (Com Pesos)", 
                   command=lambda: self.visualizar_notas_gui(aluno_id)).pack(pady=25, fill="x", padx=50)
                   
        ttk.Button(self.current_frame, text="🚪 Sair do Sistema", 
                   command=self.show_main_menu).pack(side="bottom", pady=20)


if __name__ == "__main__":
    # Inicializa o Tkinter
    root = tk.Tk()
    
    # Cria e executa a aplicação
    app = GerenciadorNotasApp(root)
    root.mainloop()
