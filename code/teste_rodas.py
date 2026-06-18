from requests.sessions import default_headers
import math
import requests
import time
import pyautogui
import pynput
import os
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MedidasHandler(FileSystemEventHandler):
    def __init__(self, fila_medidas, caminho_arquivo):
        self.fila_medidas = fila_medidas
        # Força o caminho a ser absoluto para evitar problemas de pasta correspondente
        self.caminho_arquivo = os.path.abspath(caminho_arquivo)
        self.ultima_leitura = (0.0, 0.0)

    # Mudamos de 'on_modified' para 'on_any_event' para capturar se o arquivo for deletado/recriado
    def on_any_event(self, event):
        # Ignora se for um evento de diretório
        if event.is_directory:
            return

        # Verifica se o evento aconteceu EXATAMENTE no nosso arquivo de medidas
        if os.path.abspath(event.src_path) == self.caminho_arquivo:
            # Só age se for modificação, criação ou movimentação (ignora deleção pura)
            if event.event_type in ("modified", "created", "moved"):
                # Dá um tempo ligeiramente maior para o outro programa fechar o arquivo
                time.sleep(0.3)

                try:
                    with open(
                        self.caminho_arquivo, "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        conteudo = f.read().strip()

                    if not conteudo:
                        return

                    valores = conteudo.replace(";", ",").split(",")
                    if len(valores) < 2:
                        return

                    x = float(valores[0].strip())
                    y = float(valores[1].strip())

                    if (x, y) != self.ultima_leitura:
                        print(f"[DEBUG-WATCHDOG] Detectado no arquivo: X={x}, Y={y}")
                        self.ultima_leitura = (x, y)
                        self.fila_medidas.put((x, y))
                except Exception as e:
                    # Se der erro de permissão porque o arquivo ainda estava aberto,
                    # printamos para você saber o que está acontecendo
                    print(f"[DEBUG-ERRO] Erro ao tentar ler o arquivo: {e}")


def get_position():
    while True:
        pos = input("Digite a coordenada (X Y) [mm]: ").split()
        if len(pos) == 2:
            try:
                return list(map(float, pos))
            except ValueError:
                print("ERRO: Digite apenas números válidos.")
        else:
            print("ERRO: Digitar apenas 2 números separados por espaço.")


def get_position_mouse():
    print("Posicione o cursor e pressione Enter...")
    with pynput.keyboard.Events() as events:
        for event in events:
            if (
                isinstance(event, pynput.keyboard.Events.Press)
                and event.key == pynput.keyboard.Key.space
            ):
                x, y = pyautogui.position()
                print(f"Coordenadas capturadas: X={x} px, Y={y} px")
                return x, y


def parada_emergencia():
    """Envia o comando de parada imediata para o Wemos"""
    url_stop = "http://192.168.4.1/stop"
    try:
        print("\n[!!!] CANCELAMENTO SOLICITADO [!!!]")
        requests.get(url_stop, timeout=2)
        print("[+] Robô imobilizado com sucesso.")
    except Exception as e:
        print(f"[ERRO FATAL] Não foi possível parar o robô: {e}")


def enviar_comando(vX=0, pX=0, vY=0, pY=0, vZ=0, pZ=0, vA=0, pA=0, servo=0):
    query = f"vX={vX}&pX={pX}&vY={vY}&pY={pY}&vZ={vZ}&pZ={pZ}&vA={vA}&pA={pA}&s1={servo}&s2={servo}"
    url = f"http://192.168.4.1/run?{query}"
    try:
        print(f"[SISTEMA] Enviando: {query}")
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"[ERRO] Arduino retornou status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na conexão com o Wemos: {e}")


def desenhar_cruz(velocity, passo_mm):
    delay = 1
    enviar_comando(vX=velocity, pX=-70 * passo_mm, vA=velocity, pA=70 * passo_mm)
    time.sleep(delay)

    enviar_comando(servo=1)
    time.sleep(delay)
    enviar_comando()
    time.sleep(delay)
    enviar_comando(vX=velocity, pX=5 * passo_mm, vA=velocity, pA=-5 * passo_mm)
    time.sleep(delay)
    enviar_comando(
        vX=velocity, pX=20 * passo_mm, vA=velocity, pA=-20 * passo_mm, servo=1
    )
    time.sleep(delay)
    enviar_comando(vX=velocity, pX=-30 * passo_mm, vA=velocity, pA=30 * passo_mm)
    time.sleep(delay)
    enviar_comando(
        vX=velocity, pX=-20 * passo_mm, vA=velocity, pA=20 * passo_mm, servo=1
    )
    time.sleep(delay)
    enviar_comando(vX=velocity, pX=25 * passo_mm, vA=velocity, pA=-25 * passo_mm)
    time.sleep(delay)

    enviar_comando(vY=velocity, pY=5 * passo_mm, vZ=velocity, pZ=-5 * passo_mm)
    time.sleep(delay)
    enviar_comando(
        vY=velocity, pY=20 * passo_mm, vZ=velocity, pZ=-20 * passo_mm, servo=1
    )
    time.sleep(delay)
    enviar_comando(vY=velocity, pY=-30 * passo_mm, vZ=velocity, pZ=30 * passo_mm)
    time.sleep(delay)
    enviar_comando(
        vY=velocity, pY=-20 * passo_mm, vZ=velocity, pZ=20 * passo_mm, servo=1
    )
    time.sleep(delay)
    enviar_comando(vY=velocity, pY=25 * passo_mm, vZ=velocity, pZ=-25 * passo_mm)
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=70 * passo_mm, vA=velocity, pA=-70 * passo_mm)
    time.sleep(delay)


def rad_movement(velocity, delta_r, dp):
    vA = velocity
    pA = -round(delta_r / dp)
    vX = vA
    pX = -1 * pA

    t_real = abs(pA / float(vA)) if vA != 0 else 0

    print("\n>>> MOVIMENTO RADIAL <<<")
    enviar_comando(vX=vX, pX=pX, vA=vA, pA=pA)

    time.sleep(t_real + 1)


def tan_movement(velocity, e, g, j, passo_mm, delta_alpha, R_f):
    delta_alpha = math.atan2(math.sin(delta_alpha), math.cos(delta_alpha))

    pZ = round(delta_alpha * (R_f + g) * passo_mm)
    pY = round(-delta_alpha * (R_f - j) * passo_mm)

    pA = round(delta_alpha * e / 2 * passo_mm)
    pX = pA

    if pX == 0 and pY == 0 and pZ == 0 and pA == 0:
        return

    max_passos = max(abs(pX), abs(pY), abs(pZ), abs(pA))
    t_real = max_passos / float(velocity)

    vX = abs(int(pX / t_real))
    vY = abs(int(pY / t_real))
    vZ = abs(int(pZ / t_real))
    vA = abs(int(pA / t_real))

    if pX != 0 and vX == 0:
        vX = 10
    if pY != 0 and vY == 0:
        vY = 10
    if pZ != 0 and vZ == 0:
        vZ = 10
    if pA != 0 and vA == 0:
        vA = 10

    print("\n>>> MOVIMENTO TANGENCIAL <<<")
    enviar_comando(vX=vX, pX=pX, vY=vY, pY=pY, vZ=vZ, pZ=pZ, vA=vA, pA=pA)

    time.sleep(t_real + 1.5)


def desenhar_cruz(velocity, passo_mm):
    delay = 1
    enviar_comando(vX=velocity, pX=-25 * passo_mm, vA=velocity, pA=35 * passo_mm)
    time.sleep(delay)
    enviar_comando(vX=velocity, pX=-25 * passo_mm, vA=velocity, pA=35 * passo_mm)
    time.sleep(delay)

    enviar_comando(servo=1)
    time.sleep(delay)
    enviar_comando()
    time.sleep(delay)
    enviar_comando(vX=velocity, pX=5 * passo_mm, vA=velocity, pA=-5 * passo_mm)
    time.sleep(delay)
    enviar_comando(
        vX=velocity, pX=20 * passo_mm, vA=velocity, pA=-20 * passo_mm, servo=1
    )
    time.sleep(delay)
    enviar_comando(vX=velocity, pX=-30 * passo_mm, vA=velocity, pA=30 * passo_mm)
    time.sleep(delay)
    enviar_comando(
        vX=velocity, pX=-20 * passo_mm, vA=velocity, pA=20 * passo_mm, servo=1
    )
    time.sleep(delay)
    enviar_comando(vX=velocity, pX=25 * passo_mm, vA=velocity, pA=-25 * passo_mm)
    time.sleep(delay)

    enviar_comando(vY=velocity, pY=5 * passo_mm, vZ=velocity, pZ=-5 * passo_mm)
    time.sleep(delay)
    enviar_comando(
        vY=velocity, pY=20 * passo_mm, vZ=velocity, pZ=-20 * passo_mm, servo=1
    )
    time.sleep(delay)
    enviar_comando(vY=velocity, pY=-30 * passo_mm, vZ=velocity, pZ=30 * passo_mm)
    time.sleep(delay)
    enviar_comando(
        vY=velocity, pY=-20 * passo_mm, vZ=velocity, pZ=20 * passo_mm, servo=1
    )
    time.sleep(delay)
    enviar_comando(vY=velocity, pY=25 * passo_mm, vZ=velocity, pZ=-25 * passo_mm)
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=250 * passo_mm, vA=velocity, pA=-250 * passo_mm)
    time.sleep(delay)


def mover_por_passos_manuais(velocity=400):
    """
    Pede ao usuário a quantidade de passos para cada eixo (X, Y, Z, A)
    e envia o comando de execução com a velocidade definida.
    """
    print("\n--- MOVIMENTAÇÃO MANUAL POR PASSOS ---")
    print(f"Velocidade configurada: {velocity} passos/s")

    eixos = ["X", "Y", "Z", "A"]
    passos_finais = {}

    for eixo in eixos:
        while True:
            entrada = input(
                f"Digite a quantidade de passos para o eixo p{eixo} (positivo ou negativo): "
            ).strip()

            # Se o usuário apenas apertar Enter, assume 0 passos para aquele eixo
            if entrada == "":
                passos_finais[f"p{eixo}"] = 0
                break

            try:
                passos_finais[f"p{eixo}"] = int(entrada)
                break
            except ValueError:
                print(
                    "ERRO: Digite um número inteiro válido (ex: 200, -400) ou pressione Enter para 0."
                )

    print("\n[MANUAL] Calculando velocidades correspondentes...")

    # Define a velocidade padrão para os eixos que vão se mover
    vX = velocity if passos_finais["pX"] != 0 else 0
    vY = velocity if passos_finais["pY"] != 0 else 0
    vZ = velocity if passos_finais["pZ"] != 0 else 0
    vA = velocity if passos_finais["pA"] != 0 else 0

    # Envia o comando para o Wemos utilizando o dicionário descompactado e as velocidades
    enviar_comando(
        vX=vX,
        pX=passos_finais["pX"],
        vY=vY,
        pY=passos_finais["pY"],
        vZ=vZ,
        pZ=passos_finais["pZ"],
        vA=vA,
        pA=passos_finais["pA"],
    )

    # Calcula um tempo estimado de espera baseado no maior número de passos para o script não encavalar comandos
    maior_passo = max(
        abs(passos_finais["pX"]),
        abs(passos_finais["pY"]),
        abs(passos_finais["pZ"]),
        abs(passos_finais["pA"]),
    )
    tempo_estimado = maior_passo / float(velocity) if maior_passo > 0 else 0

    if tempo_estimado > 0:
        print(f"[MANUAL] Aguardando movimento terminar (~{tempo_estimado:.2f}s)...")
        time.sleep(tempo_estimado + 0.5)


def exec():
    velocity = 400

    # mover_por_passos_manuais(velocity=velocity)

    desenhar_cruz(velocity, 5)


if __name__ == "__main__":
    try:
        exec()
    except KeyboardInterrupt:
        parada_emergencia()
