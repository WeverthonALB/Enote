import uuid
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ATENÇÃO: As bibliotecas 'requests' e 'Pillow' foram removidas, 
# tornando o código totalmente independente de instalações externas.

class GerenciadorNotasApp:
    """
    Aplicação eNote para gerenciamento de notas escolares usando Tkinter.
    Interface com design moderno Dark Mode.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("eNote - Sistema de Notas Inteligente")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # --- Esquema de Cores e Estilos Dark Mode (eNote Style) ---
        self.BG_MAIN = '#1f1f1f'        # Fundo principal (quase preto)
        self.BG_CONTAINER = '#2c2c2c'   # Fundo dos painéis e caixas (cinza escuro)
        self.TEXT_LIGHT = '#e0e0e0'     # Cor principal do texto (quase branco)
        self.ACCENT_COLOR = '#00b8e9'   # Cor de destaque (Ciano vibrante)
        self.DANGER_COLOR = '#F44336'   # Vermelho para reprovado/erro
        self.SUCCESS_COLOR = '#4CAF50'  # Verde para aprovado/sucesso
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuração do Fundo da Janela Principal
        self.root.configure(bg=self.BG_MAIN)
        
        # Estilos Gerais de Frames
        self.style.configure("TFrame", background=self.BG_MAIN)
        self.style.configure("Content.TFrame", background=self.BG_CONTAINER, borderwidth=1, relief="flat")

        # Estilos de Títulos e Headers
        self.style.configure("Title.TLabel", font=('Inter', 24, 'bold'), background=self.BG_MAIN, foreground=self.ACCENT_COLOR, padding=10)
        self.style.configure("Header.TLabel", font=('Inter', 14, 'bold'), background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT, padding=(10, 5))
        
        # Estilos de Botões (Flat e com Cor de Destaque)
        self.style.configure("TButton", 
            padding=10, 
            relief="flat", 
            background=self.ACCENT_COLOR, 
            foreground=self.BG_CONTAINER, # Texto escuro no botão claro para melhor contraste
            font=('Inter', 11, 'bold')
        )
        self.style.map("TButton", 
            background=[('active', '#0097c2')], # Tom mais escuro ao clicar
            foreground=[('active', self.BG_MAIN)]
        )

        # Estilos de Labels de Texto Simples
        self.style.configure("TLabel", padding=5, font=('Inter', 10), background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT)
        
        # Estilos para Entradas (Entry)
        self.style.configure("TEntry", fieldbackground='#3a3a3a', foreground=self.TEXT_LIGHT, borderwidth=0, relief="flat", padding=5)
        self.style.map("TEntry", fieldbackground=[('focus', '#444444')])

        # Estilo Treeview (Tabela de Dados)
        self.style.configure("Treeview", 
            background=self.BG_CONTAINER, 
            foreground=self.TEXT_LIGHT, 
            fieldbackground=self.BG_CONTAINER,
            rowheight=25,
            borderwidth=0
        )
        self.style.map("Treeview", background=[('selected', self.ACCENT_COLOR)])
        self.style.configure("Treeview.Heading", 
            font=('Inter', 10, 'bold'), 
            background='#444444', 
            foreground=self.TEXT_LIGHT,
            relief="flat"
        )
        
        # Dados armazenados em memória (Estrutura de dados original mantida)
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
        self.current_frame = ttk.Frame(self.root, padding="60", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")
        
        # Centralizar o conteúdo no Frame de Conteúdo Estilizado
        center_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=40)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Ícone/Marca (Representação textual "eNote")
        ttk.Label(center_frame, text="eNote", 
                  font=('Inter', 36, 'bold'), 
                  foreground=self.ACCENT_COLOR, 
                  background=self.BG_CONTAINER).pack(pady=(10, 5))

        # Título
        title_label = ttk.Label(center_frame, text="Sistema de Gestão Escolar", 
                                font=('Inter', 18), 
                                background=self.BG_CONTAINER, 
                                foreground=self.TEXT_LIGHT)
        title_label.pack(pady=(0, 30))

        subtitle_label = ttk.Label(center_frame, text="Selecione o Perfil:", background=self.BG_CONTAINER)
        subtitle_label.pack(pady=10)

        professor_button = ttk.Button(center_frame, text="🧑‍🏫 Professor/Administrador", command=self.show_professor_menu, width=30)
        professor_button.pack(pady=10)

        aluno_button = ttk.Button(center_frame, text="🎓 Aluno", command=self.show_aluno_menu, width=30)
        aluno_button.pack(pady=10)

        sair_button = ttk.Button(center_frame, text="❌ Sair", command=self.root.quit, width=30)
        sair_button.pack(pady=30)

    # --- Métodos do Professor ---

    def show_professor_menu(self):
        """Cria e exibe a tela de gestão do professor."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="10", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        # Configuração de Grid Layout (Left: Menu, Right: List)
        self.current_frame.columnconfigure(0, weight=0) 
        self.current_frame.columnconfigure(1, weight=1) 
        self.current_frame.rowconfigure(0, weight=1)

        # Frame da Esquerda: Ações
        left_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=20)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=10)

        ttk.Label(left_frame, text="Menu do Professor", style="Header.TLabel", background=self.BG_CONTAINER).pack(pady=10, fill="x")

        # Botões de Ação
        actions = [
            ("➕ Adicionar Aluno", self.adicionar_aluno_gui),
            ("📝 Adicionar Notas", self.adicionar_notas_gui),
            ("📈 Visualizar Notas", self.visualizar_notas_gui),
            ("🧮 Calcular Média Geral", self.calcular_media_gui),
            ("🗑️ Excluir Aluno", self.excluir_aluno_gui),
        ]

        for text, command in actions:
            ttk.Button(left_frame, text=text, command=command).pack(pady=8, fill="x", padx=10)
            
        # Botão Voltar (na parte inferior do frame esquerdo)
        ttk.Button(left_frame, text="⬅️ Voltar ao Menu Principal", command=self.show_main_menu).pack(side="bottom", pady=20, fill="x", padx=10)

        # Frame da Direita: Lista de Alunos (TreeView)
        list_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=20)
        list_frame.grid(row=0, column=1, sticky="nsew", pady=10, padx=(0, 10))

        ttk.Label(list_frame, text="Alunos Cadastrados", style="Header.TLabel", background=self.BG_CONTAINER).pack(pady=10, fill="x")

        # Treeview (Tabela)
        cols = ('Nome', 'ID Único')
        self.tree = ttk.Treeview(list_frame, columns=cols, show='headings')
        self.tree.column('Nome', anchor='w', width=200)
        self.tree.column('ID Único', anchor='center', width=150)
        
        for col in cols:
            self.tree.heading(col, text=col)

        # Adiciona Scrollbar
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(expand=True, fill="both")
        self.atualizar_lista_alunos()

    def atualizar_lista_alunos(self):
        """Limpa e preenche a Treeview com os dados dos alunos."""
        self.tree.delete(*self.tree.get_children())
        
        for aluno_id, info in self.alunos.items():
            self.tree.insert("", "end", values=(info['nome'], aluno_id))

    def adicionar_aluno_gui(self):
        """Abre uma nova janela (Toplevel) para cadastrar um novo aluno."""
        top = tk.Toplevel(self.root)
        top.title("eNote: Cadastro de Novo Aluno")
        top.geometry("450x450")
        top.configure(bg=self.BG_CONTAINER) # Fundo da janela modal
        top.transient(self.root)
        top.grab_set()

        campos = {
            "nome": "Nome Completo",
            "matricula": "Matrícula",
            "data_nascimento": "Data de Nascimento (dd/mm/aaaa)",
            "turma": "Turma/Série",
            "contato": "Telefone/Email",
        }

        entradas = {}

        form_frame = ttk.Frame(top, padding=20, style="Content.TFrame") # Usando BG_CONTAINER
        form_frame.pack(expand=True, fill="both")

        row = 0
        for chave, label in campos.items():
            # Labels com cor de fundo do container
            ttk.Label(form_frame, text=label + ":", font=('Inter', 10, 'bold'), background=self.BG_CONTAINER).grid(row=row, column=0, sticky="w", pady=5, padx=5)
            entry = ttk.Entry(form_frame, width=45)
            entry.grid(row=row, column=1, pady=5, padx=5, sticky="ew")
            entradas[chave] = entry
            row += 1
            
        ttk.Separator(form_frame, orient='horizontal').grid(row=row, columnspan=2, sticky='ew', pady=10)
        row += 1

        def salvar():
            """Função interna para salvar os dados do novo aluno."""
            dados = {chave: entrada.get().strip() for chave, entrada in entradas.items()}
            
            if not dados.get('nome') or not dados.get('turma'):
                messagebox.showerror("Erro de Cadastro", "Os campos 'Nome Completo' e 'Turma/Série' são obrigatórios.", parent=top)
                return

            # Geração de ID único
            novo_id = str(uuid.uuid4())
            self.alunos[novo_id] = dados
            self.notas[novo_id] = []
            
            messagebox.showinfo("Sucesso", f"Aluno '{dados['nome']}' cadastrado com sucesso!\n\nID do Aluno (Guardar): {novo_id}", parent=top)
            
            self.atualizar_lista_alunos()
            top.destroy()

        ttk.Button(form_frame, text="✅ Salvar Aluno", command=salvar).grid(row=row, columnspan=2, pady=20, padx=5, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

    def get_selected_aluno_id(self):
        """Retorna o ID do aluno selecionado na Treeview ou exibe um aviso."""
        try:
            selected_item = self.tree.selection()[0]
            aluno_id = self.tree.item(selected_item)['values'][1]
            return aluno_id
        except IndexError:
            messagebox.showwarning("Aviso", "Por favor, selecione um aluno na lista primeiro para realizar esta ação.")
            return None

    def adicionar_notas_gui(self):
        """Abre uma nova janela para adicionar notas a um aluno selecionado."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id:
            return

        aluno_nome = self.alunos[aluno_id]['nome']

        top = tk.Toplevel(self.root)
        top.title(f"eNote: Adicionar Notas para {aluno_nome}")
        top.geometry("380x350")
        top.configure(bg=self.BG_CONTAINER)
        top.transient(self.root)
        top.grab_set()

        form_frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        form_frame.pack(expand=True, fill="both")
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Disciplina:", font=('Inter', 10, 'bold'), background=self.BG_CONTAINER).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        disciplina_entry = ttk.Entry(form_frame)
        disciplina_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Nota do Trabalho (0-10):", background=self.BG_CONTAINER).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        trabalho_entry = ttk.Entry(form_frame)
        trabalho_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Nota do Teste (0-10):", background=self.BG_CONTAINER).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        teste_entry = ttk.Entry(form_frame)
        teste_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Nota da Prova (0-10):", background=self.BG_CONTAINER).grid(row=3, column=0, sticky="w", pady=5, padx=5)
        prova_entry = ttk.Entry(form_frame)
        prova_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

        def submit():
            """Função interna para validar e salvar as notas."""
            try:
                disciplina = disciplina_entry.get().strip()
                # Aceita vírgula ou ponto como separador decimal
                trabalho = float(trabalho_entry.get().replace(',', '.'))
                teste = float(teste_entry.get().replace(',', '.'))
                prova = float(prova_entry.get().replace(',', '.'))

                if not disciplina:
                    messagebox.showerror("Erro de Nota", "O nome da disciplina não pode ser vazio.", parent=top)
                    return

                if not all(0 <= nota <= 10 for nota in [trabalho, teste, prova]):
                    messagebox.showerror("Erro de Nota", "As notas devem ser valores entre 0 e 10.", parent=top)
                    return

                # Verifica se a disciplina já foi cadastrada para este aluno
                for item in self.notas[aluno_id]:
                    if item['disciplina'].lower() == disciplina.lower():
                        messagebox.showwarning("Aviso", f"A disciplina '{disciplina}' já possui notas cadastradas. Por favor, exclua a anterior para registrar novas notas.", parent=top)
                        return

                self.notas[aluno_id].append({
                    "disciplina": disciplina,
                    "notas": {"trabalho": trabalho, "teste": teste, "prova": prova}
                })
                messagebox.showinfo("Sucesso", f"Notas de '{disciplina}' para '{aluno_nome}' adicionadas.", parent=top)
                top.destroy()

            except ValueError:
                messagebox.showerror("Erro de Entrada", "As notas devem ser números válidos (ex: 7.5 ou 8).", parent=top)
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {str(e)}", parent=top)

        submit_button = ttk.Button(form_frame, text="✅ Adicionar Notas", command=submit)
        submit_button.grid(row=4, columnspan=2, pady=30, padx=5, sticky="ew")

    def calcular_media_por_disciplina(self, nota_item):
        """Calcula a média de um item de nota específico (trabalho, teste, prova)."""
        if not nota_item or not nota_item.get('notas'):
             return 0.0
        
        notas = nota_item['notas']
        media = sum(notas.values()) / len(notas)
        return media

    def visualizar_notas_gui(self, aluno_id=None):
        """Abre uma janela para visualizar todas as notas e médias de um aluno."""
        if not aluno_id:
            aluno_id = self.get_selected_aluno_id()
            if not aluno_id:
                return

        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
            messagebox.showinfo("Informação", f"Nenhuma nota encontrada para {aluno_nome}.")
            return

        top = tk.Toplevel(self.root)
        top.title(f"eNote: Histórico de Notas de {aluno_nome}")
        top.geometry("600x450")
        top.configure(bg=self.BG_CONTAINER)
        top.transient(self.root)
        top.grab_set()

        list_frame = ttk.Frame(top, padding=10, style="Content.TFrame")
        list_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Treeview para exibir a tabela de notas
        cols = ('Disciplina', 'Trabalho', 'Teste', 'Prova', 'Média', 'Status')
        tree_notas = ttk.Treeview(list_frame, columns=cols, show='headings')
        
        tree_notas.column('Disciplina', anchor='w', width=120)
        tree_notas.column('Trabalho', anchor='center', width=70)
        tree_notas.column('Teste', anchor='center', width=70)
        tree_notas.column('Prova', anchor='center', width=70)
        tree_notas.column('Média', anchor='center', width=70)
        tree_notas.column('Status', anchor='center', width=80)
        
        for col in cols:
            tree_notas.heading(col, text=col)
            
        # Adiciona Scrollbar
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=tree_notas.yview)
        vsb.pack(side='right', fill='y')
        tree_notas.configure(yscrollcommand=vsb.set)
        tree_notas.pack(expand=True, fill="both")
        
        # Preenche a Treeview
        for i, nota_item in enumerate(notas_aluno):
            media_disciplina = self.calcular_media_por_disciplina(nota_item)
            media_corte = 6.0
            status = "APROVADO" if media_disciplina >= media_corte else "REPROVADO"
            
            # Aplica tags de cor na linha
            tag = "aprovado" if status == "APROVADO" else "reprovado"
            tree_notas.tag_configure("aprovado", foreground=self.SUCCESS_COLOR)
            tree_notas.tag_configure("reprovado", foreground=self.DANGER_COLOR)
            
            # Formatação para exibir com vírgula como separador decimal
            trabalho = f"{nota_item['notas']['trabalho']:.2f}".replace('.', ',')
            teste = f"{nota_item['notas']['teste']:.2f}".replace('.', ',')
            prova = f"{nota_item['notas']['prova']:.2f}".replace('.', ',')
            media_str = f"{media_disciplina:.2f}".replace('.', ',')

            tree_notas.insert("", "end", values=(
                nota_item['disciplina'],
                trabalho,
                teste,
                prova,
                media_str,
                status
            ), tags=(tag,))

    def calcular_media_gui(self, aluno_id=None, show_message=True):
        """Calcula a média geral de todas as disciplinas do aluno."""
        if not aluno_id:
            aluno_id = self.get_selected_aluno_id()
            if not aluno_id:
                return "0.00"

        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
            if show_message:
                messagebox.showerror("Erro de Cálculo", f"Nenhuma nota foi registrada para '{aluno_nome}'.")
            return "0.00"

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
                                f"A média geral de '{aluno_nome}' é: {media_str}\n\nStatus Final: {status} {emoji}")

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
        self.current_frame = ttk.Frame(self.root, padding="60", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        center_frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=30)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(center_frame, text="Área do Aluno", style="Header.TLabel", background=self.BG_CONTAINER).pack(pady=(5, 20))
        ttk.Label(center_frame, text="Digite seu ID de aluno:", background=self.BG_CONTAINER).pack(pady=5)

        id_entry = ttk.Entry(center_frame, width=40)
        id_entry.pack(pady=5, padx=10)

        def on_submit():
            aluno_id = id_entry.get().strip()
            if aluno_id in self.alunos:
                self.show_aluno_dashboard(aluno_id)
            else:
                messagebox.showerror("Erro de Acesso", "ID de aluno não encontrado. Verifique com a secretaria/professor.")

        submit_button = ttk.Button(center_frame, text="🔑 Acessar Dashboard", command=on_submit, width=25)
        submit_button.pack(pady=20)

        back_button = ttk.Button(center_frame, text="⬅️ Voltar ao Menu Principal", command=self.show_main_menu)
        back_button.pack(pady=10)

    def show_aluno_dashboard(self, aluno_id):
        """Dashboard com as informações e notas do aluno logado."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="40", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        aluno_nome = self.alunos[aluno_id]['nome']

        ttk.Label(self.current_frame, text=f"Dashboard de: {aluno_nome}", style="Title.TLabel", background=self.BG_MAIN).pack(pady=(0, 20))

        # Box de Informações
        info_box = ttk.Frame(self.current_frame, style="Content.TFrame", padding=20)
        info_box.pack(pady=20, padx=10, fill="x")

        # Média e Status
        media_str = self.calcular_media_gui(aluno_id, show_message=False)
        # Média em float para a lógica de aprovação
        media_float = float(media_str.replace(',', '.')) 
        status = "APROVADO" if media_float >= 6.0 else "REPROVADO"
        status_color = self.SUCCESS_COLOR if status == "APROVADO" else self.DANGER_COLOR
        
        ttk.Label(info_box, text=f"Média Geral Atual:", style="Header.TLabel", background=self.BG_CONTAINER).pack(anchor="w")
        ttk.Label(info_box, text=media_str, font=('Inter', 20, 'bold'), foreground=self.ACCENT_COLOR, background=self.BG_CONTAINER).pack(anchor="w", padx=10)
        
        ttk.Label(info_box, text=f"Status: {status}", font=('Inter', 12, 'bold'), foreground=status_color, background=self.BG_CONTAINER).pack(anchor="w", pady=(5, 15))
        
        # Detalhes do Aluno
        ttk.Label(info_box, text="Detalhes Pessoais:", font=('Inter', 11, 'underline'), background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT).pack(anchor="w", pady=(10, 5))
        for key, label in [("turma", "Turma"), ("matricula", "Matrícula"), ("contato", "Contato")]:
            value = self.alunos[aluno_id].get(key, "Não Informado")
            ttk.Label(info_box, text=f"{label}: {value}", background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT).pack(anchor="w", padx=10)

        # Ações
        ttk.Button(self.current_frame, text="📈 Visualizar Histórico de Notas", 
                   command=lambda: self.visualizar_notas_gui(aluno_id)).pack(pady=15, fill="x", padx=100)
                   
        ttk.Button(self.current_frame, text="🚪 Sair do Sistema", 
                   command=self.show_main_menu).pack(side="bottom", pady=20)


if __name__ == "__main__":
    # Inicializa o Tkinter
    root = tk.Tk()
    
    # Cria e executa a aplicação
    app = GerenciadorNotasApp(root)
    root.mainloop()
