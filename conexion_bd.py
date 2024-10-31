# conexion_bd.py
import pyodbc
import hashlib

# Función para conectar a la base de datos
def conectar_bd():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-C1J5V6J;'
        'DATABASE=AlmacenDB3;'
        'Trusted_Connection=yes;'
    )
    return conn

# Función para crear un nuevo usuario
def crear_usuario(username, password):
    conn = conectar_bd()
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO Usuarios (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# Función para verificar credenciales
def verificar_credenciales(username, password):
    conn = conectar_bd()
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM Usuarios WHERE username = ? AND password = ?", (username, hashed_password))
    usuario = cursor.fetchone()
    conn.close()
    return usuario is not None

# Función para asignar un pallet a una ubicación
def asignar_ubicacion(pallet_id, ubicacion_nombre):
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # Verificar si el pallet existe y si ya tiene una ubicación asignada
    cursor.execute("""
        SELECT Pallets.ubicacion_actual, Ubicaciones.ubicacion 
        FROM Pallets 
        LEFT JOIN Ubicaciones ON Pallets.ubicacion_actual = Ubicaciones.ubicacion_id 
        WHERE pallet_id = ?
    """, (pallet_id,))
    
    pallet_row = cursor.fetchone()
    if not pallet_row:
        conn.close()
        return f"Error: El Pallet con ID {pallet_id} no existe."

    ubicacion_actual_id, ubicacion_actual_nombre = pallet_row
    if ubicacion_actual_id is not None:
        conn.close()
        return f"Error: El Pallet con ID {pallet_id} ya tiene una ubicación asignada: {ubicacion_actual_nombre}."
    
    # Obtener el ubicacion_id y disponibilidad de la ubicación usando su nombre
    cursor.execute("SELECT ubicacion_id, disponibilidad FROM Ubicaciones WHERE ubicacion = ?", (ubicacion_nombre,))
    ubicacion_row = cursor.fetchone()
    
    if not ubicacion_row:
        conn.close()
        return f"Error: La Ubicación {ubicacion_nombre} no existe."
    
    ubicacion_id, disponibilidad = ubicacion_row

    # Verificar si la ubicación ya está ocupada
    if disponibilidad == 'Ocupado':
        conn.close()
        return f"Error: La Ubicación {ubicacion_nombre} ya está ocupada."
    
    # Asignar la ubicación al pallet usando el ubicacion_id y actualizar la disponibilidad
    try:
        cursor.execute("UPDATE Pallets SET ubicacion_actual = ?, fecha_ingreso = CURRENT_TIMESTAMP WHERE pallet_id = ?", (ubicacion_id, pallet_id))
        cursor.execute("UPDATE Ubicaciones SET disponibilidad = 'Ocupado' WHERE ubicacion_id = ?", (ubicacion_id,))
        conn.commit()
        return f"Pallet {pallet_id} asignado a la ubicación {ubicacion_nombre}."
    except Exception as e:
        return f"Error al asignar ubicación: {e}"
    finally:
        conn.close()


# Función para liberar una ubicación
def liberar_ubicacion(pallet_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # Obtener el ubicacion_id actual del pallet
    cursor.execute("SELECT ubicacion_actual FROM Pallets WHERE pallet_id = ?", (pallet_id,))
    ubicacion_row = cursor.fetchone()
    
    if not ubicacion_row:
        conn.close()
        return f"Error: El Pallet con ID {pallet_id} no tiene una ubicación asignada o no existe."
    
    ubicacion_id = ubicacion_row[0]
    
    if ubicacion_id is None:
        conn.close()
        return f"Error: El Pallet con ID {pallet_id} ya está libre y no tiene ninguna ubicación asignada."
    
    # Liberar la ubicación y actualizar el pallet
    try:
        cursor.execute("UPDATE Ubicaciones SET disponibilidad = 'Libre' WHERE ubicacion_id = ?", (ubicacion_id,))
        cursor.execute("UPDATE Pallets SET ubicacion_actual = NULL WHERE pallet_id = ?", (pallet_id,))
        conn.commit()
        return f"Ubicación liberada del Pallet {pallet_id}."
    except Exception as e:
        return f"Error al liberar ubicación: {e}"
    finally:
        conn.close()

# Función para obtener todas las posiciones
def obtener_todas_las_posiciones():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo_almacen, ubicacion, piso, rack, posicion_pallet, letra, disponibilidad FROM Ubicaciones")
    posiciones = cursor.fetchall()
    conn.close()
    return posiciones


