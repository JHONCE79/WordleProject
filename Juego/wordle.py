from tkinter import *
import requests
import time

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

        while self.num_intentos < 6:
            if palabra == self.palabra_correcta:
                for i, letra in enumerate(palabra):
                    self.matriz[self.num_intentos][i] = letra
                break
            else:
                for i, letra in enumerate(palabra):
                    if letra == self.palabra_correcta[i]:
                        self.matriz[self.num_intentos][i] = letra
                    elif letra in self.palabra_correcta:
                        self.matriz[self.num_intentos][i] = letra.lower()
                    else:
                        self.matriz[self.num_intentos][i] = letra
                self.num_intentos += 1
class WordleGame:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Wordle")
        self.ventana.configure(bg="white")

        for i in range(11):
            self.ventana.rowconfigure(i, weight=1)
        for j in range(5):
            self.ventana.columnconfigure(j, weight=1)

        self.palabra_correcta = self.obtener_palabra_aleatoria()
        self.tablero = Tablero(self.palabra_correcta)

        self.etiqueta = Label(ventana, text="WORDLE", font=("Courier", 16))
        self.etiqueta.grid(row=0, column=0, columnspan=5, sticky="nsew")

        self.etiqueta_palabra = Label(ventana, text="Ingresa una palabra de 5 letras en minúsculas:", font=("Courier", 12))
        self.etiqueta_palabra.grid(row=1, column=0, columnspan=5, sticky="nsew")

        self.entrada_palabra = Entry(ventana, font=("Courier", 12))
        self.entrada_palabra.grid(row=2, column=0, columnspan=5, sticky="nsew")

        self.boton_adivinar = Button(ventana, text="Adivinar", command=self.adivinar_palabra, font=("Courier", 12))
        self.boton_adivinar.grid(row=3, column=0, columnspan=5, sticky="nsew")

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
                #self.guardar_resultado(self.palabra_correcta, palabra, "Victoria")
                self.mostrar_resultados()
            elif self.tablero.num_intentos == 6:
                self.etiqueta_tablero.config(
                    text=f"¡Agotaste tus intentos! La palabra correcta era: {self.palabra_correcta}")
                self.detener_cronometro()
                #self.guardar_resultado(self.palabra_correcta, palabra, "Derrota")
                self.mostrar_resultados()

                # Nueva línea para mostrar estadísticas al finalizar la partida
                estadisticas.actualizar("Victoria" if palabra == self.palabra_correcta else "Derrota")
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

        # Muestra estadísticas en la nueva ventana
        Label(self.resultado_ventana, text=f"Partidas Jugadas: {partidas_jugadas}", font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"% Victorias: {victorias / partidas_jugadas * 100:.2f}%",
              font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"Racha Actual: {racha_actual}", font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"Mejor Racha: {mejor_racha}", font=("Courier", 12)).pack()

    def iniciar_cronometro(self):
        self.tiempo_inicio = time.time()
        self.actualizar_cronometro()

    def detener_cronometro(self):
        self.tiempo_inicio = None

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

    def obtener_palabra_aleatoria(self):
        while True:
            api_url = 'https://api.api-ninjas.com/v1/randomword'
            response = requests.get(api_url, headers={'X-Api-Key': 'JcKNlhomgsmGlSuULikw6w==RSl3LFwKuqUPSky5'})

            if response.status_code == requests.codes.ok:
                palabra = response.json().get("word")
                if palabra and len(palabra) == 5 and palabra.isalpha() and palabra.islower():
                    return palabra
            else:
                print("Error al obtener una palabra de la API.")

    def guardar_resultado(self, palabra_correcta, palabra_ingresada, resultado):
        with open("historial_juegos.txt", "a") as file:
            file.write(f"Palabra correcta: {palabra_correcta}, Palabra ingresada: {palabra_ingresada}, Resultado: {resultado}\n")

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

        # Muestra estadísticas en la nueva ventana
        Label(self.resultado_ventana, text=f"Partidas Jugadas: {partidas_jugadas}", font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"% Victorias: {victorias / partidas_jugadas * 100:.2f}%",
              font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"Racha Actual: {racha_actual}", font=("Courier", 12)).pack()
        Label(self.resultado_ventana, text=f"Mejor Racha: {mejor_racha}", font=("Courier", 12)).pack()

        # Mostrar ventana de estadísticas al finalizar una ronda
        self.resultado_ventana.transient(self.ventana)
        self.resultado_ventana.grab_set()
        self.ventana.wait_window(self.resultado_ventana)

ventana = Tk()


class Estadisticas:
    def __init__(self, ventana):
        self.ventana = ventana
        self.partidas_jugadas = 0
        self.victorias = 0
        self.racha_actual = 0
        self.mejor_racha = 0

        self.frame = Toplevel(ventana)  # Usa Toplevel para la ventana de estadísticas
        self.frame.title("Estadísticas")
        self.frame.geometry("400x200")

        self.label_partidas = Label(self.frame, text="Partidas jugadas: 0", font=("Courier", 12))
        self.label_partidas.pack()

        self.label_victorias = Label(self.frame, text="Victorias: 0 (0%)", font=("Courier", 12))
        self.label_victorias.pack()

        self.label_racha_actual = Label(self.frame, text="Racha actual: 0", font=("Courier", 12))
        self.label_racha_actual.pack()

        self.label_mejor_racha = Label(self.frame, text="Mejor racha: 0", font=("Courier", 12))
        self.label_mejor_racha.pack()

    def actualizar(self, resultado):
        self.partidas_jugadas += 1
        self.label_partidas["text"] = f"Partidas jugadas: {self.partidas_jugadas}"

        if resultado == "Victoria":
            self.victorias += 1
            self.racha_actual += 1
            porcentaje = int(self.victorias / self.partidas_jugadas * 100)
            self.label_victorias["text"] = f"Victorias: {self.victorias} ({porcentaje}%)"

            if self.racha_actual > self.mejor_racha:
                self.mejor_racha = self.racha_actual
            self.label_racha_actual["text"] = f"Racha actual: {self.racha_actual}"
            self.label_mejor_racha["text"] = f"Mejor racha: {self.mejor_racha}"


if __name__ == "__main__":
    ventana.configure(bg="white")
    juego = WordleGame(ventana)
    estadisticas = Estadisticas(ventana)
    ventana.mainloop()