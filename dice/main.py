import json
import random
import tkinter as tk
from collections import Counter
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk


class DiceApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("Simulador de Dado")
		self.root.geometry("980x640")
		self.root.minsize(900, 700)

		self.sessions_dir = Path(__file__).resolve().parent / "sessions"
		self.sessions_dir.mkdir(parents=True, exist_ok=True)

		self.historial: list[int] = []
		self.seleccionados: set[int] = set(range(1, 7))
		self.animando = False

		self.check_vars: dict[int, tk.BooleanVar] = {
			cara: tk.BooleanVar(value=True) for cara in range(1, 7)
		}

		self._crear_interfaz()
		self._dibujar_dado(1)
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

		self.entrada_n = ttk.Entry(controles, width=8)
		self.entrada_n.insert(0, "10")
		self.entrada_n.grid(row=0, column=1, padx=4, pady=4)

		self.btn_n = ttk.Button(controles, text="Lanzar N veces", command=self.lanzar_n_veces)
		self.btn_n.grid(row=0, column=2, padx=4, pady=4, sticky="ew")

		self.btn_hist = ttk.Button(controles, text="Histograma", command=self.mostrar_histograma)
		self.btn_hist.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

		self.btn_graf = ttk.Button(controles, text="Graficar resultados", command=self.mostrar_grafica)
		self.btn_graf.grid(row=1, column=2, padx=4, pady=4, sticky="ew")

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

		self.var_espacio = tk.StringVar(value="Ω = {1, 2, 3, 4, 5, 6}")
		entrada_espacio = ttk.Entry(espacio_frame, textvariable=self.var_espacio, state="readonly")
		entrada_espacio.pack(fill="x")

		lbl_cardinalidad = ttk.Label(espacio_frame, text="Cardinalidad: n(Ω) = 6")
		lbl_cardinalidad.pack(anchor="w", pady=(6, 0))

		check_frame.pack(fill="x", pady=(0, 10))

		for cara in range(1, 7):
			chk = ttk.Checkbutton(
				check_frame,
				text=f"Cara {cara}",
				variable=self.check_vars[cara],
				command=self._actualizar_seleccion,
			)
			chk.pack(anchor="w")

		stats_frame = ttk.LabelFrame(col_der, text="Estadísticas", padding=10)
		stats_frame.pack(fill="both", expand=True)

		self.lbl_totales = ttk.Label(stats_frame, text="Tiradas totales: 0")
		self.lbl_totales.pack(anchor="w")

		self.lbl_filtradas = ttk.Label(stats_frame, text="Tiradas filtradas: 0")
		self.lbl_filtradas.pack(anchor="w", pady=(0, 8))

		self.lbl_media = ttk.Label(stats_frame, text="Media: -")
		self.lbl_media.pack(anchor="w")

		self.lbl_moda = ttk.Label(stats_frame, text="Moda: -")
		self.lbl_moda.pack(anchor="w", pady=(0, 10))

		self.lbl_frecuencias = ttk.Label(stats_frame, text="Frecuencias (abs y rel):\n-", justify="left")
		self.lbl_frecuencias.pack(anchor="w")

	def _dibujar_dado(self, valor: int) -> None:
		self.canvas.delete("all")

		x0, y0, x1, y1 = 50, 50, 310, 310
		self.canvas.create_rectangle(
			x0,
			y0,
			x1,
			y1,
			fill="#d62828",
			outline="#8d0d0d",
			width=4,
		)

		cx = [95, 180, 265]
		cy = [95, 180, 265]
		pos = {
			"tl": (cx[0], cy[0]),
			"tc": (cx[1], cy[0]),
			"tr": (cx[2], cy[0]),
			"ml": (cx[0], cy[1]),
			"mc": (cx[1], cy[1]),
			"mr": (cx[2], cy[1]),
			"bl": (cx[0], cy[2]),
			"bc": (cx[1], cy[2]),
			"br": (cx[2], cy[2]),
		}

		mapa_puntos = {
			1: ["mc"],
			2: ["tl", "br"],
			3: ["tl", "mc", "br"],
			4: ["tl", "tr", "bl", "br"],
			5: ["tl", "tr", "mc", "bl", "br"],
			6: ["tl", "tr", "ml", "mr", "bl", "br"],
		}

		for clave in mapa_puntos[valor]:
			x, y = pos[clave]
			r = 15
			self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="white")

		self.canvas.create_text(
			180,
			338,
			text=f"Resultado: {valor}",
			fill="#333333",
			font=("TkDefaultFont", 13, "bold"),
		)

	def _actualizar_historial(self) -> None:
		texto = ", ".join(str(v) for v in self.historial) if self.historial else "Aún no hay lanzamientos."
		self.txt_historial.configure(state="normal")
		self.txt_historial.delete("1.0", "end")
		self.txt_historial.insert("1.0", texto)
		self.txt_historial.configure(state="disabled")

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

	def _actualizar_estadisticas(self) -> None:
		filtrados = [v for v in self.historial if v in self.seleccionados]

		self.lbl_totales.config(text=f"Tiradas totales: {len(self.historial)}")
		self.lbl_filtradas.config(text=f"Tiradas filtradas: {len(filtrados)}")

		if not filtrados:
			self.lbl_media.config(text="Media: -")
			self.lbl_moda.config(text="Moda: -")
			lineas = ["Frecuencias (abs y rel):"]
			for cara in sorted(self.seleccionados):
				lineas.append(f"Cara {cara}: fa=0 | fr=0.0000 (0.00%)")
			self.lbl_frecuencias.config(text="\n".join(lineas))
			return

		conteo = Counter(filtrados)
		media = sum(filtrados) / len(filtrados)
		max_frec = max(conteo.values())
		modas = sorted([cara for cara, frec in conteo.items() if frec == max_frec])

		self.lbl_media.config(text=f"Media: {media:.4f}")
		self.lbl_moda.config(text=f"Moda: {modas} (f={max_frec})")

		total = len(filtrados)
		lineas = ["Frecuencias (abs y rel):"]
		for cara in sorted(self.seleccionados):
			fa = conteo.get(cara, 0)
			rel = fa / total
			lineas.append(f"Cara {cara}: fa={fa} | fr={rel:.4f} ({rel * 100:.2f}%)")
		self.lbl_frecuencias.config(text="\n".join(lineas))

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
			"historial": self.historial,
			"seleccionados": sorted(self.seleccionados),
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

		if not isinstance(historial, list) or any(v not in {1, 2, 3, 4, 5, 6} for v in historial):
			messagebox.showerror("Datos inválidos", "El historial de la sesión es inválido.")
			return

		if not seleccionados or any(v not in {1, 2, 3, 4, 5, 6} for v in seleccionados):
			messagebox.showerror("Datos inválidos", "La selección de caras en la sesión es inválida.")
			return

		self.historial = [int(v) for v in historial]
		self.seleccionados = {int(v) for v in seleccionados}

		for cara, var in self.check_vars.items():
			var.set(cara in self.seleccionados)

		ultimo = self.historial[-1] if self.historial else 1
		self._dibujar_dado(ultimo)
		self._actualizar_historial()
		self._actualizar_estadisticas()
		self._actualizar_lista_sesiones()
		self.combo_sesiones.set(ruta.stem)
		self.lbl_estado.config(text=f"Sesión cargada: {ruta.stem}")

	def _registrar_resultado(self, resultado: int) -> None:
		self.historial.append(resultado)
		self._dibujar_dado(resultado)
		self._actualizar_historial()
		self._actualizar_estadisticas()

	def lanzar_animado(self) -> None:
		if self.animando:
			return

		self.animando = True
		self.btn_lanzar.configure(state="disabled")
		self.btn_n.configure(state="disabled")
		self.lbl_estado.config(text="Lanzando...")
		self._animar_paso(0, 14)

	def _animar_paso(self, paso: int, total_pasos: int) -> None:
		cara = random.randint(1, 6)
		self._dibujar_dado(cara)

		if paso < total_pasos:
			delay = 45 + paso * 8
			self.root.after(delay, lambda: self._animar_paso(paso + 1, total_pasos))
			return

		self._registrar_resultado(cara)
		self.lbl_estado.config(text=f"Resultado registrado: {cara}")
		self.animando = False
		self.btn_lanzar.configure(state="normal")
		self.btn_n.configure(state="normal")

	def lanzar_n_veces(self) -> None:
		if self.animando:
			return

		texto = self.entrada_n.get().strip()
		if not texto.isdigit() or int(texto) <= 0:
			self.lbl_estado.config(text="Ingresa un entero positivo para N.")
			return

		cantidad = int(texto)
		resultados = [random.randint(1, 6) for _ in range(cantidad)]
		self.historial.extend(resultados)
		self._dibujar_dado(resultados[-1])
		self._actualizar_historial()
		self._actualizar_estadisticas()
		self.lbl_estado.config(text=f"Se registraron {cantidad} tiradas.")

	def _obtener_filtrados(self) -> list[int]:
		return [v for v in self.historial if v in self.seleccionados]

	def mostrar_histograma(self) -> None:
		filtrados = self._obtener_filtrados()
		if not filtrados:
			messagebox.showinfo("Histograma", "No hay datos para graficar con la selección actual.")
			return

		conteo = Counter(filtrados)
		ventana = tk.Toplevel(self.root)
		ventana.title("Histograma de resultados")
		ventana.geometry("720x460")

		canvas = tk.Canvas(ventana, width=720, height=460, bg="white", highlightthickness=0)
		canvas.pack(fill="both", expand=True)

		margen_izq, margen_der = 70, 30
		margen_sup, margen_inf = 50, 70
		ancho = 720 - margen_izq - margen_der
		alto = 460 - margen_sup - margen_inf

		canvas.create_text(360, 24, text="Histograma de Tiradas", font=("TkDefaultFont", 14, "bold"))
		canvas.create_line(margen_izq, margen_sup, margen_izq, margen_sup + alto, width=2)
		canvas.create_line(margen_izq, margen_sup + alto, margen_izq + ancho, margen_sup + alto, width=2)

		max_frec = max(conteo.get(c, 0) for c in range(1, 7))
		if max_frec == 0:
			max_frec = 1

		ancho_barra = ancho / 6 * 0.65
		separacion = ancho / 6

		for i, cara in enumerate(range(1, 7)):
			frec = conteo.get(cara, 0)
			bar_h = (frec / max_frec) * (alto - 10)
			x_centro = margen_izq + separacion * (i + 0.5)
			x0 = x_centro - ancho_barra / 2
			x1 = x_centro + ancho_barra / 2
			y1 = margen_sup + alto
			y0 = y1 - bar_h

			color = "#d62828" if cara in self.seleccionados else "#cccccc"
			canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#7f1d1d")
			canvas.create_text(x_centro, y1 + 18, text=str(cara), font=("TkDefaultFont", 10, "bold"))
			canvas.create_text(x_centro, y0 - 12, text=str(frec), font=("TkDefaultFont", 9))

		canvas.create_text(360, 440, text="Eje X: cara del dado | Eje Y: frecuencia absoluta", fill="#444444")

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
