import textwrap
from tkinter import *
import requests
import time
import os

historial_juegos_file = "historial_juegos.txt"

if not os.path.exists(historial_juegos_file):
    with open(historial_juegos_file, "w") as file:
        pass

# Define la función para obtener una palabra aleatoria
def get_random_word(length):
    random_word_api_url = "https://random-word-api.herokuapp.com/word"

    random_word_api_response = requests.get(
        random_word_api_url, params={"length": length, "lang": "en"})

    random_word = random_word_api_response.json()[0]

    return random_word

def get_word_definition(word):
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
    response = requests.get(url.format(word))
    return response

def get_random_word_with_meaning(length):
    status_code = 404

    while status_code != 200:
        word = get_random_word(length)
        meaning_response = get_word_definition(word)

        status_code = meaning_response.status_code

    definition = meaning_response.json()[0]["meanings"][0]["definitions"][0]["definition"]

    random_word = {
        'word': word,
        'definition': definition
    }

    return random_word

class Tablero:
    def __init__(self, palabra_correcta):
        self.num_intentos = 0
        self.matriz = []
        self.palabra_correcta = palabra_correcta
        self.llenar_matriz()

    def llenar_matriz(self):
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

class palabra:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Wordle")
        self.ventana.configure(bg="white")

        for i in range(11):
            self.ventana.rowconfigure(i, weight=1)
        for j in range(5):
            self.ventana.columnconfigure(j, weight=1)

        self.palabra_correcta = get_random_word(5)
        self.tablero = Tablero(self.palabra_correcta)

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

        self.tiempo_inicio = None
        self.cronometro_corriendo = False

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
        self.palabra_correcta = get_random_word(5)
        self.tablero = Tablero(self.palabra_correcta)
        self.entrada_palabra.delete(0, END)
        self.etiqueta_error.config(text="")
        self.etiqueta_tablero.config(text="")
        self.actualizar_tablero()
        self.tiempo_inicio = None
        self.cronometro_corriendo = False
        self.etiqueta_cronometro.config(text="Tiempo: 00:00")
        self.resultado_ventana.destroy() if self.resultado_ventana else None
        self.boton_adivinar.config(state="normal")

    def adivinar_palabra(self):
        palabra = self.entrada_palabra.get()
        if not self.cronometro_corriendo:
            self.iniciar_cronometro()
            self.cronometro_corriendo = True

        if len(palabra) == 5 and palabra.isalpha() and palabra.islower():
            self.etiqueta_error.config(text="")
            self.tablero.actualizar_tablero(palabra)
            self.actualizar_tablero()
            if "".join(self.tablero.matriz[self.tablero.num_intentos - 1]) == self.palabra_correcta:
                self.etiqueta_tablero.config(text="¡Has adivinado la palabra!")
                self.detener_cronometro()
                self.mostrar_resultados()
                self.boton_adivinar.config(state="disabled")
            elif self.tablero.num_intentos == 6:
                self.etiqueta_tablero.config(
                    text=f"¡Agotaste tus intentos! La palabra correcta era: {self.palabra_correcta}")
                self.detener_cronometro()
                self.mostrar_resultados()
                self.boton_adivinar.config(state="disabled")
        else:
            self.etiqueta_error.config(text="Por favor, ingresa una palabra válida de 5 letras en minúsculas.")

    def mostrar_resultados(self):
        if self.resultado_ventana:
            self.resultado_ventana.destroy()

        self.resultado_ventana = Toplevel(self.ventana)
        self.resultado_ventana.title("Resultados")

        # Calcula estadísticas
        partidas_jugadas = 0
        victorias = 0
        racha_actual = 0
        mejor_racha = 0

        with open("historial_juegos.txt", "r") as file:
            lines = file.readlines()
            partidas_jugadas = len(lines)
            for line in lines:
                if "Victoria" in line:
                    victorias += 1
                    racha_actual += 1
                    mejor_racha = max(mejor_racha, racha_actual)
                else:
                    racha_actual = 0

        # Obtener el significado de la palabra correcta
        palabra_correcta = self.palabra_correcta
        meaning_response = get_word_definition(palabra_correcta)

        if meaning_response.status_code == 200:
            definition = meaning_response.json()[0]["meanings"][0]["definitions"][0]["definition"]
        else:
            definition = "No se encontró una definición para esta palabra."

        # Muestra estadísticas en la nueva ventana
        Label(self.resultado_ventana, text=f"Partidas Jugadas: {partidas_jugadas}", font=("Courier", 12)).pack()

        if partidas_jugadas > 0:
            porcentaje_victorias = (victorias / partidas_jugadas) * 100
        else:
            porcentaje_victorias = 0

        Label(self.resultado_ventana, text=f"% Victorias: {porcentaje_victorias:.2f}%", font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"Racha Actual: {racha_actual}", font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"Mejor Racha: {mejor_racha}", font=("Courier", 12)).pack()

        # Muestra el significado de la palabra correcta o un mensaje de error
        if definition == "No se encontró una definición para esta palabra.":
            Label(self.resultado_ventana, text=f"Palabra correcta: {palabra_correcta}", font=("Courier", 12)).pack()
            Label(self.resultado_ventana, text="Significado no encontrado.", font=("Courier", 12)).pack()
        else:
            significado_lineas = "\n".join(
                textwrap.wrap(definition, width=40))  # Ajusta el texto a 40 caracteres por línea
            Label(self.resultado_ventana, text=f"Palabra correcta: {palabra_correcta}", font=("Courier", 12)).pack()
            Label(self.resultado_ventana, text=f"Significado:", font=("Courier", 12)).pack()
            Label(self.resultado_ventana, text=significado_lineas, font=("Courier", 12)).pack()


    def iniciar_cronometro(self):
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

    def actualizar_tablero(self):
        for i in range(6):
            for j in range(5):
                letra = self.tablero.matriz[i][j]
                label = self.tablero_labels[i][j]
                if letra == "_":
                    label.config(text=letra, bg="white")
                elif letra == self.palabra_correcta[j]:
                    label.config(text=letra, bg="green")
                elif letra in self.palabra_correcta:
                    label.config(text=letra, bg="yellow")
                else:
                    label.config(text=letra, bg="white")

    def guardar_resultado(self, palabra_correcta, palabra_ingresada, resultado):
        historial_juegos_file = "historial_juegos.txt"

        if os.path.exists(historial_juegos_file):
            with open(historial_juegos_file, "a") as file:
                file.write(
                    f"Palabra correcta: {palabra_correcta}, Palabra ingresada: {palabra_ingresada}, Resultado: {resultado}\n")

ventana = Tk()

if __name__ == "__main__":
    ventana.configure(bg="white")
    juego = palabra(ventana)
    ventana.mainloop()