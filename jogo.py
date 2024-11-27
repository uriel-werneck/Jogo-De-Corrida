import pygame
import constantes
import classes

"""
REGRAS DO JOGO:
- Você vence se sobreviver por 40 segundos;
- Você perde se bater o carro 3 vezes;
- Para mover o carro, use as teclas esquerda e direita do teclado.
"""

# iniciando o pygame e o módulo de áudio
pygame.init()
pygame.mixer.init()

# iniciando classes
eventos = classes.Eventos()
tela = classes.Tela((500, 700))
npcs = classes.NPCS('./imagens/npcs', (84, 168))
estrada = classes.Estrada('./imagens/estrada.png', (500, 750))
jogador = classes.Jogador('./imagens/jogador.png', (78, 187))
temporizador = classes.Temporizador()
detector_colisao = classes.DetectorColisao('./imagens/explosao', (175, 175))
barra_de_vida = classes.BarraDeVida('./imagens/vida', (165, 45))
gerenciador_audio = classes.GerenciadorAudio()
clock_fps = pygame.time.Clock() # define o fps

# # tocando música inicial
gerenciador_audio.tocar_trilha_sonora(0.5)

# looping principal
while True:
    # define o fps do jogo
    clock_fps.tick(constantes.FPS_JOGO)

    # verifica as entradas do usuario
    eventos.verificar_input()

    # validando fim de jogo
    if temporizador.tempo_atual >= 40 or barra_de_vida.vida_atual == 0:
        # desenha o que vai aparecer na tela de fim de jogo
        estrada.desenhar(tela)
        npcs.desenhar(tela)
        jogador.desenhar(tela)
        temporizador.desenhar_tempo_atual(tela)
        barra_de_vida.desenhar(tela)
        # verifica o motivo do fim do jogo
        if temporizador.tempo_atual >= 40:
            tela.escrever('VOCÊ VENCEU!', constantes.COR_AMARELA)
            gerenciador_audio.tocar_musica_vitoria(0.7)
        elif barra_de_vida.vida_atual == 0:
            tela.escrever('VOCÊ PERDEU!', constantes.COR_VERMELHA)
            gerenciador_audio.tocar_musica_derrota(0.7)
        # salva as alteracoes feitas na tela
        pygame.display.flip()
        continue # pula para a proxima iteracao (nao lê as linhas de baixo)

    # desenhando e movendo a estrada
    estrada.desenhar(tela)
    estrada.mover()

    # spawnando o npc
    npcs.spawnar(temporizador.tempo_atual, constantes.DELAY_SPAWN_NPC)
    npcs.desenhar(tela)
    npcs.mover(tela)

    # desenhando o tempo de duracao do jogo
    temporizador.desenhar_tempo_atual(tela)

    # desenhando e movendo o jogador
    jogador.desenhar(tela)
    jogador.mover(tela, eventos.direcao)

    # detectando colisao, animando a explosão e removendo npcs colididos
    detector_colisao.validar_colisao(jogador, npcs, barra_de_vida)
    detector_colisao.gerenciar_animacao_explosao(tela)
    npcs.npcs_spawnados = detector_colisao.lista_npcs_intactos

    # desenhando barra de vida
    barra_de_vida.desenhar(tela)

    # calculando a duracao do jogo
    temporizador.contabilzar_duracao()

    # salvando as alteracoes feitas na tela
    pygame.display.flip()