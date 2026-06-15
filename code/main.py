from requests.sessions import default_headers
import math
import requests
import time
import pyautogui
import pynput


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
                and event.key == pynput.keyboard.Key.enter
            ):
                x, y = pyautogui.position()
                print(f"Coordenadas capturadas: X={x} mm, Y={y} mm")
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


def exec():
    diameter = 101.9
    velocity = 400
    passo_volta = 1600

    g = 230
    j = 130
    e = g + j

    dv = diameter * math.pi
    dp = dv / passo_volta
    passo_mm = passo_volta / dv

    margem_erro = 1.0

    x_cursor, y_cursor = get_position_mouse()

    print("--- PARA ONDE ELE VAI? ---")
    x_raw, y_raw = get_position()
    x_f, y_f = float(x_raw), float(y_raw)
    r_f = math.sqrt(x_f**2 + y_f**2)
    alpha_f = math.atan2(y_f, x_f)

    caminho_csv = "../medidas/medidas.csv"

    # 1. Faz uma leitura inicial antes de começar o loop para registrar onde o laser está parado agora
    try:
        with open(caminho_csv, "r", encoding="utf-8", errors="ignore") as f:
            conteudo_inicial = f.read().strip().replace(";", ",").split(",")
            ultima_medida_processada = (
                float(conteudo_inicial[0]),
                float(conteudo_inicial[1]),
            )
    except:
        # Se falhar ou o arquivo não existir, inicia zerado
        ultima_medida_processada = (0.0, 0.0)

    while True:
        print("\n--- INICIANDO NOVO CICLO DE MEDIÇÃO ---")

        # 2. Executa o clique na tela (apenas uma vez por ciclo)
        pyautogui.moveTo(x_cursor, y_cursor)
        pyautogui.click()
        print("[MOU-CLICK] Tela clicada. Aguardando processamento do arquivo...")

        x_i, y_i = None, None

        # 3. LOOP INTERNO: Escaneia o arquivo ATÉ que uma NOVA coordenada seja registrada
        while True:
            time.sleep(0.3)  # Intervalo de segurança para não travar o disco rígido
            try:
                with open(caminho_csv, "r", encoding="utf-8", errors="ignore") as f:
                    conteudo = f.read().strip()

                if not conteudo:
                    continue

                valores = conteudo.replace(";", ",").split(",")
                if len(valores) < 2:
                    continue

                temp_x = float(valores[0].strip())
                temp_y = float(valores[1].strip())

                # SE a coordenada encontrada for diferente do histórico, o clique funcionou!
                if (temp_x, temp_y) != ultima_medida_processada:
                    x_i = temp_x
                    y_i = temp_y
                    break  # Sai do loop de escaneamento interno

            except Exception:
                continue  # Ignora erros momentâneos de leitura e tenta de novo rápido

        # Se saímos do loop interno, significa que pegamos a medida do clique atual!
        print(f"[PRODUÇÃO] Nova medida coletada com sucesso -> X: {x_i} Y: {y_i}")
        ultima_medida_processada = (x_i, y_i)

        r_i = math.sqrt(x_i**2 + y_i**2)
        alpha_i = math.atan2(y_i, x_i)

        # Condição de saída se o robô atingir o destino
        if abs(x_i - x_f) <= margem_erro and abs(y_i - y_f) <= margem_erro:
            print("[+] Destino alcançado com sucesso!")
            break

        delta_r = r_f - r_i
        delta_alpha = alpha_f - alpha_i

        # Executa os movimentos correspondentes
        if y_i <= y_f:
            rad_movement(velocity, delta_r, dp)
            tan_movement(velocity, e, g, j, passo_mm, delta_alpha, r_f)
        else:
            tan_movement(velocity, e, g, j, passo_mm, delta_alpha, r_i)
            rad_movement(velocity, delta_r, dp)

    desenhar_cruz(velocity, passo_mm)


if __name__ == "__main__":
    try:
        exec()
    except KeyboardInterrupt:
        parada_emergencia()
