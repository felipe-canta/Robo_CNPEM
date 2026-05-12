from requests.sessions import default_headers
import teste
import math
import requests
import time


def enviar_comando(msg_do_teste):
    url = "http://192.168.4.1/run"
    partes = msg_do_teste.split()

    if len(partes) == 5:
        # Mapeia os valores para os nomes que o seu código Arduino (API) espera
        payload = {
            "vX": partes[0],
            "pX": partes[1],
            "vY": partes[2],
            "pY": partes[3],
            "vZ": partes[4],
            "pZ": partes[5],
            "vA": partes[6],
            "pA": partes[7],
            "sA": partes[8],
        }

        try:
            print(f"\n[SISTEMA] Enviando: {payload}")
            # Realiza a chamada HTTP: http://192.168.4.1/run?vA=...&pA=...
            response = requests.get(url, params=payload, timeout=5)

            if response.status_code == 200:
                print(f"[ROBÔ] Resposta: {response.text}")
            else:
                print(f"[ERRO] Arduino retornou status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"[ERRO] Falha na conexão com o Wemos: {e}")
            print("Verifique se você está conectado no Wi-Fi 'Robo_da_PUC'")
    else:
        print(f"[ERRO] String inválida recebida do teste.py: '{msg_do_teste}'")


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


def rad_movement(velocity, delta_r, dp):
    vA = velocity
    sA = int(delta_r / dp)
    vX = vA
    sX = sA

    t = int(sA / vA)

    query = f"{vA} {sA} 0 0 0 0 {vX} {sX} 0 0"

    print(query)


def tan_movement(velocity, g, j, dp, distancia_tan, delta_alpha, r_i):
    sZ = int(delta_alpha * (r_i + g) / dp)
    vZ = velocity

    t = sZ / vZ

    sY = int(-delta_alpha * (r_i - j) / dp)
    vY = abs(int(sY / t))

    sX = int(distancia_tan)
    vX = abs(int(sX / t))

    sA = sX
    vA = vX

    query = f"{vX} {sX} {vY} {sY} {vZ} {sZ} {vA} {sA} 0 0"

    print(query)


def exec():
    diameter = 101.9
    velocity = 400
    passo_volta = 1600
    dv = diameter * math.pi
    dp = dv / passo_volta

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

    distancia_tan = (g + j) * delta_alpha
    passo_tan = distancia_tan / dv * passo_volta

    rad_movement(velocity, delta_r, dp)

    tan_movement(velocity, g, j, dp, distancia_tan, delta_alpha, r_i)


if __name__ == "__main__":
    exec()
