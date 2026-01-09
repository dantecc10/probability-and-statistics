# Probabilidad y Estadística
## Mtro. Pedro García Juárez
Los horarios de asesoría son:
- [Esperando]
- [Esperando]
- 9 - 11

Cubículo: [Esperando]
## Bibliografía
- ["Probabilidad y Estadística para ingenieros y ciencia"](https://github.com/dantecc10/probability-and-statistics/blob/master/8va-probabilidad-y-estadistica-para-ingenier-walpo_260109_092408.pdf "Ver libro")

## Contenidos
Probabilidad y Estadística
Contenidos:
#### Unidad 1:
#### Unidad 2:
#### Unidad 3:
#### Unidad 4:
#### Unidad 5:

## Criterios de evaluación
- Tarea
- Exámenes
- Participación
- Asistencia

**"Todo cuenta".**

## Sesiones
### Viernes 9 de enero
Se empieza a hablar de los criterios de evaluación.

Se habla de la primera tarea: grabar un video de 26 segundos en el que nos presentemos. Esta actividad contará como un examen. La calificación mínima será de un 7 en esta entrega.

#### Enfoques de la probabilidad
La probabilidad tiene varios enfoques, los más relevantes son:
- Clásico
- Frecuencial
- Axiomático
- Subjetivo

Probablemente (90%) el lunes realizaremos el primer *quiz*; sobre el tema **"enfoques de la probabilidad"** para el cual debemos investigar los enfoques de la probabilidad, características de cada uno y enfoques..

#### Espacio muestral
Los espacios muestrales van a depender directamente de un experimento: ¿qué entendemos por experimento?...

[Se pregunta a la clase: no todo aquí es de utilidad].

ChatGPT:
>En probabilidad y estadística, un experimento es un proceso o procedimiento bien definido que, al ejecutarse bajo las mismas condiciones, puede producir diferentes resultados, aunque el conjunto de resultados posibles sea conocido.
>
> Formalmente, un experimento se caracteriza por:
>
>- Ser reproducible: puede repetirse en condiciones similares.
> Tener resultados observables: cada ejecución genera un resultado identificable.
> Incertidumbre en el resultado individual: no se puede predecir con certeza qué resultado ocurrirá antes de realizarlo.
> Conjunto de resultados posibles conocido: dicho conjunto se denomina espacio muestral.
> Ejemplos:
>
>- Lanzar una moneda y observar si cae cara o cruz.
>
>- Medir el tiempo de vida útil de un foco.
>
>- Registrar el número de defectos en un lote de producción.
>
>- Extraer una carta de una baraja.






---

El espacio muestral es un conjunto no vacío con las posibilidades de un experimento y se suele denotar por "S".
Experimento 1:  Usemos el ejemplo de lanzar una moneda y realizar la anotación.
Espacio muestral: S = {"Águila", "Sol"}.

Experimento 2: Lanzar 2 veces un dado y realizar las anotaciones.
S = {(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), ..., (6, 6)}

Los eventos son subconjuntos del espacio muestral, así como el propio espacio muestral de sí mismo.

**Podemos afirmar que**

$$A \subseteq S$$

$$\varnothing \subseteq S$$

$$S \subseteq S$$

El espacio muestral se puede caracterizar por la probabilidad. Son equiprobables si cada evento tiene el mismo peso que todos los demás.
La cardinalidad de un espacio muestral depende del experimento: puede ser finito o infinito.
Algunos espacios muestrales infinitos son numerables, así como todos los finitos. Los infinitos son no numerables.

Los espacios muestrales **numerables** se conocen como **discretos**.

Los espacios muestrales **no numerables** se conocen como **continuos**.

¿Cómo asignar probabilidades?

Antes de asignar probabilidades a los subconjuntos del espacio es necesario obtener probabilidades a cada uno de los elementos del espacio.

Cuando la selección es aleatoria, todos los elementos del espacio muestral tienen la misma probabilidad de ser seleccionados.

**Probabilidad**

$P(S) = 1$

$P(S) = P(e_1) + P(e_2) + P(e_3) + \cdots + P(e_n)$

$P(S) = \sum_{i=1}^{n} P(e_i)$


Cuando se tiene un espacio muestral equiprobable y además es finito:


$$A \subseteq S$$

$$ P(A) = \frac{P(S)}{P(e_i)} $$


Cuando dos conjuntos no tienen elementos en común; son mutuamente excluyentes:

$A \cap B = \varnothing$

$P(A \cup B) = $P(A) + P(B)$

$P(S) = P(A \cup A')$

$P(A) + P(A') = 1$
