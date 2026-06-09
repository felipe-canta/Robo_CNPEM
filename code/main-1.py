import math
import requests
import time


def get_position():
    while True:
        pos = input("digite a coordenada inicial (Xi Yi) [mm]: ").split()
        result = list(map(int, pos))
        if len(pos) == 2:
            print(result)
            return result
        else:
            print("digitar apenas 2 digitos")
            break


def enviar_comando(msg_do_teste):
    # Como a query já vem formatada (vX=400&pX=...), basta concatenar na URL
    url = f"http://192.168.4.1/run?{msg_do_teste}"

    try:
        print(f"\n[SISTEMA] Enviando requisição: {url}")
        # Envia diretamente a URL completa
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            print(f"[ROBÔ] Resposta: {response.text}")
        else:
            print(f"[ERRO] Arduino retornou status: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na conexão com o Wemos: {e}")
        print("Verifique se você está conectado no Wi-Fi 'Robo_da_PUC'")


def rad_movement(velocity, delta_r, dp):
    vA = velocity
    sA = int(delta_r / dp)
    vX = vA
    sX = sA

    # Previne erro caso vA seja zero
    if vA != 0:
        t = abs(int(sA / vA))
    else:
        t = 0

    query = f"vX={vX}&pX={sX}&vY=0&pY=0&vZ=0&pZ=0&vA={vA}&pA={sA}&s1=0&s2=0"

    print("movimento radial")
    print(query)
    enviar_comando(query)
    time.sleep(t + 1)


def tan_movement_corrigido(velocity, e, f, g, passo_mm, delta_alpha, R_f):
    # Cálculos originais de passos
    sZ = int(delta_alpha * (R_f + f) * passo_mm)
    sY = -1 * int(delta_alpha * (R_f - g) * passo_mm)
    sA = int(delta_alpha * e / 2 * passo_mm)
    sX = sA

    # Prevenção: se não houver movimento, encerra a função
    if sX == 0 and sY == 0 and sZ == 0 and sA == 0:
        return

    # CORREÇÃO: Sincronização Perfeita de Velocidade usando Float
    max_passos = max(abs(sX), abs(sY), abs(sZ), abs(sA))
    t_real = max_passos / float(velocity)

    # Recalcula a velocidade exata de cada roda baseada no tempo real
    vX = abs(int(sX / t_real))
    vY = abs(int(sY / t_real))
    vZ = abs(int(sZ / t_real))
    vA = abs(int(sA / t_real))

    # Prevenção contra Divisão por Zero no Arduino
    if sX != 0 and vX == 0:
        vX = 10
    if sY != 0 and vY == 0:
        vY = 10
    if sZ != 0 and vZ == 0:
        vZ = 10
    if sA != 0 and vA == 0:
        vA = 10

    # O s1=1 abaixa a caneta para desenhar a curva
    query = f"vX={vX}&pX={sX}&vY={vY}&pY={sY}&vZ={vZ}&pZ={sZ}&vA={vA}&pA={sA}&s1=1&s2=0"

    print("\n[MOVIMENTO TANGENCIAL - ARCO]")
    print(f"Tempo estimado: {t_real:.2f}s")
    print(query)

    enviar_comando(query)

    # Pausa o Python até o robô terminar fisicamente
    time.sleep(t_real + 1)

    # Levanta a caneta ao terminar o trajeto
    enviar_comando("vX=0&pX=0&vY=0&pY=0&vZ=0&pZ=0&vA=0&pA=0&s1=0&s2=0")


def exec():
    diameter = 101.9
    velocity = 400
    passo_volta = 1600
    dv = diameter * math.pi

    # Suas taxas de conversão mecânica
    dp = dv / passo_volta
    passo_mm = passo_volta / dv

    g = 230
    j = 130
    e = g + j

    # =========================================================
    # LÓGICA DIRETA PARA O SEMICÍRCULO (180 Graus)
    # =========================================================
    print("--- INICIANDO SEMICÍRCULO DE 180 GRAUS ---")

    # Define o raio do semicírculo em milímetros (Ex: 200mm = 20cm)
    raio = 1000

    # Para um semicírculo perfeito, o ângulo percorrido é exatamente PI
    delta_alpha = math.pi

    print(f"Raio configurado: {raio}mm | Girando 180 graus (PI radianos)")

    # Envia os parâmetros para a função tangencial corrigida
    tan_movement_corrigido(velocity, e, g, j, passo_mm, delta_alpha, raio)

    print("\n[+] Semicírculo finalizado!")


if __name__ == "__main__":
    exec()
