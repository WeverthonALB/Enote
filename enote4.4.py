import uuid
import json
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from functools import partial
import webbrowser
import os

class GerenciadorNotasApp:
    """
    ENOTE - Sistema de Notas Escolares (sem pesos, com componentes padrão)
    """
    def __init__(self, root):
        self.root = root
        self.root.title("ENOTE - SISTEMA DE NOTAS ESCOLARES (SEM PESO)")
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

        self.alunos = {}
        self.notas = {}
        self.prof_password = None
        self.carregar_dados()
        self.carregar_config()

        # --- Tema Dark ---
        self.BG_MAIN = '#0a0a0a'
        self.BG_CONTAINER = '#1e1e1e'
        self.TEXT_LIGHT = '#f0f0f0'
        self.ACCENT_COLOR = '#4A90E2'
        self.DANGER_COLOR = '#E74C3C' # Vermelho para perigo/remoção
        self.SUCCESS_COLOR = '#2ECC71'
        self.HEADER_BG = '#282828'
        self.DETAIL_BG = '#252525'

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.root.configure(bg=self.BG_MAIN)

        # Estilos
        self.style.configure("TFrame", background=self.BG_MAIN)
        self.style.configure("Content.TFrame", background=self.BG_CONTAINER)
        self.style.configure("Header.TLabel", font=('Inter', 18, 'bold'),
                             background=self.HEADER_BG, foreground=self.TEXT_LIGHT)
        self.style.configure("TLabel", background=self.BG_CONTAINER, foreground=self.TEXT_LIGHT)
        self.style.configure("TButton", font=('Inter', 11, 'bold'),
                             background=self.ACCENT_COLOR, foreground="white")
        self.style.map("TButton",
                       background=[('active', '#5aa0f2'), ('pressed', '#3a80d2')])
        
        # Estilo para Treeview
        self.style.configure("Treeview", background=self.DETAIL_BG, 
                             foreground=self.TEXT_LIGHT, fieldbackground=self.DETAIL_BG, 
                             rowheight=25)
        self.style.configure("Treeview.Heading", font=('Inter', 10, 'bold'), 
                             background=self.HEADER_BG, foreground=self.TEXT_LIGHT)
        
        # NOVO: Estilo para botão de Remover/Perigo
        self.style.configure("Danger.TButton", background=self.DANGER_COLOR, foreground="white")
        self.style.map("Danger.TButton",
                       background=[('active', '#e85a4a'), ('pressed', '#c0392b')])
        
        # NOVO: Estilo para botão de Sucesso/Salvar
        self.style.configure("Success.TButton", background=self.SUCCESS_COLOR, foreground="white")
        self.style.map("Success.TButton",
                       background=[('active', '#3c9e5b'), ('pressed', '#1e8449')])


        self.current_frame = None
        self.show_main_menu()

    # ======================================================
    # BANCO DE DADOS
    # ======================================================
    def criar_tabelas(self):
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
            pk_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            aluno_id TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            componentes TEXT NOT NULL,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
        """)
        self.conexao.commit()

    def carregar_config(self):
        self.cursor.execute("SELECT valor FROM config WHERE chave = 'prof_password'")
        row = self.cursor.fetchone()
        if row and row[0]:
            self.prof_password = row[0]
        else:
            self.prof_password = "ADMIN"
            self.cursor.execute("INSERT OR REPLACE INTO config VALUES (?, ?)",
                                 ('prof_password', self.prof_password))
            self.conexao.commit()

    def salvar_senha_professor(self, nova):
        self.prof_password = nova
        self.cursor.execute("INSERT OR REPLACE INTO config VALUES (?, ?)",
                            ('prof_password', nova))
        self.conexao.commit()

    def carregar_dados(self):
        self.alunos.clear()
        self.notas.clear()

        self.cursor.execute("SELECT * FROM alunos")
        for row in self.cursor.fetchall():
            aluno_id, nome, matricula, nasc, turma, contato = row
            self.alunos[aluno_id] = {
                "nome": nome, "matricula": matricula,
                "data_nascimento": nasc, "turma": turma, "contato": contato
            }

        self.cursor.execute("SELECT pk_id, aluno_id, disciplina, componentes FROM notas")
        for pk_id, aluno_id, disciplina, comp_json in self.cursor.fetchall():
            comps = json.loads(comp_json)
            self.notas.setdefault(aluno_id, []).append(
                {"pk_id": pk_id, "disciplina": disciplina, "componentes": comps}
            )

    # ======================================================
    # INTERFACE
    # ======================================================
    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def formatar_numero(self, numero, casas=2):
        return f"{numero:.{casas}f}".replace('.', ',')

    def show_main_menu(self):
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding="80", style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        frame = ttk.Frame(self.current_frame, style="Content.TFrame", padding=60)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(frame, text="📄 ENOTE", font=('Inter', 42, 'bold'),
                  foreground=self.ACCENT_COLOR, background=self.BG_CONTAINER).pack(pady=20)

        ttk.Button(frame, text="🧑‍🏫 PROFESSOR", command=self.request_professor_password).pack(pady=10, fill='x')
        ttk.Button(frame, text="🎓 ALUNO", command=self.show_aluno_menu).pack(pady=10, fill='x')
        ttk.Button(frame, text="❌ SAIR", command=self.root.quit).pack(pady=20, fill='x')

    # ======================================================
    # LOGIN PROFESSOR
    # ======================================================
    def request_professor_password(self):
        senha = simpledialog.askstring("Senha de Professor", "Digite a senha do professor:", show='*', parent=self.root)
        if senha == self.prof_password:
            self.show_professor_menu()
        elif senha is not None:
            messagebox.showerror("Erro", "Senha incorreta.")

    # ======================================================
    # MENU PROFESSOR
    # ======================================================
    def show_professor_menu(self):
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding=20, style="TFrame")
        self.current_frame.pack(expand=True, fill="both")

        left = ttk.Frame(self.current_frame, style="Content.TFrame", padding=20)
        left.pack(side="left", fill="y")

        ttk.Label(left, text="MENU DE AÇÕES", style="Header.TLabel").pack(pady=10, fill='x')

        ttk.Button(left, text="➕ Adicionar Aluno", command=self.adicionar_aluno_gui).pack(pady=10, fill='x')
        ttk.Button(left, text="📝 Atribuir Notas", command=self.adicionar_notas_gui).pack(pady=10, fill='x')
        ttk.Button(left, text="✏️ Editar Notas", command=self.editar_notas_gui).pack(pady=10, fill='x') 
        ttk.Button(left, text="📈 Visualizar Notas", command=self.visualizar_notas_gui).pack(pady=10, fill='x')
        ttk.Button(left, text="🧮 Calcular Média", command=self.calcular_media_gui).pack(pady=10, fill='x')
        ttk.Button(left, text="🔑 Alterar Senha", command=self.alterar_senha_gui).pack(pady=10, fill='x')
        ttk.Button(left, text="⬅️ Voltar", command=self.show_main_menu).pack(pady=30, fill='x')

        self.tree = ttk.Treeview(self.current_frame, columns=('Nome', 'Turma', 'ID'), show='headings')
        self.tree.heading('Nome', text='Nome')
        self.tree.heading('Turma', text='Turma')
        self.tree.heading('ID', text='ID do Aluno')
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)
        self.atualizar_lista_alunos()

    def alterar_senha_gui(self):
        atual = simpledialog.askstring("Senha Atual", "Digite a senha atual:", show='*', parent=self.root)
        if atual != self.prof_password:
            messagebox.showerror("Erro", "Senha atual incorreta.")
            return
        nova = simpledialog.askstring("Nova Senha", "Digite a nova senha:", show='*', parent=self.root)
        if nova:
            self.salvar_senha_professor(nova)
            messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")

    def get_selected_aluno_id(self):
        try:
            sel = self.tree.selection()[0]
            return self.tree.item(sel)['values'][2]
        except IndexError:
            messagebox.showwarning("Atenção", "Selecione um aluno primeiro.")
            return None

    def atualizar_lista_alunos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for a_id, info in self.alunos.items():
            self.tree.insert("", "end", values=(info['nome'], info['turma'], a_id))

    # ======================================================
    # ADICIONAR ALUNO
    # ======================================================
    def adicionar_aluno_gui(self):
        top = tk.Toplevel(self.root)
        top.title("Cadastrar Aluno")
        top.geometry("400x400")
        frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        frame.pack(expand=True, fill="both")

        campos = {
            "nome": "Nome",
            "matricula": "Matrícula (opcional)",
            "data_nascimento": "Data de Nascimento (opcional)",
            "turma": "Turma/Série",
            "contato": "Contato (opcional)"
        }
        entradas = {}
        for i, (chave, label) in enumerate(campos.items()):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', pady=5)
            ent = ttk.Entry(frame, width=30)
            ent.grid(row=i, column=1, pady=5)
            entradas[chave] = ent

        def salvar():
            dados = {k: e.get().strip() for k, e in entradas.items()}
            if not dados['nome'] or not dados['turma']:
                messagebox.showerror("Erro", "Nome e Turma são obrigatórios.")
                return
            novo_id = str(uuid.uuid4())[:8].upper()
            self.cursor.execute("INSERT INTO alunos VALUES (?, ?, ?, ?, ?, ?)",
                                 (novo_id, dados['nome'], dados['matricula'],
                                  dados['data_nascimento'], dados['turma'], dados['contato']))
            self.conexao.commit()
            self.alunos[novo_id] = dados
            self.atualizar_lista_alunos()
            messagebox.showinfo("Sucesso", f"Aluno {dados['nome']} cadastrado!\nID: {novo_id}")
            top.destroy()

        ttk.Button(frame, text="Salvar", command=salvar).grid(columnspan=2, pady=20)

    # ======================================================
    # ADICIONAR NOTAS (SEM PESO + PADRÃO)
    # ======================================================
    def adicionar_notas_gui(self):
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id: return
        aluno_nome = self.alunos[aluno_id]['nome']

        top = tk.Toplevel(self.root)
        top.title(f"Notas de {aluno_nome}")
        top.geometry("700x600")

        frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text=f"Disciplina:", background=self.BG_CONTAINER).pack(pady=5)
        disciplina_entry = ttk.Entry(frame, width=40)
        disciplina_entry.pack(pady=5)

        cols = ('Componente', 'Nota')
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols: tree.heading(col, text=col)
        tree.pack(expand=True, fill='both', pady=10)

        # --- Componentes padrão automáticos ---
        componentes_padrao = ["Trabalho 1", "Trabalho 2", "Teste", "Prova"]
        for nome in componentes_padrao:
            tree.insert("", "end", values=(nome, "0,0"))

        ttk.Label(frame, text="Selecione um componente e digite a nova nota (0-10):").pack(pady=5)
        nota_entry = ttk.Entry(frame, width=10)
        nota_entry.pack(pady=5)

        def atualizar_nota():
            try:
                sel = tree.selection()[0]
            except IndexError:
                messagebox.showwarning("Aviso", "Selecione um componente.")
                return
            try:
                nova_nota = float(nota_entry.get().replace(',', '.')) 
                if not (0 <= nova_nota <= 10): raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Nota inválida (deve ser um número entre 0 e 10).")
                return
            nome = tree.item(sel)['values'][0]
            tree.item(sel, values=(nome, self.formatar_numero(nova_nota, 1))) 
            nota_entry.delete(0, tk.END)

        ttk.Button(frame, text="Atualizar Nota", command=atualizar_nota).pack(pady=5)

        def salvar():
            disc = disciplina_entry.get().strip().upper()
            if not disc:
                messagebox.showerror("Erro", "Disciplina obrigatória.")
                return
            comps = []
            for item in tree.get_children():
                nome, nota = tree.item(item)['values']
                comps.append({"nome": nome, "nota": float(str(nota).replace(',', '.'))}) 

            comp_json = json.dumps(comps)
            self.cursor.execute("INSERT INTO notas (aluno_id, disciplina, componentes) VALUES (?, ?, ?)",
                                 (aluno_id, disc, comp_json))
            pk_id = self.cursor.lastrowid
            self.conexao.commit()
            self.notas.setdefault(aluno_id, []).append({"pk_id": pk_id, "disciplina": disc, "componentes": comps}) 
            messagebox.showinfo("Sucesso", f"Notas de {disc} salvas!")
            top.destroy()

    # ======================================================
    # EDITAR NOTAS
    # ======================================================
    def editar_notas_gui(self):
        """ Mostra as disciplinas do aluno selecionado para edição. """
        aluno_id = self.get_selected_aluno_id()
        if not aluno_id: return
        aluno_nome = self.alunos[aluno_id]['nome']
        self.carregar_dados() # Recarrega para ter certeza de ter os dados mais recentes
        notas_aluno = self.notas.get(aluno_id, [])

        if not notas_aluno:
             messagebox.showinfo("Aviso", f"{aluno_nome} não tem notas cadastradas para edição.")
             return

        top = tk.Toplevel(self.root)
        top.title(f"Editar Notas - {aluno_nome}")
        top.geometry("500x400")
        
        frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text=f"Selecione a Disciplina para Editar:", style="Header.TLabel").pack(pady=10, fill='x')

        cols = ('Disciplina', 'Média')
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols: tree.heading(col, text=col)
        tree.pack(expand=True, fill='both', pady=10)

        tree_map = {} 
        for item in notas_aluno:
            media = self.calcular_media_por_disciplina(item)
            media_str = self.formatar_numero(media)
            tree_id = tree.insert("", "end", values=(item['disciplina'], media_str))
            tree_map[tree_id] = item 
            

        def abrir_edicao():
            try:
                sel = tree.selection()[0]
                disciplina_item = tree_map[sel]
            except IndexError:
                messagebox.showwarning("Aviso", "Selecione uma disciplina.")
                return
            
            self.editar_notas_disciplina_top_level(aluno_id, disciplina_item, top)

        ttk.Button(frame, text="Abrir Edição de Componentes", command=abrir_edicao).pack(pady=10)
        ttk.Button(frame, text="Fechar", command=top.destroy).pack(pady=10)
        
    def editar_notas_disciplina_top_level(self, aluno_id, disciplina_item, parent_window):
        """ Abre a interface para editar os componentes de nota de uma disciplina. """
        
        pk_id = disciplina_item['pk_id']
        disciplina = disciplina_item['disciplina']
        aluno_nome = self.alunos[aluno_id]['nome']
        
        top = tk.Toplevel(self.root)
        top.title(f"Editar Notas e Componentes de {disciplina} - {aluno_nome}")
        top.geometry("800x650")

        frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text=f"Editando: **{disciplina}**", 
                  style="Header.TLabel", foreground=self.ACCENT_COLOR).pack(pady=10, fill='x')

        cols = ('Componente', 'Nota')
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols: tree.heading(col, text=col)
        tree.pack(expand=True, fill='both', pady=10)
        
        # Preenche com as notas atuais
        for comp in disciplina_item['componentes']:
            tree.insert("", "end", values=(comp['nome'], self.formatar_numero(comp['nota'], 1)))


        # --- Seção para Edição e Atualização de Notas ---
        update_frame = ttk.Frame(frame, style="Content.TFrame")
        update_frame.pack(fill='x', pady=5)
        
        ttk.Label(update_frame, text="Selecione e mude a nota (0-10):").pack(side="left", padx=5)
        nota_entry = ttk.Entry(update_frame, width=10)
        nota_entry.pack(side="left", padx=5)

        def atualizar_nota():
            try:
                sel = tree.selection()[0]
            except IndexError:
                messagebox.showwarning("Aviso", "Selecione um componente.")
                return
            try:
                nova_nota = float(nota_entry.get().replace(',', '.'))
                if not (0 <= nova_nota <= 10): raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Nota inválida (deve ser um número entre 0 e 10).")
                return
            nome = tree.item(sel)['values'][0]
            tree.item(sel, values=(nome, self.formatar_numero(nova_nota, 1)))
            nota_entry.delete(0, tk.END)

        ttk.Button(update_frame, text="Atualizar Nota", command=atualizar_nota).pack(side="left", padx=10)
        
        # --- Seção para Adicionar/Remover Componentes (Corrigida) ---
        comp_frame = ttk.Frame(frame, style="Content.TFrame")
        comp_frame.pack(fill='x', pady=15)
        
        ttk.Label(comp_frame, text="Nome do Novo Componente:").pack(side="left", padx=5)
        novo_comp_entry = ttk.Entry(comp_frame, width=25)
        novo_comp_entry.pack(side="left", padx=5)
        
        def adicionar_componente():
            novo_nome = novo_comp_entry.get().strip()
            if not novo_nome:
                messagebox.showwarning("Aviso", "Digite um nome para o componente.")
                return
            
            # --- Melhoria: Verifica se já existe um componente (Case-insensitive) ---
            componentes_existentes = [tree.item(item)['values'][0].lower() for item in tree.get_children()]
            if novo_nome.lower() in componentes_existentes:
                messagebox.showwarning("Aviso", f"O componente '{novo_nome}' já existe. Use um nome diferente.")
                return

            tree.insert("", "end", values=(novo_nome, "0,0"))
            novo_comp_entry.delete(0, tk.END)
            # Retorna uma mensagem de sucesso mais sutil
            # messagebox.showinfo("Sucesso", f"Componente '{novo_nome}' adicionado. Salve para confirmar.")
            
        def remover_componente():
            try:
                sel = tree.selection()[0]
            except IndexError:
                messagebox.showwarning("Aviso", "Selecione um componente para remover.")
                return
            
            nome_comp = tree.item(sel)['values'][0]
            
            if messagebox.askyesno("Confirmar Remoção", 
                                   f"Tem certeza que deseja remover o componente '{nome_comp}'?\n\nIsto removerá a nota associada **após o salvamento**.", 
                                   parent=top):
                tree.delete(sel)
                # Não precisa de messagebox de sucesso, pois o usuário verá a remoção imediata.

        ttk.Button(comp_frame, text="➕ Adicionar Componente", command=adicionar_componente).pack(side="left", padx=10)
        # CORREÇÃO APLICADA: O estilo "Danger.TButton" agora funciona
        ttk.Button(comp_frame, text="➖ Remover Selecionado", command=remover_componente, style="Danger.TButton").pack(side="left", padx=10)

        # --- Botão Salvar Principal ---
        def salvar_edicao():
            novos_comps = []
            
            # Garante que haja pelo menos um componente antes de salvar
            if not tree.get_children():
                messagebox.showwarning("Aviso", "A disciplina deve ter pelo menos um componente de nota. Adicione um componente antes de salvar.")
                return
                
            for item in tree.get_children():
                nome, nota_str = tree.item(item)['values']
                nova_nota = float(str(nota_str).replace(',', '.'))
                novos_comps.append({"nome": nome, "nota": nova_nota})

            novo_comp_json = json.dumps(novos_comps)
            
            # Atualiza o banco de dados
            self.cursor.execute("UPDATE notas SET componentes = ? WHERE pk_id = ?",
                                 (novo_comp_json, pk_id))
            self.conexao.commit()
            
            # Atualiza os dados em memória (self.notas)
            for i, item in enumerate(self.notas.get(aluno_id, [])):
                if item.get('pk_id') == pk_id:
                    self.notas[aluno_id][i]['componentes'] = novos_comps
                    break
            
            messagebox.showinfo("Sucesso", f"Notas e Componentes de {disciplina} atualizados!")
            top.destroy()
            parent_window.destroy()

        ttk.Button(frame, text="✅ Salvar Edição", command=salvar_edicao, style="Success.TButton").pack(pady=20)
        ttk.Button(frame, text="Cancelar", command=top.destroy).pack(pady=5)


    # ======================================================
    # CÁLCULOS E VISUALIZAÇÃO
    # ======================================================
    def calcular_media_por_disciplina(self, nota_item):
        notas = [c.get('nota', 0) for c in nota_item['componentes']]
        return sum(notas) / len(notas) if notas else 0.0 

    def calcular_media_gui(self, aluno_id=None, show_message=True):
        aluno_id = aluno_id or self.get_selected_aluno_id()
        if not aluno_id: return "0,00"
        aluno = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])
        if not notas_aluno:
            if show_message: messagebox.showinfo("Aviso", f"{aluno} não tem notas.")
            return "0,00"
        medias = [self.calcular_media_por_disciplina(n) for n in notas_aluno]
        media_final = sum(medias) / len(medias) if medias else 0.0 
        media_str = self.formatar_numero(media_final)
        if show_message:
            status = "APROVADO" if media_final >= 6 else "REPROVADO"
            messagebox.showinfo("Média", f"Média Final: {media_str}\nStatus: {status}")
        return media_str

    def visualizar_notas_gui(self, aluno_id_param=None):
        aluno_id = aluno_id_param or self.get_selected_aluno_id()
        if not aluno_id: return
        aluno_nome = self.alunos[aluno_id]['nome']
        notas_aluno = self.notas.get(aluno_id, [])

        top = tk.Toplevel(self.root)
        top.title(f"Boletim - {aluno_nome}")
        top.geometry("800x600")

        frame = ttk.Frame(top, padding=20, style="Content.TFrame")
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text=f"Boletim de {aluno_nome}", style="Header.TLabel").pack(pady=10, fill='x')

        cols = ('Disciplina', 'Média')
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols: tree.heading(col, text=col)
        tree.pack(expand=True, fill='both')

        for item in notas_aluno:
            media = self.calcular_media_por_disciplina(item)
            tree.insert("", "end", values=(item['disciplina'], self.formatar_numero(media)))

        # --- FUNÇÃO DE EXPORTAR ---
        def exportar_para_impressao():
            # ... (código da exportação omitido para brevidade)
            filepath = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                title=f"Salvar Boletim - {aluno_nome}",
                initialfile=f"boletim_{aluno_nome.replace(' ', '_')}.html",
                parent=top
            )
            if not filepath: return 
            html = f"""
            <html>
            <head>
                <title>Boletim - {aluno_nome}</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", Arial, sans-serif; margin: 25px; }}
                    h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 5px; }}
                    p {{ font-size: 1.1em; }}
                    table {{ width: 100%; max-width: 700px; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ccc; padding: 12px; text-align: left; }}
                    th {{ background-color: #f4f4f4; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    tfoot th {{ text-align: right; background-color: #e9e9e9; font-weight: bold; }}
                    tfoot th:last-child {{ text-align: left; }}
                    .footer {{ margin-top: 40px; font-style: italic; color: #888; font-size: 0.9em; }}
                    @media print {{
                        .no-print {{ display: none; }}
                        body {{ margin: 0; font-size: 12pt; }}
                        table {{ max-width: 100%; }}
                    }}
                </style>
            </head>
            <body>
                <h1>Boletim do Aluno</h1>
                <p><strong>Aluno:</strong> {aluno_nome}</p>
                <p><strong>ID:</strong> {aluno_id}</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Disciplina</th>
                            <th>Média</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for item in notas_aluno:
                media = self.calcular_media_por_disciplina(item)
                media_str = self.formatar_numero(media)
                html += f"<tr><td>{item['disciplina']}</td><td>{media_str}</td></tr>\n"
            media_total_str = self.calcular_media_gui(aluno_id=aluno_id, show_message=False)
            html += f"""
                    </tbody>
                    <tfoot>
                        <tr>
                            <th>Média Geral:</th>
                            <th>{media_total_str}</th>
                        </tr>
                    </tfoot>
                </table>
                
                <div class="footer">
                    <p>Gerado por ENOTE - Sistema de Notas Escolares</p>
                </div>
            </body>
            </html>
            """
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
                webbrowser.open(f'file://{os.path.realpath(filepath)}')
                messagebox.showinfo("Sucesso", "Boletim exportado!\n\nO arquivo foi aberto no seu navegador. Use a função de impressão (Ctrl+P) do navegador.", parent=top)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}", parent=top)
        
        # --- FIM DA FUNÇÃO DE EXPORTAR ---

        button_frame = ttk.Frame(frame, style="Content.TFrame")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="🖨️ Exportar para Impressão", command=exportar_para_impressao).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Fechar", command=top.destroy).pack(side="left", padx=10)

    # ======================================================
    # MENU ALUNO
    # ======================================================
    def show_aluno_menu(self):
        self.clear_frame()
        frame = ttk.Frame(self.root, style="Content.TFrame", padding=60)
        frame.place(relx=0.5, rely=0.5, anchor='center')

        ttk.Label(frame, text="Digite seu ID:", font=('Inter', 14, 'bold'),
                  background=self.BG_CONTAINER).pack(pady=10)
        entry = ttk.Entry(frame, width=30, justify="center")
        entry.pack(pady=5)

        def acessar():
            aluno_id = entry.get().strip().upper()
            if aluno_id in self.alunos:
                self.visualizar_notas_gui(aluno_id_param=aluno_id)
            else:
                messagebox.showerror("Erro", "ID inválido.")

        ttk.Button(frame, text="Acessar Boletim", command=acessar).pack(pady=15)
        ttk.Button(frame, text="⬅️ Voltar", command=self.show_main_menu).pack(pady=10)

# ======================================================
# EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorNotasApp(root)
    root.mainloop()