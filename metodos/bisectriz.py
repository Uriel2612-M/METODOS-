# metodos/bisectriz.py
import math 

def calcular_tabla_bisectriz(funcion_str, a, b, tolerancia, max_iteraciones=50):
    """
    Calcula la tabla completa de iteraciones para el Método de la Bisectriz.

    Args:
        funcion_str (str): La función a evaluar en formato Python (ej. "x**3 - 4.5*x + 1.5").
        a (float): Límite inferior del intervalo inicial.
        b (float): Límite superior del intervalo inicial.
        tolerancia (float): El error máximo permitido (ej. 0.001).
        max_iteraciones (int, opcional): Límite de seguridad para evitar bucles infinitos.
    """
    
    # 1. Validación inicial: ¿El intervalo encierra una raíz?
    try:
        x = a
        f_a = eval(funcion_str)
        x = b
        f_b = eval(funcion_str)
    except Exception as e:
         return {"estado": f"error_sintaxis: {e}", "iteraciones": []}

    if (f_a * f_b) > 0:
        return {"estado": "error_intervalo", "iteraciones": []}

    # 2. Inicialización de variables para el bucle
    iteraciones = []
    error = float('inf') 
    x_anterior = None
    paso = 1

    # 3. Bucle principal de la Bisectriz
    while (error is None or error > tolerancia) and paso <= max_iteraciones:
        # Calcular el punto medio según la fórmula de la inge: x = (a + b) / 2
        x_medio = (a + b) / 2
        
        # Calcular el error (a partir de la iteración 2)
        if paso > 1:
            error = abs(x_medio - x_anterior)
        else:
            error = None 
            
        # Evaluar la función en 'a' y en 'x_medio'
        x = a
        f_a = eval(funcion_str)
        
        x = x_medio
        f_x_medio = eval(funcion_str)
        
        # 4. Guardar los datos de esta iteración
        fila = {
            "iteracion": paso,
            "a": round(a, 6),      
            "b": round(b, 6),
            "x_medio": round(x_medio, 6),
            "f_x_medio": round(f_x_medio, 6),
            "error": round(error, 6) if error is not None else None
        }
        iteraciones.append(fila)
        
        if f_x_medio == 0.0:
            break
        
        # 6. Actualizar el intervalo
        if (f_a * f_x_medio) < 0:
            b = x_medio
        else:
            a = x_medio
            
        x_anterior = x_medio
        paso += 1
        
    if paso > max_iteraciones:
        return {"estado": "no_converge", "iteraciones": iteraciones}
    else:
        return {"estado": "exito", "iteraciones": iteraciones}


# =====================================================================
# PRUEBA INDEPENDIENTE 
# =====================================================================
if __name__ == "__main__":
    # Prueba basada en el apunte PB03
    funcion = "x**3 - 4.5*x + 1.5"
    a_inicial = 0.0
    b_inicial = 1.0
    tol = 0.001
    
    print("--- INICIANDO PRUEBA DEL MÉTODO DE LA BISECTRIZ ---")
    resultado = calcular_tabla_bisectriz(funcion_str=funcion, a=a_inicial, b=b_inicial, tolerancia=tol)
    
    if resultado["estado"] == "exito":
        print("¡Cálculo exitoso! Tabla de iteraciones:")
        print(f"{'It':<4} | {'a':<10} | {'b':<10} | {'x (Medio)':<10} | {'f(x)':<10} | {'Error'}")
        print("-" * 65)
        for fila in resultado["iteraciones"]:
            err_str = str(fila['error']) if fila['error'] is not None else "---"
            print(f"{fila['iteracion']:<4} | {fila['a']:<10} | {fila['b']:<10} | {fila['x_medio']:<10} | {fila['f_x_medio']:<10} | {err_str}")
    else:
        print(f"Falla detectada: {resultado['estado']}")