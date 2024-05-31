import pyodbc
import face_recognition
from PIL import Image
import io
import numpy as np
# Configurar la conexión a SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=kevinpc\SQLEXPRESS;'
    'DATABASE=reconocimiento;'
    'UID=USUARIOFACE;'
    'PWD=123456;'
    'TrustServerCertificate=Yes;'
)

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
def verify_face(stored_image, test_image,tolerance=0.4):
    stored_encodings = face_recognition.face_encodings(stored_image)[0]
    test_encodings = face_recognition.face_encodings(test_image)[0]
    if len(stored_encodings) == 0 or len(test_encodings) == 0:
        return False

    stored_encoding = stored_encodings[0]
    test_encoding = test_encodings[0]

    results = face_recognition.compare_faces([stored_encoding], test_encoding, tolerance=tolerance)
    return results[0]

# Guardar una imagen en la base de datos
#save_image_to_db('C:\\Users\\kevin\\OneDrive\\Escritorio\\Foto.jpg','Kevin')

# Recuperar la imagen de la base de datos
stored_image = get_image_from_db('Kevin')

# Leer la imagen de prueba
test_image = face_recognition.load_image_file('C:\\Users\\kevin\\OneDrive\\Escritorio\\gabo.jpg')

# Verificar si las caras coinciden
def verify_face(stored_image, test_image):
    stored_encoding = face_recognition.face_encodings(stored_image)[0]
    test_encoding = face_recognition.face_encodings(test_image)[0]
    results = face_recognition.compare_faces([stored_encoding], test_encoding)
    return results[0]

# Verificar si las caras coinciden
is_match = verify_face(stored_image, test_image)
print('Match found:', is_match)
