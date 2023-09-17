import serial
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging
from serial.tools import list_ports
import threading
import datetime  # Importa el módulo datetime para generar nombres de archivo únicos

# Genera un nombre de archivo de registro único basado en la fecha y hora
log_filename = datetime.datetime.now().strftime("uart_log_%Y%m%d_%H%M%S.txt")

# Configura la configuración de registro
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Variables globales
uart = None
connected = False
connecting = False  # Variable para rastrear el proceso de conexión
baud_rate = 115200  # Velocidad de baudios ajustada a 115200

# Función para conectar al puerto seleccionado
def connect():
    global uart, connected, connecting
    if connecting:
        return
    port = port_combo.get()
    try:
        uart = serial.Serial(port, baud_rate)
        connected = True
        connecting = False
        messagebox.showinfo("Conexión", f"Conectado al puerto {port} con {baud_rate} baudios")
        logging.info(f"Conectado al puerto {port} con {baud_rate} baudios")
        disconnect_button["state"] = "normal"
        connect_button["state"] = "disabled"
        communication_thread = threading.Thread(target=read_data)
        communication_thread.start()
    except serial.SerialException as e:
        connecting = False
        messagebox.showerror("Error de conexión", str(e))
        logging.error(f"Error de conexión: {str(e)}")

# Función para leer datos en tiempo real y registrarlos
def read_data():
    global uart, connected
    while connected:
        try:
            data = uart.readline()
            if data:
                data_str = data.decode('utf-8', errors='replace')
                print("Datos recibidos:", data_str)
                logging.info(data_str)
                update_monitor(data_str)  # Actualiza el monitor con los datos recibidos
        except serial.SerialException as e:
            messagebox.showerror("Error de lectura", str(e))
            logging.error(f"Error de lectura: {str(e)}")
            disconnect()
            break

# Función para enviar un comando al lector TTL
def send_command():
    command = command_entry.get()
    if uart and connected:
        uart.write(command.encode('utf-8') + b'\n')
        logging.info(f"Enviado: {command}")
    else:
        messagebox.showerror("Error", "No se puede enviar el comando: no hay conexión activa.")

# Función para desconectar la conexión
def disconnect():
    global uart, connected
    if uart:
        uart.close()
        connected = False
        messagebox.showinfo("Desconexión", "Conexión cerrada.")
        logging.info("Conexión cerrada.")
        connect_button["state"] = "normal"
        disconnect_button["state"] = "disabled"
        update_monitor("Desconectado del puerto COM")  # Actualiza el monitor

# Función para verificar si el puerto COM está disponible
def check_port():
    available_ports = [port.device for port in list_ports.comports()]
    for port in available_ports:
        if port.upper() not in ['COM1', 'COM2', 'COM3', 'COM4']:  # Evitar COM1, COM2, COM3 y COM4
            try:
                test_uart = serial.Serial(port, baud_rate, timeout=1)
                test_uart.close()
                return port
            except serial.SerialException:
                continue
    return None

# Función para actualizar el monitor con datos recibidos
def update_monitor(data):
    monitor_text.config(state=tk.NORMAL)  # Habilita la edición del texto
    monitor_text.insert(tk.END, data + "\n")  # Agrega los datos al monitor
    monitor_text.see(tk.END)  # Desplaza el monitor al final
    monitor_text.config(state=tk.DISABLED)  # Deshabilita la edición del texto

# Función para abrir el archivo de registro (log)
def open_log():
    try:
        with open(log_filename, 'r') as log_file:
            log_contents = log_file.read()
            log_window = tk.Toplevel(root)
            log_window.title("Registro de Log")
            log_text = tk.Text(log_window, wrap=tk.WORD)
            log_text.pack(fill=tk.BOTH, expand=True)
            log_text.insert(tk.END, log_contents)
            log_text.config(state=tk.DISABLED)
    except FileNotFoundError:
        messagebox.showinfo("Registro de Log", "El registro de log aún no existe.")

# Función para cerrar el programa
def close_program():
    if connected:
        disconnect()  # Desconecta si aún está conectado
    root.destroy()  # Cierra la ventana principal y finaliza el programa

# Crea una ventana tkinter
root = tk.Tk()
root.title("PS4 UART VIEWER")  # Cambia el título de la ventana

# Frame para botones de control (Conectar, Desconectar, Log, Cerrar)
button_frame = ttk.Frame(root)
button_frame.pack(fill=tk.X, padx=10, pady=10)

# Botón de conexión
connect_button = ttk.Button(button_frame, text="Conectar", command=connect)
connect_button.pack(side=tk.LEFT)

# Botón de desconexión
disconnect_button = ttk.Button(button_frame, text="Desconectar", command=disconnect)
disconnect_button.pack(side=tk.LEFT)
disconnect_button["state"] = "disabled"

# Botón de registro (log)
log_button = ttk.Button(button_frame, text="Log", command=open_log)
log_button.pack(side=tk.LEFT)

# Botón de Cerrar
close_button = ttk.Button(button_frame, text="Cerrar", command=close_program)
close_button.pack(side=tk.LEFT)

# Combobox para mostrar el puerto COM detectado automáticamente
port_combo = ttk.Combobox(root, values=["Detectando..."], state="readonly")
port_combo.pack()

# Monitor de comunicación en tiempo real con barra de desplazamiento
monitor_frame = ttk.LabelFrame(root, text="Monitor de Comunicación")
monitor_frame.pack(fill=tk.BOTH, expand=True)

monitor_text = tk.Text(monitor_frame, wrap=tk.WORD, bg="black", fg="white")  # Cambia los colores
scrollbar = ttk.Scrollbar(monitor_frame, orient=tk.VERTICAL, command=monitor_text.yview)
monitor_text.config(yscrollcommand=scrollbar.set)

monitor_text.pack(fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Entrada de texto para enviar comandos
command_frame = ttk.LabelFrame(root, text="Enviar Comando al Lector TTL")
command_frame.pack(fill=tk.BOTH, expand=True)

command_entry = ttk.Entry(command_frame)
command_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

send_button = ttk.Button(command_frame, text="Enviar Comando", command=send_command)
send_button.pack(side=tk.RIGHT)

# Verifica y actualiza automáticamente el puerto COM
def update_port():
    global connecting
    if not connecting:
        port = check_port()
        if port:
            port_combo["values"] = [port]
            port_combo.set(port)
            connect_button["state"] = "normal"
            if connected:
                disconnect_button["state"] = "normal"
        else:
            port_combo["values"] = []
            port_combo.set("No se ha detectado ningún puerto COM disponible")
            connect_button["state"] = "disabled"
        connecting = False  # Reiniciamos la variable de conexión
    root.after(1000, update_port)

update_port()

# Configura la ventana para que sea redimensionable
root.resizable(True, True)

if __name__ == "__main__":
    root.mainloop()