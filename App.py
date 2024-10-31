# app.py
import streamlit as st
import pandas as pd
import time
from conexion_bd import (
    crear_usuario, verificar_credenciales, asignar_ubicacion, liberar_ubicacion, obtener_todas_las_posiciones
)

# Variables de sesión para gestionar el login y la vista seleccionada
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["vista"] = "login"

# Función de login
def vista_login():
    st.title("Sistema de Gestión de Almacén - Login")

    st.subheader("Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if verificar_credenciales(username, password):
            st.session_state["logged_in"] = True
            st.session_state["vista"] = "gestion"
            st.success("Inicio de sesión exitoso")
        else:
            st.error("Credenciales incorrectas")

    st.subheader("Crear Usuario")
    new_username = st.text_input("Nuevo Usuario")
    new_password = st.text_input("Nueva Contraseña", type="password")
    if st.button("Crear Usuario"):
        if crear_usuario(new_username, new_password):
            st.success("Usuario creado exitosamente")
        else:
            st.error("Error al crear usuario (puede que el usuario ya exista)")

# Función para la vista de gestión de pallets
def vista_gestion():
    st.title("Gestión de Ubicaciones de Pallets")
    st.header("Asignar Pallet a Ubicación")
    pallet_id = st.text_input("ID del Pallet para asignar")
    ubicacion = st.text_input("Ubicación para asignar")
    if st.button("Asignar Ubicación"):
        mensaje = asignar_ubicacion(pallet_id, ubicacion)
        if "Error" in mensaje:
            st.error(mensaje)
        else:
            st.success(mensaje)

    st.header("Liberar Pallet de Ubicación")
    pallet_id_liberar = st.text_input("ID del Pallet para liberar")
    if st.button("Liberar Ubicación"):
        liberar_ubicacion(pallet_id_liberar)
        st.success(f"Pallet {pallet_id_liberar} liberado de su ubicación")

# Función para la vista de visualización de almacén con actualización automática solo de las tablas en paralelo
def vista_visualizacion():
    st.title("Visualización del Almacén")

    # Crear las columnas una vez
    col1, col2 = st.columns(2)
    contenedor_rack1 = col1.empty()
    contenedor_rack2 = col2.empty()

    # Bucle para actualizar solo el contenido de las tablas
    while True:
        posiciones = obtener_todas_las_posiciones()

        # Crear el DataFrame usando from_records
        try:
            df_posiciones = pd.DataFrame.from_records(posiciones, columns=["Tipo Almacén", "Ubicación", "Piso", "Rack", "Ubi", "Letra", "Disponibilidad"])
        except ValueError as e:
            st.error(f"Error al crear DataFrame: {e}")
            return

        # Filtrar por cada rack
        df_rack1 = df_posiciones[df_posiciones["Rack"] == "RACK 1"]
        df_rack2 = df_posiciones[df_posiciones["Rack"] == "RACK 2"]

        # Crear matrices para cada rack
        matriz_rack1 = pd.crosstab(index=[df_rack1["Piso"], df_rack1["Ubi"]],
                                   columns=df_rack1["Letra"],
                                   values=df_rack1["Ubicación"],
                                   aggfunc="first").fillna("")

        matriz_rack2 = pd.crosstab(index=[df_rack2["Piso"], df_rack2["Ubi"]],
                                   columns=df_rack2["Letra"],
                                   values=df_rack2["Ubicación"],
                                   aggfunc="first").fillna("")

        matriz_rack1 = matriz_rack1.sort_index(ascending=False)
        matriz_rack2 = matriz_rack2.sort_index(ascending=False)

        # Definir el estilo de las celdas basado en la disponibilidad
        def estilo_celda(val):
            if pd.isna(val) or val == "":
                return ""
            disponibilidad = df_posiciones.loc[df_posiciones["Ubicación"] == val, "Disponibilidad"].values[0]
            color = "green" if disponibilidad == "Libre" else "red"
            return f"background-color: {color}; color: white; text-align: center; font-weight: bold"

        # Actualizar el contenido de cada contenedor con los datos actuales
        contenedor_rack1.subheader("Rack 1")
        contenedor_rack1.dataframe(matriz_rack1.style.applymap(estilo_celda), height=600)

        contenedor_rack2.subheader("Rack 2")
        contenedor_rack2.dataframe(matriz_rack2.style.applymap(estilo_celda), height=600)

        # Esperar 5 segundos antes de la siguiente actualización
        time.sleep(5)

# Selección de la vista según el estado de sesión
if st.session_state["logged_in"]:
    st.sidebar.button("Cerrar sesión", on_click=lambda: st.session_state.update({"logged_in": False, "vista": "login"}))
    if st.session_state["vista"] == "gestion":
        vista_gestion()
    elif st.session_state["vista"] == "visualizacion":
        vista_visualizacion()
    st.sidebar.button("Ver Gestión de Pallets", on_click=lambda: st.session_state.update({"vista": "gestion"}))
    st.sidebar.button("Ver Visualización de Almacén", on_click=lambda: st.session_state.update({"vista": "visualizacion"}))
else:
    vista_login()
