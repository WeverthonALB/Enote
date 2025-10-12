import uuid
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class GerenciadorNotasApp:
    """
    Classe principal para o aplicativo de gerenciamento de notas com interface gráfica (GUI).
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Notas Escolares")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", padding=6, relief="flat", background="#0078d7", foreground="white")
        self.style.map("TButton", background=[('active', '#005a9e')])
        self.style.configure("TLabel", padding=5, font=('Arial', 10))
        self.style.configure("Title.TLabel", font=('Arial', 16, 'bold'))
        self.style.configure("Header.TLabel", font=('Arial', 12, 'bold'))
        self.style.configure("TEntry", padding=5)
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Content.TFrame", background="white", borderwidth=1, relief="solid")

        # Dicionários para armazenar dados em memória
        self.alunos = {}
        self.notas = {}

        self.current_frame = None
        self.show_main_menu()

    def clear_frame(self):
        """Limpa o frame atual antes de desenhar um novo."""
        if self.current_frame:
            self.current_frame.destroy()

    def show_main_menu(self):
        """Exibe o menu principal para selecionar o papel (Professor ou Aluno)."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.pack(expand=True, fill="both")

        title_label = ttk.Label(self.current_frame, text="Gerenciador de Notas Escolares", style="Title.TLabel")
        title_label.pack(pady=20)

        subtitle_label = ttk.Label(self.current_frame, text="Selecione seu papel:")
        subtitle_label.pack(pady=10)

        professor_button = ttk.Button(self.current_frame, text="Professor", command=self.show_professor_menu, width=20)
        professor_button.pack(pady=10)

        aluno_button = ttk.Button(self.current_frame, text="Aluno", command=self.show_aluno_menu, width=20)
        aluno_button.pack(pady=10)

        sair_button = ttk.Button(self.current_frame, text="Sair", command=self.root.quit, width=20)
        sair_button.pack(pady=20)
    
    # --- Lógica do Professor ---
    def show_professor_menu(self):
        """Exibe o menu principal de ações do professor."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="10")
        self.current_frame.pack(expand=True, fill="both")
        
        # Layout principal com 2 colunas
        left_frame = ttk.Frame(self.current_frame, width=250)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)

        right_frame = ttk.Frame(self.current_frame)
        right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Coluna da Esquerda: Ações
        actions_frame = ttk.Frame(left_frame, style="Content.TFrame")
        actions_frame.pack(expand=True, fill="both")
        
        ttk.Label(actions_frame, text="Menu do Professor", style="Header.TLabel").pack(pady=10)
        
        ttk.Button(actions_frame, text="Adicionar Aluno", command=self.adicionar_aluno_gui).pack(pady=5, fill="x", padx=10)
        ttk.Button(actions_frame, text="Adicionar Notas", command=self.adicionar_notas_gui).pack(pady=5, fill="x", padx=10)
        ttk.Button(actions_frame, text="Visualizar Notas", command=self.visualizar_notas_gui).pack(pady=5, fill="x", padx=10)
        ttk.Button(actions_frame, text="Calcular Média", command=self.calcular_media_gui).pack(pady=5, fill="x", padx=10)
        ttk.Button(actions_frame, text="Excluir Aluno", command=self.excluir_aluno_gui).pack(pady=5, fill="x", padx=10)
        ttk.Button(actions_frame, text="Voltar", command=self.show_main_menu).pack(side="bottom", pady=20, fill="x", padx=10)

        # Coluna da Direita: Lista de Alunos
        list_frame = ttk.Frame(right_frame, style="Content.TFrame")
        list_frame.pack(expand=True, fill="both")

        ttk.Label(list_frame, text="Lista de Alunos", style="Header.TLabel").pack(pady=10)
        
        cols = ('Nome', 'ID')
        self.tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=50)
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        self.atualizar_lista_alunos()

    def atualizar_lista_alunos(self):
        """Atualiza a Treeview com a lista de alunos."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for aluno_id, info in self.alunos.items():
            self.tree.insert("", "end", values=(info['nome'], aluno_id))
            
    def adicionar_aluno_gui(self):
        """Cria um popup para adicionar um novo aluno."""
        nome = simpledialog.askstring("Adicionar Aluno", "Digite o nome do aluno:", parent=self.root)
        if nome:
            novo_id = str(uuid.uuid4())
            self.alunos[novo_id] = {"nome": nome}
            self.notas[novo_id] = []
            messagebox.showinfo("Sucesso", f"Aluno '{nome}' adicionado com sucesso.\nID: {novo_id}")
            self.atualizar_lista_alunos()
        elif nome is not None: # Se clicou OK com campo vazio
            messagebox.showerror("Erro", "O nome não pode ser vazio.")

    def get_selected_aluno_id(self):
        """Obtém o ID do aluno selecionado na lista."""
        try:
            selected_item = self.tree.selection()[0]
            aluno_id = self.tree.item(selected_item)['values'][1]
            return aluno_id
        except IndexError:
            messagebox.showwarning("Aviso", "Por favor, selecione um aluno na lista primeiro.")
            return None
    
    def adicionar_notas_gui(self):
        """Abre uma janela para adicionar notas a um aluno selecionado."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id:
            return

        aluno_nome = self.alunos[aluno_id]['nome']
        
        # Cria uma nova janela (Toplevel) para o formulário de notas
        top = tk.Toplevel(self.root)
        top.title(f"Adicionar Notas para {aluno_nome}")
        top.geometry("350x250")
        top.transient(self.root) # Mantém a janela no topo
        top.grab_set() # Modal

        form_frame = ttk.Frame(top, padding=20)
        form_frame.pack(expand=True, fill="both")

        ttk.Label(form_frame, text="Disciplina:").grid(row=0, column=0, sticky="w", pady=5)
        disciplina_entry = ttk.Entry(form_frame)
        disciplina_entry.grid(row=0, column=1, sticky="ew")
        
        ttk.Label(form_frame, text="Nota do Trabalho (0-10):").grid(row=1, column=0, sticky="w", pady=5)
        trabalho_entry = ttk.Entry(form_frame)
        trabalho_entry.grid(row=1, column=1, sticky="ew")

        ttk.Label(form_frame, text="Nota do Teste (0-10):").grid(row=2, column=0, sticky="w", pady=5)
        teste_entry = ttk.Entry(form_frame)
        teste_entry.grid(row=2, column=1, sticky="ew")

        ttk.Label(form_frame, text="Nota da Prova (0-10):").grid(row=3, column=0, sticky="w", pady=5)
        prova_entry = ttk.Entry(form_frame)
        prova_entry.grid(row=3, column=1, sticky="ew")

        def submit():
            try:
                disciplina = disciplina_entry.get()
                trabalho = float(trabalho_entry.get())
                teste = float(teste_entry.get())
                prova = float(prova_entry.get())

                if not disciplina:
                    messagebox.showerror("Erro", "O nome da disciplina não pode ser vazio.", parent=top)
                    return
                
                if not all(0 <= nota <= 10 for nota in [trabalho, teste, prova]):
                    messagebox.showerror("Erro", "As notas devem ser números entre 0 e 10.", parent=top)
                    return
                
                self.notas[aluno_id].append({
                    "disciplina": disciplina,
                    "notas": {"trabalho": trabalho, "teste": teste, "prova": prova}
                })
                messagebox.showinfo("Sucesso", f"Notas de '{disciplina}' adicionadas com sucesso!", parent=top)
                top.destroy()

            except ValueError:
                messagebox.showerror("Erro", "Entrada inválida. Por favor, digite números para as notas.", parent=top)
            except Exception as e:
                messagebox.showerror("Erro Inesperado", str(e), parent=top)

        submit_button = ttk.Button(form_frame, text="Adicionar", command=submit)
        submit_button.grid(row=4, columnspan=2, pady=20)
        
    def visualizar_notas_gui(self, aluno_id=None):
        """Mostra as notas de um aluno em uma nova janela."""
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
        top.title(f"Notas de {aluno_nome}")
        top.geometry("400x400")
        top.transient(self.root)
        top.grab_set()

        text_widget = tk.Text(top, wrap="word", font=("Courier New", 10), relief="sunken", borderwidth=1)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        
        report = f"--- Notas de {aluno_nome} ---\n\n"
        for nota_item in notas_aluno:
            media_disciplina = sum(nota_item['notas'].values()) / 3
            report += f"Disciplina: {nota_item['disciplina']}\n"
            report += f"  Trabalho: {nota_item['notas']['trabalho']:.2f}\n"
            report += f"  Teste:    {nota_item['notas']['teste']:.2f}\n"
            report += f"  Prova:    {nota_item['notas']['prova']:.2f}\n"
            report += f"  Média da Disciplina: {media_disciplina:.2f}\n"
            report += "--------------------------------------\n"
        
        text_widget.insert("1.0", report)
        text_widget.config(state="disabled") # Torna o texto somente leitura

    def calcular_media_gui(self, aluno_id=None, show_message=True):
        """Calcula a média geral de um aluno e exibe."""
        is_aluno_view = bool(aluno_id)
        if not aluno_id:
            aluno_id = self.get_selected_aluno_id()
            if not aluno_id:
                return

        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
            if show_message: messagebox.showerror("Erro", f"Nenhuma nota encontrada para {aluno_nome} para calcular a média.")
            return "N/A"
        
        total_soma = 0
        total_notas_count = 0
        for nota_item in notas_aluno:
            total_soma += sum(nota_item['notas'].values())
            total_notas_count += len(nota_item['notas'])
        
        media_final = total_soma / total_notas_count if total_notas_count > 0 else 0
        
        if show_message:
            messagebox.showinfo("Média Final", f"A média final de '{aluno_nome}' é: {media_final:.2f}")

        return f"{media_final:.2f}"

    def excluir_aluno_gui(self):
        """Exclui um aluno selecionado após confirmação."""
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id:
            return

        aluno_nome = self.alunos[aluno_id]['nome']
        confirm = messagebox.askyesno("Confirmar Exclusão", 
                                       f"Tem certeza que deseja excluir o aluno '{aluno_nome}' e todas as suas notas?\n\nEsta ação não pode ser desfeita.")
        
        if confirm:
            del self.alunos[aluno_id]
            if aluno_id in self.notas:
                del self.notas[aluno_id]
            
            messagebox.showinfo("Sucesso", f"Aluno '{aluno_nome}' foi excluído.")
            self.atualizar_lista_alunos()

    # --- Lógica do Aluno ---
    def show_aluno_menu(self):
        """Mostra o menu do aluno para inserir ID."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.pack(expand=True, fill="both")
        
        content_frame = ttk.Frame(self.current_frame)
        content_frame.pack(expand=True)

        ttk.Label(content_frame, text="Área do Aluno", style="Title.TLabel").pack(pady=20)
        ttk.Label(content_frame, text="Digite seu ID de aluno para continuar:").pack(pady=5)
        
        id_entry = ttk.Entry(content_frame, width=40)
        id_entry.pack(pady=5)
        
        def on_submit():
            aluno_id = id_entry.get().strip()
            if aluno_id in self.alunos:
                self.show_aluno_dashboard(aluno_id)
            else:
                messagebox.showerror("Erro", "ID de aluno não encontrado. Verifique o ID e tente novamente.")

        submit_button = ttk.Button(content_frame, text="Acessar", command=on_submit)
        submit_button.pack(pady=20)
        
        back_button = ttk.Button(self.current_frame, text="Voltar ao Menu Principal", command=self.show_main_menu)
        back_button.pack(side="bottom", pady=20)

    def show_aluno_dashboard(self, aluno_id):
        """Mostra o painel do aluno com suas notas e média."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.pack(expand=True, fill="both")
        
        aluno_nome = self.alunos[aluno_id]['nome']

        ttk.Label(self.current_frame, text=f"Bem-vindo(a), {aluno_nome}!", style="Title.TLabel").pack(pady=10)
        
        # Frame para botões e informações
        info_frame = ttk.Frame(self.current_frame)
        info_frame.pack(pady=20)
        
        media = self.calcular_media_gui(aluno_id, show_message=False)
        ttk.Label(info_frame, text=f"Sua Média Final: {media}", style="Header.TLabel").pack(pady=10)

        ttk.Button(info_frame, text="Visualizar Detalhes das Notas", command=lambda: self.visualizar_notas_gui(aluno_id)).pack(pady=10)

        ttk.Button(self.current_frame, text="Sair (Voltar ao menu)", command=self.show_main_menu).pack(side="bottom", pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorNotasApp(root)
    root.mainloop()