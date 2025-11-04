import uuid
import json
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from functools import partial

class GerenciadorNotasApp:
# ... (código existente) ...
    # ======================================================
    # BANCO DE DADOS (Unido do Script A)
    # ======================================================
# ... (código existente) ...
        """)
        self.conexao.commit()

    def carregar_dados(self):
        """Carrega alunos e notas do SQLite para a memória."""
        self.alunos.clear()
        self.notas.clear()
        
        # Carregar Alunos
        # --- CORREÇÃO AQUI ---
        # Usamos um SELECT explícito para garantir que pegamos apenas as 6 colunas
        # que esta versão do código espera, ignorando colunas antigas do .db
        self.cursor.execute("SELECT id, nome, matricula, data_nascimento, turma, contato FROM alunos")
        # --- FIM DA CORREÇÃO ---
        
        for row in self.cursor.fetchall():
            aluno_id, nome, matricula, nasc, turma, contato = row # Agora 'row' terá exatamente 6 valores
            self.alunos[aluno_id] = {
                "nome": nome, "matricula": matricula,
                "data_nascimento": nasc, "turma": turma, "contato": contato
            }
# ... (código existente) ...

