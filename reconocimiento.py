import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import pyodbc
import io
import pyttsx3
# Configurar la conexión a SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=kevinpc\SQLEXPRESS;'
    'DATABASE=reconocimiento;'
    'UID=USUARIOFACE;'
    'PWD=123456;'
    'TrustServerCertificate=Yes;'
)
# Inicializar el motor de texto a voz
engine = pyttsx3.init()
volume = engine.getProperty('volume')
engine.setProperty('volume', 1.0)
# Función para convertir una imagen a un BLOB
def image_to_blob(image_path):
    with open(image_path, 'rb') as file:
        blob = file.read()
    return blob

# Función para guardar una imagen en la base de datos
def save_image_to_db(image_path, person_name):
    cursor = conn.cursor()
    blob = image_to_blob(image_path)
    cursor.execute("INSERT INTO Personas (nombre, imagen) VALUES (?, ?)", (person_name, blob))
    conn.commit()

# Función para recuperar una imagen de la base de datos
def get_image_from_db(person_name):
    cursor = conn.cursor()
    cursor.execute("SELECT imagen FROM Personas WHERE nombre = ?", (person_name,))
    blob = cursor.fetchone()[0]
    image = Image.open(io.BytesIO(blob))
    return np.array(image)

# Función para verificar si una imagen contiene una cara que coincide con una almacenada
def verify_face_libreria(stored_image, test_image,tolerance=0.5):
    stored_encodings = face_recognition.face_encodings(stored_image)
    test_encodings = face_recognition.face_encodings(test_image)
    if len(stored_encodings) == 0 or len(test_encodings) == 0:
        return False

    stored_encoding = stored_encodings[0]
    test_encoding = test_encodings[0]

    results = face_recognition.compare_faces([stored_encoding], test_encoding, tolerance=tolerance)
    return results[0]

# Función para obtener los nombres de las personas almacenadas en la base de datos
def get_person_names():
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM Personas")
    names = [row[0] for row in cursor.fetchall()]
    return names

class FaceRecognitionApp:
    def __init__(self, root):
        #creacion de cuadro de app y seleccion de nombres, botones de inicio
        self.root = root
        self.root.title("App Reconocimiento Facial")

        self.label = tk.Label(root, text="App Reconocimiento Facial", font=("Helvetica", 16))
        self.label.pack(pady=20)

        self.name_label = tk.Label(root, text="Selelccionar nombre:")
        self.name_label.pack(pady=5)

        self.name_combobox = ttk.Combobox(root, values=get_person_names())
        self.name_combobox.pack(pady=5)

        self.upload_button = tk.Button(root, text="Subir Imagen", command=self.upload_image)
        self.upload_button.pack(pady=10)

        self.verify_button = tk.Button(root, text="Verificar cara", command=self.verify_face)
        self.verify_button.pack(pady=10)

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        self.image_path = None
        # Seccion para subir imagenes
        self.label = tk.Label(root, text="Nuevo Registro", font=("Helvetica", 12))
        self.label.pack(pady=20)

        self.new_name_label = tk.Label(root, text="Ingresa el nombre:")
        self.new_name_label.pack(pady=5)

        self.new_name_entry = tk.Entry(root)
        self.new_name_entry.pack(pady=5)

        self.new_upload_button = tk.Button(root, text="Subir y guardar Imagen", command=self.save_image)
        self.new_upload_button.pack(pady=10)
        
    def upload_image(self):
        #buscador de imagen 
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if self.image_path:
            img = Image.open(self.image_path)
            img.thumbnail((300, 300))
            img = ImageTk.PhotoImage(img)
            self.image_label.config(image=img)
            self.image_label.image = img

    def verify_face(self):
        if not self.image_path:
            messagebox.showwarning("Precaucion", "Por favor subir la imagen primero")
            return

        person_name = self.name_combobox.get()
        if not person_name:
            messagebox.showwarning("Precaucion", "Seleccione el nombre de una persona primero")
            return
 
        stored_image = get_image_from_db(person_name)
        test_image = face_recognition.load_image_file(self.image_path)
        
        is_match = verify_face_libreria(stored_image, test_image)
        #Mensaje de resultado y utilizacion de libreria de voz
        if is_match:
            messagebox.showinfo("Resultado", "Se ha encontrado Match")
            engine.say(f"{person_name}.")   
            engine.runAndWait()
        else:
            messagebox.showinfo("Resultado", "No se ha encontrado Match.")
    def save_image(self):
        new_person_name = self.new_name_entry.get()
        if not new_person_name:
            messagebox.showwarning("Precaucion", "Por favor ingrese el nombre de la nueva persona")
            return

        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if not self.image_path:
            messagebox.showwarning("Precaucion", "Por favor sube una imagen")
            return

        save_image_to_db(self.image_path, new_person_name)
        messagebox.showinfo("Satisfactorio", "Imagen subida exitosamente")
        self.name_combobox['values'] = get_person_names()
    
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

