from requests.sessions import default_headers
import teste
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

    # abs() garante tempo positivo mesmo se sA for negativo (movimento inverso)
    t = abs(int(sA / vA))

    query = f"vX={vX}&pX={sX}&vY=0&pY=0&vZ=0&pZ=0&vA={vA}&pA={sA}&s1=0&s2=0"

    print("movimento radial")
    print(query)
    enviar_comando(query)
    time.sleep(t + 1)


def tan_movement_corrigido(velocity, e, f, g, passo_mm, delta_alpha, R_f):
    vZ = velocity
    sZ = int(-1 * delta_alpha * (R_f + f) * passo_mm)

    t = int(abs(sZ / vZ))

    sY = int(delta_alpha * (R_f - g) * passo_mm)

    vY = int(-1 * sY / t)

    sA = int(delta_alpha * e / 2 * passo_mm)

    vA = int(-1 * sA / sZ * velocity)

    vX = vA
    sX = sA

    query = f"vX={vX}&pX={sX}&vY={vY}&pY={sY}&vZ={vZ}&pZ={sZ}&vA={vA}&pA={sA}&s1=0&s2=0"
    print("movimento tangencial")
    print(query)
    enviar_comando(query)
    time.sleep(t + 1)


def tan_movement(velocity, g, j, dp, distancia_tan, delta_alpha, r_i):
    sZ = int(delta_alpha * (r_i + g) / dp)
    vZ = velocity

    # abs() evita tempo negativo se delta_alpha for negativo
    t = abs(sZ / vZ)

    # Evita divisão por zero caso t seja 0 em micro-movimentos
    if t == 0:
        t = 0.1

    sY = int(-delta_alpha * (r_i - j) / dp)
    vY = abs(int(sY / t))

    sX = int(distancia_tan)
    vX = abs(int(sX / t))

    sA = sX
    vA = vX

    query = f"vX={vX}&pX={sX}&vY={vY}&pY={sY}&vZ={vZ}&pZ={sZ}&vA={vA}&pA={sA}&s1=0&s2=0"
    print("oi")
    print(query)
    enviar_comando(query)
    time.sleep(t + 1)


def exec():
    diameter = 101.9
    velocity = 400
    passo_volta = 1600
    dv = diameter * math.pi
    dp = dv / passo_volta

    passo_mm = passo_volta / dv

    x_raw, y_raw = get_position()
    x_i, y_i = int(x_raw), int(y_raw)
    r_i = math.sqrt(x_i**2 + y_i**2)
    alpha_i = math.atan2(y_i, x_i)

    x_raw, y_raw = get_position()
    x_f, y_f = int(x_raw), int(y_raw)
    r_f = math.sqrt(x_f**2 + y_f**2)
    alpha_f = math.atan2(y_f, x_f)

    delta_r = r_f - r_i
    delta_alpha = alpha_f - alpha_i

    g = 230
    j = 130

    e = g + j

    distancia_tan = (g + j) * delta_alpha
    passo_tan = distancia_tan / dv * passo_volta

    # rad_movement(velocity, delta_r, dp)

    tan_movement_corrigido(velocity, e, g, j, passo_mm, delta_alpha, r_f)

    # tan_movement(velocity, g, j, dp, distancia_tan, delta_alpha, r_i)


if __name__ == "__main__":
    exec()
