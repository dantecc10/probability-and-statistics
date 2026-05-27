# Capítulo 3 - Ejercicios por resolver

Este archivo continua el mismo estilo de clase usado en la sección 2 (Markdown + LaTeX).

## Índice de ejercicios resueltos

- [X] Ejercicio 3.7
- [X] Ejercicio 3.14
- [X] Ejercicio 3.15
- [X] Ejercicio 3.16
- [X] Ejercicio 3.17
- [X] Ejercicio 3.18
- [X] Ejercicio 3.21
- [X] Ejercicio 3.30
- [X] Ejercicio 3.42
- [X] Ejercicio 3.43
- [X] Ejercicio 3.45
- [X] Ejercicio 3.47
- [X] Ejercicio 3.49
- [X] Ejercicio 3.61
- [X] Ejercicio 3.65
- [X] Ejercicio 3.75

---

### Ejercicio 3.7

> El número total de horas, medidas en unidades de 100 horas, que una familia utiliza una aspiradora en un periodo de un año es una variable aleatoria continua $X$ con densidad
>
> $$
> f(x)=\begin{cases}
> x, & 0<x<1,\\
> 2-x, & 1\le x<2,\\
> 0, & \text{en otro caso}.
> \end{cases}
> $$
>
> Calcule:
>
> a) la probabilidad de que se use menos de 120 horas;
>
> b) la probabilidad de que se use entre 50 y 100 horas.

Solución:

a) Menos de 120 horas equivale a $X<1.2$:

$$
P(X<1.2)=\int_0^1 x\,dx+\int_1^{1.2}(2-x)\,dx
$$

$$
P(X<1.2)=\frac{1}{2}+0.18=0.68
$$

b) Entre 50 y 100 horas equivale a $0.5<X<1$:

$$
P(0.5<X<1)=\int_{0.5}^{1}x\,dx=\left.\frac{x^2}{2}\right|_{0.5}^{1}=0.375
$$

---

### Ejercicio 3.14

> El tiempo $X$ (horas) entre conductores sucesivos que exceden el límite tiene función de distribución acumulativa
>
> $$
> F(x)=\begin{cases}
> 0, & x<0,\\
> 1-e^{-8x}, & x\ge 0.
> \end{cases}
> $$
>
> Calcule la probabilidad de que el tiempo sea menor de 12 minutos:
>
> a) usando $F(x)$;
>
> b) usando la densidad.

Solución:

Como 12 minutos $=0.2$ horas:

a) Con la CDF:

$$
P(X<0.2)=F(0.2)=1-e^{-8(0.2)}=1-e^{-1.6}\approx 0.7981
$$

b) La densidad es $f(x)=F'(x)=8e^{-8x}$ para $x\ge 0$.

$$
P(X<0.2)=\int_0^{0.2}8e^{-8x}\,dx=1-e^{-1.6}\approx 0.7981
$$

---

### Ejercicio 3.15

> Para el ejercicio 3.11 (7 televisores, 2 defectuosos, se compran 3), construya $F(x)$ para $X=$ numero de defectuosos comprados.
>
> Luego calcule:
>
> a) $P(X=1)$;
>
> b) $P(0<X\le 2)$.

Solución:

Primero, distribución de $X$ (hipergeométrica):

$$
P(X=0)=\frac{\binom{2}{0}\binom{5}{3}}{\binom{7}{3}}=\frac{2}{7},\quad
P(X=1)=\frac{\binom{2}{1}\binom{5}{2}}{\binom{7}{3}}=\frac{4}{7},\quad
P(X=2)=\frac{\binom{2}{2}\binom{5}{1}}{\binom{7}{3}}=\frac{1}{7}
$$

Entonces:

F(x)=\begin{cases}
0, & x<0,\\
\frac{2}{7}, & 0\le x<1,\\
\frac{6}{7}, & 1\le x<2,\\
1, & x\ge 2.
\end{cases}
$$

a)

$$
P(X=1)=\frac{4}{7}
$$

b)

$$
P(0<X\le 2)=P(X=1)+P(X=2)=\frac{4}{7}+\frac{1}{7}=\frac{5}{7}
$$

---

### Ejercicio 3.16

> Construya una gráfica de la función de distribución acumulativa del ejercicio 3.15.

Solución:

La gráfica es una función escalón con saltos en $x=0,1,2$:

$$
F(x)=\begin{cases}
0, & x<0,\\
\frac{2}{7}, & 0\le x<1,\\
\frac{6}{7}, & 1\le x<2,\\
1, & x\ge 2.
\end{cases}
$$

Niveles del escalón: $0 \to 2/7 \to 6/7 \to 1$.

---

### Ejercicio 3.17

> $X$ continua en $1\le x\le 3$ con densidad $f(x)=1/2$.
>
> a) Muestre que el área bajo la curva es 1.
>
> b) Calcule $P(2<X<2.5)$;
>
> c) Calcule $P(X\le 1.6)$.

Solución:

a)

$$
\int_1^3 \frac{1}{2}\,dx=\frac{1}{2}(3-1)=1
$$

b)

$$
P(2<X<2.5)=\int_2^{2.5}\frac{1}{2}\,dx=\frac{1}{2}(0.5)=0.25
$$

c)

$$
P(X\le 1.6)=\int_1^{1.6}\frac{1}{2}\,dx=0.3
$$

---

### Ejercicio 3.18

> $X$ continúa en $2\le x\le 5$ con densidad
>
> $$
> f(x)=\frac{2(1+x)}{27}.
> $$
>
> Calcule:
>
> a) $P(X<4)$;
>
> b) $P(3\le X<4)$.

Solución:

a)

$$
P(X<4)=\int_2^4\frac{2(1+x)}{27}\,dx
=\frac{2}{27}\left[x+\frac{x^2}{2}\right]_2^4
=\frac{16}{27}
$$

b)

$$
P(3\le X<4)=\int_3^4\frac{2(1+x)}{27}\,dx
=\frac{1}{3}
$$

---

### Ejercicio 3.21

> Considere
>
> $$
> f(x)=\begin{cases}
> k\sqrt{x}, & 0<x<1,\\
> 0, & \text{en otro caso}.
> \end{cases}
> $$
>
> a) Evalue $k$.
>
> b) Calcule $F(x)$ y úsela para evaluar $P(0.3<X<0.6)$.

Solución:

a) Normalización:

$$
\int_0^1 kx^{1/2}\,dx = k\frac{2}{3}=1 \Rightarrow k=\frac{3}{2}
$$

b) CDF:

$$
F(x)=\begin{cases}
0, & x\le 0,\\
x^{3/2}, & 0<x<1,\\
1, & x\ge 1.
\end{cases}
$$

Entonces:

$$
P(0.3<X<0.6)=F(0.6)-F(0.3)=0.6^{3/2}-0.3^{3/2}\approx 0.3004
$$

---

### Ejercicio 3.30

> Error de medición $X$ con densidad
>
> $$
> f(x)=\begin{cases}
> k(3-x^2), & -1\le x\le 1,\\
> 0, & \text{en otro caso}.
> \end{cases}
> $$
>
> a) Determine $k$.
>
> b) Calcule $P(X<1/2)$.
>
> c) Calcule $P(|X|>0.8)$.

Solución:

a) Normalización:

$$
1=\int_{-1}^{1}k(3-x^2)\,dx=k\frac{16}{3}
\Rightarrow k=\frac{3}{16}
$$

b)

$$
P(X<1/2)=\int_{-1}^{1/2}\frac{3}{16}(3-x^2)\,dx=\frac{99}{128}\approx 0.7734
$$

c)

$$
P(|X|>0.8)=1-P(-0.8\le X\le 0.8)=1-0.836=0.164
$$

---

### Ejercicio 3.42

> Sean $X$ y $Y$ la vida (anos) de dos componentes, con densidad conjunta
>
> $$
> f(x,y)=\begin{cases}
> e^{-(x+y)}, & x>0,\ y>0,\\
> 0, & \text{en otro caso}.
> \end{cases}
> $$
>
> Calcule $P(0<X<1\mid Y=2)$.

Solución:

Densidad marginal de $Y$:

$$
f_Y(y)=\int_0^\infty e^{-(x+y)}dx=e^{-y},\quad y>0
$$

Densidad condicional:

$$
f_{X\mid Y}(x\mid y)=\frac{f(x,y)}{f_Y(y)}=e^{-x},\quad x>0
$$

Por tanto,

$$
P(0<X<1\mid Y=2)=\int_0^1 e^{-x}dx=1-e^{-1}\approx 0.6321
$$

---

### Ejercicio 3.43

> Sean $X$ (tiempo de reacción) y $Y$ (temperatura) con
>
> $$
> f(x,y)=\begin{cases}
> 4xy, & 0<x<1,\ 0<y<1,\\
> 0, & \text{en otro caso}.
> \end{cases}
> $$
>
> Calcule:
>
> a) $P(0\le X\le 1/2,\ 1/4\le Y\le 1/2)$;
>
> b) $P(X<Y)$.

Solución:

a)

$$
P=\int_0^{1/2}\int_{1/4}^{1/2}4xy\,dy\,dx
=\frac{3}{64}
$$

b)

$$
P(X<Y)=\int_0^1\int_0^y4xy\,dx\,dy=\frac{1}{2}
$$

---

### Ejercicio 3.45

> Sean $X$ y $Y$ con densidad conjunta
>
> $$
> f(x,y)=\begin{cases}
> \frac{1}{y}, & 0<x<y<1,\\
> 0, & \text{en otro caso}.
> \end{cases}
> $$
>
> Calcule $P(X+Y>1/2)$.

Solución:

Se integra sobre la región $\{(x,y): 0<x<y<1,\ x+y>1/2\}$:

$$
P=\int_{1/4}^{1/2}\int_{1/2-y}^{y}\frac{1}{y}\,dx\,dy
+\int_{1/2}^{1}\int_0^y\frac{1}{y}\,dx\,dy
$$

$$
P=1-\frac{1}{2}\ln 2\approx 0.6534
$$

---

### Ejercicio 3.47

> Al inicio del día, la cantidad de queroseno en un tanque es $Y$ (miles de litros) y durante el día se vende $X$, con $x\le y$ y densidad conjunta
>
> $$
> f(x,y)=\begin{cases}
> 2, & 0<x\le y<1,\\
> 0, & \text{en otro caso}.
> \end{cases}
> $$
>
> a) Determine si $X$ y $Y$ son independientes.
>
> b) Calcule $P(1/4<X<1/2\mid Y=3/4)$.

Solución:

a) Marginales:

$$
f_X(x)=\int_x^1 2\,dy=2(1-x),\quad
f_Y(y)=\int_0^y 2\,dx=2y
$$

Como $f_X(x)f_Y(y)=4y(1-x)\neq 2=f(x,y)$, no son independientes.

b) Densidad condicional:

$$
f_{X\mid Y}(x\mid y)=\frac{f(x,y)}{f_Y(y)}=\frac{1}{y},\quad 0<x<y
$$

Para $y=3/4$:

$$
P\left(\frac14<X<\frac12\mid Y=\frac34\right)
=\int_{1/4}^{1/2}\frac{1}{3/4}\,dx
=\frac{1}{3}
$$

---

### Ejercicio 3.49

> La distribución conjunta de $X$ (fallas de máquina: 1,2,3) y $Y$ (llamadas de emergencia: 1,3,5) es:
>
> $$
> \begin{array}{c|ccc}
> f(x,y) & x=1 & x=2 & x=3\\\hline
> y=1 & 0.05 & 0.05 & 0.10\\
> y=3 & 0.05 & 0.10 & 0.35\\
> y=5 & 0.00 & 0.20 & 0.10
> \end{array}
> $$
>
> a) Distribucion marginal de $X$.
>
> b) Distribucion marginal de $Y$.
>
> c) $P(Y=3\mid X=2)$.

Solucion:

a) Marginal de $X$:

$$
P(X=1)=0.10,\quad P(X=2)=0.35,\quad P(X=3)=0.55
$$

b) Marginal de $Y$:

$$
P(Y=1)=0.20,\quad P(Y=3)=0.50,\quad P(Y=5)=0.30
$$

c)

$$
P(Y=3\mid X=2)=\frac{P(X=2,Y=3)}{P(X=2)}=\frac{0.10}{0.35}=\frac{2}{7}\approx 0.2857
$$

---

### Ejercicio 3.61

> Mezcla de tabaco con densidad conjunta
>
> $$
> f(x,y)=\begin{cases}
> 24xy, & 0\le x,y\le 1,\ x+y\le 1,\\
> 0, & \text{en otro caso},
> \end{cases}
> $$
>
> donde $X$ = proporción de tabaco turco y $Y$ = proporción de tabaco de la región.
>
> a) Probabilidad de que el tabaco turco represente más de la mitad.
>
> b) Densidad marginal de $Y$.
>
> c) Probabilidad de que $X<1/8$ dado $Y=3/4$.

Solución:

a)

$$
P(X>1/2)=\int_{1/2}^{1}\int_0^{1-x}24xy\,dy\,dx=\frac{5}{16}=0.3125
$$

b)

$$
f_Y(y)=\int_0^{1-y}24xy\,dx=12y(1-y)^2,\quad 0\le y\le 1
$$

c)

$$
f_{X\mid Y}(x\mid y)=\frac{24xy}{12y(1-y)^2}=\frac{2x}{(1-y)^2},\quad 0\le x\le 1-y
$$

Para $y=3/4$:

$$
f_{X\mid Y}(x\mid 3/4)=32x,\quad 0\le x\le 1/4
$$

Entonces:

$$
P(X<1/8\mid Y=3/4)=\int_0^{1/8}32x\,dx=\frac{1}{4}=0.25
$$

---

### Ejercicio 3.65

> $X$ = número de llamadas en 5 minutos, con función de probabilidad
>
> $$
> f(x)=\frac{e^{-2}2^x}{x!},\quad x=0,1,2,\dots
> $$
>
> a) Determine $P(X=x)$ para $x=0,1,2,3,4,5,6$.
>
> b) Grafique la función de masa para esos valores.
>
> c) Determine la función de distribución acumulada para esos valores.

Solución:

Es una Poisson con $\lambda=2$.

a) Valores:

$$
\begin{aligned}
P(X=0)&=e^{-2}=0.135335,\\
P(X=1)&=2e^{-2}=0.270671,\\
P(X=2)&=\frac{2^2}{2!}e^{-2}=0.270671,\\
P(X=3)&=\frac{2^3}{3!}e^{-2}=0.180447,\\
P(X=4)&=\frac{2^4}{4!}e^{-2}=0.090224,\\
P(X=5)&=\frac{2^5}{5!}e^{-2}=0.036089,\\
P(X=6)&=\frac{2^6}{6!}e^{-2}=0.012030.
\end{aligned}
$$

b) Para la grafica (barras), use esos 7 pares $(x, P(X=x))$.

c) CDF en esos puntos:

$$
\begin{aligned}
F(0)&=0.135335,\\
F(1)&=0.406006,\\
F(2)&=0.676676,\\
F(3)&=0.857123,\\
F(4)&=0.947347,\\
F(5)&=0.983436,\\
F(6)&=0.995466.
\end{aligned}
$$

---

### Ejercicio 3.75

> Sistema quimico con proporciones $(X_1, X_2)$ y densidad conjunta
>
> $$
> f(x_1,x_2)=\begin{cases}
> 2, & 0<x_1<x_2<1,\\
> 0, & \text{en otro caso}.
> \end{cases}
> $$
>
> a) Determine la marginal de $X_1$.
>
> b) Determine la marginal de $X_2$.
>
> c) Calcule $P(X_1<0.2,\ X_2>0.5)$.
>
> d) Determine la distribución condicional $f_{X_1\mid X_2}(x_1\mid x_2)$.

Solución:

a) Marginal de $X_1$:

$$
f_{X_1}(x_1)=\int_{x_1}^{1}2\,dx_2=2(1-x_1),\quad 0<x_1<1
$$

b) Marginal de $X_2$:

$$
f_{X_2}(x_2)=\int_0^{x_2}2\,dx_1=2x_2,\quad 0<x_2<1
$$

c)

$$
P(X_1<0.2, X_2>0.5)=\int_0^{0.2}\int_{0.5}^{1}2\,dx_2\,dx_1
=0.2
$$

d) Condicional:

$$
f_{X_1\mid X_2}(x_1\mid x_2)=\frac{f(x_1,x_2)}{f_{X_2}(x_2)}
=\frac{2}{2x_2}=\frac{1}{x_2},\quad 0<x_1<x_2<1
$$
