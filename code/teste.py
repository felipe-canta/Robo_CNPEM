import math


def distance(f_x, c_x, f_y, c_y):
    """Calcula a distância euclidiana entre dois pontos."""
    return math.sqrt((f_x - c_x) ** 2 + (f_y - c_y) ** 2)


def radial_movement(current_pos, final_pos, velocity, passo_por_mm):
    """
    Calcula o movimento em linha reta.
    current_pos e final_pos podem ser números (distância) ou coordenadas.
    O 'passo' aqui deve ser quanto 1mm vale em passos de motor.
    """

    servo = input("Garra: 1 para ABRIR, 0 para FECHAR: ")

    # Se você passar apenas a distância total como 'final_pos' e 0 como 'current_pos':
    dist_total = final_pos - current_pos

    # Calculando os passos necessários
    steps = dist_total * passo_por_mm

    # Formato: speed1 steps1 speed2 steps2 latch
    # Rodas giram na mesma direção para frente
    message = f"{velocity} {steps:.2f} {velocity} {steps:.2f} {servo}"
    return message


def tangent_movement(degrees, velocity, giro_const):
    """
    Calcula o giro sobre o próprio eixo.
    giro_const: constante que converte graus em passos de motor.
    """
    # Normaliza o ângulo para o menor caminho (-180 a 180)
    if degrees > 180:
        degrees -= 360
    elif degrees < -180:
        degrees += 360

    servo = input("Garra: 1 para ABRIR, 0 para FECHAR: ")

    # Para girar no próprio eixo, uma roda vai para frente e a outra para trás
    steps = degrees * giro_const

    # Roda 1 (positiva), Roda 2 (negativa) para rotacionar
    message = f"{velocity} {steps:.2f} {velocity} {-steps:.2f} {servo}"
    return message
