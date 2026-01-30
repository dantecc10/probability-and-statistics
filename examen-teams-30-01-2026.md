# Probabilidad y Estadística
## Mtro. Pedro García Juárez
### Examen en presencial en Teams: 30-01-2026

#### Pregunta 5
Considero innecesaria una justificación, es una pregunta de conocimiento teórico.

#### Pregunta 6

> "Se lanzan tres monedas sin truco y se realizan anotaciones. ¿Cuál es el tamaño del espacio muestral?"

El espacio muestral sería $S$:

$S = \\{(A, A, A), (A, A, S), (A, S, A), (S, A, A), (S, A, S), (S, S, A), (A, S, S), (S, S, S) \\}$

Esto es igual a *tres veces* la ejecución de un evento que tiene *dos posibilidades* equiprobables.

El tamaño del espacio muestra (*cardinalidad*) es **8**.

$2 \cdot 2 \cdot 2 = 2^3 = Card(S) = 8$


#### Pregunta 7

> "Se lanza un dado bien balanceado. ¿Cuál es la probabilidad de que salga un número primo o un número par?"

Debemos *determinar* los números *pares y primos* para poder *sumar los conjuntos* y obtener una probabilidad total con respecto al resto de números en el dado.

Recordamos que:
- Los números pares son aquellos que se pueden dividir entre dos con un residuo 0.
- Los números primos son aquellos que se pueden dividir sólo entre 1 y sí mismos (no tienen factores de descomposición). No se cuenta al 1.

Números pares presentes en el dado ($S_Pares$):

$S_Pares = \\{2, 4, 6 \\}$

Números primos presentes en el dado ($S_Primos$):

$S_Primos = \\{2, 3, 5 \\}$

La respuesta a la pregunta es $(S_Pares \cup S_Primos)$:

$\\{2, 4, 6 \\} \cup \\{1, 2, 3, 5 \\} = \\{2, 3, 4, 5, 6 \\}$

La cardinalidad de la unión anterior es 5:

$Card(S_Pares \cup S_Primos) = 5 \therefore$ la probabilidad de que salga un primo o impar es $\frac{5}{6}$

#### Pregunta 8 

Desconozco la composición de una baraja. Imagino que puede haber más cartas de cierta imagen que de otra; si no fuera el caso, además de ser **independientes**, serían _equiprobables_.

#### Pregunta 9

Seré breve con mi notación y usaré las iniciales de los colores.

$S = \\{R, R, R, R, R, A, A, A, V, V \\}$

$S_{(S_R \cup S_A)} = \\{R, R, R, R, R, A, A, A \\}$

$Card(S_{(S_R \cup S_A)}) = 8$

#### Pregunta 11

$6 \cdot 6$: *dos veces* la ejecución de un evento de *6 posibilidades*. Como ya denoté -en un contexto similar- en la respuesta a la _pregunta 6_.

#### Pregunta 12

> "Si la probabilidad de que eun estudiante apruebe el examen de matemáticas es de 0.8, y la de que apruebe el de física es de 0.7, y la probabilidad de que apruebe ambos es de 0.6. ¿Cuál es la probabilidad de que apruebe al menos uno de los dos exámenes?"

Sean

$S_M = .8$ la probabilidad de aprobar matemáticas,

$S_F = .7$ la probabilidad de aprobar física,

$S_A = S_M \cap S_F = .6 la probabilidad de aprobar ambos,

significa que $P(S_M|S_F)$ y $P(S_F|S_M)$ es igual a $.6$.
 
La probabilidad de aprobar sólo uno es de $P(S_M|S_F')$ **_y_** $P(S_F|S_M')$.

Sea la equivalencia $P(A | B) = \frac{A \cdot B}{B}$.

Sustituyo:

$P(S_M|S_F') = \frac{S_M \cdot S_F'}{S_F'} = \frac{.8 \cdot .3}{.3} = \frac{.24}{.3}$

$P(S_F|S_M') = \frac{S_F \cdot S_M'}{S_M'} = \frac{.7 \cdot .2}{.2} = \frac{.14}{.2}$

Falta aplicar una suma.

#### Pregunta 13

Sea el espacio muestral:

$S = \\{(P), (R), (O), (B), (A), (B), (I), (L), (I), (D), (A), (D) \\}$

$S_P = \\{P \\}$

$S_R = \\{R \\}$

$S_O = \\{O \\}$

$S_B = \\{B, B \\}$

$S_A = \\{A, A \\}$

$S_I = \\{I, I \\}$

$S_L = \\{L \\}$

$S_D = \\{D, D \\}$


