from requests.sessions import default_headers
import teste
import math
import requests
import time


def get_position():
    while True:
        pos = input("digite a coordenada inicial (Xi Yi) [mm]: ").split()
        result = list(map(float, pos))
        if len(pos) == 2:
            print(result)
            return result
        else:
            print("digitar apenas 2 digitos")
            break


"""
def enviar_comando(vX=0, pX=0, vY=0, pY=0, vZ=0, pZ=0, vA=0, pA=0, s1=0, s2=0, margem_delay=1.0):
    Monta a URL, envia para o robô e pausa a execução do Python pelo tempo necessário 
    para o robô terminar fisicamente o movimento, mais uma margem de segurança.
    
    # 1. Monta a string da query dinamicamente
    query = f"vX={vX}&pX={pX}&vY={vY}&pY={pY}&vZ={vZ}&pZ={pZ}&vA={vA}&pA={pA}&s1={s1}&s2={s2}"
    url = f"http://192.168.4.1/run?{query}"

    # 2. Calcula o tempo estimado de movimento
    # O tempo de um motor é a distância (passos) dividida pela velocidade.
    # O tempo total da manobra é o tempo do motor que demorar mais.
    tempos = [0] # Garante que haja pelo menos um valor na lista
    
    if vX != 0: tempos.append(abs(pX / vX))
    if vY != 0: tempos.append(abs(pY / vY))
    if vZ != 0: tempos.append(abs(pZ / vZ))
    if vA != 0: tempos.append(abs(pA / vA))

    tempo_movimento = max(tempos)
    tempo_total_espera = tempo_movimento + margem_delay

    # 3. Envia a requisição HTTP
    try:
        print(f"\n[SISTEMA] URL: {url}")
        print(f"[SISTEMA] Tempo de movimento: {tempo_movimento:.2f}s (Pausando por {tempo_total_espera:.2f}s)")
        
        # O timeout é apenas para a conexão de rede, não para o movimento
        response = requests.get(url, timeout=5)
2
        if response.status_code == 200:
            print(f"[ROBÔ] Resposta: {response.text}")
        else:
            print(f"[ERRO] Arduino retornou status: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na conexão com a placa: {e}")
        print("Verifique se você está conectado no Wi-Fi 'Robo_da_PUC'")
        return # Se deu erro de conexão, aborta o delay e sai da função

    # 4. Pausa o script Python enquanto o robô se move fisicamente
    if tempo_total_espera > margem_delay: 
        time.sleep(tempo_total_espera)
    else:
        # Se for só acionamento de servo sem mover as rodas, dorme só o delay
        time.sleep(margem_delay)
"""


def parada_emergencia():
    """Envia o comando de parada imediata para o Wemos"""
    url_stop = "http://192.168.4.1/stop"
    try:
        print("\n[!!!] CANCELAMENTO SOLICITADO [!!!]")
        print("Enviando ordem de parada para os motores...")
        requests.get(url_stop, timeout=2)
        print("[+] Robô imobilizado com sucesso.")
    except Exception as e:
        print(f"[ERRO FATAL] Não foi possível parar o robô: {e}")


def tempo_accel(passos, velocidade, aceleracao=1000):
    """Tempo real com rampa de aceleração do AccelStepper."""
    import math

    # Passos para atingir velocidade máxima
    passos_rampa = (velocidade**2) / (2 * aceleracao)
    if abs(passos) <= 2 * passos_rampa:
        # Movimento triangular: nunca atinge vmax
        t = 2 * math.sqrt(abs(passos) / aceleracao)
    else:
        # Movimento trapezoidal
        t_rampa = velocidade / aceleracao
        passos_cruzeiro = abs(passos) - 2 * passos_rampa
        t = 2 * t_rampa + passos_cruzeiro / velocidade
    return t


def enviar_comando(vX=0, pX=0, vY=0, pY=0, vZ=0, pZ=0, vA=0, pA=0, servo=1):
    query = f"vX={vX}&pX={pX}&vY={vY}&pY={pY}&vZ={vZ}&pZ={pZ}&vA={vA}&pA={pA}&s1={servo}&s2={servo}"
    url = f"http://192.168.4.1/run?{query}"
    try:
        print(f"\n[SISTEMA] Enviando requisição: {url}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[ROBÔ] Resposta: {response.text}")
        else:
            print(f"[ERRO] Arduino retornou status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na conexão com o Wemos: {e}")

        print("Verifique se você está conectado no Wi-Fi 'Robo_da_PUC'")


def parar_robo():
    enviar_comando()


def desenhar_cruz(velocity):
    delay = 3
    enviar_comando(servo=1)
    time.sleep(delay)

    enviar_comando()
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=305, vA=velocity, pA=-305)
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=254, vA=velocity, pA=-254)
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=1018, vA=velocity, pA=-1018, servo=1)
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=-1527, vA=velocity, pA=1527)
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=-1018, vA=velocity, pA=1018, servo=1)
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=1273, vA=velocity, pA=-1273)
    time.sleep(delay)

    enviar_comando(vY=velocity, pY=254, vZ=velocity, pZ=-254)
    time.sleep(delay)

    enviar_comando(vY=velocity, pY=1018, vZ=velocity, pZ=-1018, servo=1)
    time.sleep(delay)

    enviar_comando(vY=velocity, pY=-1527, vZ=velocity, pZ=-1527)
    time.sleep(delay)

    enviar_comando(vY=velocity, pY=-1018, vZ=velocity, pZ=1018, servo=1)
    time.sleep(delay)

    enviar_comando(vY=velocity, pY=1273, vZ=velocity, pZ=-1273)
    time.sleep(delay)

    enviar_comando(vX=velocity, pX=-305, vA=velocity, pA=305)
    time.sleep(delay)


def rad_movement(velocity, delta_r, dp):
    vA = velocity
    pA = round(delta_r / dp)
    vX = vA
    pX = -1 * pA

    # abs() garante tempo positivo mesmo se pA for negativo (movimento inverso)
    t = abs(int(pA / vA))

    query = f"vX={vX}&pX={pX}&vY=0&pY=0&vZ=0&pZ=0&vA={vA}&pA={pA}&s1=0&s2=0"

    print("movimento radial")
    print(query)
    enviar_comando(vX=vX, pX=pX, vA=vA, pA=pA)
    time.sleep(t + 1)


def tan_movement(velocity, e, f, g, passo_mm, delta_alpha, R_f):
    delta_alpha = math.atan2(math.sin(delta_alpha), math.cos(delta_alpha))

    # Rodas Y e Z: arco lateral (mantido)
    pZ = round(delta_alpha * (R_f + f) * passo_mm)
    pY = round(-delta_alpha * (R_f - g) * passo_mm)

    # Rodas X e A: giro em torno do laser tracker com sinais OPOSTOS
    pA = -round(delta_alpha * e / 2 * passo_mm)
    pX = pA  # ← CORREÇÃO PRINCIPAL

    if pX == 0 and pY == 0 and pZ == 0 and pA == 0:
        return

    max_passos = max(abs(pX), abs(pY), abs(pZ), abs(pA))
    t_real = max_passos / float(velocity)

    vX = abs(int(pX / t_real))
    vY = abs(int(pY / t_real))
    vZ = abs(int(pZ / t_real))
    vA = abs(int(pA / t_real))
    # Velocidade mínima 1 para motores que precisam mover
    if pX != 0 and vX == 0:
        vX = 10
    if pY != 0 and vY == 0:
        vY = 10
    if pZ != 0 and vZ == 0:
        vZ = 10
    if pA != 0 and vA == 0:
        vA = 10
    query = f"vX={vX}&pX={pX}&vY={vY}&pY={pY}&vZ={vZ}&pZ={pZ}&vA={vA}&pA={pA}&s1=0&s2=0"
    enviar_comando(vX, pX, vY, pY, vZ, pZ, vA, pA)
    time.sleep(t_real + 1)  # margem maior para compensar aceleração


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

    error = 1
    # desenhar_cruz(velocity)

    while True:
        x_raw, y_raw = get_position()
        x_i, y_i = float(x_raw), float(y_raw)
        r_i = math.sqrt(x_i**2 + y_i**2)
        alpha_i = math.atan2(y_i, x_i)

        x_raw, y_raw = get_position()
        x_f, y_f = float(x_raw), float(y_raw)
        r_f = math.sqrt(x_f**2 + y_f**2)
        alpha_f = math.atan2(y_f, x_f)
        if abs(x_i - x_f) <= error and abs(y_i - y_f) <= error:
            break
        delta_r = r_f - r_i
        delta_alpha = alpha_f - alpha_i

        if r_i >= r_f:
            rad_movement(velocity, delta_r, dp)
            tan_movement(velocity, e, g, j, passo_mm, delta_alpha, r_f)

        else:
            tan_movement(velocity, e, g, j, passo_mm, delta_alpha, r_f)
            rad_movement(velocity, delta_r, dp)


if __name__ == "__main__":
    try:
        exec()
    except KeyboardInterrupt:
        parada_emergencia()
