import json
import random
import tkinter as tk
from collections import Counter
from itertools import islice, product
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk

PALETA_DADOS = ["#d62828", "#1df700", "#1e3adb", "#2a9d8f", "#e7e42c", "#7b2cbf", "#9B1960", "#36250f"]


def _oscurecer_color(hex_color: str, factor: float = 0.6) -> str:
	"""Devuelve una versión más oscura de hex_color multiplicando cada canal por factor."""
	h = hex_color.lstrip("#")
	r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
	r, g, b = int(r * factor), int(g * factor), int(b * factor)
	return f"#{r:02x}{g:02x}{b:02x}"


class DiceApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("Simulador de Dado")
		self.root.geometry("980x640")
		self.root.minsize(900, 750)

		self.sessions_dir = Path(__file__).resolve().parent / "sessions"
		self.sessions_dir.mkdir(parents=True, exist_ok=True)

		self.historial: list[tuple[int, ...]] = []
		self.seleccionados: set[int] = set(range(1, 7))
		self.cantidad_dados = 1
		self.animando = False

		self.check_vars: dict[int, tk.BooleanVar] = {
			cara: tk.BooleanVar(value=True) for cara in range(1, 7)
		}

		self._crear_interfaz()
		self._dibujar_dados((1,))
		self._actualizar_estadisticas()

	def _crear_interfaz(self) -> None:
		contenedor = ttk.Frame(self.root, padding=12)
		contenedor.pack(fill="both", expand=True)

		col_izq = ttk.Frame(contenedor)
		col_izq.pack(side="left", fill="both", expand=True, padx=(0, 8))

		col_der = ttk.Frame(contenedor)
		col_der.pack(side="right", fill="y", padx=(8, 0))

		self.canvas = tk.Canvas(
			col_izq,
			width=360,
			height=360,
			bg="#f8f8f8",
			highlightthickness=0,
		)
		self.canvas.pack(pady=(0, 10))

		controles = ttk.Frame(col_izq)
		controles.pack(fill="x", pady=(0, 10))

		self.btn_lanzar = ttk.Button(controles, text="Lanzar", command=self.lanzar_animado)
		self.btn_lanzar.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

		self.lbl_dados = ttk.Label(controles, text="Dados por experimento:")
		self.lbl_dados.grid(row=0, column=1, padx=4, pady=4, sticky="e")

		self.entrada_dados = ttk.Entry(controles, width=6)
		self.entrada_dados.insert(0, "1")
		self.entrada_dados.grid(row=0, column=2, padx=4, pady=4, sticky="w")

		self.entrada_n = ttk.Entry(controles, width=8)
		self.entrada_n.insert(0, "10")
		self.entrada_n.grid(row=1, column=1, padx=4, pady=4, sticky="e")

		self.lbl_n = ttk.Label(controles, text="Experimentos:")
		self.lbl_n.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

		self.btn_n = ttk.Button(controles, text="Lanzar N veces", command=self.lanzar_n_veces)
		self.btn_n.grid(row=1, column=2, padx=4, pady=4, sticky="ew")

		self.btn_hist = ttk.Button(controles, text="Histograma", command=self.mostrar_histograma)
		self.btn_hist.grid(row=2, column=0, padx=4, pady=4, sticky="ew")

		self.btn_graf = ttk.Button(controles, text="Graficar resultados", command=self.mostrar_grafica)
		self.btn_graf.grid(row=2, column=2, padx=4, pady=4, sticky="ew")

		for i in (0, 2):
			controles.columnconfigure(i, weight=1)

		sesion_frame = ttk.LabelFrame(col_izq, text="Sesiones", padding=8)
		sesion_frame.pack(fill="x", pady=(0, 10))

		self.entrada_sesion = ttk.Entry(sesion_frame)
		self.entrada_sesion.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
		self.entrada_sesion.insert(0, "mi_sesion")

		self.btn_guardar_sesion = ttk.Button(
			sesion_frame,
			text="Guardar sesión",
			command=self.guardar_sesion,
		)
		self.btn_guardar_sesion.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

		self.btn_cargar_sesion = ttk.Button(
			sesion_frame,
			text="Cargar sesión",
			command=self.cargar_sesion,
		)
		self.btn_cargar_sesion.grid(row=0, column=2, padx=4, pady=4, sticky="ew")

		self.combo_sesiones = ttk.Combobox(sesion_frame, state="readonly")
		self.combo_sesiones.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
		self.combo_sesiones.bind("<<ComboboxSelected>>", self._copiar_nombre_sesion)

		self.btn_actualizar_sesiones = ttk.Button(
			sesion_frame,
			text="Actualizar lista",
			command=self._actualizar_lista_sesiones,
		)
		self.btn_actualizar_sesiones.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

		sesion_frame.columnconfigure(0, weight=2)
		for i in (1, 2):
			sesion_frame.columnconfigure(i, weight=1)

		self._actualizar_lista_sesiones()

		self.lbl_estado = ttk.Label(col_izq, text="Listo.")
		self.lbl_estado.pack(anchor="w", pady=(0, 8))

		historial_frame = ttk.LabelFrame(col_izq, text="Historial")
		historial_frame.pack(fill="both", expand=True)

		self.txt_historial = tk.Text(historial_frame, height=8, wrap="word")
		self.txt_historial.pack(fill="both", expand=True, padx=8, pady=8)
		self.txt_historial.configure(state="disabled")

		check_frame = ttk.LabelFrame(col_der, text="Checklist (caras seleccionadas)", padding=8)

		espacio_frame = ttk.LabelFrame(col_der, text="Espacio muestral", padding=8)
		espacio_frame.pack(fill="x", pady=(0, 10))

		self.txt_espacio = tk.Text(espacio_frame, height=4, wrap="word")
		self.txt_espacio.pack(fill="x")
		self.txt_espacio.configure(state="disabled")

		self.lbl_cardinalidad = ttk.Label(espacio_frame, text="Cardinalidad: n(Ω) = 6")
		self.lbl_cardinalidad.pack(anchor="w", pady=(6, 0))

		check_frame.pack(fill="x", pady=(0, 10))

		for cara in range(1, 7):
			chk = ttk.Checkbutton(
				check_frame,
				text=f"Cara {cara}",
				variable=self.check_vars[cara],
				command=self._actualizar_seleccion,
			)
			chk.pack(anchor="w")

		stats_frame = ttk.LabelFrame(col_der, text="Estadísticas", padding=(6, 4))
		stats_frame.pack(fill="both", expand=True)
		stats_frame.rowconfigure(0, weight=1)
		stats_frame.columnconfigure(0, weight=1)

		self.txt_stats = tk.Text(
			stats_frame,
			wrap="word",
			width=32,
			state="disabled",
			relief="flat",
			font=("TkDefaultFont", 9),
		)
		_sb_stats = ttk.Scrollbar(stats_frame, orient="vertical", command=self.txt_stats.yview)
		self.txt_stats.configure(yscrollcommand=_sb_stats.set)
		self.txt_stats.grid(row=0, column=0, sticky="nsew")
		_sb_stats.grid(row=0, column=1, sticky="ns")
		self._actualizar_espacio_muestral()

	def _obtener_cantidad_dados(self) -> int | None:
		texto = self.entrada_dados.get().strip()
		if not texto.isdigit() or int(texto) <= 0:
			self.lbl_estado.config(text="Ingresa una cantidad positiva de dados.")
			return None
		return int(texto)

	def _formatear_espacio_muestral(self, cantidad_dados: int) -> str:
		if cantidad_dados == 1:
			return "Ω = {1, 2, 3, 4, 5, 6}"

		if cantidad_dados == 2:
			elementos = [str(par) for par in product(range(1, 7), repeat=2)]
			return "Ω = {" + ", ".join(elementos) + "}"

		muestras = [str(t) for t in islice(product(range(1, 7), repeat=cantidad_dados), 12)]
		return (
			f"Ω = {{(x1, ..., x{cantidad_dados}) : xi ∈ {{1, 2, 3, 4, 5, 6}}}}\n"
			+ "Ejemplos: "
			+ ", ".join(muestras)
			+ ", ..."
		)

	def _actualizar_espacio_muestral(self) -> None:
		texto = self._formatear_espacio_muestral(self.cantidad_dados)
		self.txt_espacio.configure(state="normal")
		self.txt_espacio.delete("1.0", "end")
		self.txt_espacio.insert("1.0", texto)
		self.txt_espacio.configure(state="disabled")
		self.lbl_cardinalidad.config(text=f"Cardinalidad: n(Ω) = 6^{self.cantidad_dados} = {6 ** self.cantidad_dados}")

	def _dibujar_dado(self, valor: int, x0: int, y0: int, lado: int) -> None:
		x1, y1 = x0 + lado, y0 + lado
		self.canvas.delete("all")

	def _dibujar_dados(self, valores: tuple[int, ...] | list[int]) -> None:
		self.canvas.delete("all")
		valores_lista = list(valores)
		cantidad = len(valores_lista)
		if cantidad == 0:
			return

		columnas = min(3, cantidad)
		filas = (cantidad + columnas - 1) // columnas
		margen = 18
		ancho_total = 360 - margen * 2
		alto_total = 300 - margen * 2
		lado = min(ancho_total // columnas - 12, alto_total // filas - 12)
		lado = max(70, min(lado, 110))
		paso_x = 0 if columnas == 1 else (ancho_total - lado) / (columnas - 1)
		paso_y = 0 if filas == 1 else (alto_total - lado) / (filas - 1)

		for indice, valor in enumerate(valores_lista):
			fila = indice // columnas
			columna = indice % columnas
			x0 = int(margen + columna * paso_x)
			y0 = int(margen + fila * paso_y)
			x1 = x0 + lado
			y1 = y0 + lado
			color_dado = PALETA_DADOS[indice % len(PALETA_DADOS)]
			color_borde = _oscurecer_color(color_dado)
			self.canvas.create_rectangle(
				x0,
				y0,
				x1,
				y1,
				fill=color_dado,
				outline=color_borde,
				width=4,
			)

			centros_x = [x0 + int(lado * 0.18), x0 + lado // 2, x0 + int(lado * 0.82)]
			centros_y = [y0 + int(lado * 0.18), y0 + lado // 2, y0 + int(lado * 0.82)]
			pos = {
				"tl": (centros_x[0], centros_y[0]),
				"tr": (centros_x[2], centros_y[0]),
				"ml": (centros_x[0], centros_y[1]),
				"mc": (centros_x[1], centros_y[1]),
				"mr": (centros_x[2], centros_y[1]),
				"bl": (centros_x[0], centros_y[2]),
				"br": (centros_x[2], centros_y[2]),
			}

			mapa_puntos = {
				1: ["mc"],
				2: ["tl", "br"],
				3: ["tl", "mc", "br"],
				4: ["tl", "tr", "bl", "br"],
				5: ["tl", "tr", "mc", "bl", "br"],
				6: ["tl", "tr", "ml", "mr", "bl", "br"],
			}

			r = max(6, lado // 14)
			for clave in mapa_puntos[valor]:
				x, y = pos[clave]
				self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="white")

		self.canvas.create_text(
			180,
			338,
			text=f"Resultado: {tuple(valores_lista)}",
			fill="#333333",
			font=("TkDefaultFont", 12, "bold"),
		)

	def _actualizar_historial(self) -> None:
		self.txt_historial.configure(state="normal")
		self.txt_historial.delete("1.0", "end")
		if not self.historial:
			self.txt_historial.insert("1.0", "Aún no hay lanzamientos.")
		else:
			# Crear tags de color por índice de dado (uno por color de paleta)
			for i, color in enumerate(PALETA_DADOS):
				tag = f"dado_{i}"
				self.txt_historial.tag_configure(tag, foreground=color)
			primero = True
			for experimento in self.historial:
				if not primero:
					self.txt_historial.insert("end", ", ")
				primero = False
				self.txt_historial.insert("end", "(")
				for j, valor in enumerate(experimento):
					if j > 0:
						self.txt_historial.insert("end", ", ")
					tag = f"dado_{j % len(PALETA_DADOS)}"
					self.txt_historial.insert("end", str(valor), tag)
				self.txt_historial.insert("end", ")")
		self.txt_historial.configure(state="disabled")

	def _obtener_resultados_individuales(self) -> list[int]:
		return [valor for experimento in self.historial for valor in experimento]

	def _obtener_resultados_por_dado(self) -> list[list[int]]:
		resultados_por_dado = [[] for _ in range(self.cantidad_dados)]
		for experimento in self.historial:
			for indice, valor in enumerate(experimento):
				resultados_por_dado[indice].append(valor)
		return resultados_por_dado

	def _actualizar_seleccion(self) -> None:
		nuevo = {cara for cara, var in self.check_vars.items() if var.get()}
		if not nuevo:
			self.lbl_estado.config(text="Debe haber al menos una cara seleccionada.")
			for cara, var in self.check_vars.items():
				if cara in self.seleccionados:
					var.set(True)
			return

		self.seleccionados = nuevo
		self._actualizar_estadisticas()

	def _escribir_stats(self, texto: str) -> None:
		self.txt_stats.configure(state="normal")
		self.txt_stats.delete("1.0", "end")
		self.txt_stats.insert("1.0", texto)
		self.txt_stats.configure(state="disabled")

	def _actualizar_estadisticas(self) -> None:
		filtrados = [v for v in self._obtener_resultados_individuales() if v in self.seleccionados]

		lineas: list[str] = []
		lineas.append(f"Experimentos totales: {len(self.historial)}")
		lineas.append(f"Resultados filtrados: {len(filtrados)}")
		lineas.append("")

		if not filtrados:
			lineas.append("Media: -")
			lineas.append("Moda: -")
			lineas.append("")
			lineas.append("Frecuencias (abs y rel):")
			for cara in sorted(self.seleccionados):
				lineas.append(f"  Cara {cara}: fa=0 | fr=0.0000 (0.00%)")
			lineas.append("")
			lineas.append("Estadísticas por dado:")
			for indice_dado in range(self.cantidad_dados):
				lineas.append(f"  Dado {indice_dado + 1}:")
				lineas.append("    Media: -")
				lineas.append("    Moda: -")
				lineas.append("    Frecuencias:")
				for cara in sorted(self.seleccionados):
					lineas.append(f"      Cara {cara}: fa=0 | fr=0.0000 (0.00%)")
			self._escribir_stats("\n".join(lineas))
			return

		conteo = Counter(filtrados)
		media = sum(filtrados) / len(filtrados)
		max_frec = max(conteo.values())
		modas = sorted(cara for cara, frec in conteo.items() if frec == max_frec)

		lineas.append(f"Media: {media:.4f}")
		lineas.append(f"Moda: {modas} (f={max_frec})")
		lineas.append("")

		total = len(filtrados)
		lineas.append("Frecuencias (abs y rel):")
		for cara in sorted(self.seleccionados):
			fa = conteo.get(cara, 0)
			rel = fa / total
			lineas.append(f"  Cara {cara}: fa={fa} | fr={rel:.4f} ({rel * 100:.2f}%)")
		lineas.append("")

		lineas.append("Estadísticas por dado:")
		for indice_dado, resultados_dado in enumerate(self._obtener_resultados_por_dado(), start=1):
			filtrados_dado = [valor for valor in resultados_dado if valor in self.seleccionados]
			if not filtrados_dado:
				lineas.append(f"  Dado {indice_dado}:")
				lineas.append("    Media: -")
				lineas.append("    Moda: -")
				lineas.append("    Frecuencias:")
				for cara in sorted(self.seleccionados):
					lineas.append(f"      Cara {cara}: fa=0 | fr=0.0000 (0.00%)")
				continue

			conteo_dado = Counter(filtrados_dado)
			media_dado = sum(filtrados_dado) / len(filtrados_dado)
			max_frec_dado = max(conteo_dado.values())
			modas_dado = sorted(cara for cara, frec in conteo_dado.items() if frec == max_frec_dado)
			lineas.append(f"  Dado {indice_dado}:")
			lineas.append(f"    Media: {media_dado:.4f}")
			lineas.append(f"    Moda: {modas_dado} (f={max_frec_dado})")
			lineas.append("    Frecuencias:")
			for cara in sorted(self.seleccionados):
				fa_dado = conteo_dado.get(cara, 0)
				fr_dado = fa_dado / len(filtrados_dado)
				lineas.append(f"      Cara {cara}: fa={fa_dado} | fr={fr_dado:.4f} ({fr_dado * 100:.2f}%)")
		self._escribir_stats("\n".join(lineas))

	def _nombre_sesion_limpio(self, nombre: str) -> str:
		permitidos = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
		nombre_base = nombre.strip().replace(" ", "_")
		limpio = "".join(ch for ch in nombre_base if ch in permitidos)
		return limpio

	def _ruta_sesion(self, nombre: str) -> Path | None:
		nombre_limpio = self._nombre_sesion_limpio(nombre)
		if not nombre_limpio:
			return None
		return self.sessions_dir / f"{nombre_limpio}.json"

	def _actualizar_lista_sesiones(self) -> None:
		nombres = sorted(p.stem for p in self.sessions_dir.glob("*.json"))
		self.combo_sesiones["values"] = nombres
		if nombres and not self.combo_sesiones.get():
			self.combo_sesiones.set(nombres[0])

	def _copiar_nombre_sesion(self, _event: tk.Event) -> None:
		nombre = self.combo_sesiones.get().strip()
		if not nombre:
			return
		self.entrada_sesion.delete(0, "end")
		self.entrada_sesion.insert(0, nombre)

	def guardar_sesion(self) -> None:
		if self.animando:
			self.lbl_estado.config(text="Espera a que termine la animación para guardar.")
			return

		nombre = self.entrada_sesion.get().strip()
		ruta = self._ruta_sesion(nombre)
		if ruta is None:
			messagebox.showerror(
				"Nombre inválido",
				"Usa letras, números, guion o guion bajo para el nombre de sesión.",
			)
			return

		payload = {
			"historial": [list(experimento) for experimento in self.historial],
			"seleccionados": sorted(self.seleccionados),
			"cantidad_dados": self.cantidad_dados,
		}

		try:
			with ruta.open("w", encoding="utf-8") as f:
				json.dump(payload, f, ensure_ascii=False, indent=2)
		except OSError as exc:
			messagebox.showerror("Error", f"No se pudo guardar la sesión: {exc}")
			return

		self._actualizar_lista_sesiones()
		self.combo_sesiones.set(ruta.stem)
		self.lbl_estado.config(text=f"Sesión guardada: {ruta.stem}")

	def cargar_sesion(self) -> None:
		if self.animando:
			self.lbl_estado.config(text="Espera a que termine la animación para cargar.")
			return

		nombre = self.entrada_sesion.get().strip()
		ruta = self._ruta_sesion(nombre)
		if ruta is None or not ruta.exists():
			messagebox.showerror("No encontrada", "La sesión indicada no existe en la carpeta sessions.")
			return

		try:
			with ruta.open("r", encoding="utf-8") as f:
				payload = json.load(f)
		except (OSError, json.JSONDecodeError) as exc:
			messagebox.showerror("Error", f"No se pudo leer la sesión: {exc}")
			return

		historial = payload.get("historial", [])
		seleccionados = set(payload.get("seleccionados", [1, 2, 3, 4, 5, 6]))
		cantidad_dados = int(payload.get("cantidad_dados", 1))

		if not isinstance(historial, list):
			messagebox.showerror("Datos inválidos", "El historial de la sesión es inválido.")
			return

		historial_normalizado: list[tuple[int, ...]] = []
		for item in historial:
			if isinstance(item, int):
				item = [item]
			if not isinstance(item, list) or not item or any(v not in {1, 2, 3, 4, 5, 6} for v in item):
				messagebox.showerror("Datos inválidos", "El historial de la sesión es inválido.")
				return
			historial_normalizado.append(tuple(int(v) for v in item))

		if cantidad_dados <= 0:
			messagebox.showerror("Datos inválidos", "El historial de la sesión es inválido.")
			return

		if historial_normalizado and any(len(item) != len(historial_normalizado[0]) for item in historial_normalizado):
			messagebox.showerror("Datos inválidos", "La sesión contiene experimentos con distinta cantidad de dados.")
			return

		if historial_normalizado:
			cantidad_dados = len(historial_normalizado[0])

		if not seleccionados or any(v not in {1, 2, 3, 4, 5, 6} for v in seleccionados):
			messagebox.showerror("Datos inválidos", "La selección de caras en la sesión es inválida.")
			return

		self.historial = historial_normalizado
		self.seleccionados = {int(v) for v in seleccionados}
		self.cantidad_dados = cantidad_dados
		self.entrada_dados.delete(0, "end")
		self.entrada_dados.insert(0, str(self.cantidad_dados))
		self._actualizar_espacio_muestral()

		for cara, var in self.check_vars.items():
			var.set(cara in self.seleccionados)

		ultimo = self.historial[-1] if self.historial else (1,)
		self._dibujar_dados(ultimo)
		self._actualizar_historial()
		self._actualizar_estadisticas()
		self._actualizar_lista_sesiones()
		self.combo_sesiones.set(ruta.stem)
		self.lbl_estado.config(text=f"Sesión cargada: {ruta.stem}")

	def _registrar_resultado(self, resultado: tuple[int, ...]) -> None:
		self.historial.append(resultado)
		self._dibujar_dados(resultado)
		self._actualizar_historial()
		self._actualizar_estadisticas()

	def lanzar_animado(self) -> None:
		if self.animando:
			return

		cantidad_dados = self._obtener_cantidad_dados()
		if cantidad_dados is None:
			return
		self.cantidad_dados = cantidad_dados
		self._actualizar_espacio_muestral()

		self.animando = True
		self.btn_lanzar.configure(state="disabled")
		self.btn_n.configure(state="disabled")
		self.lbl_estado.config(text="Lanzando...")
		self._animar_paso(0, 14)

	def _animar_paso(self, paso: int, total_pasos: int) -> None:
		resultado = tuple(random.randint(1, 6) for _ in range(self.cantidad_dados))
		self._dibujar_dados(resultado)

		if paso < total_pasos:
			delay = 45 + paso * 8
			self.root.after(delay, lambda: self._animar_paso(paso + 1, total_pasos))
			return

		self._registrar_resultado(resultado)
		self.lbl_estado.config(text=f"Resultado registrado: {resultado}")
		self.animando = False
		self.btn_lanzar.configure(state="normal")
		self.btn_n.configure(state="normal")

	def lanzar_n_veces(self) -> None:
		if self.animando:
			return

		cantidad_dados = self._obtener_cantidad_dados()
		if cantidad_dados is None:
			return
		self.cantidad_dados = cantidad_dados
		self._actualizar_espacio_muestral()

		texto = self.entrada_n.get().strip()
		if not texto.isdigit() or int(texto) <= 0:
			self.lbl_estado.config(text="Ingresa un entero positivo para N.")
			return

		cantidad = int(texto)
		resultados = [tuple(random.randint(1, 6) for _ in range(self.cantidad_dados)) for _ in range(cantidad)]
		self.historial.extend(resultados)
		self._dibujar_dados(resultados[-1])
		self._actualizar_historial()
		self._actualizar_estadisticas()
		self.lbl_estado.config(text=f"Se registraron {cantidad} experimentos de {self.cantidad_dados} dado(s).")

	def _obtener_filtrados(self) -> list[int]:
		return [v for v in self._obtener_resultados_individuales() if v in self.seleccionados]

	def _obtener_frecuencias_por_dado(self) -> list[Counter[int]]:
		frecuencias = [Counter() for _ in range(self.cantidad_dados)]
		for experimento in self.historial:
			for indice, valor in enumerate(experimento):
				frecuencias[indice][valor] += 1
		return frecuencias

	def mostrar_histograma(self) -> None:
		if not self.historial:
			messagebox.showinfo("Histograma", "No hay datos para graficar con la selección actual.")
			return

		frecuencias_por_dado = self._obtener_frecuencias_por_dado()
		paleta = PALETA_DADOS
		ventana = tk.Toplevel(self.root)
		ventana.title("Histograma de resultados")
		ventana.geometry("860x520")

		canvas = tk.Canvas(ventana, width=860, height=520, bg="white", highlightthickness=0)
		canvas.pack(fill="both", expand=True)

		margen_izq, margen_der = 70, 30
		margen_sup, margen_inf = 60, 95
		ancho = 860 - margen_izq - margen_der
		alto = 520 - margen_sup - margen_inf

		canvas.create_text(430, 24, text="Histograma por Cara y por Dado", font=("TkDefaultFont", 14, "bold"))
		canvas.create_line(margen_izq, margen_sup, margen_izq, margen_sup + alto, width=2)
		canvas.create_line(margen_izq, margen_sup + alto, margen_izq + ancho, margen_sup + alto, width=2)

		max_frec = max(
			frecuencias[indice_cara]
			for frecuencias in frecuencias_por_dado
			for indice_cara in range(1, 7)
		)
		if max_frec == 0:
			max_frec = 1

		ancho_grupo = ancho / 6
		ancho_barra = min((ancho_grupo * 0.75) / max(1, self.cantidad_dados), 26)

		for i, cara in enumerate(range(1, 7)):
			x_centro = margen_izq + ancho_grupo * (i + 0.5)
			grupo_ancho_total = ancho_barra * self.cantidad_dados
			inicio_grupo = x_centro - grupo_ancho_total / 2
			for indice_dado in range(self.cantidad_dados):
				frec = frecuencias_por_dado[indice_dado].get(cara, 0)
				bar_h = (frec / max_frec) * (alto - 10)
				x0 = inicio_grupo + indice_dado * ancho_barra
				x1 = x0 + ancho_barra - 2
				y1 = margen_sup + alto
				y0 = y1 - bar_h

				color = paleta[indice_dado % len(paleta)] if cara in self.seleccionados else "#cccccc"
				canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#444444")
				canvas.create_text((x0 + x1) / 2, y0 - 12, text=str(frec), font=("TkDefaultFont", 8))

			canvas.create_text(x_centro, margen_sup + alto + 18, text=str(cara), font=("TkDefaultFont", 10, "bold"))

		for indice_dado in range(self.cantidad_dados):
			color = paleta[indice_dado % len(paleta)]
			x0 = margen_izq + indice_dado * 92
			y0 = margen_sup + alto + 40
			canvas.create_rectangle(x0, y0, x0 + 18, y0 + 12, fill=color, outline="#444444")
			canvas.create_text(x0 + 48, y0 + 6, text=f"Dado {indice_dado + 1}", anchor="w", font=("TkDefaultFont", 9))

		canvas.create_text(
			430,
			500,
			text="Eje X: cara del dado | Eje Y: frecuencia absoluta | Cada color representa un dado distinto",
			fill="#444444",
		)

	def mostrar_grafica(self) -> None:
		filtrados = self._obtener_filtrados()
		if not filtrados:
			messagebox.showinfo("Gráfica", "No hay datos para graficar con la selección actual.")
			return

		ventana = tk.Toplevel(self.root)
		ventana.title("Gráfica de resultados")
		ventana.geometry("820x480")

		canvas = tk.Canvas(ventana, width=820, height=480, bg="white", highlightthickness=0)
		canvas.pack(fill="both", expand=True)

		margen_izq, margen_der = 70, 25
		margen_sup, margen_inf = 45, 60
		ancho = 820 - margen_izq - margen_der
		alto = 480 - margen_sup - margen_inf

		canvas.create_text(410, 22, text="Evolución de Resultados", font=("TkDefaultFont", 14, "bold"))
		canvas.create_line(margen_izq, margen_sup, margen_izq, margen_sup + alto, width=2)
		canvas.create_line(margen_izq, margen_sup + alto, margen_izq + ancho, margen_sup + alto, width=2)

		for cara in range(1, 7):
			y = margen_sup + alto - ((cara - 1) / 5) * alto
			canvas.create_line(margen_izq - 5, y, margen_izq, y, width=2)
			canvas.create_text(margen_izq - 18, y, text=str(cara))

		n = len(filtrados)
		if n == 1:
			x = margen_izq + ancho / 2
			y = margen_sup + alto - ((filtrados[0] - 1) / 5) * alto
			canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#d62828", outline="#d62828")
		else:
			puntos: list[float] = []
			for i, valor in enumerate(filtrados):
				x = margen_izq + (i / (n - 1)) * ancho
				y = margen_sup + alto - ((valor - 1) / 5) * alto
				puntos.extend([x, y])
				canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#d62828", outline="#d62828")
			canvas.create_line(*puntos, fill="#d62828", width=2, smooth=True)

		canvas.create_text(410, 458, text="Eje X: número de tirada filtrada | Eje Y: valor obtenido", fill="#444444")


def main() -> None:
	root = tk.Tk()
	DiceApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
