import uuid
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog 
from functools import partial

class GerenciadorNotasApp:
    """
    Aplicação ENOTE para gerenciamento de notas escolares usando Tkinter.
    Suporta cálculo de Média Ponderada e componentes de avaliação dinâmicos.
    Design otimizado em Dark Mode.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("ENOTE - SISTEMA DE NOTAS ESCOLARES")
        self.root.geometry("1000x750") 
        self.root.minsize(900, 650)

        # --- Esquema de Cores e Estilos Dark Mode (Mais Profissional) ---
        self.BG_MAIN = '#0a0a0a'        # Fundo principal (Preto Profundo)
        self.BG_CONTAINER = '#1e1e1e'   # Fundo dos painéis
        self.TEXT_LIGHT = '#f0f0f0'     # Cor principal do texto
        self.ACCENT_COLOR = '#4A90E2'   # Azul Corporativo de Destaque
        self.DANGER_COLOR = '#E74C3C'   # Vermelho Forte (Reprovado)
        self.SUCCESS_COLOR = '#2ECC71'  # Verde Forte (Aprovado)
        self.HEADER_BG = '#282828'      # Fundo para cabeçalhos/Barras

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuração do Fundo da Janela Principal
        self.root.configure(bg=self.BG_MAIN)
        
        # Estilos gerais
        self.style.configure("TFrame", background=self.BG_MAIN)
        self.style.configure("Content.TFrame", background=self.BG_CONTAINER, borderwidth=1, relief="flat") 
        self.style.configure("Detail.TFrame", background='#252525', borderwidth=1, relief="solid")
        
        # Estilos de Labels
        self.style.configure("Title.TLabel", font=('Inter', 36, 'bold'), background=self.BG_MAIN, foreground=self.ACCENT_COLOR, padding=15)
        self.style.configure("Header.TLabel", font=('Inter', 18, 'bold'), background=self.HEADER_BG, foreground=self.TEXT_LIGHT, padding=(20, 15))
        self.style.configure("Detail.TLabel", font=('Inter', 14, 'bold'), background='#252525', foreground=self.TEXT_LIGHT)
        self.style.configure("TLabel", background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT) # Default Label Style

        # Estilos de Treeview para a tabela
        self.style.configure("Treeview", 
            background=self.BG_CONTAINER, 
            foreground=self.TEXT_LIGHT, 
            fieldbackground=self.BG_CONTAINER,
            rowheight=35,
            borderwidth=0
        )
        self.style.map("Treeview", 
            background=[('selected', self.ACCENT_COLOR)], 
            foreground=[('selected', 'white')] # Texto branco no item selecionado
        )
        self.style.configure("Treeview.Heading", 
            font=('Inter', 12, 'bold'), 
            background=self.HEADER_BG, 
            foreground=self.TEXT_LIGHT,
            relief="flat",
            padding=12
        )
        
        # Dados: Estrutura de notas
        self.alunos = {}
        self.notas = {}

        self.current_frame = None
        self.show_main_menu()

    def clear_frame(self):
        """Destrói o frame atual para alternar entre telas."""
        if self.current_frame:
            self.current_frame.destroy()
            
    # Funções auxiliares

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
        
        logo_icon = ttk.Label(center_frame, text="📄", 
                  font=('Inter', 64, 'bold'), 
                  foreground=self.ACCENT_COLOR, 
                  background=self.BG_CONTAINER)
        logo_icon.pack(pady=(10, 5))
        
        logo_text = ttk.Label(center_frame, text="ENOTE", 
                  font=('Inter', 48, 'bold'), 
                  foreground=self.ACCENT_COLOR, 
                  background=self.BG_CONTAINER)
        logo_text.pack(pady=(0, 20))

        title_label = ttk.Label(center_frame, text="SISTEMA DE GESTÃO DE NOTAS ESCOLARES", 
                                font=('Inter', 16), 
                                background=self.BG_CONTAINER, 
                                foreground=self.TEXT_LIGHT)
        title_label.pack(pady=(0, 40))

        professor_button = ttk.Button(center_frame, text="🧑‍🏫 PROFESSOR/ADMIN", command=self.show_professor_menu, width=30)
        professor_button.pack(pady=15)

        aluno_button = ttk.Button(center_frame, text="🎓 ALUNO", command=self.show_aluno_menu, width=30)
        aluno_button.pack(pady=15)

        sair_button = ttk.Button(center_frame, text="❌ SAIR", command=self.root.quit, width=30)
        sair_button.pack(pady=30)


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
        
        ttk.Label(left_frame, text="MENU DE AÇÕES", style="Header.TLabel", background=self.HEADER_BG).pack(pady=15, fill="x")
        
        actions_container = ttk.Frame(left_frame, style="Content.TFrame")
        actions_container.pack(expand=True, fill="both", pady=10)

        # Botões de Ação
        actions = [
            ("➕ ADICIONAR ALUNO", self.adicionar_aluno_gui),
            ("📝 ATRIBUIR NOTAS (DINÂMICO)", self.adicionar_notas_gui), # Nome em maiúsculo
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

        ttk.Label(list_frame, text="ALUNOS CADASTRADOS", style="Header.TLabel", background=self.HEADER_BG).pack(pady=10, fill="x")

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
        self.tree.delete(*self.tree.get_children())
        
        for aluno_id, info in self.alunos.items():
            self.tree.insert("", "end", values=(info['nome'], info['turma'], aluno_id))
            
    # --- CRUD Aluno (Mantido) ---

    def adicionar_aluno_gui(self):
        """Abre uma nova janela (Toplevel) para cadastrar um novo aluno."""
        top = tk.Toplevel(self.root)
        top.title("ENOTE: CADASTRO DE NOVO ALUNO")
        top.geometry("500x550")
        top.configure(bg=self.BG_MAIN) 
        top.transient(self.root)
        top.grab_set()

        campos = {
            "nome": "NOME COMPLETO",
            "matricula": "MATRÍCULA (opcional)",
            "data_nascimento": "DATA DE NASCIMENTO (opcional)",
            "turma": "TURMA/SÉRIE (obrigatório)",
            "contato": "TELEFONE/EMAIL (opcional)",
        }

        entradas = {}

        form_frame = ttk.Frame(top, padding=30, style="Content.TFrame") 
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Título do Formulário
        ttk.Label(form_frame, text="PREENCHA OS DADOS DO NOVO ALUNO", style="Header.TLabel", background=self.BG_CONTAINER).grid(row=0, columnspan=2, sticky='ew', pady=(0, 20))
        
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

            # Gera um ID mais curto e legível
            novo_id = str(uuid.uuid4()).split('-')[0].upper() 
            self.alunos[novo_id] = dados
            self.notas[novo_id] = []
            
            messagebox.showinfo("SUCESSO", f"Aluno '{dados['nome']}' cadastrado com sucesso!\n\nID DO ALUNO (ACESSO): {novo_id}", parent=top)
            
            self.atualizar_lista_alunos()
            top.destroy()

        ttk.Button(form_frame, text="✅ SALVAR ALUNO E GERAR ID", command=salvar).grid(row=row, columnspan=2, pady=20, padx=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

    def excluir_aluno_gui(self):
        """Exclui um aluno e suas notas após confirmação."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id: return

        aluno_nome = self.alunos[aluno_id]['nome']
        confirm = messagebox.askyesno("CONFIRMAR EXCLUSÃO",
                                      f"Tem certeza que deseja excluir o aluno '{aluno_nome}' e todas as suas notas?\n\nEsta ação é irreversível!")

        if confirm:
            del self.alunos[aluno_id]
            if aluno_id in self.notas:
                del self.notas[aluno_id]
            messagebox.showinfo("SUCESSO", f"Aluno '{aluno_nome}' foi excluído com sucesso.")
            self.atualizar_lista_alunos() 

    # --- Adicionar Notas Dinâmico (REFEITO PARA MELHOR USABILIDADE) ---

    def adicionar_notas_gui(self):
        """Abre uma nova janela para adicionar notas e pesos DINÂMICOS para um aluno, com UX aprimorada."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id: return

        aluno_nome = self.alunos[aluno_id]['nome']

        top = tk.Toplevel(self.root)
        top.title(f"ENOTE: ATRIBUIR NOTAS E PESOS (DINÂMICOS) - {aluno_nome}")
        top.geometry("750x700")
        top.configure(bg=self.BG_MAIN)
        top.transient(self.root)
        top.grab_set()

        form_frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(3, weight=1) # A Treeview deve expandir

        # 1. Disciplina e Aluno
        ttk.Label(form_frame, text=f"DISCIPLINA PARA: {aluno_nome}", style="Header.TLabel", background=self.HEADER_BG).grid(row=0, column=0, sticky='ew', pady=(0, 15))
        
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

        # Rótulos
        ttk.Label(input_frame, text="NOME (Ex: Prova):", background=self.BG_CONTAINER).grid(row=1, column=0, sticky="w", padx=5)
        ttk.Label(input_frame, text="NOTA (0-10):", background=self.BG_CONTAINER).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(input_frame, text="PESO (1-5):", background=self.BG_CONTAINER).grid(row=1, column=2, sticky="w", padx=5)

        # Entradas
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
            """Adiciona um componente válido à Treeview temporária."""
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

            # Adiciona ao Treeview (exibe nota formatada)
            tree_componentes.insert("", "end", values=(comp, self.formatar_numero(nota_val, 1), peso_val))
            
            # Limpa os campos de entrada e foca no nome
            componente_entry.delete(0, tk.END)
            nota_entry.delete(0, tk.END)
            peso_entry.delete(0, tk.END)
            peso_entry.insert(0, "1")
            componente_entry.focus_set()
            
        ttk.Button(input_frame, text="➕ ADICIONAR COMPONENTE", command=adicionar_componente, style="TButton").grid(row=2, column=3, sticky="ew", padx=5, pady=(0, 10), ipady=3)
        
        
        # 4. Botões de Controle e Submissão
        control_frame = ttk.Frame(form_frame, style="Content.TFrame")
        control_frame.grid(row=4, column=0, sticky="ew", pady=10)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        
        def remover_componente():
            """Remove o item selecionado da Treeview temporária."""
            selected = tree_componentes.selection()
            if selected:
                tree_componentes.delete(selected[0])
            else:
                messagebox.showwarning("AVISO", "Selecione um componente para remover.", parent=top)
                
        def limpar_componentes():
            """Remove todos os itens da Treeview temporária."""
            if tree_componentes.get_children():
                confirm = messagebox.askyesno("CONFIRMAR LIMPEZA", "Deseja remover TODOS os componentes adicionados?", parent=top)
                if confirm:
                    tree_componentes.delete(*tree_componentes.get_children())
            else:
                 messagebox.showinfo("AVISO", "Não há componentes para limpar.", parent=top)
        
        ttk.Button(control_frame, text="🗑️ REMOVER SELECIONADO", command=remover_componente).grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Button(control_frame, text="🧹 LIMPAR TUDO", command=limpar_componentes).grid(row=0, column=1, sticky="ew", padx=5)

        def submit():
            """Salva a disciplina e os componentes dinâmicos."""
            disciplina = disciplina_entry.get().strip().upper()
            if not disciplina:
                messagebox.showerror("ERRO DE NOTA", "O NOME DA DISCIPLINA é obrigatório.", parent=top)
                return
            
            if not tree_componentes.get_children():
                messagebox.showerror("ERRO DE NOTA", "Adicione pelo menos um componente de avaliação (Ex: Prova, Teste, Trabalho).", parent=top)
                return
            
            # Verifica se a disciplina já foi cadastrada
            for item in self.notas.get(aluno_id, []):
                if item['disciplina'] == disciplina:
                    messagebox.showwarning("AVISO", f"A disciplina '{disciplina}' já possui notas cadastradas.", parent=top)
                    return
            
            componentes_salvar = []
            for item_id in tree_componentes.get_children():
                comp_data = tree_componentes.item(item_id, 'values')
                # A nota é recuperada como string formatada (ex: "8,5"), precisamos converter de volta para float
                nota_float = float(comp_data[1].replace(',', '.')) 
                peso_int = int(comp_data[2])
                
                componentes_salvar.append({
                    "nome": comp_data[0],
                    "nota": nota_float,
                    "peso": peso_int
                })

            self.notas.setdefault(aluno_id, []).append({
                "disciplina": disciplina,
                "componentes": componentes_salvar 
            })
            messagebox.showinfo("SUCESSO", f"Notas de '{disciplina}' para '{aluno_nome}' adicionadas e ponderadas.", parent=top)
            top.destroy()
            
        ttk.Button(control_frame, text="✅ SALVAR DISCIPLINA E COMPONENTES", command=submit, style="TButton").grid(row=1, column=0, columnspan=3, sticky="ew", pady=(15, 5))


    # --- Métodos de Cálculo e Visualização (Mantidos, mas com novo tema) ---

    def calcular_media_por_disciplina(self, nota_item):
        """Calcula a média PONDERADA de um item de nota específico (agora dinâmico)."""
        if not nota_item or not nota_item.get('componentes'):
             return 0.0
        
        componentes = nota_item['componentes']
        
        soma_produtos = 0
        soma_pesos = 0
        
        for comp in componentes:
            soma_produtos += comp['nota'] * comp['peso']
            soma_pesos += comp['peso']

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
    
    def atualizar_detalhes_disciplina(self, event, tree_notas, aluno_id, detail_frame):
        """Atualiza o painel de detalhes quando uma disciplina é selecionada na Treeview."""
        selected_item = tree_notas.selection()
        if not selected_item:
            return

        # Pega a disciplina (primeira coluna) do item selecionado
        disciplina_selecionada = tree_notas.item(selected_item[0], 'values')[0]
        
        # Encontra o objeto de nota correspondente
        nota_item = next((item for item in self.notas[aluno_id] if item['disciplina'] == disciplina_selecionada), None)

        # Limpa o frame de detalhes
        for widget in detail_frame.winfo_children():
            widget.destroy()

        if nota_item:
            ttk.Label(detail_frame, text=f"COMPONENTES DE: {disciplina_selecionada}", style="Detail.TLabel").pack(anchor="w", pady=(0, 10))
            
            # Treeview para detalhes dos componentes
            cols = ('Componente', 'Nota', 'Peso')
            tree_detalhes = ttk.Treeview(detail_frame, columns=cols, show='headings', height=len(nota_item['componentes']))
            
            tree_detalhes.column('Componente', anchor='w', width=150)
            tree_detalhes.column('Nota', anchor='center', width=70)
            tree_detalhes.column('Peso', anchor='center', width=70)
            for col in cols: tree_detalhes.heading(col, text=col)
            
            for comp in nota_item['componentes']:
                tree_detalhes.insert("", "end", values=(
                    comp['nome'],
                    self.formatar_numero(comp['nota'], 1),
                    comp['peso']
                ))
            
            tree_detalhes.pack(expand=True, fill="both")
        
        else:
             ttk.Label(detail_frame, text="Detalhes indisponíveis.", style="Detail.TLabel").pack(padx=10, pady=10)

    def visualizar_notas_gui(self, aluno_id=None):
        """Abre uma janela para visualizar todas as notas, médias e detalhes dinâmicos de um aluno."""
        if not aluno_id:
            aluno_id = self.get_selected_aluno_id()
            if not aluno_id: return

        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
            messagebox.showinfo("INFORMAÇÃO", f"Nenhuma nota ponderada encontrada para {aluno_nome}.")
            return

        top = tk.Toplevel(self.root)
        top.title(f"ENOTE: HISTÓRICO DE NOTAS DE {aluno_nome}")
        top.geometry("1100x650") 
        top.configure(bg=self.BG_MAIN)
        top.transient(self.root)
        top.grab_set()

        main_frame = ttk.Frame(top, padding=15, style="Content.TFrame")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        main_frame.columnconfigure(0, weight=2) 
        main_frame.columnconfigure(1, weight=1) 
        main_frame.rowconfigure(1, weight=1)

        ttk.Label(main_frame, text=f"HISTÓRICO DE NOTAS (RESUMO) - {aluno_nome}", style="Header.TLabel", background=self.HEADER_BG).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # --- Frame da Esquerda: Tabela de Resumo ---
        summary_frame = ttk.Frame(main_frame, style="Content.TFrame")
        summary_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        cols = ('Disciplina', 'Média Ponderada', 'Status')
        tree_notas = ttk.Treeview(summary_frame, columns=cols, show='headings')
        
        tree_notas.column('Disciplina', anchor='w', width=200)
        tree_notas.column('Média Ponderada', anchor='center', width=150)
        tree_notas.column('Status', anchor='center', width=100)
        
        for col in cols: tree_notas.heading(col, text=col)
            
        vsb = ttk.Scrollbar(summary_frame, orient="vertical", command=tree_notas.yview)
        vsb.pack(side='right', fill='y')
        tree_notas.configure(yscrollcommand=vsb.set)
        tree_notas.pack(expand=True, fill="both")
        
        # --- Frame da Direita: Painel de Detalhes Dinâmico ---
        detail_container = ttk.Frame(main_frame, style="Detail.TFrame", padding=15)
        detail_container.grid(row=1, column=1, sticky="nsew", pady=(0, 10))
        detail_container.rowconfigure(1, weight=1)
        
        ttk.Label(detail_container, text="DETALHES DO COMPONENTE (CLIQUE EM UMA DISCIPLINA)", font=('Inter', 12, 'bold'), background='#252525', foreground=self.ACCENT_COLOR).pack(anchor="w", pady=(0, 10))
        
        detail_frame = ttk.Frame(detail_container, style="Detail.TFrame", padding=5) 
        detail_frame.pack(expand=True, fill="both")
        
        # Evento de seleção para atualizar o painel de detalhes
        tree_notas.bind('<<TreeviewSelect>>', partial(self.atualizar_detalhes_disciplina, tree_notas=tree_notas, aluno_id=aluno_id, detail_frame=detail_frame))

        # Preenche a Treeview de Resumo
        for nota_item in notas_aluno:
            media_disciplina = self.calcular_media_por_disciplina(nota_item)
            media_corte = 6.0
            status = "APROVADO" if media_disciplina >= media_corte else "REPROVADO"
            
            tag = "aprovado" if status == "APROVADO" else "reprovado"
            tree_notas.tag_configure("aprovado", foreground=self.SUCCESS_COLOR)
            tree_notas.tag_configure("reprovado", foreground=self.DANGER_COLOR)
            
            media_str = self.formatar_numero(media_disciplina, 2)

            tree_notas.insert("", "end", values=(
                nota_item['disciplina'],
                media_str,
                status
            ), tags=(tag,))
            
        # --- Frame de Ações (Rodapé) ---
        button_frame = ttk.Frame(main_frame, style="Content.TFrame")
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Botão de Exportar
        ttk.Button(button_frame, 
                   text="⬇️ EXPORTAR PARA DOWNLOAD/IMPRIMIR (CSV)", 
                   command=lambda: self.exportar_notas_csv(aluno_id),
                   style="TButton"
                   ).pack(side="left", padx=10, expand=True, fill="x")

        # Botão Fechar
        ttk.Button(button_frame, 
                   text="FECHAR", 
                   command=top.destroy,
                   style="TButton"
                   ).pack(side="right", padx=10, expand=True, fill="x")

    def exportar_notas_csv(self, aluno_id):
        """Exporta um relatório de resumo de notas (Disciplina, Média Ponderada, Status)."""
        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
            messagebox.showwarning("AVISO DE EXPORTAÇÃO", f"Não há notas para exportar para {aluno_nome}.")
            return

        # Cabeçalho do CSV (apenas resumo)
        header = ["DISCIPLINA", "MEDIA PONDERADA", "STATUS"]
        csv_content = [";".join(header)] 

        # Iterar sobre as notas
        for nota_item in notas_aluno:
            media_disciplina = self.calcular_media_por_disciplina(nota_item)
            media_corte = 6.0
            status = "APROVADO" if media_disciplina >= media_corte else "REPROVADO"
            
            row = [
                nota_item['disciplina'],
                self.formatar_numero(media_disciplina, 2), 
                status
            ]
            
            csv_content.append(";".join(row))

        full_csv_string = "\n".join(csv_content)

        # Diálogo de salvamento de arquivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"Relatorio_Notas_{aluno_nome.replace(' ', '_')}.csv",
            filetypes=[("Arquivo CSV", "*.csv"), ("Todos os Arquivos", "*.*")],
            title=f"SALVAR RELATÓRIO DE NOTAS DE {aluno_nome}"
        )

        if file_path:
            try:
                # Adiciona informações do aluno no topo para contexto
                context = [
                    f"--- RELATORIO DE NOTAS PONDERADAS - {aluno_nome} ---\n",
                    f"Turma: {self.alunos[aluno_id].get('turma', 'N/A')}\n\n",
                    full_csv_string
                ]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(context))
                messagebox.showinfo("SUCESSO", f"Relatório exportado com sucesso para:\n{file_path}")
            except Exception as e:
                messagebox.showerror("ERRO DE EXPORTAÇÃO", f"Não foi possível salvar o arquivo: {e}")

    # --- Métodos do Aluno (Atualizados para o novo tema) ---

    def show_aluno_menu(self):
        """Tela inicial para o aluno (login por ID)."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="80", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        center_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=50)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(center_frame, text="🔑 ÁREA DE ACESSO DO ALUNO", style="Header.TLabel", background=self.HEADER_BG).pack(pady=(0, 20), fill="x")
        ttk.Label(center_frame, text="INSIRA SEU ID ÚNICO PARA ACESSAR SUAS NOTAS:", background=self.BG_CONTAINER).pack(pady=10)

        id_entry = ttk.Entry(center_frame, width=30)
        id_entry.pack(pady=5, padx=10)

        def on_submit():
            aluno_id = id_entry.get().strip().upper()
            if aluno_id in self.alunos:
                self.show_aluno_dashboard(aluno_id)
            else:
                messagebox.showerror("ERRO DE ACESSO", "ID de aluno não encontrado. Verifique se o ID está correto.")

        submit_button = ttk.Button(center_frame, text="🔐 ACESSAR DASHBOARD", command=on_submit, width=30)
        submit_button.pack(pady=20)

        back_button = ttk.Button(center_frame, text="⬅️ VOLTAR AO MENU PRINCIPAL", command=self.show_main_menu)
        back_button.pack(pady=10)

    def show_aluno_dashboard(self, aluno_id):
        """Dashboard com as informações e notas do aluno logado."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="40", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        aluno_nome = self.alunos[aluno_id]['nome']

        ttk.Label(self.current_frame, text=f"BEM-VINDO(A), {aluno_nome.upper()}!", style="Title.TLabel", background=self.BG_MAIN).pack(pady=(0, 20))

        top_row_frame = ttk.Frame(self.current_frame, style="TFrame")
        top_row_frame.pack(pady=10, fill="x")
        top_row_frame.columnconfigure(0, weight=1)
        top_row_frame.columnconfigure(1, weight=1)

        # 1. Box de Informações Pessoais
        info_box = ttk.Frame(top_row_frame, style="Content.TFrame", padding=30)
        info_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ttk.Label(info_box, text="👤 DADOS PESSOAIS", font=('Inter', 12, 'bold'), background=self.BG_CONTAINER, foreground=self.ACCENT_COLOR).pack(anchor="w", pady=(0, 10))
        
        for key, label in [("turma", "TURMA"), ("matricula", "MATRÍCULA"), ("data_nascimento", "NASCIMENTO"), ("contato", "CONTATO")]:
            value = self.alunos[aluno_id].get(key, "NÃO INFORMADO")
            ttk.Label(info_box, text=f"• {label}: {value.upper()}", background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT).pack(anchor="w", padx=10)


        # 2. Box de Média Principal
        media_box = ttk.Frame(top_row_frame, style="Content.TFrame", padding=30)
        media_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        media_str = self.calcular_media_gui(aluno_id, show_message=False)
        try: media_float = float(media_str.replace(',', '.')) 
        except ValueError: media_float = 0.0
             
        status = "APROVADO" if media_float >= 6.0 else "REPROVADO"
        status_color = self.SUCCESS_COLOR if status == "APROVADO" else self.DANGER_COLOR

        ttk.Label(media_box, text="📈 MÉDIA GERAL PONDERADA", font=('Inter', 12, 'bold'), background=self.BG_CONTAINER, foreground=self.ACCENT_COLOR).pack(anchor="w")
        ttk.Label(media_box, text=media_str, font=('Inter', 48, 'bold'), foreground=self.TEXT_LIGHT, background=self.BG_CONTAINER).pack(anchor="center", pady=10)
        
        status_label = ttk.Label(media_box, text=f"STATUS FINAL: {status}", font=('Inter', 16, 'bold'), foreground=status_color, background=self.BG_CONTAINER)
        status_label.pack(anchor="center", pady=5)


        # Botão Ação Principal
        ttk.Button(self.current_frame, text="📊 VISUALIZAR DETALHES DAS NOTAS (COM PESOS)", 
                   command=lambda: self.visualizar_notas_gui(aluno_id)).pack(pady=25, fill="x", padx=50)
                   
        ttk.Button(self.current_frame, text="🚪 SAIR DO SISTEMA", 
                   command=self.show_main_menu).pack(side="bottom", pady=20)


if __name__ == "__main__":
    # Inicializa o Tkinter
    root = tk.Tk()
    
    # Cria e executa a aplicação
    app = GerenciadorNotasApp(root)
    root.mainloop()
