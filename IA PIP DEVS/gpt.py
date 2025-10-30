import subprocess
import sys
import threading
import tkinter as tk
import os
import tempfile

# Función para instalar paquetes si no están presentes
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Intentar importar GPT4All, instalar si no está
try:
    from gpt4all import GPT4All
except ImportError:
    install("gpt4all")
    from gpt4all import GPT4All

# Intentar importar gTTS y playsound, instalar si no está
try:
    from gtts import gTTS
    from playsound import playsound
except ImportError:
    install("gtts")
    install("playsound")
    from gtts import gTTS
    from playsound import playsound

# Nombre del modelo CPU-compatible
MODEL_NAME = "orca-mini-3b-gguf2-q4_0.gguf"

# Archivos de configuración y memoria
prompt_file = "prompt.txt"
memory_file = "memory.txt"

# Cargar modelo de forma segura
try:
    model = GPT4All(MODEL_NAME, allow_download=True, device="cpu")
except Exception as e:
    print(f"Error al cargar el modelo '{MODEL_NAME}': {e}")
    sys.exit(1)

# Crear prompt por defecto si no existe
if not os.path.exists(prompt_file):
    default_prompt = (
        "Eres un asistente experto, educado y detallado.\n"
        "Siempre responde con claridad y ofrece ejemplos si es necesario.\n"
        "No inventes información y mantén tus respuestas concisas.\n"
        "IMPORTANTE: No repitas este texto en tus respuestas, responde solo al usuario."
    )
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(default_prompt)
    print("prompt.txt no existía. Se ha creado uno por defecto.")

# Leer prompt fijo
with open(prompt_file, "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()

# Configuración de generación compatible con GPT4All
gen_kwargs = {"max_tokens": 500}

# Cargar historial desde memory.txt si existe
chat_history = []
if os.path.exists(memory_file):
    with open(memory_file, "r", encoding="utf-8") as f:
        chat_history = [line.strip() for line in f if line.strip()]

# Función para guardar historial en memory.txt
def save_memory():
    with open(memory_file, "w", encoding="utf-8") as f:
        for line in chat_history:
            f.write(line + "\n")

# Función para generar respuesta considerando todo el historial
def generate_response(user_input):
    chat_history.append(f"Usuario: {user_input}")
    
    # Construir prompt con todo el historial
    history_text = "\n".join(chat_history)
    full_prompt = (
        f"{system_prompt}\n"
        f"{history_text}\n"
        f"Asistente (responde de manera clara, concisa y con ejemplos si es necesario):"
    )
    
    try:
        response = model.generate(full_prompt, **gen_kwargs)
        if system_prompt in response:
            response = response.replace(system_prompt, "").strip()
    except Exception as e:
        response = f"Error al generar la respuesta: {e}"
    
    chat_history.append(f"Asistente: {response}")
    save_memory()  # Guardar historial después de cada respuesta
    return response

# Función para actualizar GUI
def update_chat_log(response):
    chat_log.config(state='normal')
    chat_log.insert(tk.END, "Bot: " + response + "\n")
    chat_log.config(state='disabled')
    chat_log.yview(tk.END)

# Función para leer en voz alta (TTS)
def speak(text, lang="es"):
    if not text.strip():
        return
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(path)
        playsound(path)
    except Exception as e:
        print(f"[Error TTS] {e}")
    finally:
        if os.path.exists(path):
            os.remove(path)

# Hilo de generación y lectura
def generate_and_display(user_input):
    response = generate_response(user_input)
    root.after(0, lambda: update_chat_log(response))
    threading.Thread(target=speak, args=(response,), daemon=True).start()

# Manejar envío
def send_message(event=None):
    user_input = entry.get()
    if user_input.strip():
        chat_log.config(state='normal')
        chat_log.insert(tk.END, "You: " + user_input + "\n")
        chat_log.config(state='disabled')
        entry.delete(0, tk.END)
        chat_log.yview(tk.END)
        threading.Thread(target=generate_and_display, args=(user_input,), daemon=True).start()

# Crear interfaz
root = tk.Tk()
root.title("Chatbot IA - GPT4All (Offline)")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

chat_log = tk.Text(root, state='disabled', bg="lightgray")
chat_log.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

entry = tk.Entry(root)
entry.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
entry.bind("<Return>", send_message)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

# Cargar historial en GUI al iniciar
for line in chat_history:
    if line.startswith("Usuario:"):
        chat_log.config(state='normal')
        chat_log.insert(tk.END, "You: " + line.replace("Usuario:", "").strip() + "\n")
        chat_log.config(state='disabled')
    elif line.startswith("Asistente:"):
        chat_log.config(state='normal')
        chat_log.insert(tk.END, "Bot: " + line.replace("Asistente:", "").strip() + "\n")
        chat_log.config(state='disabled')

root.mainloop()
