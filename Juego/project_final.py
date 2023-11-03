import textwrap
from tkinter import *
import requests
import time
import os

historial_juegos_file = "historial_juegos.txt"

if not os.path.exists(historial_juegos_file):
    with open(historial_juegos_file, "w") as file:
        pass

class Tablero:
    def __init__(self):
        self.num_intentos = 0
        self.matriz = []
        self.palabra_correcta = ""

    def crear_tablero(self):
        for i in range(6):
            self.matriz.append(["_" for _ in range(5)])

    def actualizar_tablero(self, palabra):
        if self.num_intentos < 6:
            if palabra == self.palabra_correcta:
                for i, letra in enumerate(palabra):
                    self.matriz[self.num_intentos][i] = letra
                self.num_intentos = 6
                return
            else:
                for i, letra in enumerate(palabra):
                    if letra == self.palabra_correcta[i]:
                        self.matriz[self.num_intentos][i] = letra
                    elif letra in self.palabra_correcta:
                        self.matriz[self.num_intentos][i] = letra.lower()
                    else:
                        self.matriz[self.num_intentos][i] = letra
                self.num_intentos += 1

class Palabra:
    def __init__(self):
        self.palabra_correcta = ""
        self.tablero = Tablero()

    def escoger_palabra(self):
        random_word_api_url = "https://random-word-api.herokuapp.com/word"
        random_word_api_response = requests.get(
            random_word_api_url, params={"length": 5, "lang": "en"})
        self.palabra_correcta = random_word_api_response.json()[0]

    def comparar_palabra(self, palabra):
        return palabra == self.palabra_correcta

    def colorear_letras(self):
        # Implementa la lógica para colorear las casillas del tablero
        pass

    def validar_palabra(self, palabra):
        return len(palabra) == 5 and palabra.isalpha() and palabra.islower()

    def definicion_palabra(self):
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
        response = requests.get(url.format(self.palabra_correcta))
        if response.status_code == 200:
            definition = response.json()[0]["meanings"][0]["definitions"][0]["definition"]
        else:
            definition = "No se encontró una definición para esta palabra."
        return definition

class Estadisticas:
    def __init__(self):
        self.resultado_ventana = None

    def guardar_resultados(self, palabra_correcta, palabra_ingresada, resultado):
        with open("historial_juegos.txt", "a") as file:
            file.write(
                f"Palabra correcta: {palabra_correcta}, Palabra ingresada: {palabra_ingresada}, Resultado: {resultado}\n")

    def mostrar_estadisticas(self):
        if self.resultado_ventana:
            self.resultado_ventana.destroy()

        self.resultado_ventana = Toplevel(self.ventana)
        self.resultado_ventana.title("Resultados")
        # Implementa la lógica para mostrar estadísticas en la ventana
        pass

    def mostrar_graficos(self):
        # Implementa la lógica para mostrar gráficos de estadísticas
        pass

class Tiempo:
    def __init__(self):
        self.tiempo_inicio = None
        self.cronometro_corriendo = False

    def inicie_cronometro(self):
        self.tiempo_inicio = time.time()
        self.actualizar_cronometro()
        self.boton_reiniciar.config(state="disabled")
        self.boton_salir.config(state="disabled")

    def detener_cronometro(self):
        self.tiempo_inicio = None
        self.boton_reiniciar.config(state="normal")
        self.boton_salir.config(state="normal")

    def actualizar_cronometro(self):
        if self.tiempo_inicio:
            tiempo_transcurrido = time.time() - self.tiempo_inicio
            minutos = int(tiempo_transcurrido // 60)
            segundos = int(tiempo_transcurrido % 60)
            tiempo_formateado = f"Tiempo: {minutos:02d}:{segundos:02d}"
            self.etiqueta_cronometro.config(text=tiempo_formateado)
            self.ventana.after(1000, self.actualizar_cronometro)

class Juego:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Wordle")
        self.ventana.configure(bg="white")

        for i in range(11):
            self.ventana.rowconfigure(i, weight=1)
        for j in range(5):
            self.ventana.columnconfigure(j, weight=1)

        self.palabra = Palabra()
        self.tablero = Tablero()
        self.estadisticas = Estadisticas()
        self.tiempo = Tiempo()

        self.etiqueta = Label(ventana, text="WORDLE", font=("Courier", 16))
        self.etiqueta.grid(row=0, column=0, columnspan=5, sticky="nsew")

        self.etiqueta_palabra = Label(ventana, text="Ingresa una palabra de 5 letras en minúsculas:", font=("Courier", 12))
        self.etiqueta_palabra.grid(row=1, column=0, columnspan=5, sticky="nsew")

        self.entrada_palabra = Entry(ventana, font=("Courier", 12))
        self.entrada_palabra.grid(row=2, column=0, columnspan=5, sticky="nsew")

        self.etiqueta_error = Label(ventana, text="", fg="red", font=("Courier", 12))
        self.etiqueta_error.grid(row=4, column=0, columnspan=5, sticky="nsew")

        self.etiqueta_tablero = Label(ventana, text="", font=("Courier", 16))
        self.etiqueta_tablero.grid(row=11, column=0, columnspan=5, sticky="nsew")

        self.tablero_labels = []
        for i in range(6):
            fila_labels = []
            for j in range(5):
                label = Label(ventana, text="", width=2, height=1, font=("Courier", 16),
                              relief="solid", borderwidth=1)
                label.grid(row=i + 5, column=j, sticky="nsew")
                fila_labels.append(label)
            self.tablero_labels.append(fila_labels)

        self.tiempo.inicie_cronometro()

        self.etiqueta_cronometro = Label(ventana, text="Tiempo: 00:00", font=("Courier", 12))
        self.etiqueta_cronometro.grid(row=11, column=5, sticky="nsew")

        self.resultado_ventana = None

        self.boton_reiniciar = Button(ventana, text="Reiniciar Juego", command=self.reiniciar_juego, font=("Courier", 12))
        self.boton_reiniciar.grid(row=5, column=5, columnspan=5, sticky="nsew")

        self.boton_salir = Button(ventana, text="Salir", command=ventana.quit, font=("Courier", 12))
        self.boton_salir.grid(row=6, column=5, columnspan=5, sticky="nsew")

        self.boton_adivinar = Button(ventana, text="Adivinar", command=self.adivinar_palabra, font=("Courier", 12))
        self.boton_adivinar.grid(row=3, column=0, columnspan=5, sticky="nsew")

    def reiniciar_juego(self):
        self.palabra.escoger_palabra()
        self.tablero.crear_tablero()
        self.entrada_palabra.delete(0, END)
        self.etiqueta_error.config(text="")
        self.etiqueta_tablero.config(text="")
        self.tiempo.inicie_cronometro()
        self.boton_adivinar.config(state="normal")

    def adivinar_palabra(self):
        palabra = self.entrada_palabra.get()

        if self.palabra.validar_palabra(palabra):
            self.etiqueta_error.config(text="")
            if self.palabra.comparar_palabra(palabra):
                self.tablero.actualizar_tablero(palabra)
                self.actualizar_tablero()
                self.etiqueta_tablero.config(text="¡Has adivinado la palabra!")
                self.tiempo.detener_cronometro()
                self.estadisticas.guardar_resultados(self.palabra.palabra_correcta, palabra, "Victoria")
                self.mostrar_resultados()
                self.boton_adivinar.config(state="disabled")
            else:
                self.tablero.actualizar_tablero(palabra)
                self.actualizar_tablero()
                if self.tablero.num_intentos == 6:
                    self.etiqueta_tablero.config(
                        f"¡Agotaste tus intentos! La palabra correcta era: {self.palabra.palabra_correcta}")
                    self.tiempo.detener_cronometro()
                    self.estadisticas.guardar_resultados(self.palabra.palabra_correcta, palabra, "Derrota")
                    self.mostrar_resultados()
                    self.boton_adivinar.config(state="disabled")
        else:
            self.etiqueta_error.config(text="Por favor, ingresa una palabra válida de 5 letras en minúsculas.")

    def mostrar_resultados(self):
        self.estadisticas.mostrar_estadisticas()

    def actualizar_tablero(self):
        for i in range(6):
            for j in range(5):
                letra = self.tablero.matriz[i][j]
                label = self.tablero_labels[i][j]
                if letra == "_":
                    label.config(text=letra, bg="white")
                elif letra == self.palabra.palabra_correcta[j]:
                    label.config(text=letra, bg="green")
                elif letra in self.palabra.palabra_correcta:
                    label.config(text=letra, bg="yellow")
                else:
                    label.config(text=letra, bg="white")

ventana = Tk()

if __name__ == "__main__":
    ventana.configure(bg="white")
    juego = Juego(ventana)
    ventana.mainloop()
