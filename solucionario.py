import os
from datetime import datetime
from logica.gestor_problemas import GestorProblemas
from metodos.bisectriz import calcular_tabla_bisectriz
# Aquí importarás los demás métodos conforme los vayas creando
# from metodos.falsa_posicion import calcular_tabla_falsa_posicion

def generar_reporte_pruebas():
    ruta_reporte = "Reporte_Validacion_Matematica.txt"
    
    with open(ruta_reporte, "w", encoding="utf-8") as archivo:
        archivo.write("=================================================================\n")
        archivo.write("REPORTE DE VALIDACIÓN MATEMÁTICA - PROYECTO ZERO LIMIT\n")
        archivo.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        archivo.write("=================================================================\n\n")

        # Obtenemos todos los problemas instanciados (ya con sus números aleatorios generados)
        problemas = GestorProblemas.obtener_todos_instanciados()

        for p in problemas:
            archivo.write(f"ID: {p['id']} - {p['titulo']}\n")
            archivo.write(f"Función: {p.get('funcion_display', p.get('funcion_python'))}\n")
            
            # Extraemos el primer método viable para resolverlo
            metodo = p.get("metodos_viables", [])[0] if p.get("metodos_viables") else None
            
            archivo.write(f"Método a evaluar: {metodo}\n")
            
            if metodo == "BISECTRIZ":
                a = p["valores_iniciales"]["a"]
                b = p["valores_iniciales"]["b"]
                tol = p["tolerancia"]
                archivo.write(f"Valores Iniciales Generados: a = {a}, b = {b}, Tolerancia = {tol}\n\n")
                
                # Llamamos a tu motor matemático
                resultado = calcular_tabla_bisectriz(p["funcion_python"], a, b, tol)
                
                if resultado["estado"] == "exito":
                    archivo.write(f"{'It':<4} | {'a':<10} | {'b':<10} | {'x_medio':<10} | {'f(x)':<10} | {'Error'}\n")
                    archivo.write("-" * 70 + "\n")
                    for fila in resultado["iteraciones"]:
                        err_str = str(fila['error']) if fila['error'] is not None else "---"
                        archivo.write(f"{fila['iteracion']:<4} | {fila['a']:<10} | {fila['b']:<10} | {fila['x_medio']:<10} | {fila['f_x_medio']:<10} | {err_str}\n")
                    archivo.write("\n>>> ESTADO: MÓDULO ESTABILIZADO (Cálculo Correcto)\n")
                else:
                    archivo.write(f"\n>>> ESTADO: FALLA EN EL MOTOR ({resultado['estado']})\n")
            
            # Aquí agregarías los 'elif' para FALSA_POSICION, NEWTON_RAPHSON, etc.
            elif metodo == "NEWTON_RAPHSON":
                archivo.write("[ Motor de Newton-Raphson pendiente de integración ]\n")
            else:
                archivo.write(f"[ Motor para {metodo} no implementado en el reporte aún ]\n")
                
            archivo.write("\n" + "="*65 + "\n\n")

    print(f"¡Reporte generado exitosamente en: {ruta_reporte}!")

if __name__ == "__main__":
    generar_reporte_pruebas()