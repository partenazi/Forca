import sqlite3
import random

def criar_banco_de_dados():
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS jogadores (nome TEXT, pontos INT, categoria TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS palavras (palavra TEXT, dica TEXT, categoria TEXT)")

    cursor.execute("PRAGMA table_info('jogadores')")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    if 'categoria' not in column_names:
        cursor.execute("ALTER TABLE jogadores ADD COLUMN categoria TEXT")

    conn.commit()
    conn.close()

def adicionar_palavra_e_dica(palavra, dica, categoria):
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO palavras (palavra, dica, categoria) VALUES (?, ?, ?)", (palavra, dica, categoria))
    conn.commit()
    conn.close()

criar_banco_de_dados()

adicionar_palavra_e_dica("python", "Uma linguagem de programação", "animal")

def obter_palavra_e_dica(categoria):
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT palavra, dica FROM palavras WHERE categoria = ? ORDER BY RANDOM() LIMIT 1", (categoria,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def adicionar_pontuacao(nome, categoria, pontos=0):
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT pontos FROM jogadores WHERE nome = ? AND categoria = ?", (nome, categoria))
    resultado = cursor.fetchone()
    
    if resultado:
        pontos_atuais = resultado[0]
        pontos_atuais -= pontos
        cursor.execute("UPDATE jogadores SET pontos = ? WHERE nome = ? AND categoria = ?", (pontos_atuais, nome, categoria))
    else:
        cursor.execute("INSERT INTO jogadores (nome, pontos, categoria) VALUES (?, ?, ?)", (nome, pontos, categoria))
    
    conn.commit()
    conn.close()



def listar_pontuacao_com_media():
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome, pontos, categoria FROM jogadores")
    resultados = cursor.fetchall()
    
    pontuacoes = {}
    for jogador, pontos, categoria in resultados:
        if jogador not in pontuacoes:
            pontuacoes[jogador] = {"pontos": 0, "categoria": categoria}
        pontuacoes[jogador]["pontos"] += pontos
    
    media_pontos = {}
    for jogador, info in pontuacoes.items():
        pontos = info["pontos"]
        categoria = info["categoria"]
        media = pontos
        media_pontos[jogador] = (pontos, media, categoria)
    
    conn.close()
    
    return media_pontos

def novo_jogador(nome, categoria):
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()

    cursor.execute("SELECT nome FROM jogadores WHERE nome LIKE ? AND categoria = ?", (f'%{nome}%', categoria))
    nomes_semelhantes = cursor.fetchall()

    if not nomes_semelhantes:
        cursor.execute("INSERT INTO jogadores (nome, pontos, categoria) VALUES (?, 0, ?)", (nome,categoria))
    else:
        for jogador in nomes_semelhantes:
            cursor.execute("UPDATE jogadores SET pontos = pontos + 1 WHERE nome = ? AND categoria = ?", (jogador[0], categoria))

    conn.commit()
    conn.close()

def exibir_palavra_com_acertos(palavra, letras_adivinhadas):
    palavra_mostrada = ""
    for letra in palavra:
        if letra.isalpha() and letra.lower() in letras_adivinhadas:
            palavra_mostrada += letra
        else:
            palavra_mostrada += "_"
    return palavra_mostrada

def dar_resposta_certa(palavra, nome):
    resposta = input("Digite a resposta certa: ").lower()  # Converter a resposta para minúsculas

    if resposta == palavra.lower():  # Comparar com a palavra correta em minúsculas
        print(f"Parabéns, {nome}! Você acertou a palavra!")
        adicionar_pontuacao(nome, 1)
        return True
    else:
        print(f"Resposta incorreta, {nome}. O jogo será encerrado.")
        remover_pontos(nome, -1)
        return False

def remover_pontos(nome, pontos):
    conn = sqlite3.connect("jogo.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT pontos FROM jogadores WHERE nome = ? ", (nome))  # Adicionando a cláusula WHERE corretamente
    resultado = cursor.fetchone()
    
    if resultado:
        pontos_atuais = resultado[0]
        pontos_atuais -= pontos
        cursor.execute("UPDATE jogadores SET pontos = ? WHERE nome = ?", (pontos_atuais, nome))
    else:
        print("Jogador não encontrado.")
    
    conn.commit()
    conn.close()

def jogo_da_forca():
    criar_banco_de_dados()

    while True:
        print("Opções:")
        print("1. Começar o Jogo")
        print("2. Ver Pontuação")
        print("3. Sair")
        escolha = input("Escolha a opção (1/2/3): ")
        
        if escolha == "1":
            nome = input("Digite o seu nome: ")
            categoria = input("Escolha uma categoria (animal/fruta/nome): ").lower()
            novo_jogador(nome, categoria)
            
            while True:
                palavra, dica = obter_palavra_e_dica(categoria)
                
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
                            print(f"Você errou, {nome}! O jogo terminou.")
                            remover_pontos(nome, 1)
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
                    remover_pontos(nome, 1)
                    
                
                escolha = input("Deseja jogar novamente ou voltar ao menu? (J/M): ").lower()
                if escolha != 'j':
                    break
        elif escolha == "2":
            pontuacoes = listar_pontuacao_com_media()
            print("Pontuações:")
            for jogador, (pontos, media, categoria) in pontuacoes.items():
                print(f"{jogador}: {pontos} ponto(s) - Média: {media:.2f}")
            input("Pressione Enter para voltar ao menu.")
        elif escolha == "3":
            break
        else:
            print("Opção inválida. Escolha 1 para começar o jogo, 2 para ver a pontuação ou 3 para sair.")

if __name__ == "__main__":
    criar_banco_de_dados()
       
  
    adicionar_palavra_e_dica("python", "Uma linguagem de programação", "animal")
    adicionar_palavra_e_dica("girafa", "Um animal de pescoço longo", "animal")
    adicionar_palavra_e_dica("coco", "É redondo e tem na praia", "fruta")

    jogo_da_forca()
