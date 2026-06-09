from requests.sessions import default_headers
import math
import requests
import time


def get_position():
    while True:
        pos = input("Digite a coordenada (X Y) [mm]: ").split()
        result = list(map(float, pos))
        if len(pos) == 2:
            return result
        else:
            print("ERRO: Digitar apenas 2 números separados por espaço.")


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


def rad_movement(velocity, delta_r, dp):
    vA = velocity
    pA = -round(delta_r / dp)
    vX = vA
    # NOTA FÍSICA: Se as rodas X e A precisarem girar na mesma direção para andar reto, remova este -1
    pX = -1 * pA

    # CORREÇÃO: Usa float para não zerar tempos quebrados
    t_real = abs(pA / float(vA)) if vA != 0 else 0

    print("\n>>> MOVIMENTO RADIAL <<<")
    enviar_comando(vX=vX, pX=pX, vA=vA, pA=pA)

    time.sleep(t_real + 1)


def tan_movement(velocity, e, g, j, passo_mm, delta_alpha, R_f):
    # CORREÇÃO: As variáveis g e j agora batem com o exec()
    delta_alpha = math.atan2(math.sin(delta_alpha), math.cos(delta_alpha))

    # Rodas Y e Z: arco lateral usando as medidas g e j corretamente
    pZ = round(delta_alpha * (R_f + g) * passo_mm)
    pY = round(-delta_alpha * (R_f - j) * passo_mm)

    # Rodas X e A: giro em torno do chassi
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

    # Velocidade mínima de 10 para motores que precisam se mover
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

    time.sleep(t_real + 1.5)  # Margem aumentada para compensar arrasto da curva


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

    while True:
        print("\n--- ONDE O ROBÔ ESTÁ? ---")
        x_raw, y_raw = get_position()
        x_i, y_i = float(x_raw), float(y_raw)
        r_i = math.sqrt(x_i**2 + y_i**2)
        alpha_i = math.atan2(y_i, x_i)

        print("--- PARA ONDE ELE VAI? ---")
        x_raw, y_raw = get_position()
        x_f, y_f = float(x_raw), float(y_raw)
        r_f = math.sqrt(x_f**2 + y_f**2)
        alpha_f = math.atan2(y_f, x_f)

        # Condição de saída limpa se o alvo for alcançado
        if abs(x_i - x_f) <= margem_erro and abs(y_i - y_f) <= margem_erro:
            print("[+] Destino alcançado!")
            break

        delta_r = r_f - r_i
        delta_alpha = alpha_f - alpha_i

        # Lógica de aproximação dividida em R e T
        if y_i <= y_f:
            rad_movement(velocity, delta_r, dp)
            tan_movement(velocity, e, g, j, passo_mm, delta_alpha, r_f)
        else:
            tan_movement(velocity, e, g, j, passo_mm, delta_alpha, r_i)
            rad_movement(velocity, delta_r, dp)


if __name__ == "__main__":
    try:
        exec()
    except KeyboardInterrupt:
        parada_emergencia()
