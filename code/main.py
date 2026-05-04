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
            "vA": partes[0],
            "pA": partes[1],
            "vX": partes[2],
            "pX": partes[3],
            "sA": partes[4],
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


def exec():
    # Parâmetros Mecânicos
    velocity = 500  # Velocidade padrão (passos/seg)
    passo_volta = 1600  # Configuração do Driver (Microstepping)
    wheel_diameter = 100  # mm
    wheel_radius = wheel_diameter / 2
    giro_const = 2.5  # Ajuste este valor se o robô girar mais ou menos que o pedido

    # Cálculo de quantos passos equivalem a 1mm
    perimetro = 2 * math.pi * wheel_radius
    passo_por_mm = passo_volta / perimetro

    while True:
        print("\n" + "=" * 40)
        print("      INTERFACE DE CONTROLE - CNPEM")
        print("=" * 40)
        print("1 - Mover em Reta (mm)")
        print("2 - Girar Robô (graus)")
        print("3 - Ajustar Velocidade")
        print("4 - Abrir/Fechar Garra (Servo)")
        print("5 - Modo Livre")
        print("0 - Sair")

        try:
            opcao = input("\nEscolha uma opção: ")

            if opcao == "0":
                print("Encerrando sistema...")
                break

            elif opcao == "1":
                dist = float(input("Distância para mover (mm): "))
                # Chama a lógica modularizada
                msg = teste.radial_movement(0, dist, velocity, passo_por_mm)
                enviar_comando(msg)

            elif opcao == "2":
                deg = float(input("Ângulo para girar (graus - positivo=direita): "))
                # Chama a lógica modularizada
                msg = teste.tangent_movement(deg, velocity, giro_const)
                enviar_comando(msg)

            elif opcao == "3":
                velocity = float(input(f"Velocidade atual é {velocity}. Nova: "))
                print(f"Velocidade alterada para {velocity}")

            elif opcao == "4":
                estado = input("Garra: 1 para ABRIR, 0 para FECHAR: ")
                # Envia comando parado (vel=0, passos=0) apenas para mexer o servo
                msg = f"0 0 0 0 {estado}"
                enviar_comando(msg)

            elif opcao == "5":
                servo, v1, p1, v2, p2 = input(
                    "crie o um comando livre ( servo, velocidade1, passo1, velocidade2, passo2 ): "
                ).split()
                msg = f"{v1} {p1} {v2} {p2} {servo}"

                enviar_comando(msg)

            else:
                print("Opção inválida!")

        except ValueError:
            print("Erro: Por favor, digite apenas números.")
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuário.")
            break


if __name__ == "__main__":
    exec()
