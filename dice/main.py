import json
import importlib
import logging
import os
import queue
import random
import threading
import time
import tkinter as tk
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from itertools import islice, product
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk
from typing import Callable

try:
	cp = importlib.import_module("cupy")
except Exception:  # pragma: no cover - opcional en tiempo de ejecucion
	cp = None

PALETA_DADOS = ["#d62828", "#1df700", "#1e3adb", "#2a9d8f", "#e7e42c", "#7b2cbf", "#9B1960", "#36250f"]
MAXIMO_HISTORIAL_MUESTRA = 3000
MAXIMO_HISTORIAL_RENDER_UI = 800
UMBRAL_PARALELISMO = 50000
UMBRAL_GPU_AUTO = 40000
TAMANIO_LOTE_GPU = 120000
LOG_FILENAME = "dice_app.log"

LOGGER = logging.getLogger("dice_app")


def _configurar_logging(log_path: Path) -> logging.Logger:
	logger = logging.getLogger("dice_app")
	if logger.handlers:
		return logger

	logger.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(processName)s | %(message)s")

	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.INFO)
	stream_handler.setFormatter(formatter)

	file_handler = logging.FileHandler(log_path, encoding="utf-8")
	file_handler.setLevel(logging.INFO)
	file_handler.setFormatter(formatter)

	logger.addHandler(stream_handler)
	logger.addHandler(file_handler)
	logger.propagate = False
	return logger


def _simular_lote_estadistico(args: tuple[int, int]) -> tuple[int, list[Counter[int]], Counter[int], Counter[tuple[int, ...]], tuple[int, ...]]:
	cantidad_experimentos, cantidad_dados = args
	LOGGER.info(
		"[CPU worker] inicio lote: experimentos=%s, dados=%s, pid=%s",
		cantidad_experimentos,
		cantidad_dados,
		os.getpid(),
	)
	frecuencias_globales = Counter()
	frecuencias_por_dado = [Counter() for _ in range(cantidad_dados)]
	eventos = Counter()
	ultimo: tuple[int, ...] = tuple()

	for _ in range(cantidad_experimentos):
		resultado = tuple(random.randint(1, 6) for _ in range(cantidad_dados))
		ultimo = resultado
		eventos[resultado] += 1
		for indice, valor in enumerate(resultado):
			frecuencias_por_dado[indice][valor] += 1
			frecuencias_globales[valor] += 1

	LOGGER.info(
		"[CPU worker] fin lote: experimentos=%s, pid=%s",
		cantidad_experimentos,
		os.getpid(),
	)
	return cantidad_experimentos, frecuencias_por_dado, frecuencias_globales, eventos, ultimo


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
		self.root.geometry("1360x860")
		self.root.minsize(1200, 800)

		self.sessions_dir = Path(__file__).resolve().parent / "sessions"
		self.sessions_dir.mkdir(parents=True, exist_ok=True)
		self.log_path = Path(__file__).resolve().parent / LOG_FILENAME
		self.logger = _configurar_logging(self.log_path)

		self.historial: list[tuple[int, ...]] = []
		self.historial_recortado = False
		self.seleccionados: set[int] = set(range(1, 7))
		self.cantidad_dados = 1
		self._cache_espacios: dict[int, list[tuple[int, ...]]] = {}
		self._resumen_por_dimension: dict[int, dict[str, object]] = {}
		self._benchmark_perfiles: dict[tuple[int, int], dict[str, float]] = {}
		self.animando = False
		self._gpu_disponible_cache = self._gpu_disponible()
		self.modo_ejecucion_var = tk.StringVar(value="AUTO")
		self._loader_ventana: tk.Toplevel | None = None
		self._loader_label_etapa: ttk.Label | None = None
		self._loader_label_valor: ttk.Label | None = None
		self._loader_barra: ttk.Progressbar | None = None
		self._ultimo_bucket_log: int = -1
		self._sim_thread: threading.Thread | None = None
		self._progreso_queue: queue.Queue[tuple[int, int, str] | None] = queue.Queue()
		self._postprocesando_simulacion = False
		self.logger.info(
			"App iniciada | gpu_disponible=%s | log=%s",
			self._gpu_disponible_cache,
			self.log_path,
		)

		self.check_vars: dict[int, tk.BooleanVar] = {
			cara: tk.BooleanVar(value=True) for cara in range(1, 7)
		}
		self.ordenar_frecuencia_espacio = tk.BooleanVar(value=False)

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
		self.entrada_dados.grid(row=0, column=3, padx=4, pady=4, sticky="w")

		self.entrada_n = ttk.Entry(controles, width=8)
		self.entrada_n.insert(0, "10")
		self.entrada_n.grid(row=1, column=1, padx=4, pady=4, sticky="e")

		self.lbl_n = ttk.Label(controles, text="Experimentos:")
		self.lbl_n.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

		self.btn_n = ttk.Button(controles, text="Lanzar N veces", command=self.lanzar_n_veces)
		self.btn_n.grid(row=1, column=2, padx=4, pady=4, sticky="ew")

		self.lbl_segundos = ttk.Label(controles, text="Duracion (s):")
		self.lbl_segundos.grid(row=2, column=0, padx=4, pady=4, sticky="ew")

		self.entrada_segundos = ttk.Entry(controles, width=8)
		self.entrada_segundos.insert(0, "5")
		self.entrada_segundos.grid(row=2, column=1, padx=4, pady=4, sticky="e")

		self.btn_tiempo = ttk.Button(controles, text="Lanzar por tiempo", command=self.lanzar_por_tiempo)
		self.btn_tiempo.grid(row=2, column=2, padx=4, pady=4, sticky="ew")

		self.lbl_lote = ttk.Label(controles, text="Tamano lote:")
		self.lbl_lote.grid(row=5, column=0, padx=4, pady=4, sticky="ew")

		self.entrada_lote = ttk.Entry(controles, width=8)
		self.entrada_lote.insert(0, "auto")
		self.entrada_lote.grid(row=5, column=1, padx=4, pady=4, sticky="e")

		self.lbl_trabajadores = ttk.Label(controles, text="Procesos paralelos:")
		self.lbl_trabajadores.grid(row=6, column=0, padx=4, pady=4, sticky="ew")

		self.entrada_trabajadores = ttk.Entry(controles, width=8)
		self.entrada_trabajadores.insert(0, "auto")
		self.entrada_trabajadores.grid(row=6, column=2, padx=4, pady=4, sticky="w")

		self.lbl_modo = ttk.Label(controles, text="Modo ejecución:")
		self.lbl_modo.grid(row=7, column=0, padx=4, pady=4, sticky="ew")

		self.combo_modo = ttk.Combobox(
			controles,
			state="readonly",
			textvariable=self.modo_ejecucion_var,
			values=["CPU", "GPU", "AUTO", "AMBAS"],
			width=12,
		)
		self.combo_modo.grid(row=7, column=2, padx=4, pady=4, sticky="w")
		self.combo_modo.set("AUTO")

		self.btn_benchmark = ttk.Button(
			controles,
			text="Benchmark modos",
			command=self.mostrar_benchmark_modos,
		)
		self.btn_benchmark.grid(row=7, column=1, padx=4, pady=4, sticky="ew")

		self.btn_hist = ttk.Button(controles, text="Histograma", command=self.mostrar_histograma)
		self.btn_hist.grid(row=3, column=0, padx=4, pady=4, sticky="ew")

		self.btn_graf = ttk.Button(controles, text="Graficar resultados", command=self.mostrar_grafica)
		self.btn_graf.grid(row=3, column=2, padx=4, pady=4, sticky="ew")

		self.btn_lista_espacio = ttk.Button(
			controles,
			text="Ver espacio muestral",
			command=self.mostrar_lista_espacio_muestral,
		)
		self.btn_lista_espacio.grid(row=4, column=0, padx=4, pady=4, sticky="ew")

		self.btn_hist_espacio = ttk.Button(
			controles,
			text="Histograma espacio",
			command=self.mostrar_histograma_espacio_muestral,
		)
		self.btn_hist_espacio.grid(row=4, column=2, padx=4, pady=4, sticky="ew")

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

		self.chk_ordenar_frecuencia_espacio = ttk.Checkbutton(
			espacio_frame,
			text="Ordenar por frecuencia (desc) en histograma",
			variable=self.ordenar_frecuencia_espacio,
		)
		self.chk_ordenar_frecuencia_espacio.pack(anchor="w", pady=(6, 0))

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
			wrap="none",
			width=32,
			state="disabled",
			relief="flat",
			font=("TkFixedFont", 9),
		)
		_sb_stats = ttk.Scrollbar(stats_frame, orient="vertical", command=self.txt_stats.yview)
		_sb_stats_x = ttk.Scrollbar(stats_frame, orient="horizontal", command=self.txt_stats.xview)
		self.txt_stats.configure(yscrollcommand=_sb_stats.set, xscrollcommand=_sb_stats_x.set)
		self.txt_stats.grid(row=0, column=0, sticky="nsew")
		_sb_stats.grid(row=0, column=1, sticky="ns")
		_sb_stats_x.grid(row=1, column=0, sticky="ew")
		self._actualizar_espacio_muestral()

	def _obtener_cantidad_dados(self) -> int | None:
		texto = self.entrada_dados.get().strip()
		if not texto.isdigit() or int(texto) <= 0:
			self.lbl_estado.config(text="Ingresa una cantidad positiva de dados.")
			return None
		return int(texto)

	def _obtener_trabajadores(self) -> int | None:
		texto = self.entrada_trabajadores.get().strip().lower()
		if texto in {"", "auto", "0"}:
			return os.cpu_count() or 1
		if not texto.isdigit() or int(texto) <= 0:
			self.lbl_estado.config(text="Ingresa un número positivo de procesos o 'auto'.")
			return None
		return int(texto)

	def _obtener_tamanio_lote(self) -> int | None:
		texto = self.entrada_lote.get().strip().lower()
		if texto in {"", "auto", "0"}:
			return 0
		if not texto.isdigit() or int(texto) <= 0:
			self.lbl_estado.config(text="Ingresa un tamano de lote positivo o 'auto'.")
			return None
		return int(texto)

	def _gpu_disponible(self) -> bool:
		if cp is None:
			return False
		try:
			if cp.cuda.runtime.getDeviceCount() <= 0:
				return False
			# Verifica librerias runtime necesarias (ej. curand) con una operacion minima.
			_ = cp.random.randint(1, 7, size=(1,), dtype=cp.int16)
			cp.cuda.Stream.null.synchronize()
			return True
		except Exception:
			return False

	def _modo_solicitado(self) -> str:
		modo = self.modo_ejecucion_var.get().strip().upper()
		if modo not in {"CPU", "GPU", "AUTO", "AMBAS"}:
			return "AUTO"
		return modo

	def _guardar_resultado_benchmark(self, cantidad: int, cantidad_dados: int, resultados: dict[str, float]) -> None:
		self._benchmark_perfiles[(cantidad_dados, cantidad)] = resultados
		self.logger.info(
			"Benchmark guardado | dados=%s | N=%s | resultados=%s",
			cantidad_dados,
			cantidad,
			resultados,
		)

	def _modo_auto_aprendido(self, cantidad_experimentos: int, cantidad_dados: int) -> str | None:
		if not self._benchmark_perfiles:
			return None

		candidatos = [
			((dados, n), tiempos)
			for (dados, n), tiempos in self._benchmark_perfiles.items()
			if dados == cantidad_dados
		]
		if not candidatos:
			return None

		(_, _), tiempos = min(candidatos, key=lambda item: abs(item[0][1] - cantidad_experimentos))
		if not tiempos:
			return None

		modo_ganador, _ = min(tiempos.items(), key=lambda t: t[1])
		if modo_ganador in {"CPU", "GPU", "AMBAS"}:
			return modo_ganador
		return None

	def _resolver_modo_real(self, modo_solicitado: str, cantidad_experimentos: int) -> tuple[str, str]:
		if modo_solicitado == "CPU":
			return "CPU", ""

		if modo_solicitado == "GPU":
			if self._gpu_disponible_cache:
				return "GPU", ""
			return "CPU", "GPU no disponible; se usó CPU."

		if modo_solicitado == "AMBAS":
			if self._gpu_disponible_cache and cantidad_experimentos >= 2:
				return "AMBAS", ""
			if not self._gpu_disponible_cache:
				return "CPU", "GPU no disponible; se usó CPU."
			return "CPU", "Se requieren al menos 2 experimentos para AMBAS; se usó CPU."

		modo_aprendido = self._modo_auto_aprendido(cantidad_experimentos, self.cantidad_dados)
		if modo_aprendido is not None:
			if modo_aprendido == "GPU" and not self._gpu_disponible_cache:
				return "CPU", "AUTO aprendió GPU, pero no está disponible; se usó CPU."
			if modo_aprendido == "AMBAS" and not self._gpu_disponible_cache:
				return "CPU", "AUTO aprendió AMBAS, pero GPU no está disponible; se usó CPU."
			return modo_aprendido, f"AUTO eligió {modo_aprendido} según benchmark aprendido."

		if self._gpu_disponible_cache and cantidad_experimentos >= UMBRAL_GPU_AUTO:
			return "GPU", "AUTO eligió GPU por umbral base."
		return "CPU", "AUTO eligió CPU por umbral base."

	def _crear_resumen_dimension(self, cantidad_dados: int) -> dict[str, object]:
		return {
			"total": 0,
			"frecuencias_globales": Counter(),
			"frecuencias_por_dado": [Counter() for _ in range(cantidad_dados)],
			"eventos": Counter(),
		}

	def _obtener_resumen_dimension(self, cantidad_dados: int) -> dict[str, object]:
		resumen = self._resumen_por_dimension.get(cantidad_dados)
		if resumen is None:
			resumen = self._crear_resumen_dimension(cantidad_dados)
			self._resumen_por_dimension[cantidad_dados] = resumen
		return resumen

	def _registrar_resultado_en_resumen(self, resultado: tuple[int, ...]) -> None:
		resumen = self._obtener_resumen_dimension(len(resultado))
		resumen["total"] = int(resumen["total"]) + 1
		frecuencias_globales: Counter[int] = resumen["frecuencias_globales"]  # type: ignore[assignment]
		frecuencias_por_dado: list[Counter[int]] = resumen["frecuencias_por_dado"]  # type: ignore[assignment]
		eventos: Counter[tuple[int, ...]] = resumen["eventos"]  # type: ignore[assignment]
		eventos[resultado] += 1
		for indice, valor in enumerate(resultado):
			frecuencias_por_dado[indice][valor] += 1
			frecuencias_globales[valor] += 1

	def _registrar_muestra_historial(self, resultados: list[tuple[int, ...]]) -> None:
		if not resultados:
			return
		self.historial.extend(resultados)
		if len(self.historial) > MAXIMO_HISTORIAL_MUESTRA:
			exceso = len(self.historial) - MAXIMO_HISTORIAL_MUESTRA
			del self.historial[:exceso]
			self.historial_recortado = True

	def _aplicar_resultados(self, resultados: list[tuple[int, ...]]) -> None:
		for resultado in resultados:
			self._registrar_resultado_en_resumen(resultado)
		self._registrar_muestra_historial(resultados)

	def _combinar_resumen_parcial(
		self,
		cantidad_dados: int,
		cantidad_experimentos: int,
		frecuencias_por_dado: list[Counter[int]],
		frecuencias_globales: Counter[int],
		eventos: Counter[tuple[int, ...]],
	) -> None:
		resumen = self._obtener_resumen_dimension(cantidad_dados)
		resumen["total"] = int(resumen["total"]) + cantidad_experimentos
		frecuencias_globales_total: Counter[int] = resumen["frecuencias_globales"]  # type: ignore[assignment]
		frecuencias_por_dado_total: list[Counter[int]] = resumen["frecuencias_por_dado"]  # type: ignore[assignment]
		eventos_total: Counter[tuple[int, ...]] = resumen["eventos"]  # type: ignore[assignment]
		for indice, conteo in enumerate(frecuencias_por_dado):
			frecuencias_por_dado_total[indice].update(conteo)
		frecuencias_globales_total.update(frecuencias_globales)
		eventos_total.update(eventos)

	def _generar_resultados_masivos(
		self,
		cantidad_experimentos: int,
		cantidad_dados: int,
		trabajadores: int,
		progreso_cb: Callable[[int], None] | None = None,
	) -> tuple[list[tuple[int, ...]], tuple[int, ...]]:
		self.logger.info(
			"Generar masivos | experimentos=%s | dados=%s | trabajadores=%s",
			cantidad_experimentos,
			cantidad_dados,
			trabajadores,
		)
		if cantidad_experimentos <= 0:
			return [], tuple()

		if trabajadores <= 1 or cantidad_experimentos < UMBRAL_PARALELISMO:
			resultados: list[tuple[int, ...]] = []
			ultimo: tuple[int, ...] = tuple()
			for indice in range(cantidad_experimentos):
				resultado = tuple(random.randint(1, 6) for _ in range(cantidad_dados))
				resultados.append(resultado)
				ultimo = resultado
				if progreso_cb is not None and (indice == cantidad_experimentos - 1 or (indice + 1) % max(1, cantidad_experimentos // 40) == 0):
					progreso_cb(indice + 1)
			return resultados, ultimo

		chunk_size = max(10000, cantidad_experimentos // trabajadores)
		trabajos: list[tuple[int, int]] = []
		restante = cantidad_experimentos
		while restante > 0:
			lote = min(chunk_size, restante)
			trabajos.append((lote, cantidad_dados))
			restante -= lote

		ultimo: tuple[int, ...] = tuple()
		muestra: list[tuple[int, ...]] = []
		procesados = 0
		with ProcessPoolExecutor(max_workers=trabajadores) as executor:
			total_trabajos = len(trabajos)
			for indice_trabajo, (cantidad_lote, frecuencias_por_dado, frecuencias_globales, eventos, ultimo_lote) in enumerate(
				executor.map(_simular_lote_estadistico, trabajos),
				start=1,
			):
				self._combinar_resumen_parcial(
					cantidad_dados,
					cantidad_lote,
					frecuencias_por_dado,
					frecuencias_globales,
					eventos,
				)
				ultimo = ultimo_lote
				if ultimo_lote:
					muestra.append(ultimo_lote)
				procesados += cantidad_lote
				if progreso_cb is not None:
					progreso_cb(procesados)
				if indice_trabajo == 1 or indice_trabajo == total_trabajos or indice_trabajo % max(1, total_trabajos // 5) == 0:
					self.logger.info(
						"CPU paralelo progreso | trabajo=%s/%s",
						indice_trabajo,
						total_trabajos,
					)

		return muestra, ultimo

	def _simular_gpu_con_resumen(
		self,
		cantidad_experimentos: int,
		cantidad_dados: int,
		tamanio_lote_gpu: int = TAMANIO_LOTE_GPU,
		progreso_cb: Callable[[int], None] | None = None,
	) -> tuple[list[tuple[int, ...]], tuple[int, ...]]:
		if cp is None or not self._gpu_disponible_cache or cantidad_experimentos <= 0:
			return [], tuple()

		tamanio_lote_gpu = max(1, int(tamanio_lote_gpu))

		self.logger.info(
			"GPU inicio | experimentos=%s | dados=%s | lote_max=%s",
			cantidad_experimentos,
			cantidad_dados,
			tamanio_lote_gpu,
		)

		muestra: list[tuple[int, ...]] = []
		ultimo: tuple[int, ...] = tuple()
		restante = cantidad_experimentos
		procesados = 0

		while restante > 0:
			lote = min(tamanio_lote_gpu, restante)
			self.logger.info("GPU lote inicio | lote=%s | restante_antes=%s", lote, restante)
			datos_gpu = cp.random.randint(1, 7, size=(lote, cantidad_dados), dtype=cp.int16)
			cp.cuda.Stream.null.synchronize()
			datos_np = cp.asnumpy(datos_gpu)

			frecuencias_por_dado: list[Counter[int]] = []
			frecuencias_globales = Counter()
			for indice in range(cantidad_dados):
				conteos = [0] * 7
				for fila in datos_np:
					conteos[int(fila[indice])] += 1
				conteo_dado = Counter({cara: int(conteos[cara]) for cara in range(1, 7) if int(conteos[cara]) > 0})
				frecuencias_por_dado.append(conteo_dado)
				frecuencias_globales.update(conteo_dado)

			eventos: Counter[tuple[int, ...]] = Counter()
			for fila in datos_np:
				evento = tuple(int(v) for v in fila.tolist())
				eventos[evento] += 1

			ultimo = tuple(int(v) for v in datos_np[-1].tolist())
			self._combinar_resumen_parcial(cantidad_dados, lote, frecuencias_por_dado, frecuencias_globales, eventos)
			if ultimo:
				muestra.append(ultimo)

			restante -= lote
			procesados += lote
			if progreso_cb is not None:
				progreso_cb(procesados)
			self.logger.info("GPU progreso | lote=%s | restante=%s", lote, restante)

		self.logger.info("GPU fin | experimentos=%s", cantidad_experimentos)
		return muestra, ultimo

	def _ejecutar_cpu(
		self,
		cantidad: int,
		trabajadores: int,
		progreso_cb: Callable[[int], None] | None = None,
	) -> tuple[list[tuple[int, ...]], tuple[int, ...], bool]:
		if cantidad >= UMBRAL_PARALELISMO and trabajadores > 1:
			muestra, ultimo = self._generar_resultados_masivos(cantidad, self.cantidad_dados, trabajadores, progreso_cb=progreso_cb)
			return muestra, ultimo, True

		resultados, ultimo = self._generar_resultados_masivos(cantidad, self.cantidad_dados, 1, progreso_cb=progreso_cb)
		self._aplicar_resultados(resultados)
		return resultados, ultimo, False

	def _benchmark_cpu(self, cantidad: int, cantidad_dados: int, trabajadores: int) -> float:
		inicio = time.perf_counter()
		if cantidad >= UMBRAL_PARALELISMO and trabajadores > 1:
			chunk_size = max(10000, cantidad // trabajadores)
			trabajos: list[tuple[int, int]] = []
			restante = cantidad
			while restante > 0:
				lote = min(chunk_size, restante)
				trabajos.append((lote, cantidad_dados))
				restante -= lote

			with ProcessPoolExecutor(max_workers=trabajadores) as executor:
				for _ in executor.map(_simular_lote_estadistico, trabajos):
					pass
		else:
			for _ in range(cantidad):
				for _ in range(cantidad_dados):
					random.randint(1, 6)

		return time.perf_counter() - inicio

	def _benchmark_gpu(self, cantidad: int, cantidad_dados: int) -> float | None:
		if cp is None or not self._gpu_disponible_cache:
			return None

		inicio = time.perf_counter()
		restante = cantidad
		while restante > 0:
			lote = min(TAMANIO_LOTE_GPU, restante)
			datos_gpu = cp.random.randint(1, 7, size=(lote, cantidad_dados), dtype=cp.int16)
			_ = cp.sum(datos_gpu)
			restante -= lote

		cp.cuda.Stream.null.synchronize()
		return time.perf_counter() - inicio

	def _benchmark_ambas(self, cantidad: int, cantidad_dados: int, trabajadores: int) -> float | None:
		if cp is None or not self._gpu_disponible_cache or cantidad < 2:
			return None

		cantidad_gpu = cantidad // 2
		cantidad_cpu = cantidad - cantidad_gpu
		inicio = time.perf_counter()
		_ = self._benchmark_gpu(cantidad_gpu, cantidad_dados)
		_ = self._benchmark_cpu(cantidad_cpu, cantidad_dados, trabajadores)
		return time.perf_counter() - inicio

	def mostrar_benchmark_modos(self) -> None:
		cantidad_dados = self._obtener_cantidad_dados()
		if cantidad_dados is None:
			return

		trabajadores = self._obtener_trabajadores()
		if trabajadores is None:
			return

		texto = self.entrada_n.get().strip()
		if not texto.isdigit() or int(texto) <= 0:
			self.lbl_estado.config(text="Ingresa un entero positivo para N.")
			return

		cantidad = int(texto)
		self.logger.info(
			"Benchmark inicio | N=%s | dados=%s | trabajadores=%s",
			cantidad,
			cantidad_dados,
			trabajadores,
		)
		self.root.config(cursor="watch")
		self.root.update_idletasks()

		try:
			tiempo_cpu = self._benchmark_cpu(cantidad, cantidad_dados, trabajadores)
			tiempo_gpu = self._benchmark_gpu(cantidad, cantidad_dados)
			tiempo_ambas = self._benchmark_ambas(cantidad, cantidad_dados, trabajadores)
		finally:
			self.root.config(cursor="")

		resultados: list[tuple[str, float]] = [("CPU", tiempo_cpu)]
		if tiempo_gpu is not None:
			resultados.append(("GPU", tiempo_gpu))
		if tiempo_ambas is not None:
			resultados.append(("AMBAS", tiempo_ambas))

		if self._gpu_disponible_cache and tiempo_gpu is not None and cantidad >= UMBRAL_GPU_AUTO:
			modo_auto = "GPU"
		else:
			modo_auto = "CPU"

		mejor_modo, mejor_tiempo = min(resultados, key=lambda t: t[1])

		lineas: list[str] = []
		lineas.append("Benchmark de modos")
		lineas.append(f"N={cantidad}, dados={cantidad_dados}, procesos CPU={trabajadores}")
		lineas.append("")
		for modo, tiempo_modo in resultados:
			lineas.append(f"{modo}: {tiempo_modo:.4f} s")
		if tiempo_gpu is None:
			lineas.append("GPU: no disponible")
		if tiempo_ambas is None:
			lineas.append("AMBAS: no disponible")
		lineas.append("")
		lineas.append(f"AUTO sugerido para este N: {modo_auto}")
		lineas.append(f"Modo mas rapido medido: {mejor_modo} ({mejor_tiempo:.4f} s)")

		resultados_dict = {modo: tiempo_modo for modo, tiempo_modo in resultados}
		self._guardar_resultado_benchmark(cantidad, cantidad_dados, resultados_dict)
		self.logger.info(
			"Benchmark fin | N=%s | dados=%s | resultados=%s | mejor=%s",
			cantidad,
			cantidad_dados,
			resultados_dict,
			mejor_modo,
		)

		ventana = tk.Toplevel(self.root)
		ventana.title("Benchmark de modos")
		ventana.geometry("620x340")

		texto_benchmark = tk.Text(ventana, wrap="word")
		texto_benchmark.pack(fill="both", expand=True, padx=10, pady=10)
		texto_benchmark.insert("1.0", "\n".join(lineas))
		texto_benchmark.configure(state="disabled")

		self.lbl_estado.config(text=f"Benchmark completado. Mejor modo: {mejor_modo}.")

	def _serializar_resumenes(self) -> dict[str, dict[str, object]]:
		serializados: dict[str, dict[str, object]] = {}
		for dimension, resumen in self._resumen_por_dimension.items():
			frecuencias_por_dado: list[Counter[int]] = resumen["frecuencias_por_dado"]  # type: ignore[assignment]
			eventos: Counter[tuple[int, ...]] = resumen["eventos"]  # type: ignore[assignment]
			serializados[str(dimension)] = {
				"total": int(resumen["total"]),
				"frecuencias_globales": dict(resumen["frecuencias_globales"]),
				"frecuencias_por_dado": [dict(conteo) for conteo in frecuencias_por_dado],
				"eventos": [[list(evento), fa] for evento, fa in eventos.items()],
			}
		return serializados

	def _serializar_benchmark_perfiles(self) -> dict[str, dict[str, float]]:
		serializado: dict[str, dict[str, float]] = {}
		for (dados, n), tiempos in self._benchmark_perfiles.items():
			clave = f"{dados}|{n}"
			serializado[clave] = {modo: float(valor) for modo, valor in tiempos.items()}
		return serializado

	def _cargar_benchmark_perfiles(self, datos: object) -> bool:
		if not isinstance(datos, dict):
			return False

		perfiles: dict[tuple[int, int], dict[str, float]] = {}
		for clave, valor in datos.items():
			if not isinstance(clave, str) or "|" not in clave or not isinstance(valor, dict):
				return False
			partes = clave.split("|", maxsplit=1)
			try:
				dados = int(partes[0])
				n = int(partes[1])
			except (TypeError, ValueError):
				return False

			tiempos: dict[str, float] = {}
			for modo, tiempo in valor.items():
				if modo not in {"CPU", "GPU", "AMBAS"}:
					continue
				try:
					tiempos[modo] = float(tiempo)
				except (TypeError, ValueError):
					return False

			if tiempos:
				perfiles[(dados, n)] = tiempos

		self._benchmark_perfiles = perfiles
		return True

	def _cargar_resumenes_serializados(self, datos: object) -> bool:
		if not isinstance(datos, dict):
			return False

		resumenes: dict[int, dict[str, object]] = {}
		for clave, valor in datos.items():
			if not isinstance(valor, dict):
				return False
			try:
				dimension = int(clave)
			except (TypeError, ValueError):
				return False

			frecuencias_globales_raw = valor.get("frecuencias_globales", {})
			frecuencias_por_dado_raw = valor.get("frecuencias_por_dado", [])
			eventos_raw = valor.get("eventos", [])
			if not isinstance(frecuencias_globales_raw, dict) or not isinstance(frecuencias_por_dado_raw, list) or not isinstance(eventos_raw, list):
				return False

			frecuencias_por_dado: list[Counter[int]] = []
			for conteo_raw in frecuencias_por_dado_raw:
				if not isinstance(conteo_raw, dict):
					return False
				frecuencias_por_dado.append(Counter({int(k): int(v) for k, v in conteo_raw.items()}))

			if len(frecuencias_por_dado) != dimension:
				return False

			eventos: Counter[tuple[int, ...]] = Counter()
			for item in eventos_raw:
				if not isinstance(item, list) or len(item) != 2:
					return False
				evento_raw, fa_raw = item
				if not isinstance(evento_raw, list):
					return False
				try:
					evento = tuple(int(x) for x in evento_raw)
					fa = int(fa_raw)
				except (TypeError, ValueError):
					return False
				eventos[evento] = fa

			resumenes[dimension] = {
				"total": int(valor.get("total", 0)),
				"frecuencias_globales": Counter({int(k): int(v) for k, v in frecuencias_globales_raw.items()}),
				"frecuencias_por_dado": frecuencias_por_dado,
				"eventos": eventos,
			}

		self._resumen_por_dimension = resumenes
		return True

	def _resumen_dimension_actual(self) -> dict[str, object] | None:
		return self._resumen_por_dimension.get(self.cantidad_dados)

	def _formatear_espacio_muestral(self, cantidad_dados: int) -> str:
		espacio = self._obtener_espacio_muestral(cantidad_dados)
		if cantidad_dados == 1:
			contenido = ", ".join(str(t[0]) for t in espacio)
			return f"Ω = {{{contenido}}}"

		if cantidad_dados <= 2:
			contenido = ", ".join(str(t) for t in espacio)
			return f"Ω = {{{contenido}}}"

		muestras = ", ".join(str(t) for t in islice(espacio, 15))
		nombres = {
			3: "(x, y, z)",
			4: "(x, y, z, w)",
			5: "(x, y, z, w, u)",
			6: "(x, y, z, w, u, v)",
		}
		notacion = nombres.get(cantidad_dados, f"(x1, ..., x{cantidad_dados})")
		return (
			f"Ω = {{{notacion} : cada componente en {{1, 2, 3, 4, 5, 6}}}}\n"
			+ f"Total de eventos: {len(espacio)}. "
			+ "Ejemplos: "
			+ muestras
			+ ", ..."
		)

	def _obtener_espacio_muestral(self, cantidad_dados: int) -> list[tuple[int, ...]]:
		if cantidad_dados not in self._cache_espacios:
			self._cache_espacios[cantidad_dados] = list(product(range(1, 7), repeat=cantidad_dados))
		return self._cache_espacios[cantidad_dados]

	def _formatear_evento(self, evento: tuple[int, ...]) -> str:
		if len(evento) == 1:
			return str(evento[0])
		return str(evento)

	def _historial_misma_dimension(self) -> list[tuple[int, ...]]:
		return [evento for evento in self.historial if len(evento) == self.cantidad_dados]

	def _obtener_frecuencias_espacio_muestral(self) -> list[tuple[tuple[int, ...], int, float]]:
		espacio = self._obtener_espacio_muestral(self.cantidad_dados)
		resumen = self._resumen_dimension_actual()
		if resumen is None:
			return [(evento, 0, 0.0) for evento in espacio]
		total = int(resumen["total"])
		conteo: Counter[tuple[int, ...]] = resumen["eventos"]  # type: ignore[assignment]
		if total == 0:
			return [(evento, 0, 0.0) for evento in espacio]
		return [(evento, conteo.get(evento, 0), conteo.get(evento, 0) / total) for evento in espacio]

	def _crear_tooltip_canvas(self, canvas: tk.Canvas) -> tuple[int, int]:
		texto_id = canvas.create_text(
			0,
			0,
			text="",
			anchor="nw",
			fill="#111111",
			font=("TkDefaultFont", 9, "bold"),
			state="hidden",
			tags=("tooltip",),
		)
		rec_id = canvas.create_rectangle(
			0,
			0,
			0,
			0,
			fill="#fff7cc",
			outline="#8a7b2d",
			width=1,
			state="hidden",
			tags=("tooltip",),
		)
		canvas.tag_raise(texto_id)
		return rec_id, texto_id

	def _mostrar_tooltip_canvas(
		self,
		canvas: tk.Canvas,
		rec_id: int,
		texto_id: int,
		event: tk.Event,
		texto: str,
	) -> None:
		x = canvas.canvasx(event.x) + 12
		y = canvas.canvasy(event.y) + 12
		canvas.itemconfigure(texto_id, text=texto, state="normal")
		canvas.coords(texto_id, x, y)
		x0, y0, x1, y1 = canvas.bbox(texto_id)
		canvas.coords(rec_id, x0 - 6, y0 - 4, x1 + 6, y1 + 4)
		canvas.itemconfigure(rec_id, state="normal")
		canvas.tag_raise(texto_id)

	def _ocultar_tooltip_canvas(self, canvas: tk.Canvas, rec_id: int, texto_id: int) -> None:
		canvas.itemconfigure(texto_id, state="hidden")
		canvas.itemconfigure(rec_id, state="hidden")

	def _habilitar_zoom_y_arrastre_canvas(self, canvas: tk.Canvas) -> None:
		canvas._zoom_level = 1.0  # type: ignore[attr-defined]

		def actualizar_scrollregion() -> None:
			bbox = canvas.bbox("all")
			if bbox is not None:
				canvas.configure(scrollregion=(bbox[0] - 40, bbox[1] - 40, bbox[2] + 40, bbox[3] + 40))

		def iniciar_arrastre(event: tk.Event) -> None:
			canvas.scan_mark(event.x, event.y)

		def arrastrar(event: tk.Event) -> None:
			canvas.scan_dragto(event.x, event.y, gain=1)

		def hacer_zoom(event: tk.Event, acercar: bool) -> None:
			actual = float(getattr(canvas, "_zoom_level", 1.0))
			factor = 1.1 if acercar else 0.9
			nuevo = actual * factor
			if nuevo < 0.35 or nuevo > 6.0:
				return
			x = canvas.canvasx(event.x)
			y = canvas.canvasy(event.y)
			canvas.scale("all", x, y, factor, factor)
			canvas._zoom_level = nuevo  # type: ignore[attr-defined]
			actualizar_scrollregion()

		def on_mousewheel(event: tk.Event) -> None:
			if event.state & 0x0004:  # Control presionado
				hacer_zoom(event, getattr(event, "delta", 0) > 0)
				return
			canvas.yview_scroll(-1 if getattr(event, "delta", 0) > 0 else 1, "units")

		def on_shift_mousewheel(event: tk.Event) -> None:
			canvas.xview_scroll(-1 if getattr(event, "delta", 0) > 0 else 1, "units")

		def on_button_4(event: tk.Event) -> None:
			if event.state & 0x0004:  # Control + rueda arriba
				hacer_zoom(event, True)
				return
			canvas.yview_scroll(-1, "units")

		def on_button_5(event: tk.Event) -> None:
			if event.state & 0x0004:  # Control + rueda abajo
				hacer_zoom(event, False)
				return
			canvas.yview_scroll(1, "units")

		canvas.bind("<ButtonPress-1>", iniciar_arrastre)
		canvas.bind("<B1-Motion>", arrastrar)
		canvas.bind("<MouseWheel>", on_mousewheel)
		canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)
		canvas.bind("<Button-4>", on_button_4)
		canvas.bind("<Button-5>", on_button_5)
		actualizar_scrollregion()

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
			resumen = self._resumen_dimension_actual()
			if resumen is not None and int(resumen["total"]) > 0:
				self.txt_historial.insert("1.0", "Se guardó el resumen exacto, pero no hay muestra reciente en memoria.")
			else:
				self.txt_historial.insert("1.0", "Aún no hay lanzamientos.")
		else:
			total_historial = len(self.historial)
			mostrar_desde = max(0, total_historial - MAXIMO_HISTORIAL_RENDER_UI)
			historial_ui = self.historial[mostrar_desde:]

			prefijos: list[str] = []
			if self.historial_recortado:
				prefijos.append("Mostrando solo una muestra reciente de los resultados en memoria.")
			if mostrar_desde > 0:
				prefijos.append(
					f"Render UI limitado a los ultimos {len(historial_ui)} de {total_historial} experimentos para mantener fluidez."
				)

			texto_historial = ", ".join(str(experimento) for experimento in historial_ui)
			if prefijos:
				self.txt_historial.insert("1.0", "\n".join(prefijos) + "\n\n" + texto_historial)
			else:
				self.txt_historial.insert("1.0", texto_historial)
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

	def _mostrar_loader(self, titulo: str, total: int) -> None:
		self._cerrar_loader()
		total_seguro = max(1, total)
		ventana = tk.Toplevel(self.root)
		ventana.title(titulo)
		ventana.geometry("520x180")
		ventana.resizable(False, False)
		ventana.transient(self.root)
		ventana.protocol("WM_DELETE_WINDOW", self._cerrar_loader)

		marco = ttk.Frame(ventana, padding=16)
		marco.pack(fill="both", expand=True)

		label_etapa = ttk.Label(marco, text="Preparando...", font=("TkDefaultFont", 10, "bold"))
		label_etapa.pack(anchor="w", pady=(0, 8))

		barra = ttk.Progressbar(marco, orient="horizontal", length=460, mode="determinate", maximum=total_seguro)
		barra.pack(fill="x", pady=(0, 8))

		label_valor = ttk.Label(marco, text=f"0/{total_seguro} (0.00%)")
		label_valor.pack(anchor="w")

		btn_ocultar = ttk.Button(marco, text="Ocultar", command=self._cerrar_loader)
		btn_ocultar.pack(anchor="e", pady=(10, 0))

		self._loader_ventana = ventana
		self._loader_label_etapa = label_etapa
		self._loader_label_valor = label_valor
		self._loader_barra = barra
		self._ultimo_bucket_log = -1

	def _actualizar_loader(self, actual: int, total: int, etapa: str) -> None:
		"""
		Thread-safe: puede llamarse desde cualquier hilo.
		Encola el mensaje y el hilo principal lo consume con _poll_progreso().
		"""
		total_seguro = max(1, total)
		actual_seguro = max(0, min(actual, total_seguro))
		porcentaje = (actual_seguro / total_seguro) * 100

		# Log desde el hilo que llama (thread-safe en logging)
		bucket = int((actual_seguro / total_seguro) * 20)
		if bucket != self._ultimo_bucket_log or actual_seguro >= total_seguro:
			self._ultimo_bucket_log = bucket
			self.logger.info(
				"Progreso %s | %s/%s (%.2f%%)",
				etapa,
				actual_seguro,
				total_seguro,
				porcentaje,
			)

		# Encolar para que el hilo principal actualice la UI
		self._progreso_queue.put((actual_seguro, total_seguro, etapa))

	def _poll_progreso(self) -> None:
		"""Ejecutado en el hilo principal via after(); drena la cola y actualiza la UI."""
		try:
			while True:
				item = self._progreso_queue.get_nowait()
				if item is None:
					# Señal de fin: actualizar y cerrar loader
					self._cerrar_loader()
					self._finalizar_simulacion()
					return
				actual, total, etapa = item
				if self._loader_barra is not None:
					self._loader_barra["maximum"] = total
					self._loader_barra["value"] = actual
				if self._loader_label_etapa is not None:
					self._loader_label_etapa.config(text=f"Etapa: {etapa}")
				if self._loader_label_valor is not None:
					pct = (actual / total) * 100 if total else 0.0
					self._loader_label_valor.config(text=f"{actual}/{total} ({pct:.2f}%)")
		except queue.Empty:
			pass

		# Seguir sondeando mientras el hilo de simulacion exista
		if self._sim_thread is not None and self._sim_thread.is_alive():
			self.root.after(40, self._poll_progreso)
		else:
			# Hilo terminó sin enviar None (excepción silenciosa): cerrar de todas formas
			self._cerrar_loader()
			self._finalizar_simulacion()


	def _cerrar_loader(self) -> None:
		if self._loader_ventana is not None and self._loader_ventana.winfo_exists():
			self._loader_ventana.destroy()
		self._loader_ventana = None
		self._loader_label_etapa = None
		self._loader_label_valor = None
		self._loader_barra = None

	def _formatear_tabla(self, encabezados: list[str], filas: list[list[str]]) -> str:
		anchos = [len(h) for h in encabezados]
		for fila in filas:
			for i, celda in enumerate(fila):
				anchos[i] = max(anchos[i], len(celda))

		separador = "+-" + "-+-".join("-" * ancho for ancho in anchos) + "-+"
		encabezado = "| " + " | ".join(encabezados[i].ljust(anchos[i]) for i in range(len(encabezados))) + " |"
		cuerpo = [
			"| " + " | ".join(fila[i].ljust(anchos[i]) for i in range(len(encabezados))) + " |"
			for fila in filas
		]
		return "\n".join([separador, encabezado, separador, *cuerpo, separador])

	def _actualizar_estadisticas(self) -> None:
		resumen = self._resumen_dimension_actual()
		total_general = sum(int(datos["total"]) for datos in self._resumen_por_dimension.values())
		caras_seleccionadas = sorted(self.seleccionados)

		resumen_general_filas = [
			["Experimentos totales", str(total_general)],
			["Experimentos dimension actual", str(int(resumen["total"]) if resumen is not None else 0)],
			["Dados por experimento", str(self.cantidad_dados)],
			["Cardinalidad n(Ω)", str(6 ** self.cantidad_dados)],
		]

		if resumen is None:
			tabla_general = self._formatear_tabla(["Metrica", "Valor"], resumen_general_filas)
			tabla_frecuencias = self._formatear_tabla(
				["Cara", "fa", "fr", "%"],
				[[str(cara), "0", "0.0000", "0.00%"] for cara in caras_seleccionadas],
			)
			tabla_por_dado = self._formatear_tabla(
				["Dado", "Cara", "fa", "fr", "%", "Media dado", "Moda dado"],
				[
					[str(i + 1), str(cara), "0", "0.0000", "0.00%", "-", "-"]
					for i in range(self.cantidad_dados)
					for cara in caras_seleccionadas
				],
			)
			self._escribir_stats(
				"Tabla 1 - Resumen general\n"
				+ tabla_general
				+ "\n\nTabla 2 - Frecuencias globales\n"
				+ tabla_frecuencias
				+ "\n\nTabla 3 - Estadísticas por dado\n"
				+ tabla_por_dado
			)
			return

		frecuencias_globales: Counter[int] = resumen["frecuencias_globales"]  # type: ignore[assignment]
		frecuencias_por_dado: list[Counter[int]] = resumen["frecuencias_por_dado"]  # type: ignore[assignment]
		filtrados = sum(frecuencias_globales.get(cara, 0) for cara in caras_seleccionadas)

		if filtrados > 0:
			media = sum(cara * frecuencias_globales.get(cara, 0) for cara in caras_seleccionadas) / filtrados
			max_frec = max(frecuencias_globales.get(cara, 0) for cara in caras_seleccionadas)
			modas = sorted(cara for cara in caras_seleccionadas if frecuencias_globales.get(cara, 0) == max_frec)
			resumen_general_filas.extend(
				[
					["Media global (caras seleccionadas)", f"{media:.4f}"],
					["Moda global (caras seleccionadas)", f"{modas} (f={max_frec})"],
				]
			)
		else:
			resumen_general_filas.extend(
				[
					["Media global (caras seleccionadas)", "-"],
					["Moda global (caras seleccionadas)", "-"],
				]
			)

		filas_frecuencias: list[list[str]] = []
		for cara in caras_seleccionadas:
			fa = frecuencias_globales.get(cara, 0)
			fr = (fa / filtrados) if filtrados > 0 else 0.0
			filas_frecuencias.append([str(cara), str(fa), f"{fr:.4f}", f"{fr * 100:.2f}%"])

		filas_por_dado: list[list[str]] = []
		for indice_dado, conteos_dado in enumerate(frecuencias_por_dado, start=1):
			total_dado = sum(conteos_dado.get(cara, 0) for cara in caras_seleccionadas)
			if total_dado > 0:
				media_dado = sum(cara * conteos_dado.get(cara, 0) for cara in caras_seleccionadas) / total_dado
				max_frec_dado = max(conteos_dado.get(cara, 0) for cara in caras_seleccionadas)
				modas_dado = sorted(cara for cara in caras_seleccionadas if conteos_dado.get(cara, 0) == max_frec_dado)
				media_dado_txt = f"{media_dado:.4f}"
				moda_dado_txt = f"{modas_dado} (f={max_frec_dado})"
			else:
				media_dado_txt = "-"
				moda_dado_txt = "-"

			for cara in caras_seleccionadas:
				fa_dado = conteos_dado.get(cara, 0)
				fr_dado = (fa_dado / total_dado) if total_dado > 0 else 0.0
				filas_por_dado.append(
					[
						str(indice_dado),
						str(cara),
						str(fa_dado),
						f"{fr_dado:.4f}",
						f"{fr_dado * 100:.2f}%",
						media_dado_txt,
						moda_dado_txt,
					]
				)

		tabla_general = self._formatear_tabla(["Metrica", "Valor"], resumen_general_filas)
		tabla_frecuencias = self._formatear_tabla(["Cara", "fa", "fr", "%"], filas_frecuencias)
		tabla_por_dado = self._formatear_tabla(
			["Dado", "Cara", "fa", "fr", "%", "Media dado", "Moda dado"],
			filas_por_dado,
		)

		self._escribir_stats(
			"Tabla 1 - Resumen general\n"
			+ tabla_general
			+ "\n\nTabla 2 - Frecuencias globales\n"
			+ tabla_frecuencias
			+ "\n\nTabla 3 - Estadísticas por dado\n"
			+ tabla_por_dado
		)

	def mostrar_lista_espacio_muestral(self) -> None:
		datos = self._obtener_frecuencias_espacio_muestral()
		resumen = self._resumen_dimension_actual()
		total = int(resumen["total"]) if resumen is not None else 0

		ventana = tk.Toplevel(self.root)
		ventana.title("Lista del espacio muestral")
		ventana.geometry("900x560")

		resumen = (
			f"Dados: {self.cantidad_dados} | Cardinalidad n(Ω): {len(datos)} | "
			f"Experimentos de esta dimensión: {total}"
		)
		ttk.Label(ventana, text=resumen).pack(anchor="w", padx=10, pady=(10, 6))

		filtrar_con_frecuencia = tk.BooleanVar(value=False)

		filtro_frame = ttk.Frame(ventana, padding=(10, 0, 10, 6))
		filtro_frame.pack(fill="x")
		ttk.Checkbutton(
			filtro_frame,
			text="Mostrar solo eventos con frecuencia > 0",
			variable=filtrar_con_frecuencia,
		).pack(anchor="w")

		marco = ttk.Frame(ventana, padding=(8, 4, 8, 8))
		marco.pack(fill="both", expand=True)

		columnas = ("evento", "fa", "fr", "porcentaje")
		tabla = ttk.Treeview(marco, columns=columnas, show="headings")
		tabla.heading("evento", text="Evento")
		tabla.heading("fa", text="Frecuencia abs.")
		tabla.heading("fr", text="Frecuencia rel.")
		tabla.heading("porcentaje", text="Porcentaje")
		tabla.column("evento", width=260, anchor="w")
		tabla.column("fa", width=150, anchor="center")
		tabla.column("fr", width=150, anchor="center")
		tabla.column("porcentaje", width=150, anchor="center")

		sb_y = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
		sb_x = ttk.Scrollbar(marco, orient="horizontal", command=tabla.xview)
		tabla.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

		tabla.grid(row=0, column=0, sticky="nsew")
		sb_y.grid(row=0, column=1, sticky="ns")
		sb_x.grid(row=1, column=0, sticky="ew")
		marco.rowconfigure(0, weight=1)
		marco.columnconfigure(0, weight=1)

		def poblar_tabla() -> None:
			tabla.delete(*tabla.get_children())
			for evento, fa, fr in datos:
				if filtrar_con_frecuencia.get() and fa == 0:
					continue
				tabla.insert(
					"",
					"end",
					values=(
						self._formatear_evento(evento),
						fa,
						f"{fr:.6f}",
						f"{fr * 100:.4f}%",
					),
				)

		filtrar_con_frecuencia.trace_add("write", lambda *_: poblar_tabla())
		poblar_tabla()

	def mostrar_histograma_espacio_muestral(self) -> None:
		datos = self._obtener_frecuencias_espacio_muestral()
		resumen = self._resumen_dimension_actual()
		total = int(resumen["total"]) if resumen is not None else 0
		cantidad_eventos = len(datos)

		if total == 0:
			messagebox.showinfo("Histograma espacio", "No hay espacio muestral para mostrar.")
			return

		ordenado_por_frecuencia = self.ordenar_frecuencia_espacio.get()
		datos_graf = datos
		if ordenado_por_frecuencia:
			datos_graf = sorted(datos, key=lambda t: (t[2], t[1]), reverse=True)

		ventana = tk.Toplevel(self.root)
		ventana.title("Histograma del espacio muestral")
		ventana.geometry("1080x620")

		lienzo_frame = ttk.Frame(ventana)
		lienzo_frame.pack(fill="both", expand=True)

		canvas = tk.Canvas(lienzo_frame, bg="white", highlightthickness=0)
		self._habilitar_zoom_y_arrastre_canvas(canvas)
		tooltip_rec_id, tooltip_texto_id = self._crear_tooltip_canvas(canvas)
		sb_y = ttk.Scrollbar(lienzo_frame, orient="vertical", command=canvas.yview)
		sb_x = ttk.Scrollbar(lienzo_frame, orient="horizontal", command=canvas.xview)
		canvas.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

		canvas.grid(row=0, column=0, sticky="nsew")
		sb_y.grid(row=0, column=1, sticky="ns")
		sb_x.grid(row=1, column=0, sticky="ew")
		lienzo_frame.rowconfigure(0, weight=1)
		lienzo_frame.columnconfigure(0, weight=1)

		margen_izq = 80
		margen_sup = 70
		altura_barras = 360
		base_y = margen_sup + altura_barras
		if cantidad_eventos <= 250:
			paso_x = 34
			ancho_barra = 22
			paso_etiquetas = 1
			fuente_etiqueta = 8
		elif cantidad_eventos <= 1500:
			paso_x = 14
			ancho_barra = 8
			paso_etiquetas = 6
			fuente_etiqueta = 7
		else:
			paso_x = 8
			ancho_barra = 5
			paso_etiquetas = 20
			fuente_etiqueta = 6
		ancho_total = max(1000, margen_izq + len(datos_graf) * paso_x + 140)
		alto_total = 560

		titulo = "Histograma de frecuencia relativa por evento"
		if ordenado_por_frecuencia:
			titulo += " (ordenado por frecuencia desc)"

		canvas.create_text(
			ancho_total // 2,
			26,
			text=titulo,
			font=("TkDefaultFont", 14, "bold"),
		)
		canvas.create_line(margen_izq, margen_sup, margen_izq, base_y, width=2)
		canvas.create_line(margen_izq, base_y, ancho_total - 40, base_y, width=2)

		for pct in range(0, 101, 10):
			y = base_y - (pct / 100) * altura_barras
			canvas.create_line(margen_izq - 4, y, margen_izq, y, width=2)
			canvas.create_text(margen_izq - 28, y, text=f"{pct}%", fill="#444444")
			if pct > 0:
				canvas.create_line(margen_izq, y, ancho_total - 40, y, fill="#f0f0f0")

		for i, (evento, fa, fr) in enumerate(datos_graf):
			x0 = margen_izq + i * paso_x + 8
			x1 = x0 + ancho_barra
			y1 = base_y
			y0 = y1 - (fr * altura_barras)
			etiqueta = self._formatear_evento(evento)
			barra_id = canvas.create_rectangle(x0, y0, x1, y1, fill="#2a9d8f", outline="#1f6f63")
			if i % paso_etiquetas == 0:
				canvas.create_text(
					(x0 + x1) / 2,
					base_y + 14,
					text=etiqueta,
					angle=90,
					anchor="w",
					font=("TkDefaultFont", fuente_etiqueta),
				)
			texto_tooltip = (
				f"Evento: {etiqueta}\n"
				+ f"fa = {fa}\n"
				+ f"fr = {fr:.6f} ({fr * 100:.4f}%)"
			)
			canvas.tag_bind(
				barra_id,
				"<Enter>",
				lambda e, t=texto_tooltip: self._mostrar_tooltip_canvas(
					canvas,
					tooltip_rec_id,
					tooltip_texto_id,
					e,
					t,
				),
			)
			canvas.tag_bind(
				barra_id,
				"<Motion>",
				lambda e, t=texto_tooltip: self._mostrar_tooltip_canvas(
					canvas,
					tooltip_rec_id,
					tooltip_texto_id,
					e,
					t,
				),
			)
			canvas.tag_bind(
				barra_id,
				"<Leave>",
				lambda e: self._ocultar_tooltip_canvas(canvas, tooltip_rec_id, tooltip_texto_id),
			)

		texto_info = (
			f"Total de eventos en Ω: {cantidad_eventos}. "
			+ "Eje Y: frecuencia relativa (%) de cada evento completo. "
			+ f"Etiquetas en eje X cada {paso_etiquetas} evento(s). "
			+ (
				"Orden actual: por frecuencia descendente."
				if ordenado_por_frecuencia
				else "Orden actual: natural del espacio muestral."
			)
		)
		canvas.create_text(ancho_total // 2, alto_total - 24, text=texto_info, fill="#444444")
		canvas.configure(scrollregion=(0, 0, ancho_total, alto_total))

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
			"historial_muestra": [list(experimento) for experimento in self.historial],
			"historial_recortado": self.historial_recortado,
			"seleccionados": sorted(self.seleccionados),
			"cantidad_dados": self.cantidad_dados,
			"duracion_segundos": self.entrada_segundos.get().strip(),
			"tamanio_lote": self.entrada_lote.get().strip(),
			"modo_ejecucion": self._modo_solicitado(),
			"benchmark_perfiles": self._serializar_benchmark_perfiles(),
			"resumenes_por_dimension": self._serializar_resumenes(),
		}

		try:
			with ruta.open("w", encoding="utf-8") as f:
				json.dump(payload, f, ensure_ascii=False, indent=2)
		except OSError as exc:
			messagebox.showerror("Error", f"No se pudo guardar la sesión: {exc}")
			return

		self._actualizar_lista_sesiones()
		self.combo_sesiones.set(ruta.stem)
		self.logger.info("Sesion guardada | nombre=%s | ruta=%s", ruta.stem, ruta)
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

		historial = payload.get("historial_muestra", payload.get("historial", []))
		seleccionados = set(payload.get("seleccionados", [1, 2, 3, 4, 5, 6]))
		cantidad_dados = int(payload.get("cantidad_dados", 1))
		historial_recortado = bool(payload.get("historial_recortado", False))
		resumenes_serializados = payload.get("resumenes_por_dimension")
		benchmark_perfiles = payload.get("benchmark_perfiles")

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
		self.historial_recortado = historial_recortado
		self.seleccionados = {int(v) for v in seleccionados}
		self.cantidad_dados = cantidad_dados
		modo_sesion = str(payload.get("modo_ejecucion", "AUTO")).upper()
		if modo_sesion not in {"CPU", "GPU", "AUTO", "AMBAS"}:
			modo_sesion = "AUTO"
		self.modo_ejecucion_var.set(modo_sesion)
		self.entrada_dados.delete(0, "end")
		self.entrada_dados.insert(0, str(self.cantidad_dados))
		segundos_sesion = str(payload.get("duracion_segundos", self.entrada_segundos.get().strip() or "5"))
		self.entrada_segundos.delete(0, "end")
		self.entrada_segundos.insert(0, segundos_sesion)
		lote_sesion = str(payload.get("tamanio_lote", self.entrada_lote.get().strip() or "auto"))
		self.entrada_lote.delete(0, "end")
		self.entrada_lote.insert(0, lote_sesion)
		self._actualizar_espacio_muestral()

		if not self._cargar_resumenes_serializados(resumenes_serializados):
			self._resumen_por_dimension = {}
			for experimento in self.historial:
				self._registrar_resultado_en_resumen(experimento)

		if not self._cargar_benchmark_perfiles(benchmark_perfiles):
			self._benchmark_perfiles = {}

		for cara, var in self.check_vars.items():
			var.set(cara in self.seleccionados)

		ultimo = self.historial[-1] if self.historial else tuple(1 for _ in range(self.cantidad_dados))
		self._dibujar_dados(ultimo)
		self._actualizar_historial()
		self._actualizar_estadisticas()
		self._actualizar_lista_sesiones()
		self.combo_sesiones.set(ruta.stem)
		self.logger.info("Sesion cargada | nombre=%s | ruta=%s", ruta.stem, ruta)
		self.lbl_estado.config(text=f"Sesión cargada: {ruta.stem}")

	def _registrar_resultado(self, resultado: tuple[int, ...]) -> None:
		self._aplicar_resultados([resultado])
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
		self.btn_tiempo.configure(state="disabled")
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
		self.btn_tiempo.configure(state="normal")

	def lanzar_por_tiempo(self) -> None:
		if self.animando or self._postprocesando_simulacion or (self._sim_thread is not None and self._sim_thread.is_alive()):
			return

		cantidad_dados = self._obtener_cantidad_dados()
		if cantidad_dados is None:
			return
		self.cantidad_dados = cantidad_dados
		self._actualizar_espacio_muestral()

		trabajadores = self._obtener_trabajadores()
		if trabajadores is None:
			return

		tamanio_lote = self._obtener_tamanio_lote()
		if tamanio_lote is None:
			return

		texto = self.entrada_segundos.get().strip().replace(",", ".")
		try:
			segundos_objetivo = float(texto)
		except ValueError:
			self.lbl_estado.config(text="Ingresa un numero positivo de segundos.")
			return

		if segundos_objetivo <= 0:
			self.lbl_estado.config(text="Ingresa un numero positivo de segundos.")
			return

		modo_solicitado = self._modo_solicitado()
		modo_real, nota = self._resolver_modo_real(modo_solicitado, UMBRAL_GPU_AUTO)
		self.logger.info(
			"Lanzar por tiempo | segundos=%.3f | dados=%s | modo_solicitado=%s | modo_real=%s | trabajadores=%s | lote=%s",
			segundos_objetivo,
			self.cantidad_dados,
			modo_solicitado,
			modo_real,
			trabajadores,
			tamanio_lote if tamanio_lote > 0 else "auto",
		)

		self.btn_lanzar.configure(state="disabled")
		self.btn_n.configure(state="disabled")
		self.btn_tiempo.configure(state="disabled")

		total_ms = max(1, int(segundos_objetivo * 1000))
		self._mostrar_loader("Generando datos por tiempo", total_ms)

		while not self._progreso_queue.empty():
			try:
				self._progreso_queue.get_nowait()
			except queue.Empty:
				break

		self._ultimo_bucket_log = -1

		def _worker_tiempo():
			ultimo: tuple[int, ...] = tuple()
			muestra_para_historial: list[tuple[int, ...]] = []
			inicio = time.perf_counter()
			generados = 0
			etapa_loader = f"{modo_real} por tiempo"
			if tamanio_lote > 0:
				lote_base = tamanio_lote
			else:
				lote_base = TAMANIO_LOTE_GPU if modo_real in {"GPU", "AMBAS"} else max(UMBRAL_PARALELISMO, 60000)

			try:
				while True:
					transcurrido = time.perf_counter() - inicio
					if transcurrido >= segundos_objetivo:
						break

					restante = segundos_objetivo - transcurrido
					if tamanio_lote > 0:
						lote = lote_base
					else:
						lote = lote_base if restante > 0.25 else max(1000, lote_base // 4)

					if modo_real == "CPU":
						muestra, ultimo, fue_paralelo = self._ejecutar_cpu(lote, trabajadores)
						generados += lote
						if fue_paralelo:
							muestra_para_historial.extend(muestra)
							self.historial_recortado = True

					elif modo_real == "GPU":
						muestra, ultimo = self._simular_gpu_con_resumen(
							lote,
							self.cantidad_dados,
							tamanio_lote_gpu=lote_base,
						)
						generados += lote
						muestra_para_historial.extend(muestra)
						self.historial_recortado = True

					else:
						cantidad_gpu = lote // 2
						cantidad_cpu = lote - cantidad_gpu

						if cantidad_gpu > 0:
							muestra_gpu, ultimo_gpu = self._simular_gpu_con_resumen(
								cantidad_gpu,
								self.cantidad_dados,
								tamanio_lote_gpu=lote_base,
							)
							muestra_para_historial.extend(muestra_gpu)
							ultimo = ultimo_gpu if ultimo_gpu else ultimo

						muestra_cpu, ultimo_cpu, cpu_fue_paralelo = self._ejecutar_cpu(cantidad_cpu, trabajadores)
						if cpu_fue_paralelo:
							muestra_para_historial.extend(muestra_cpu)
						if ultimo_cpu:
							ultimo = ultimo_cpu

						generados += lote
						self.historial_recortado = True

					transcurrido_ms = min(total_ms, int((time.perf_counter() - inicio) * 1000))
					self._actualizar_loader(transcurrido_ms, total_ms, etapa_loader)

			except Exception as exc:
				self.logger.exception("Error en simulacion por tiempo | modo=%s", modo_real)
				self._pending_result = {"error": str(exc)}
				self._progreso_queue.put(None)
				return

			if muestra_para_historial:
				self._registrar_muestra_historial(muestra_para_historial)
			if ultimo:
				self._pending_ultimo = ultimo

			duracion_real = time.perf_counter() - inicio
			nota_str = f" {nota}" if nota else ""
			self._pending_result = {
				"texto_estado": (
					f"Se registraron {generados} experimentos en {duracion_real:.2f}s "
					+ f"(objetivo {segundos_objetivo:.2f}s, modo {modo_real})."
					+ nota_str
				),
				"nota": nota,
			}
			self._progreso_queue.put(None)

		self._pending_result = None
		self._pending_ultimo = tuple()
		self._sim_thread = threading.Thread(target=_worker_tiempo, daemon=True)
		self._sim_thread.start()
		self.root.after(40, self._poll_progreso)

	def lanzar_n_veces(self) -> None:
		if self.animando or self._postprocesando_simulacion or (self._sim_thread is not None and self._sim_thread.is_alive()):
			return

		cantidad_dados = self._obtener_cantidad_dados()
		if cantidad_dados is None:
			return
		self.cantidad_dados = cantidad_dados
		self._actualizar_espacio_muestral()

		trabajadores = self._obtener_trabajadores()
		if trabajadores is None:
			return

		texto = self.entrada_n.get().strip()
		if not texto.isdigit() or int(texto) <= 0:
			self.lbl_estado.config(text="Ingresa un entero positivo para N.")
			return

		cantidad = int(texto)
		modo_solicitado = self._modo_solicitado()
		modo_real, nota = self._resolver_modo_real(modo_solicitado, cantidad)
		self.logger.info(
			"Lanzar N | N=%s | dados=%s | modo_solicitado=%s | modo_real=%s | trabajadores=%s",
			cantidad,
			self.cantidad_dados,
			modo_solicitado,
			modo_real,
			trabajadores,
		)

		# Deshabilitar botones mientras corre la simulación
		self.btn_lanzar.configure(state="disabled")
		self.btn_n.configure(state="disabled")
		self.btn_tiempo.configure(state="disabled")
		self._mostrar_loader("Generando datos", cantidad)

		# Vaciar cola de progreso de ejecuciones previas
		while not self._progreso_queue.empty():
			try:
				self._progreso_queue.get_nowait()
			except queue.Empty:
				break

		self._ultimo_bucket_log = -1

		def _worker():
			ultimo: tuple[int, ...] = tuple()
			muestra_para_historial: list[tuple[int, ...]] = []
			texto_estado = ""
			try:
				if modo_real == "CPU":
					muestra, ultimo, fue_paralelo = self._ejecutar_cpu(
						cantidad,
						trabajadores,
						progreso_cb=lambda done: self._actualizar_loader(done, cantidad, "CPU"),
					)
					if fue_paralelo:
						muestra_para_historial = muestra
						self.historial_recortado = True
						texto_estado = f"Se registraron {cantidad} experimentos en CPU ({trabajadores} procesos)."
					else:
						muestra_para_historial = []
						texto_estado = f"Se registraron {cantidad} experimentos en CPU."

				elif modo_real == "GPU":
					muestra, ultimo = self._simular_gpu_con_resumen(
						cantidad,
						self.cantidad_dados,
						progreso_cb=lambda done: self._actualizar_loader(done, cantidad, "GPU"),
					)
					muestra_para_historial = muestra
					self.historial_recortado = True
					texto_estado = f"Se registraron {cantidad} experimentos en GPU."

				else:  # AMBAS
					cantidad_gpu = cantidad // 2
					cantidad_cpu = cantidad - cantidad_gpu
					muestra_gpu, ultimo_gpu = self._simular_gpu_con_resumen(
						cantidad_gpu,
						self.cantidad_dados,
						progreso_cb=lambda done: self._actualizar_loader(done, cantidad, "GPU (AMBAS)"),
					)
					muestra_cpu, ultimo_cpu, cpu_fue_paralelo = self._ejecutar_cpu(
						cantidad_cpu,
						trabajadores,
						progreso_cb=lambda done: self._actualizar_loader(cantidad_gpu + done, cantidad, "CPU (AMBAS)"),
					)
					muestra_para_historial = muestra_gpu + (muestra_cpu if cpu_fue_paralelo else [])
					ultimo = ultimo_cpu if ultimo_cpu else ultimo_gpu
					self.historial_recortado = True
					texto_estado = (
						f"Se registraron {cantidad} experimentos en AMBAS: "
						+ f"GPU={cantidad_gpu}, CPU={cantidad_cpu}."
					)
			except Exception as exc:
				self.logger.exception("Error en modo %s; fallback a CPU", modo_real)
				if modo_real in {"GPU", "AMBAS"}:
					try:
						muestra_cpu, ultimo_cpu, fue_paralelo_cpu = self._ejecutar_cpu(
							cantidad,
							trabajadores,
							progreso_cb=lambda done: self._actualizar_loader(done, cantidad, "CPU fallback"),
						)
						muestra_para_historial = muestra_cpu if fue_paralelo_cpu else []
						ultimo = ultimo_cpu
						texto_estado = f"Fallo en {modo_real}; se aplicó CPU como respaldo."
					except Exception as exc2:
						self.logger.exception("Fallback CPU también falló")
						self._pending_result = {"error": str(exc2)}
						self._progreso_queue.put(None)
						return
				else:
					self._pending_result = {"error": str(exc)}
					self._progreso_queue.put(None)
					return

			if muestra_para_historial:
				self._registrar_muestra_historial(muestra_para_historial)
			if ultimo:
				self._pending_ultimo = ultimo

			nota_str = f" {nota}" if nota else ""
			self._pending_result = {
				"texto_estado": texto_estado + nota_str,
				"nota": nota,
			}
			# Señal de fin: None en la cola
			self._progreso_queue.put(None)

		self._pending_result: dict | None = None
		self._pending_ultimo: tuple[int, ...] = tuple()
		self._sim_thread = threading.Thread(target=_worker, daemon=True)
		self._sim_thread.start()
		# Arrancar el poller en el hilo principal
		self.root.after(40, self._poll_progreso)

	def _finalizar_simulacion(self) -> None:
		"""Llamado desde el hilo principal tras confirmar que el worker terminó."""
		self.btn_lanzar.configure(state="normal")
		self.btn_n.configure(state="normal")
		self.btn_tiempo.configure(state="normal")
		self._sim_thread = None

		result = getattr(self, "_pending_result", None)
		if result is None:
			return
		self._pending_result = None

		if "error" in result:
			messagebox.showerror("Error", f"No se pudo completar la simulación: {result['error']}")
			self.lbl_estado.config(text="Error en la simulación. Revisa dice_app.log")
			return

		ultimo = getattr(self, "_pending_ultimo", tuple())
		self._pending_ultimo = tuple()

		if ultimo:
			self._dibujar_dados(ultimo)
		nota = result.get("nota")
		if nota:
			self.logger.info("Nota modo: %s", nota)
		self.lbl_estado.config(text=result.get("texto_estado", ""))
		self._postprocesando_simulacion = True
		self.root.after_idle(self._completar_postproceso_simulacion)

	def _completar_postproceso_simulacion(self) -> None:
		# Dividir el postproceso en dos ticks reduce bloqueos visibles del event loop.
		self.root.after(1, self._postproceso_paso_estadisticas)

	def _postproceso_paso_estadisticas(self) -> None:
		inicio = time.perf_counter()
		self._actualizar_estadisticas()
		self.logger.info("Postproceso UI | estadisticas=%.4fs", time.perf_counter() - inicio)
		self.root.after(1, self._postproceso_paso_historial)

	def _postproceso_paso_historial(self) -> None:
		inicio = time.perf_counter()
		try:
			self._actualizar_historial()
		finally:
			self.logger.info("Postproceso UI | historial=%.4fs", time.perf_counter() - inicio)
			self._postprocesando_simulacion = False


	def _obtener_filtrados(self) -> list[int]:
		return [v for v in self._obtener_resultados_individuales() if v in self.seleccionados]

	def _obtener_frecuencias_por_dado(self) -> list[Counter[int]]:
		resumen = self._resumen_dimension_actual()
		if resumen is None:
			return [Counter() for _ in range(self.cantidad_dados)]
		return resumen["frecuencias_por_dado"]  # type: ignore[return-value]

	def mostrar_histograma(self) -> None:
		resumen = self._resumen_dimension_actual()
		if resumen is None or int(resumen["total"]) == 0:
			messagebox.showinfo("Histograma", "No hay datos para graficar con la selección actual.")
			return

		frecuencias_por_dado = self._obtener_frecuencias_por_dado()
		paleta = PALETA_DADOS
		ventana = tk.Toplevel(self.root)
		ventana.title("Histograma de resultados")
		ventana.geometry("860x520")

		canvas = tk.Canvas(ventana, width=860, height=520, bg="white", highlightthickness=0)
		canvas.pack(fill="both", expand=True)
		self._habilitar_zoom_y_arrastre_canvas(canvas)
		tooltip_rec_id, tooltip_texto_id = self._crear_tooltip_canvas(canvas)

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
				total_dado = sum(frecuencias_por_dado[indice_dado].values())
				fr = (frec / total_dado) if total_dado else 0.0
				bar_h = (frec / max_frec) * (alto - 10)
				x0 = inicio_grupo + indice_dado * ancho_barra
				x1 = x0 + ancho_barra - 2
				y1 = margen_sup + alto
				y0 = y1 - bar_h

				color = paleta[indice_dado % len(paleta)] if cara in self.seleccionados else "#cccccc"
				barra_id = canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#444444")
				canvas.create_text((x0 + x1) / 2, y0 - 12, text=str(frec), font=("TkDefaultFont", 8))
				texto_tooltip = (
					f"Cara: {cara}\n"
					+ f"Dado: {indice_dado + 1}\n"
					+ f"fa = {frec}\n"
					+ f"fr = {fr:.6f} ({fr * 100:.4f}%)"
				)
				canvas.tag_bind(
					barra_id,
					"<Enter>",
					lambda e, t=texto_tooltip: self._mostrar_tooltip_canvas(
						canvas,
						tooltip_rec_id,
						tooltip_texto_id,
						e,
						t,
					),
				)
				canvas.tag_bind(
					barra_id,
					"<Motion>",
					lambda e, t=texto_tooltip: self._mostrar_tooltip_canvas(
						canvas,
						tooltip_rec_id,
						tooltip_texto_id,
						e,
						t,
					),
				)
				canvas.tag_bind(
					barra_id,
					"<Leave>",
					lambda e: self._ocultar_tooltip_canvas(canvas, tooltip_rec_id, tooltip_texto_id),
				)

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
		bbox = canvas.bbox("all")
		if bbox is not None:
			canvas.configure(scrollregion=(bbox[0] - 40, bbox[1] - 40, bbox[2] + 40, bbox[3] + 40))

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
