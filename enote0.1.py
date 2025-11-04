import uuid

# Dicionários para armazenar dados de alunos e notas na memória.
# A chave de cada aluno é um ID único.
alunos = {}
notas = {}

def show_message(mensagem, tipo="info"):
    """Exibe uma mensagem formatada no console."""
    if tipo == "sucesso":
        print(f"✅ SUCESSO: {mensagem}")
    elif tipo == "erro":
        print(f"❌ ERRO: {mensagem}")
    else:
        print(f"ℹ️ {mensagem}")

def adicionar_aluno():
    """Adiciona um novo aluno ao sistema."""
    nome = input("Digite o nome do aluno: ")
    if not nome:
        show_message("O nome não pode ser vazio.", "erro")
        return
    
    novo_id = str(uuid.uuid4())
    alunos[novo_id] = {"nome": nome}
    notas[novo_id] = []
    show_message(f"Aluno '{nome}' adicionado com sucesso. ID: {novo_id}", "sucesso")

def adicionar_notas():
    """Adiciona notas de trabalho, teste e prova para um aluno."""
    aluno_id = input("Digite o ID do aluno: ")
    if aluno_id not in alunos:
        show_message("Aluno não encontrado.", "erro")
        return
    
    disciplina = input("Digite a disciplina: ")
    if not disciplina:
        show_message("O nome da disciplina não pode ser vazio.", "erro")
        return
    
    try:
        trabalho = float(input("Digite a nota do trabalho (0-10): "))
        teste = float(input("Digite a nota do teste (0-10): "))
        prova = float(input("Digite a nota da prova (0-10): "))
        
        if not all(0 <= nota <= 10 for nota in [trabalho, teste, prova]):
            show_message("Entrada inválida. Por favor, digite um número entre 0 e 10.", "erro")
            return
        
        if aluno_id not in notas:
            notas[aluno_id] = []
        notas[aluno_id].append({
            "disciplina": disciplina,
            "notas": {"trabalho": trabalho, "teste": teste, "prova": prova}
        })
        show_message(f"Notas adicionadas para o aluno '{alunos[aluno_id]['nome']}'.", "sucesso")
        
    except ValueError:
        show_message("Entrada inválida. Por favor, digite um número.", "erro")

def visualizar_notas():
    """Exibe todas as notas de um aluno, incluindo a média por disciplina."""
    aluno_id = input("Digite o ID do aluno: ")
    if aluno_id not in alunos:
        show_message("Aluno não encontrado.", "erro")
        return
    
    if not notas.get(aluno_id):
        show_message(f"Nenhuma nota encontrada para {alunos[aluno_id]['nome']}.", "info")
        return
    
    print(f"\n--- Notas de {alunos[aluno_id]['nome']} ---")
    for nota_item in notas[aluno_id]:
        media_disciplina = (nota_item['notas']['trabalho'] + nota_item['notas']['teste'] + nota_item['notas']['prova']) / 3
        print(f"\nDisciplina: {nota_item['disciplina']}")
        print(f"  Trabalho: {nota_item['notas']['trabalho']}")
        print(f"  Teste:    {nota_item['notas']['teste']}")
        print(f"  Prova:    {nota_item['notas']['prova']}")
        print(f"  Média da Disciplina: {media_disciplina:.2f}")

def calcular_media():
    """Calcula e exibe a média final de um aluno."""
    aluno_id = input("Digite o ID do aluno: ")
    if aluno_id not in alunos:
        show_message("Aluno não encontrado.", "erro")
        return
    
    if not notas.get(aluno_id):
        show_message("Nenhuma nota para calcular a média.", "erro")
        return
    
    total_soma = 0
    total_notas = 0
    for nota_item in notas[aluno_id]:
        total_soma += nota_item['notas']['trabalho'] + nota_item['notas']['teste'] + nota_item['notas']['prova']
        total_notas += 3
        
    media = total_soma / total_notas
    show_message(f"A média de '{alunos[aluno_id]['nome']}' é: {media:.2f}", "sucesso")

def excluir_aluno():
    """Remove um aluno e suas notas."""
    aluno_id = input("Digite o ID do aluno para excluir: ")
    if aluno_id not in alunos:
        show_message("Aluno não encontrado.", "erro")
        return
    
    confirmacao = input(f"Tem certeza que deseja excluir o aluno '{alunos[aluno_id]['nome']}' e todas as suas notas? (s/n): ").lower()
    if confirmacao == "s":
        del alunos[aluno_id]
        if aluno_id in notas:
            del notas[aluno_id]
        show_message(f"Aluno com ID {aluno_id} e todas as suas notas foram excluídos.", "sucesso")
    else:
        show_message("Exclusão cancelada.")

def listar_alunos():
    """Exibe a lista de todos os alunos cadastrados."""
    if not alunos:
        print("--- Lista de Alunos ---\n\nNenhum aluno cadastrado.")
    else:
        print("--- Lista de Alunos ---")
        for id, info in alunos.items():
            print(f"Nome: {info['nome']}, ID: {id}")

def main():
    """Função principal do programa."""
    while True:
        print("\n=== Gerenciador de Notas Escolares ===")
        print("Selecione seu papel:")
        print("1. Professor")
        print("2. Aluno")
        print("3. Sair")
        
        papel = input("Digite sua opção: ")
        
        if papel == "1":
            menu_professor()
        elif papel == "2":
            menu_aluno()
        elif papel == "3":
            show_message("Saindo do programa. Até logo!", "info")
            break
        else:
            show_message("Opção inválida. Por favor, tente novamente.", "erro")

def menu_professor():
    """Menu de opções para o professor."""
    while True:
        print("\n--- Menu do Professor ---")
        print("1. Adicionar Aluno")
        print("2. Adicionar Notas")
        print("3. Visualizar Notas")
        print("4. Calcular Média")
        print("5. Excluir Aluno")
        print("6. Listar Alunos")
        print("7. Voltar ao menu principal")
        
        opcao = input("Digite sua opção: ")
        
        if opcao == "1":
            adicionar_aluno()
        elif opcao == "2":
            adicionar_notas()
        elif opcao == "3":
            visualizar_notas()
        elif opcao == "4":
            calcular_media()
        elif opcao == "5":
            excluir_aluno()
        elif opcao == "6":
            listar_alunos()
        elif opcao == "7":
            break
        else:
            show_message("Opção inválida. Por favor, tente novamente.", "erro")

def menu_aluno():
    """Menu de opções para o aluno."""
    while True:
        print("\n--- Menu do Aluno ---")
        print("1. Visualizar Notas")
        print("2. Calcular Média")
        print("3. Voltar ao menu principal")
        
        opcao = input("Digite sua opção: ")
        
        if opcao == "1":
            visualizar_notas()
        elif opcao == "2":
            calcular_media()
        elif opcao == "3":
            break
        else:
            show_message("Opção inválida. Por favor, tente novamente.", "erro")

if __name__ == "__main__":
    main()