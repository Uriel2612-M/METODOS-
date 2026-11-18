# Mínimos Cuadrados e Integración Numérica — documentación de implementación

Este documento describe lo que se agregó al proyecto ZERO LIMIT para la parte de **Mínimos Cuadrados** y **Integración Numérica** (Modo Desafío, Etapa 3, y Modo Práctica), cómo verificarlo y cómo integrarlo al repositorio sin afectar el trabajo de otros integrantes.

## 1. Alcance

| Área | Qué se agregó | Estado |
|---|---|---|
| Mínimos Cuadrados | 5 motores: Línea Recta, Cuadrática, Cúbica, Lineal con Función, Cuadrática con Función | Motores listos y verificados; solo hay problemas jugables para Línea Recta y Cuadrática |
| Integración | Trapecio, Simpson 1/3, Simpson 3/8, Newton-Cotes cerradas | Motores listos y verificados; hay problemas jugables para los cuatro |
| Banco de problemas (Nivel 3) | N3_08 a N3_11 agregados al final de `banco_problemas_nivel3.json` | Ver sección 4 |

No se modificó ningún archivo existente de lógica, interfaces ni de otros métodos. La única modificación de un archivo existente es la adición de cuatro entradas al final de `banco_problemas_nivel3.json`.

## 2. Archivos

Nuevos:

- `metodos/minimos_cuadrados.py`: los cinco motores de mínimos cuadrados.
- `metodos/trapecio.py` (`TRAPECIO`).
- `metodos/simpson_1_3.py` (`SIMPSON_1_3`).
- `metodos/simpson_3_8.py` (`SIMPSON_3_8`).
- `metodos/newton_cotes_cerradas.py` (`NEWTON_COTES_CERRADAS`).
- `documentacion/verificacion_minimos_integracion.py`: script de verificación (ver sección 6).
- `documentacion/INTEGRACION_MINIMOS_CUADRADOS_E_INTEGRACION.md`: este documento.

Modificados:

- `recursos/banco_problemas_nivel3.json`: se agregan N3_08, N3_09, N3_10 y N3_11. Las entradas existentes no cambian.

## 3. Cómo funciona

### 3.1 Registro de métodos

Cada motor se registra con `@registrar_metodo("NOMBRE")` (`logica/gestor_metodos.py`). El nombre debe coincidir con `metodos_viables` del JSON. El juego carga los archivos de `metodos/` automáticamente.

Cada motor devuelve una lista de pasos. Cada paso tiene `corto`, `etiqueta`, `formula` y `valor`. El último paso es el resultado final.

### 3.2 Mínimos Cuadrados

Los nombres de método y de los pasos siguen los PDF del proyecto:

| Método (JSON) | Modelo (PDF) | Base |
|---|---|---|
| `MINIMOS_CUADRADOS_LINEAL` | Línea Recta | 1, x |
| `MINIMOS_CUADRADOS_CUADRATICA` | Cuadrática | 1, x, x² |
| `MINIMOS_CUADRADOS_CUBICA` | Cúbica | 1, x, x², x³ |
| `MINIMOS_CUADRADOS_LINEAL_FUNCION` | Lineal con Función | 1, x, f(x) |
| `MINIMOS_CUADRADOS_CUADRATICA_FUNCION` | Cuadrática con Función | 1, x, x², f(x) |

Procedimiento, igual al de `LíneaRecta.pdf`:

1. Sumatorias: `n`, `Σx`, `Σx²`, ..., `Σy`, `Σxy`, ... (la matriz es simétrica, cada suma se calcula una vez).
2. Eliminación: se calcula un factor, se multiplica una ecuación y se suma a la siguiente. Se registran los coeficientes y términos independientes resultantes.
3. Sustitución hacia atrás: se obtienen los coeficientes desde el último.
4. Resultado final: el valor indicado en `resultado_final` del problema. Puede ser un coeficiente (`"a0"`, `"a1"`, `"a2"`…) o `"g(x)"`, que evalúa el modelo en `x_interpolar`.

Para 3×3 y 4×4 se usa el mismo procedimiento de eliminación que el PDF muestra para 2×2.

**`resultado_final` es obligatorio.** Si un problema no lo define, el motor lo rechaza y el juego no lo muestra. Es una decisión deliberada para no adivinar qué debe responder el jugador.

### 3.3 Integración

Las fórmulas son las de los PDF `RTMN.pdf`, `R1tercioSimpson.pdf`, `R3octavosSimpson.pdf` y `TNewtonCotesAyC.pdf` / `RNewtonC-Cerradas.pdf` (OneDrive):

- Trapecio: `h = (b−a)/n`, `I = (h/2)[f(a) + 2Σf(interiores) + f(b)]`.
- Simpson 1/3: `I = (h/3)[f(a) + 4Σimpares + 2Σpares + f(b)]`, con n par.
- Simpson 3/8: `I = (3h/8)[f(a) + 3Σ(no múltiplos de 3) + 2Σ(múltiplos de 3) + f(b)]`, con n múltiplo de 3.
- Newton-Cotes cerradas: `I = h · C_n · Σ w_i f(x_i)`, con C_n y w_i de la tabla de constantes, para n = 1 a 10.

### 3.4 Precisión

- Todos los valores que ve el jugador se redondean a 6 decimales.
- Los cálculos internos no se redondean.
- El margen de error es el margen por defecto del motor de práctica (0.0002). Los PDF no indican otro.

## 4. Banco de problemas agregado (Nivel 3)

| ID | Método | Fuente | Respuesta final |
|---|---|---|---|
| N3_08 | `NEWTON_COTES_CERRADAS` | Ejemplo ∫₀¹(1−x²)dx de `TNewtonCotesAyC.pdf` y `RNewtonC-Cerradas.pdf`. Los valores de n (2, 4, 6) son elección del banco. | I |
| N3_09 | `MINIMOS_CUADRADOS_CUADRATICA` | Ejercicio 1 de mínimos cuadrados con cuadrática, UPV/EHU (Virginia Muto Foresi), https://ocw.ehu.eus/file.php/81/prob4.pdf. Datos: 6 puntos. | a2 |
| N3_10 | `MINIMOS_CUADRADOS_CUADRATICA` | Problema 9.4, *Métodos numéricos: problemas resueltos y prácticas* (Isaac García y Susanna Maza), capítulo 9. El libro da x0 = 1,26571. | a0 (x0) |
| N3_11 | `SIMPSON_1_3` | Problema 6.3, mismo libro, capítulo 6. El libro da L ≈ 23,8104 con n = 4. | I |

Notas:

- En N3_10 los datos se perturban ±0.3 en cada partida, así que el resultado cambia. El libro pide x0, v0 y a; el banco pide solo x0.
- En N3_11 el libro usa solo n = 4. Los valores n = 2 y n = 6 son variantes del banco, para que el resultado cambie.
- N3_08 siempre da 2/3: la función es un polinomio y las reglas con n ≤ 6 lo integran exactamente. La aleatoriedad solo cambia los pasos.

## 5. Correcciones a fuentes

- **Tabla de Newton-Cotes (`ConstantesN-CotesAC.pdf`):** al comprobar que cada fila integra exactamente polinomios de grado ≤ n, se encontraron dos errores de transcripción:
  - n = 8: C_n = 4/14175 (el PDF dice 14/14175), y los pesos de i = 3 e i = 5 son 10496 (el PDF dice 10946).
  - n = 9: el peso de i = 4 e i = 5 es 5778 (el PDF dice 5788).

  El código usa los valores corregidos y lo documenta en el comentario. Conviene que el equipo lo confirme.
- **Simpson 3/8 (`R3octavosSimpson.pdf`):** dice "n siempre impar", pero el propio ejemplo y la fórmula usan múltiplos de 3. El código usa múltiplos de 3.

## 6. Verificación

Ejecutar desde la raíz del proyecto:

```
python documentacion/verificacion_minimos_integracion.py
```

Comprueba:

1. Línea Recta con los datos de `LíneaRecta.pdf`: a1 = 0.633695, a0 = 2.008444, g(1.1) = 2.705508.
2. Cuadrática del libro 9.4: x0 ≈ 1.26571.
3. Integración contra los PDF y el libro: trapecio 0.65625, Simpson 1/3 2/3, Simpson 3/8 2/3, Newton-Cotes 2/3, Simpson 1/3 del libro 23.8104.
4. Newton-Cotes exacta para x³ con n = 2 a 10.
5. Etapa 3: 40 simulaciones con respuestas correctas paso a paso.

Resultados al momento de la entrega: todas las comprobaciones pasan.

Además se probó la interfaz gráfica bajo una pantalla virtual (Xvfb): la Etapa 3 con trapecio, Simpson 1/3, Simpson 3/8, Newton-Cotes, cuadrática (N3_09, N3_10) y Simpson 1/3 (N3_11); respuestas incorrectas y texto no numérico; y el Modo Práctica con PRACTICA_08.

## 7. Problemas pendientes

1. **Cúbica, Lineal con Función y Cuadrática con Función:** los motores funcionan, pero no hay problemas jugables. No encontramos datos verificables en el libro ni en fuentes públicas, y no se inventaron.
2. **N3_01 y N3_02 (no son de esta parte):** no tienen `resultado_final`, así que el motor los descarta. Para N3_01 el campo sugerido es `"resultado_final": "a1"`. Para N3_02 también faltan `x_min` y `x_max` (para la predicción) y `"resultado_final": "g(x)"`. Lo debe agregar quien los mantiene.
3. **PRACTICA_07 (banco de práctica, no es de esta parte):** no tiene `resultado_final`. Al pulsar su protocolo en la interfaz no ocurre nada y no hay mensaje. Hay que definir qué valor pide el jugador, porque el procedimiento del documento muestra dos coeficientes (a0 y a1).
4. **Entrada de datos del jugador:** el juego no tiene ninguna pantalla donde el jugador ingrese sus propios datos. Solo ingresa los valores de cada paso. Si la especificación lo pide, hay que diseñar esa pantalla.

Problemas de interfaz encontrados en código compartido (no se modificaron):

- En "SIN PROTOCOLOS DISPONIBLES", la lista de pendientes sale vacía cuando los problemas se descartan por falta de `resultado_final`. El mensaje debería listar los problemas descartados.
- En el Modo Práctica, el botón de PRACTICA_07 no muestra ningún aviso cuando el motor rechaza el problema.
- En el enunciado de Etapa 3, "Nuevas lecturas (Y)" aparece antes que "Lecturas (X)".

## 8. Problemas del libro descartados

No se pudieron implementar directamente:

- Capítulo 9: 9.1 (base sin t, cos²t), 9.2 y 9.3 (requieren linealizar con logaritmos, paso que no está en los PDF), 9.5 y 9.8 (ajustes no lineales y Lagrange), 9.6 (ecuación diferencial), 9.7 (aproximación continua de Fourier).
- Capítulo 6: 6.1 (sin(x)/x no se evalúa en x = 0), 6.2 (la función es ilegible en el PDF), 6.4 (integral impropia), 6.5 (Gauss-Chebyshev), 6.9 (Romberg).
- 6.10 y 6.11 no se revisaron en detalle.

## 9. Cómo integrar al repositorio

Estos pasos no reemplazan el repositorio. Solo agregan un commit en una rama nueva.

1. Actualizar el repositorio y crear la rama desde `main`:

   ```
   git checkout main
   git pull
   git checkout -b feature/minimos-integracion
   ```

2. Copiar los archivos nuevos y el JSON modificado a la carpeta del repositorio. Los archivos deben tener finales de línea LF, que es como están en el repositorio. Si tu copia local usa CRLF por `core.autocrlf=true`, Git lo convierte solo.

3. Agregar **solo** estos archivos. No usar `git add .` ni `git add -A`, porque el repositorio tiene archivos `__pycache__` rastreados y podrían entrar al commit:

   ```
   git add metodos/minimos_cuadrados.py metodos/trapecio.py metodos/simpson_1_3.py metodos/simpson_3_8.py metodos/newton_cotes_cerradas.py recursos/banco_problemas_nivel3.json documentacion/verificacion_minimos_integracion.py documentacion/INTEGRACION_MINIMOS_CUADRADOS_E_INTEGRACION.md
   ```

4. Revisar que el diff solo tenga adiciones en el JSON:

   ```
   git diff --cached --stat
   git diff --cached recursos/banco_problemas_nivel3.json
   ```

   El JSON no debe mostrar líneas quitadas (`-`).

5. Ejecutar la verificación sin generar archivos `.pyc`, para no modificar los `__pycache__` rastreados:

   ```
   PYTHONDONTWRITEBYTECODE=1 python documentacion/verificacion_minimos_integracion.py
   ```

6. Hacer el commit:

   ```
   git commit -m "Agrega motores de Mínimos Cuadrados e Integración (Trapecio, Simpson 1/3 y 3/8, Newton-Cotes) y problemas N3_08 a N3_11"
   git push -u origin feature/minimos-integracion
   ```

7. Antes de hacer merge a `main`, confirmar con tu equipo los puntos de la sección 7, sobre todo N3_01, N3_02 y PRACTICA_07, que no son de esta parte.

**Qué no hacer:**

- No reemplazar la carpeta del repositorio con el ZIP. El ZIP viene sin `.git` y con finales de línea CRLF.
- No hacer commit de `__pycache__`.
- No modificar `N3_01` ni `N3_02` en esta rama.
- No cambiar el orden de las entradas existentes del JSON.

Si Git indica conflictos en `banco_problemas_nivel3.json` porque otro integrante también agregó problemas al final, resuélvelo manteniendo ambos bloques y verificando que el archivo siga siendo JSON válido (`python -c "import json; json.load(open('recursos/banco_problemas_nivel3.json', encoding='utf-8'))"`).
