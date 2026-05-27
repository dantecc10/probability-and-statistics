# Capítulo 2 - Ejercicios resueltos

---

## Índice de ejercicios

- [X] Ejercicio 2.2
- [X] Ejercicio 2.3
- [X] Ejercicio 2.4
- [X] Ejercicio 2.5
- [X] Ejercicio 2.6
- [X] Ejercicio 2.7
- [X] Ejercicio 2.8
- [X] Ejercicio 2.9
- [X] Ejercicio 2.10
- [X] Ejercicio 2.26
- [X] Ejercicio 2.27
- [X] Ejercicio 2.28
- [X] Ejercicio 2.29
- [X] Ejercicio 2.30
- [X] Ejercicio 2.31
- [X] Ejercicio 2.32
- [X] Ejercicio 2.33
- [X] Ejercicio 2.34
- [X] Ejercicio 2.35
- [X] Ejercicio 2.36
- [X] Ejercicio 2.37
- [X] Ejercicio 2.38
- [X] Ejercicio 2.39
- [X] Ejercicio 2.40
- [X] Ejercicio 2.41
- [X] Ejercicio 2.42
- [X] Ejercicio 2.48
- [X] Ejercicio 2.94

---

## Ejercicios

### Ejercicio 2.2

> Utilice el método de la regla para describir el espacio muestral $S$, que consta de todos los puntos del primer cuadrante dentro de un círculo de radio 3 con centro en el origen.

Solución:

Planteamiento:

Los puntos del círculo de radio $3$ con centro en el origen cumplen:

$$
x^2 + y^2 \le 9
$$

Además, al estar en el primer cuadrante, se exige:

$$
x > 0, \quad y > 0
$$

Resultado:

$$
S = \{(x,y) \mid x^2 + y^2 \le 9,\; x>0,\; y>0\}
$$

---

### Ejercicio 2.3

> ¿Cuáles de los siguientes eventos son iguales?
>
> a) $A = \{1, 3\}$;
>
> b) $B = \{x \mid x$ es un número de un dado$\}$;
>
> c) $C = \{x \mid x^2 - 4x + 3 = 0\}$;
>
> d) $D = \{x \mid x$ es el número de caras cuando se lanzan seis monedas al aire$\}$.

Solución:

Primero identifico cada conjunto:

$$
A = \{1,3\}
$$

$$
B = \{1,2,3,4,5,6\}
$$

Para $C$ resuelvo la ecuación:

$$
x^2 - 4x + 3 = 0 \Rightarrow (x-1)(x-3)=0
$$

$$
C = \{1,3\}
$$

Y para $D$, el número de caras al lanzar 6 monedas puede ser $0$ hasta $6$:

$$
D = \{0,1,2,3,4,5,6\}
$$

Conclusión:

$$
A = C
$$

Los demás no son iguales entre sí.

---

### Ejercicio 2.4

> Un experimento implica lanzar un par de dados, uno verde y uno rojo, y al registrar los números que resultan. Si $x$ es igual al resultado en el dado verde y $y$ es el resultado en el dado rojo, describa el espacio muestral $S$
>
> a) mediante la lista de los elementos $(x, y)$;
>
> b) por medio del método de la regla.

Solución:

a) Por lista:

$$
S = \{(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),
(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),
(3,1),(3,2),(3,3),(3,4),(3,5),(3,6),
(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),
(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),
(6,1),(6,2),(6,3),(6,4),(6,5),(6,6)\}
$$

b) Por método de la regla:

$$
S = \{(x,y) \mid x \in \{1,2,3,4,5,6\},\; y \in \{1,2,3,4,5,6\}\}
$$

---

### Ejercicio 2.5

> Un experimento consiste en lanzar un dado y después lanzar una moneda una vez si el número en el dado es par. Si el número en el dado es impar, la moneda se lanza dos veces. Use la notación $4H$, por ejemplo, para denotar el resultado de que el dado muestre 4 y después la moneda caiga en cara, y $3HT$ para denotar el resultado de que el dado muestre 3, seguido por una cara y después una cruz en la moneda; construya un diagrama de árbol para mostrar los 18 elementos del espacio muestral $S$.

Solución:

Defino el espacio muestral:

$$
S = \{1HH,1HT,1TH,1TT,2H,2T,3HH,3HT,3TH,3TT,4H,4T,5HH,5HT,5TH,5TT,6H,6T\}
$$

Tiene $18$ resultados en total: $12$ cuando sale impar (2 lanzamientos de moneda) y $6$ cuando sale par (1 lanzamiento de moneda).

---

### Ejercicio 2.6

> De un grupo de cuatro suplentes se seleccionan dos jurados para servir en un juicio por homicidio. Utilice la notación $A_1A_3$, por ejemplo, para denotar el evento simple de que se seleccionen los suplentes 1 y 3, liste los 6 elementos del espacio muestral $S$.

Solución:

$$
S = \{A_1A_2,\; A_1A_3,\; A_1A_4,\; A_2A_3,\; A_2A_4,\; A_3A_4\}
$$

Son las $\binom{4}{2}=6$ formas de elegir 2 suplentes de 4.

---

### Ejercicio 2.7

> De un grupo de estudiantes de química se seleccionan cuatro al azar y se clasifican como hombre o mujer. Liste los elementos del espacio muestral $S_1$ usando la letra $H$ para hombre y $M$ para mujer. Defina un segundo espacio muestral $S_2$ donde los elementos representen el número de mujeres seleccionadas.

Solución:

$$
S_1 = \{HHHH, HHHM, HHMH, HHMM, HMHH, HMHM, HMMH, HMMM,
MHHH, MHHM, MHMH, MHMM, MMHH, MMHM, MMMH, MMMM\}
$$

$$
S_2 = \{0,1,2,3,4\}
$$

---

### Ejercicio 2.8

> Para el espacio muestral del ejercicio 2.4,
>
> a) liste los elementos que corresponden al evento $A$ de que la suma sea mayor que 8;
>
> b) liste los elementos que corresponden al evento $B$ de que ocurra un 2 en cualquiera de los dos dados;
>
> c) liste los elementos que corresponden al evento $C$ de que salga un número mayor que 4 en el dado verde;
>
> d) liste los elementos que corresponden al evento $A \cap C$;
>
> e) liste los elementos que corresponden al evento $A \cap B$;
>
> f) liste los elementos que corresponden al evento $B \cap C$;
>
> g) construya un diagrama de Venn para ilustrar las intersecciones y uniones de los eventos $A$, $B$ y $C$.

Solución:

a)

$$
A = \{(3,6),(4,5),(4,6),(5,4),(5,5),(5,6),(6,3),(6,4),(6,5),(6,6)\}
$$

b)

$$
B = \{(1,2),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(3,2),(4,2),(5,2),(6,2)\}
$$

c)

$$
C = \{(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),(6,1),(6,2),(6,3),(6,4),(6,5),(6,6)\}
$$

d)

$$
A \cap C = \{(5,4),(5,5),(5,6),(6,3),(6,4),(6,5),(6,6)\}
$$

e)

$$
A \cap B = \varnothing
$$

f)

$$
B \cap C = \{(5,2),(6,2)\}
$$

g) Resumen para el diagrama de Venn:

$$
A \cap B = \varnothing, \quad A \cap C = \{(5,4),(5,5),(5,6),(6,3),(6,4),(6,5),(6,6)\},
$$

$$
B \cap C = \{(5,2),(6,2)\}, \quad A \cap B \cap C = \varnothing
$$

---

### Ejercicio 2.9

> Para el espacio muestral del ejercicio 2.5:
>
> a) liste los elementos que corresponden al evento $A$ en el que el dado salga un número menor que 3;
>
> b) liste los elementos que corresponden al evento $B$ de que resulten 2 cruces;
>
> c) liste los elementos que corresponden al evento $A'$;
>
> d) liste los elementos que corresponden al evento $A' \cap B$;
>
> e) liste los elementos que corresponden al evento $A \cup B$.

Solución:

a)

$$
A = \{1HH,1HT,1TH,1TT,2H,2T\}
$$

b)

$$
B = \{1TT,3TT,5TT\}
$$

c)

$$
A' = \{3HH,3HT,3TH,3TT,4H,4T,5HH,5HT,5TH,5TT,6H,6T\}
$$

d)

$$
A' \cap B = \{3TT,5TT\}
$$

e)

$$
A \cup B = \{1HH,1HT,1TH,1TT,2H,2T,3TT,5TT\}
$$

---

### Ejercicio 2.10

> Se contrata a una empresa de ingenieros para que determine si ciertas vías fluviales en Virginia, Estados Unidos, son seguras para la pesca. Se toman muestras de tres ríos.
>
> a) Liste los elementos de un espacio muestral $S$ y utilice las letras $P$ para seguro para la pesca y $N$ para inseguro para la pesca.
>
> b) Liste los elementos de $S$ que correspondan al evento $E$ de que al menos dos de los ríos son seguros para la pesca.
>
> c) Defina un evento que tiene como elementos a los puntos $\{PPP, NPP, PPN, NPNP\}$.

Solución:

a)

$$
S = \{PPP, PPN, PNP, PNN, NPP, NPN, NNP, NNN\}
$$

b)

$$
E = \{PPP, PPN, PNP, NPP\}
$$

c)

Defino el evento:

$$
F = \{PPP, NPP, PPN, NPN\}
$$

Nota: en el enunciado aparece $NPNP$, pero para tres ríos corresponde trabajar con ternas; por eso se corrige a $NPN$.

---

### Ejercicio 2.26

> Un estudio en California concluyó que siguiendo siete sencillas reglas para la salud un hombre y una mujer pueden prolongar su vida 11 y 7 años en promedio, respectivamente. Estas 7 reglas son: no fumar, hacer ejercicio de manera habitual, moderar su consumo de alcohol, dormir siete u ocho horas, mantener el peso adecuado, desayunar y no ingerir alimentos entre comidas. ¿De cuántas formas puede una persona adoptar cinco de estas reglas:
>
> a) si la persona actualmente infringe las siete reglas?
>
> b) si la persona nunca bebe y siempre desayuna?

Solución:

a) Si infringe las 7, debe elegir 5 de las 7 reglas:

$$
N_a = \binom{7}{5} = 21
$$

b) Si ya cumple 2 reglas (nunca bebe y siempre desayuna), para adoptar en total 5 debe elegir 3 adicionales de las otras 5:

$$
N_b = \binom{5}{3} = 10
$$

---

### Ejercicio 2.27

> Un urbanista de un nuevo fraccionamiento ofrece a un posible comprador de una casa elegir entre 4 diseños, 3 diferentes sistemas de calefacción, un garaje o cobertizo, y un patio o un porche cubierto. ¿De cuántos planos diferentes dispone el comprador?

Solución:

Planteamiento:

Como hay:

* 4 diseños
* 3 diferentes sistemas de calefacción
* un garaje o cobertizo (2 opciones)
* y un patio o porche cubierto (otras 2 opciones)

$$
N = (4 \cdot 3 \cdot 2 \cdot 2)
$$

Resultado:

$$
N = 48
$$

### Ejercicio 2.28

> Un medicamento para aliviar el asma se puede adquirir en 5 diferentes laboratorios y en forma de líquido, comprimidos o cápsulas, todas en concentración normal o alta. ¿De cuántas formas diferentes puede un médico recetar la medicina a un paciente que sufre de asma?

Solución:

Planteamiento:

Hay 3 decisiones independientes para recetar:

- laboratorio: $5$ opciones;
- presentación: líquido, comprimidos o cápsulas ($3$ opciones);
- concentración: normal o alta ($2$ opciones).

Por la regla del producto:

$$
N = 5 \cdot 3 \cdot 2
$$

Resultado:

$$
N = 30
$$

---

### Ejercicio 2.29

> En un estudio económico de combustibles, cada uno de 3 autos de carreras se prueba con 5 marcas diferentes de gasolina en 7 lugares de prueba que se localizan en diferentes regiones del país. Si en el estudio se utilizan 2 pilotos y las pruebas se realizan una vez en cada uno de los distintos grupos de condiciones, ¿cuántas pruebas se necesita realizar?

Solución:

Planteamiento:

Cada prueba queda determinada por:

- auto de carreras: $3$ opciones;
- marca de gasolina: $5$ opciones;
- lugar de prueba: $7$ opciones;
- piloto: $2$ opciones.

Aplicando la regla del producto:

$$
N = 3 \cdot 5 \cdot 7 \cdot 2
$$

Resultado:

$$
N = 210
$$

Se requieren $210$ pruebas.

---

### Ejercicio 2.30

> ¿De cuántas formas distintas se puede responder una prueba de falso-verdadero que consta de 9 preguntas?

Solución:

Planteamiento:

Cada pregunta de falso-verdadero tiene $2$ respuestas posibles y hay $9$ preguntas.

$$
N = 2^9
$$

Resultado:

$$
N = 512
$$

---

### Ejercicio 2.31

> Un testigo de un accidente automovilístico le dijo a la policía que la matrícula del culpable, que huyó, contenía las letras RLH seguidas por 3 dígitos, de los cuales el primero era un 5. Si el testigo no recuerda los 2 últimos dígitos, pero está seguro de que los 3 eran distintos, calcule la cantidad máxima de registros de automóviles que la policía tendría que revisar.

Solución:

Planteamiento:

La matrícula tiene letras fijas $RLH$ y luego 3 dígitos.

Se sabe que:

- el primer dígito es $5$ (fijo);
- los tres dígitos son distintos.

Entonces:

- segundo dígito: puede ser cualquier dígito excepto $5$ $\Rightarrow 9$ opciones;
- tercer dígito: no puede repetir ni el $5$ ni el segundo elegido $\Rightarrow 8$ opciones.

$$
N = 9 \cdot 8
$$

Resultado:

$$
N = 72
$$

La policía tendría que revisar como máximo $72$ registros.

---

### Ejercicio 2.32

> a) ¿De cuántas maneras se pueden formar 6 personas para abordar un autobús?
>
> b) ¿Cuántas maneras son posibles si, de las 6, 3 personas específicas insisten en formarse una después de la otra?
>
> c) ¿De cuántas maneras se pueden formar si, de las 6, 2 personas específicas se rehúsan a formarse una detrás de la otra?

Solución:

a) Personas en fila sin restricciones:

$$
N_a = 6! = 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1 = 720
$$

b) Si 3 personas específicas deben ir juntas:

Las 3 personas se tratan como un bloque. Entonces hay $4$ objetos en total (bloque + 3 personas restantes):

$$
4! = 4\cdot 3\cdot 2\cdot 1
$$

y dentro del bloque se pueden ordenar de:

$$
3! = 3\cdot 2\cdot 1
$$

Por tanto:

$$
N_b = (4\cdot 3\cdot 2\cdot 1)(3\cdot 2\cdot 1) = 24\cdot 6 = 144
$$

c) Si 2 personas específicas no quieren ir juntas:

Primero el total sin restricción:

$$
6! = 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1 = 720
$$

Ahora resto los casos en los que sí van juntas. Si van juntas, se consideran un bloque:

- objetos a ordenar: $5$ (bloque + 4 personas) $\Rightarrow 5!$;
- orden interno del bloque: $2!$.

$$
N_{\text{juntas}} = (5\cdot 4\cdot 3\cdot 2\cdot 1)(2\cdot 1) = 120\cdot 2 = 240
$$

Entonces:

$$
N_c = (6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1) - (5\cdot 4\cdot 3\cdot 2\cdot 1)(2\cdot 1) = 720 - 240 = 480
$$

---

### Ejercicio 2.33

> Si una prueba de opción múltiple consta de 5 preguntas, cada una con 4 respuestas posibles, de las cuales sólo 1 es correcta:
>
> a) ¿de cuántas formas diferentes puede un estudiante elegir una respuesta a cada pregunta?
>
> b) ¿de cuántas maneras puede un estudiante elegir una respuesta a cada pregunta y obtener todas las respuestas incorrectas?

Solución:

a) Cada una de las $5$ preguntas tiene $4$ posibles respuestas:

$$
N_a = 4^5 = 1024
$$

b) Para que todas sean incorrectas, en cada pregunta hay $3$ opciones incorrectas:

$$
N_b = 3^5 = 243
$$

---

### Ejercicio 2.34

> a) ¿Cuántas permutaciones distintas se pueden hacer con las letras de la palabra COLUMNA?
>
> b) ¿Cuántas de estas permutaciones comienzan con la letra M?

Solución:

a) La palabra COLUMNA tiene $7$ letras distintas, por lo tanto:

$$
N_a = 7! = 7\cdot 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1 = 5040
$$

b) Si deben comenzar con M, fijo esa letra en la primera posición y permuto las $6$ restantes:

$$
N_b = 6! = 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1 = 720
$$

---

### Ejercicio 2.35

> Un contratista desea construir 9 casas, cada una con diferente diseño. ¿De cuántas formas puede ubicarlas en la calle en la que las va a construir si en un lado de ésta hay 6 lotes y en el lado opuesto hay 3?

Solución:

Planteamiento:

Hay $9$ casas diferentes y $9$ lotes distintos en total ($6$ de un lado y $3$ del otro).

El número de formas de asignar casas a lotes es una permutación de $9$ elementos:

$$
N = 9! = 9\cdot 8\cdot 7\cdot 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1
$$

Resultado:

$$
N = 362880
$$

---

### Ejercicio 2.36

> a) ¿Cuántos números de tres dígitos se pueden formar con los dígitos 0, 1, 2, 3, 4, 5 y 6 si cada dígito se puede usar sólo una vez?
>
> b) ¿Cuántos de estos números son impares?
>
> c) ¿Cuántos son mayores que 330?

Solución:

a) Números de 3 dígitos con $\{0,1,2,3,4,5,6\}$ sin repetición:

- centenas: no puede ser $0$ $\Rightarrow 6$ opciones ($1$ a $6$);
- decenas: quedan $6$ opciones;
- unidades: quedan $5$ opciones.

$$
N_a = 6\cdot 6\cdot 5 = 180
$$

b) Números impares (la unidad debe ser impar):

- unidad: $\{1,3,5\}$ $\Rightarrow 3$ opciones;
- centena: de $1$ a $6$, excepto la unidad elegida $\Rightarrow 5$ opciones;
- decena: quedan $5$ opciones.

$$
N_b = 3\cdot 5\cdot 5 = 75
$$

c) Números mayores que $330$:

Caso 1: centena en $\{4,5,6\}$.

Para cada centena, las otras dos posiciones son:

$$
6\cdot 5 = 30
$$

Total caso 1:

$$
3\cdot 30 = 90
$$

Caso 2: centena $=3$.

Para ser mayor que $330$, la decena debe ser $4,5$ o $6$ ($3$ opciones). Luego la unidad tiene $5$ opciones.

$$
3\cdot 5 = 15
$$

Total:

$$
N_c = 90 + 15 = 105
$$

---

### Ejercicio 2.37

> ¿De cuántas maneras se pueden sentar 4 niños y 5 niñas en una fila, si se deben alternar unos y otras?

Solución:

Planteamiento:

Hay $4$ niños y $5$ niñas, y deben alternarse.

Como hay una niña más, el único patrón posible es:

$$
N\;M\;N\;M\;N\;M\;N\;M\;N
$$

donde $N$ = niña y $M$ = niño.

Ahora ordeno personas dentro de sus lugares:

- niñas en 5 lugares: $5!$;
- niños en 4 lugares: $4!$.

$$
N = (5\cdot 4\cdot 3\cdot 2\cdot 1)(4\cdot 3\cdot 2\cdot 1) = 120\cdot 24 = 2880
$$

---

### Ejercicio 2.38

> Cuatro parejas compran 8 lugares en la misma fila para un concierto. ¿De cuántas maneras diferentes se pueden sentar:
>
> a) sin restricciones?
>
> b) si cada pareja se sienta junta?
>
> c) si todos los hombres se sientan juntos a la derecha de todas las mujeres?

Solución:

a) Sin restricciones, se ordenan 8 personas distintas:

$$
N_a = 8! = 8\cdot 7\cdot 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1 = 40320
$$

b) Si cada pareja se sienta junta:

Trato cada pareja como bloque ($4$ bloques):

$$
4! = 4\cdot 3\cdot 2\cdot 1
$$

Dentro de cada bloque, la pareja puede ordenarse de $2$ formas. Para 4 parejas:

$$
2^4 = 2\cdot 2\cdot 2\cdot 2
$$

Entonces:

$$
N_b = (4\cdot 3\cdot 2\cdot 1)\cdot 2^4 = 24\cdot 16 = 384
$$

c) Si todos los hombres se sientan juntos a la derecha de todas las mujeres:

- las 4 mujeres ocupan los 4 asientos de la izquierda, en $4!$ formas;
- los 4 hombres ocupan los 4 de la derecha, en $4!$ formas.

$$
N_c = (4\cdot 3\cdot 2\cdot 1)(4\cdot 3\cdot 2\cdot 1) = 24\cdot 24 = 576
$$

---

### Ejercicio 2.39

> En un concurso regional de ortografía, los 8 finalistas son 3 niños y 5 niñas. Encuentre el número de puntos muestrales en el espacio muestral $S$ para el número de ordenamientos posibles al final del concurso para:
>
> a) los 8 finalistas;
>
> b) los 3 primeros lugares.

Solución:

a) Ordenamientos posibles de los 8 finalistas:

$$
N_a = 8! = 8\cdot 7\cdot 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1 = 40320
$$

b) Ordenamientos de los 3 primeros lugares (importa el orden):

$$
N_b = P(8,3) = \frac{8!}{(8-3)!} = \frac{8\cdot 7\cdot 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1}{5\cdot 4\cdot 3\cdot 2\cdot 1} = 8\cdot 7\cdot 6 = 336
$$

---

### Ejercicio 2.40

> ¿De cuántas formas se pueden cubrir las 5 posiciones iniciales en un equipo de baloncesto con 8 jugadores que pueden jugar cualquiera de las posiciones?

Solución:

Planteamiento:

Hay $5$ posiciones distintas y $8$ jugadores. Como cualquier jugador puede ocupar cualquier posición, se trata de una permutación sin reemplazo:

$$
N = P(8,5) = \frac{8!}{(8-5)!}
$$

Resultado:

$$
N = \frac{8\cdot 7\cdot 6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1}{3\cdot 2\cdot 1} = 8\cdot 7\cdot 6\cdot 5\cdot 4 = 6720
$$

---

### Ejercicio 2.41

> Encuentre el número de formas en que se puede asignar 6 profesores a 4 secciones de un curso introductorio de psicología, si ningún profesor se asigna a más de una sección.

Solución:

Planteamiento:

Se asignan $4$ secciones distintas a profesores diferentes tomados de $6$ disponibles, sin repetir profesor.

Es una permutación de $6$ tomados de $4$:

$$
N = P(6,4) = \frac{6!}{(6-4)!}
$$

Resultado:

$$
N = \frac{6\cdot 5\cdot 4\cdot 3\cdot 2\cdot 1}{2\cdot 1} = 6\cdot 5\cdot 4\cdot 3 = 360
$$

---

### Ejercicio 2.42

> De un grupo de 40 boletos se sacan 3 billetes de lotería para el primero, segundo y tercer premios. Encuentre el número de puntos muestrales en $S$ para dar los 3 premios, si cada concursante sólo tiene un billete.

Solución:

Planteamiento:

$$
N = 40 \cdot 39 \cdot 38
$$

Resultado:

$$
N = 59280
$$

Desarrollo breve:

También se puede expresar como permutación, porque el orden de premio importa (primero, segundo y tercero):

$$
N = P(40,3) = \frac{40!}{(40-3)!} = \frac{40\cdot 39\cdot 38\cdot 37!}{37!} = 40\cdot 39\cdot 38 = 59280
$$

---

### Ejercicio 2.48

> ¿Cuántas formas hay en que dos estudiantes no tengan la misma fecha de cumpleaños en un grupo de 60?

Solución:

Planteamiento:

$$
N = 365 \cdot 364 \cdot 363 \cdots 306
$$

Forma compacta:

$$
\frac{365!}{(365-60)!}
$$

Interpretación:

Cada estudiante debe tener una fecha distinta. El primero puede tener cualquiera de 365 fechas, el segundo 364, y así sucesivamente hasta el estudiante 60, que tendría 306 opciones.

Resultado:

$$
N = \frac{365!}{305!}
$$

---

### Ejercicio 2.94

> En la situación del ejercicio 2.93 se sabe que el sistema no funciona. ¿Cuál es la probabilidad de que el componente A tampoco funcione?

Solución:

Planteamiento condicional:

$$
P(A' \mid S') = \frac{P(A' \cap S')}{P(S')}
$$

con $S$ = "el sistema funciona" y $S'$ = "el sistema no funciona".

De la figura 2.11:

$$
P(A)=P(B)=0.7, \quad P(C)=P(D)=P(E)=0.8
$$

El sistema funciona si ocurre el camino superior o el inferior:

$$
S = (A \cap B) \cup (C \cap D \cap E)
$$

Entonces:

$$
P(A \cap B)=0.7\cdot 0.7=0.49, \quad P(C \cap D \cap E)=0.8^3=0.512
$$

Como los caminos usan componentes distintos:

$$
P(S') = (1-0.49)(1-0.512)=0.51\cdot 0.488=0.24888
$$

Además,

$$
A' \cap S' = A' \cap (C \cap D \cap E)'
$$

y por independencia:

$$
P(A' \cap S') = P(A')P((C \cap D \cap E)')=0.3\cdot 0.488=0.1464
$$

Por tanto,

$$
P(A' \mid S')=\frac{0.1464}{0.24888}=\frac{10}{17}\approx 0.588235
$$

Resultado final:

$$
P(A' \mid S') \approx 0.5882
$$
