import pygame as pg
import constantes as const
from random import randint
from math import floor
import sys
import os
import time

class GerenciadorAudio():
    def __init__(self):
        self.canal_0 = pg.mixer.Channel(0)
        self.trilha_sonora = pg.mixer.Sound('./audios/trilha_sonora.mp3')
        self.audio_vitoria = pg.mixer.Sound('./audios/musica_vitoria.mp3')
        self.audio_derrota = pg.mixer.Sound('./audios/musica_derrota.mp3')
        self.tocando_musica_final = False

    def tocar_trilha_sonora(self, volume=1):
        """ toca a trilha sonora do jogo """
        self.trilha_sonora.set_volume(volume) # define o volume
        self.canal_0.play(self.trilha_sonora)

    def tocar_musica_vitoria(self, volume=1):
        """ toca a musica de vitoria do jogo """
        if not self.tocando_musica_final:
            self.audio_vitoria.set_volume(volume) # define o volume
            self.canal_0.play(self.audio_vitoria)
            self.tocando_musica_final = True

    def tocar_musica_derrota(self, volume=1):
        """ toca a musica de derrota do jogo """
        if not self.tocando_musica_final:
            self.audio_derrota.set_volume(volume) # define o volume
            self.canal_0.play(self.audio_derrota)
            self.tocando_musica_final = True

class Eventos:
    def __init__(self):
        """ atributos da classe """
        self.direcao = 0

    def _verificar_direcao(self, evento):
        """ verifica as teclas pressionadas e salva a direcao apontada (0 = parado, 1 = direita, -1 = esquerda) """
        # verifica se pressionou alguma tecla
        if evento.type == pg.KEYDOWN:
            if evento.key == const.TECLA_DIREITA:
                self.direcao += 1
            elif evento.key == const.TECLA_ESQUERDA:
                self.direcao -= 1
        # verifica se soltou alguma tecla
        if evento.type == pg.KEYUP:
            if evento.key == const.TECLA_DIREITA:
                self.direcao -= 1
            elif evento.key == const.TECLA_ESQUERDA:
                self.direcao += 1

    def _verificar_fim_de_jogo(self, evento):
        """ verifica se o jogo foi finalizado """
        if evento.type == pg.QUIT:
            pg.quit()
            sys.exit()

    def verificar_input(self):
        """ verifica se o jogador esta se movendo ou se fechou o jogo """
        for evento in pg.event.get():
            self._verificar_direcao(evento)
            self._verificar_fim_de_jogo(evento)


class Temporizador:
    def __init__(self):
        """ atributos da classe """
        self._tempo_inicial = time.time()
        self.fonte = pg.font.SysFont('calibri', 35, True) # 'calibri', 50, True
        self.tempo_atual = 0
    
    def contabilzar_duracao(self):
        """ calcula quanto tempo se passou e atualiza o tempo atual """
        tempo_final = time.time()
        self.tempo_atual = tempo_final - self._tempo_inicial

    def desenhar_tempo_atual(self, tela: object):
        """ desenha na tela o tempo de duracao do jogo """
        # criando o texto do tempo de duracao
        tempo_duracao = self.fonte.render(str(floor(self.tempo_atual)), True, const.COR_PRETA)
        # definindo posicao => x = centro da tela; y = 65 pixels pra baixo
        pos_x = tela.comprimento//2 - tempo_duracao.get_rect().width//2
        pos_y = 65
        # desenhando o tempo atual na posicao especificada
        tela.superficie.blit(tempo_duracao, (pos_x, pos_y))


class DetectorColisao:
    def __init__(self, path_explosao: str, tamanho: tuple):
        """ atributos da classe """
        self.path_exploao = path_explosao
        self.canal_de_som = pg.mixer.Channel(1)
        self.som_batida = pg.mixer.Sound('./audios/batida_de_carro.mp3')
        self.tamanho = tamanho
        self.ocorrendo_explosao = False
        self.imagens_explosao = self._carregar_imagens_explosao()
        self.indice_explosao = 0
        self.lista_npcs_intactos = []
        self.ultima_posicao_colisao = ()

    def _carregar_imagens_explosao(self):
        """ carrega todas as imagens de explosao """
        lista_imagens = []
        for nome_arquivo in os.listdir(self.path_exploao):
            imagem = pg.transform.scale(pg.image.load(self.path_exploao + '/' + nome_arquivo), self.tamanho)
            lista_imagens.append(imagem)
        return lista_imagens
    
    def _animar_colisao(self, tela: pg.Surface, img: pg.Surface, posicao: tuple):
        """ desenha a imagem da colisao na posicao especificada """
        contorno_imagem = img.get_rect()
        contorno_imagem.centerx = posicao[0]
        contorno_imagem.centery = posicao[1] + self.indice_explosao * const.VELOCIDADE_NPC
        tela.blit(img, contorno_imagem)

    def validar_colisao(self, jogador: object, npcs: object, barra_de_vida: object):
        """ salva o ponto de colisao, diminui a vida do jogador e cria uma lista dos npcs intactos """
        npcs_intactos = []
        for info in npcs.npcs_spawnados:
            contorno_npc: pg.Rect = info[1]
            # verifica se houve colisao entre o jogador e algum npc
            colidiu = jogador.contorno.colliderect(contorno_npc)
            if colidiu:
                # emite o som da explosao
                self.canal_de_som.play(self.som_batida)
                # reduz a vida do jogador e impede que seja menor que 0
                barra_de_vida.vida_atual -= 1
                if barra_de_vida.vida_atual < 0:
                    barra_de_vida.vida_atual = 0
                # salva o ponto onde ocorreu a colisao
                pos_central_x = contorno_npc.x + contorno_npc.width // 2
                pos_central_y = contorno_npc.y + contorno_npc.height // 2
                self.ultima_posicao_colisao = (pos_central_x, pos_central_y)
            else:
                # cria uma nova lista, removendo os npcs que colidiram
                npcs_intactos.append(info)
        # atualiza a lista de npcs intactos
        self.lista_npcs_intactos = npcs_intactos

    def gerenciar_animacao_explosao(self, tela: object):
        """ verifica se uma explosao esta acontecendo e apresenta as imagens da explosao """
        # salvando a ultima posicao de colisao
        if self.ultima_posicao_colisao != (): # se houve uma colisao
            self.ocorrendo_explosao = True
        # rodando a animacao de explosao
        if self.ocorrendo_explosao:
            self._animar_colisao(tela.superficie, self.imagens_explosao[self.indice_explosao], self.ultima_posicao_colisao)
            # passa para a proxima imagem da explosao e reseta quando atingir a ultima
            self.indice_explosao += 1
            if self.indice_explosao > len(self.imagens_explosao) - 1:
                self.indice_explosao = 0
                self.ocorrendo_explosao = False
                self.ultima_posicao_colisao = ()


class BarraDeVida:
    def __init__(self, path: str, tamanho: tuple):
        """ atributos da classe """
        self.path = path
        self.comprimento = tamanho[0]
        self.largura = tamanho[1]
        self.imagens = self._carregar_imagens_vida()
        self.vida_atual = 3
    
    def _carregar_imagens_vida(self):
        """ carrega e redimensiona as imagens da barra de vida """
        lista_imagens = []
        for nome_arquivo in os.listdir(self.path):
            imagem = pg.transform.scale(pg.image.load(self.path + '/' + nome_arquivo), (self.comprimento, self.largura))
            lista_imagens.append(imagem)
        return lista_imagens
    
    def desenhar(self, tela: object):
        """ desenha a barra de vida na tela """
        # escolhe a imagem que vai ser desenhada
        imagem = self.imagens[self.vida_atual]
        # definindo posicao => x = centro da tela; y = 10 pixels pra baixo
        pos_x = tela.comprimento//2 - self.comprimento//2
        pos_y = 10
        # desenha a barra de vida na posicao especificada
        tela.superficie.blit(imagem, (pos_x, pos_y))


class NPCS:
    def __init__(self, path: str, tamanho: tuple):
        """ atributos da classe """
        self.path = path
        self.comprimento = tamanho[0]
        self.largura = tamanho[1]
        self.imagens = self._carregar_npcs()
        self.npcs_spawnados = []
        self._pode_spawnar = False
    
    def _carregar_npcs(self) -> list:
        """ carrega e redimensiona as imagens dos npcs """
        lista_imagens = []
        for nome_arquivo in os.listdir(self.path):
            imagem = pg.transform.scale(pg.image.load(self.path + '/' + nome_arquivo), (self.comprimento, self.largura))
            lista_imagens.append(imagem)
        return lista_imagens

    def _remover_npcs_no_final_da_tela(self, tela: object):
        """ remove todos os npcs que ultrapassaram o limite inferior da tela """
        nova_lista = []
        # percorre todos os npcs na lista de npcs spawnados
        for info in self.npcs_spawnados:
            contorno_npc = info[1]
            # adiciona na nova lista apenas os npcs que não atingiram o limite final da tela
            if contorno_npc.y < tela.largura + self.largura:
                nova_lista.append(info)
        # atualiza a lista de npcs spawnados
        self.npcs_spawnados = nova_lista

    def spawnar(self, tempo_atual: float, intervalo: float):
        """ spawna um novo npc, em posicao aleatoria da tela, a cada intervalo de tempo """
        # atualiza o tempo atual considerando apenas uma casa decimal
        tempo_atual = float(f'{tempo_atual:.1f}')
        # verifica se o tempo atual conhicide com o intervalo de spawn do npc
        if tempo_atual % intervalo == 0:
            if self._pode_spawnar:
                self._pode_spawnar = False
                # escolhe a imagem de um npc aleatorio
                indice_aleatorio = randint(0, len(self.imagens)-1)
                img_npc: pg.Surface = self.imagens[indice_aleatorio]
                contorno_npc = img_npc.get_rect()
                # escolhe uma posicao aleatoria para o npc
                posicoes_estrada = [90, 250, 410]
                posicao_aleatoria = randint(0, len(posicoes_estrada)-1)
                contorno_npc.centerx = posicoes_estrada[posicao_aleatoria]
                # posiciona o npc na parte superior da tela
                contorno_npc.y = -self.largura
                # adiciona a imagem e o contorno do npc na lista de npcs spawnados
                self.npcs_spawnados.append([img_npc, contorno_npc])
        else:
            self._pode_spawnar = True

    def desenhar(self, tela: object):
        """ desenha todos os npcs contidos na lista de npcs spawnados """
        # percorre todos os npcs na lista de npcs spawnados
        for info in self.npcs_spawnados:
            img_npc = info[0]
            contorno_npc = info[1]
            # desenha o npc na tela
            tela.superficie.blit(img_npc, contorno_npc)
    
    def mover(self, tela: object):
        """ move todos os npcs contidos na lista de npcs spawnados """
        # percorre todos os npcs na lista de npcs spawnados
        for info_npc in self.npcs_spawnados:
            # aumenta sua posicao no eixo y
            contorno_npc: pg.Rect = info_npc[1]
            contorno_npc.y += const.VELOCIDADE_NPC
        # remove todos os npcs que atingiram o limite final da tela
        self._remover_npcs_no_final_da_tela(tela)


class Estrada:
    def __init__(self, path: str, tamanho: tuple):
        """ atributos da classe """
        self.comprimento = tamanho[0]
        self.largura = tamanho[1]
        self.img1 = pg.transform.scale(pg.image.load(path), (self.comprimento, self.largura))
        self.img2 = pg.transform.scale(pg.image.load(path), (self.comprimento, self.largura))
        self.contorno_img1 = self.img1.get_rect()
        self.contorno_img2 = self.img2.get_rect()
        # posicionando a segunda estrada em cima da primeira
        self.contorno_img2.y = -self.largura

    def desenhar(self, tela: object):
        """ desenha as estradas na tela """
        tela.superficie.blit(self.img1, self.contorno_img1)
        tela.superficie.blit(self.img2, self.contorno_img2)
    
    def mover(self):
        """ move cada estrada e atualiza a posicao a medida que atinge o limite final da tela """
        # move as estradas
        self.contorno_img1.y += const.VELOCIDADE_VERTICAL
        self.contorno_img2.y += const.VELOCIDADE_VERTICAL
        # resetando a posicao da estrada quando chega no final da tela (efeito de estrada infinita)
        if self.contorno_img1.y >= self.largura:
            self.contorno_img1.y = -self.largura
        if self.contorno_img2.y >= self.largura:
            self.contorno_img2.y = -self.largura


class Jogador:
    def __init__(self, path: str, tamanho: tuple):
        """ atributos da classe """
        self.path = path
        self.comprimento = tamanho[0]
        self.largura = tamanho[1]
        self.imagem = pg.transform.scale(pg.image.load(path), tamanho)
        self.contorno = self.imagem.get_rect()
        self.desenhado = False
    
    def desenhar(self, tela: object):
        """ desenha o jogador na tela """
        # ajusta a posicao do jogador na primeira vez que for desenhado
        if not self.desenhado:
            self.desenhado = True
            self.contorno.centerx = tela.comprimento//2
            self.contorno.y = tela.largura - self.largura - 30
        # desenhando o jogador na tela
        tela.superficie.blit(self.imagem, self.contorno)
    
    def mover(self, tela: object, direcao: int):
        """ move o jogador considerando a direcao atual """
        # move o carro na direcao especificada
        self.contorno.y = tela.largura - self.largura - 30
        self.contorno.x += direcao * const.VELOCIDADE_HORIZONTAL
        # evita que o carro ultrapasse o limite horizontal da tela
        if self.contorno.x >= tela.comprimento - self.comprimento - 20:
            self.contorno.x = tela.comprimento - self.comprimento - 20
        elif self.contorno.x <= 18:
            self.contorno.x = 18


class Tela:
    def __init__(self, tamanho: tuple):
        """ atributos da classe """
        self.nome = 'Velocidade Máxima'
        self.icone = pg.image.load('./imagens/icone.png')
        self.comprimento = tamanho[0]
        self.largura = tamanho[1]
        self.superficie = pg.display.set_mode((self.comprimento, self.largura))
        self.fonte = pg.font.SysFont('arial bold', 70, True)
        # definindo o titulo e o icone do jogo
        pg.display.set_caption(self.nome)
        pg.display.set_icon(self.icone)

    def escrever(self, texto: str, cor):
        """ escreve um texto especifico no centro da tela """
        # renderizando o texto que sera escrito
        texto_tela = self.fonte.render(texto, True, cor)
        # definindo posicao => x = centro da tela; y = centro da tela
        pos_x = self.comprimento//2 - texto_tela.get_rect().width//2
        pos_y = self.largura//2 - texto_tela.get_rect().height//2
        # escreve o texto na posicao especificada
        self.superficie.blit(texto_tela, (pos_x, pos_y))