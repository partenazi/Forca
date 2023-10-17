import sqlite3
import random

# Função para criar o banco de dados
def criar_banco_de_dados():
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS jogadores (nome TEXT, pontos INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS palavras (palavra TEXT, dica TEXT)")
    conn.commit()
    conn.close()

# Função para adicionar uma palavra e dica ao banco de dados
def adicionar_palavra_e_dica(palavra, dica):
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO palavras (palavra, dica) VALUES (?, ?)", (palavra, dica))
    conn.commit()
    conn.close()

# Função para obter uma palavra e dica do banco de dados
def obter_palavra_e_dica():
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT palavra, dica FROM palavras ORDER BY RANDOM() LIMIT 1")
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# Função para adicionar a pontuação do jogador
def adicionar_pontuacao(nome, pontos):
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jogadores (nome, pontos) VALUES (?, ?)", (nome, pontos))
    conn.commit()
    conn.close()

# Função para listar a pontuação e a média dos jogadores
def listar_pontuacao_com_media():
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    
    # Selecionar os pontos de todos os jogadores
    cursor.execute("SELECT nome, pontos FROM jogadores")
    resultados = cursor.fetchall()
    
    # Calcular a média dos pontos
    pontuacoes = {}
    for jogador, pontos in resultados:
        if jogador not in pontuacoes:
            pontuacoes[jogador] = []
        pontuacoes[jogador].append(pontos)
    
    # Calcular a média de cada jogador
    media_pontos = {}
    for jogador, pontos in pontuacoes.items():
        media = sum(pontos) / len(pontos)
        media_pontos[jogador] = (sum(pontos), media)  # Correção aqui
    
    # Fechar a conexão com o banco de dados
    conn.close()
    
    return media_pontos

# Função para criar um novo jogador ou acumular pontos para jogadores com nomes semelhantes
def novo_jogador(nome):
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    
    # Verifica se já existe um jogador com nome semelhante
    cursor.execute("SELECT nome FROM jogadores WHERE nome LIKE ?", (f'%{nome}%',))
    nomes_semelhantes = cursor.fetchall()
    
    if not nomes_semelhantes:
        # Não há nomes semelhantes, então cria um novo jogador
        cursor.execute("INSERT INTO jogadores (nome, pontos) VALUES (?, 0)", (nome,))
    else:
        # Acumula pontos para jogadores com nomes semelhantes
        for jogador in nomes_semelhantes:
            cursor.execute("UPDATE jogadores SET pontos = pontos + 1 WHERE nome = ?", (jogador[0],))
    
    conn.commit()
    conn.close()

# Função para exibir a palavra com letras corretas adivinhadas
def exibir_palavra_com_acertos(palavra, letras_adivinhadas):
    palavra_mostrada = ""
    for letra in palavra:
        if letra.isalpha() and letra in letras_adivinhadas:
            palavra_mostrada += letra
        else:
            palavra_mostrada += "_"
    return palavra_mostrada

# Função para permitir que o jogador dê a resposta certa
def dar_resposta_certa(palavra, nome):
    resposta = input("Digite a resposta certa: ").lower()
    
    if resposta == palavra:
        print(f"Parabéns, {nome}! Você acertou a palavra!")
        adicionar_pontuacao(nome, 1)
        return True
    else:
        print(f"Resposta incorreta, {nome}. A palavra era: {palavra}")
        return False

# Função para jogar o jogo da forca
def jogo_da_forca():
    criar_banco_de_dados()

    while True:
        print("Opções:")
        print("1. Começar o Jogo")
        print("2. Ver Pontuação")
        escolha = input("Escolha a opção (1/2): ")
        
        if escolha == "1":
            nome = input("Digite o seu nome: ")
            novo_jogador(nome)
            
            while True:
                # Obter uma palavra e dica
                palavra, dica = obter_palavra_e_dica()
                
                # Lógica do jogo da forca
                letras_adivinhadas = set()
                tentativas = 6
                
                print("Bem-vindo ao Jogo da Forca!")
                print("Dica: " + dica)
                
                while tentativas > 0:
                    palavra_mostrada = exibir_palavra_com_acertos(palavra, letras_adivinhadas)
                    print("Palavra: " + palavra_mostrada)
                    print("Tentativas restantes: " + str(tentativas))
                    
                    letra = input("Digite uma letra ou 'resposta' para adivinhar a palavra: ").lower()
                    
                    if letra == "resposta":
                        if dar_resposta_certa(palavra, nome):
                            break
                    else:
                        if letra in letras_adivinhadas:
                            print("Você já adivinhou essa letra.")
                        elif letra in palavra:
                            letras_adivinhadas.add(letra)
                            if set(palavra) == letras_adivinhadas:
                                print(f"Parabéns, {nome}! Você adivinhou a palavra!")
                                adicionar_pontuacao(nome, 1)
                                break
                        else:
                            tentativas -= 1
                            print("Letra incorreta. Tente novamente.")
                
                if tentativas == 0:
                    print(f"Você perdeu, {nome}! A palavra era: {palavra}")
                
                resposta = input("Deseja jogar novamente ou mudar de jogador? (S/M): ").lower()
                if resposta == 'n':
                    break
                
            
        elif escolha == "2":
            pontuacoes = listar_pontuacao_com_media()
            print("Pontuações:")
            for jogador, (pontos, media) in pontuacoes.items():
                print(f"{jogador}: {pontos} ponto(s) - Média: {media:.2f}")
            escolha = input("Pressione Enter para continuar...")
        else:
            print("Opção inválida. Escolha 1 para começar o jogo ou 2 para ver a pontuação.")

        escolha = input("Deseja jogar com outro nome? (S/N): ")
        if escolha.lower() != 's':
            break

if __name__ == "__main__":
    jogo_da_forca()
