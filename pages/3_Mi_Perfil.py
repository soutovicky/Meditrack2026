import streamlit as st
import random
import sys
import os
from datetime import datetime, timedelta, timezone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import db

favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')

now = datetime.now(timezone.utc)

st.title("Establezca su Ocupación")

if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None


def check_id_in_empleado(id_to_check):
    try:
        response = db().table("empleado") \
            .select("id_Empleado, nombre, apellido") \
            .eq("id_Empleado", id_to_check) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al consultar empleado: {e}")
        return None


def check_id_in_doctor(id_to_check):
    try:
        response = db().table("doctor") \
            .select("id_Doctor, nombre, apellido") \
            .eq("id_Doctor", id_to_check) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al consultar doctor: {e}")
        return None


def get_paciente_alergias(id_paciente):
    try:
        response = db().table("pacientes") \
            .select("alergias") \
            .eq("id_Pacientes", id_paciente) \
            .execute()
        return response.data[0]["alergias"] if response.data else None
    except Exception as e:
        st.error(f"Error al obtener las alergias del paciente: {e}")
        return None


def add_prescripcion(id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_paciente, id_doctor):
    try:
        alergias = get_paciente_alergias(id_paciente)
        if alergias and nombre_medicamento.lower() in alergias.lower():
            st.warning(f"El paciente es alérgico a {nombre_medicamento}. No se puede recetar este medicamento.")
            return None

        db().table("prescripcion").insert({
            "id_Prescripcion": id_prescripcion,
            "nombre_medicamento": nombre_medicamento,
            "horario_administracion": str(horario_administracion),
            "dosis_gr": dosis_gr,
            "id_Pacientes": id_paciente,
            "id_Doctor": id_doctor
        }).execute()
        st.success("Prescripción añadida correctamente")
    except Exception as e:
        st.error(f"Error al añadir prescripción: {e}")


def delete_prescripcion(id_prescripcion):
    try:
        db().table("prescripcion") \
            .delete() \
            .eq("id_Prescripcion", id_prescripcion) \
            .execute()
        st.success("Prescripción eliminada correctamente")
    except Exception as e:
        st.error(f"Error al eliminar la prescripción: {e}")


def get_prescripciones_de_paciente(id_paciente):
    try:
        response = db().table("prescripcion") \
            .select("id_Prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_Doctor") \
            .eq("id_Pacientes", id_paciente) \
            .execute()
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error al obtener las prescripciones del paciente: {e}")
        return None


def get_paciente_info(id_paciente):
    try:
        response = db().table("pacientes") \
            .select("id_Pacientes, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social") \
            .eq("id_Pacientes", id_paciente) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al obtener información del paciente: {e}")
        return None


def update_administracion(id_empleado, selected_prescripciones):
    try:
        for prescripcion_id, estado in selected_prescripciones.items():
            # Verificar si ya existe
            check = db().table("administra") \
                .select("id_Empleado") \
                .eq("id_Empleado", id_empleado) \
                .eq("id_Prescripcion", prescripcion_id) \
                .execute()

            if check.data:
                db().table("administra") \
                    .update({"administrado": estado}) \
                    .eq("id_Empleado", id_empleado) \
                    .eq("id_Prescripcion", prescripcion_id) \
                    .execute()
            else:
                db().table("administra").insert({
                    "id_Empleado": id_empleado,
                    "id_Prescripcion": prescripcion_id,
                    "administrado": estado
                }).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar el estado de administración: {e}")
        return False


def get_prescripciones_paciente(id_paciente):
    try:
        # Traemos prescripciones y el estado de administración del empleado actual
        prescripciones = db().table("prescripcion") \
            .select("id_Prescripcion, nombre_medicamento, horario_administracion, dosis_gr") \
            .eq("id_Pacientes", id_paciente) \
            .execute()

        if not prescripciones.data:
            return None

        result = []
        for p in prescripciones.data:
            administra = db().table("administra") \
                .select("administrado") \
                .eq("id_Prescripcion", p["id_Prescripcion"]) \
                .eq("id_Empleado", st.session_state['user_id']) \
                .execute()
            administrado = administra.data[0]["administrado"] if administra.data else False
            result.append((
                p["id_Prescripcion"],
                p["nombre_medicamento"],
                p["horario_administracion"],
                p["dosis_gr"],
                administrado
            ))
        return result
    except Exception as e:
        st.error(f"Error al obtener las prescripciones del paciente: {e}")
        return None


def admin_medicamentos_page():
    st.header("Administración de Medicamentos")

    if 'paciente_encontrado' not in st.session_state:
        st.session_state['paciente_encontrado'] = False
    if 'selected_prescripciones' not in st.session_state:
        st.session_state['selected_prescripciones'] = {}

    id_paciente = st.text_input("ID del Paciente:", key="admin_paciente_id")
    prescripciones = []

    if st.button("Buscar Prescripciones", key="btn_buscar_prescripciones"):
        if id_paciente:
            prescripciones = get_prescripciones_paciente(id_paciente)
            if prescripciones:
                st.session_state['paciente_encontrado'] = True
                st.session_state['selected_prescripciones'] = {p[0]: p[4] for p in prescripciones}
                st.success("Prescripciones encontradas:")
            else:
                st.warning("No se encontraron prescripciones para el paciente.")
                st.session_state['paciente_encontrado'] = False
        else:
            st.error("Por favor, ingrese el ID del paciente.")

    if st.session_state['paciente_encontrado']:
        prescripciones = get_prescripciones_paciente(id_paciente)
        if prescripciones:
            for prescripcion in prescripciones:
                prescripcion_info = f"{prescripcion[1]} - Horario: {prescripcion[2]} - Dosis: {prescripcion[3]} mg"
                st.session_state['selected_prescripciones'][prescripcion[0]] = st.checkbox(
                    prescripcion_info,
                    value=st.session_state['selected_prescripciones'][prescripcion[0]],
                    key=f"chk_prescripcion_{prescripcion[0]}"
                )

    if st.button("Guardar Cambios", key="btn_guardar_cambios"):
        if update_administracion(st.session_state['user_id'], st.session_state['selected_prescripciones']):
            st.success("Prescripción administrada correctamente")
        else:
            st.error("Error al guardar los cambios.")
        st.session_state['paciente_encontrado'] = False
        st.session_state['selected_prescripciones'] = {}


def insertar_paciente(id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social):
    try:
        db().table("pacientes").insert({
            "id_Pacientes": id_paciente,
            "nombre": nombre,
            "apellido": apellido,
            "habitacion": habitacion,
            "alergias": alergias,
            "contacto_telefonico": contacto_telefonico,
            "diagnostico": diagnostico,
            "obra_social": obra_social
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al insertar el paciente: {e}")
        return False


def alta_paciente_page():
    st.header("Alta de Paciente")
    id_paciente = random.randint(100000000, 999999999)
    st.write(f"ID del Paciente: {id_paciente}")

    with st.form("alta_paciente_form"):
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        habitacion = st.text_input("Habitación")
        alergias = st.text_area("Alergias")
        contacto_telefonico = st.text_input("Contacto Telefónico")
        diagnostico = st.text_area("Diagnóstico")
        obra_social = st.text_input("Obra Social")
        submitted = st.form_submit_button("Dar de Alta")

        if submitted:
            if not nombre or not apellido:
                st.error("Por favor, complete los campos obligatorios (Nombre y Apellido).")
            else:
                if insertar_paciente(id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social):
                    st.success("Paciente dado de alta exitosamente.")
                else:
                    st.error("Error al dar de alta al paciente.")


def update_paciente_info(id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social):
    try:
        db().table("pacientes").update({
            "id_Pacientes": id_paciente,
            "nombre": nombre,
            "apellido": apellido,
            "habitacion": habitacion,
            "alergias": alergias,
            "contacto_telefonico": contacto_telefonico,
            "diagnostico": diagnostico,
            "obra_social": obra_social
        }).eq("id_Pacientes", id_paciente).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la información del paciente: {e}")
        return False


def perfil_pacientes_page():
    st.header("Perfil de Pacientes")

    if 'paciente_info' not in st.session_state:
        st.session_state.paciente_info = None
    if 'id_paciente' not in st.session_state:
        st.session_state.id_paciente = ""

    id_paciente = st.text_input("ID del Paciente:", key="perfil_paciente_id", value=st.session_state.id_paciente)

    if st.button("Buscar Paciente", key="btn_buscar_paciente"):
        if id_paciente:
            paciente_info = get_paciente_info(id_paciente)
            if paciente_info:
                st.success("Información del paciente encontrada:")
                st.session_state.paciente_info = paciente_info
                st.session_state.id_paciente = id_paciente
            else:
                st.warning("No se encontró información para el paciente.")
        else:
            st.error("Por favor, ingrese el ID del paciente.")

    if st.session_state.paciente_info:
        p = st.session_state.paciente_info
        st.table({
            "ID Paciente": [p["id_Pacientes"]],
            "Nombre": [p["nombre"]],
            "Apellido": [p["apellido"]],
            "Habitación": [p["habitacion"]],
            "Alergias": [p["alergias"]],
            "Contacto Telefónico": [p["contacto_telefonico"]],
            "Diagnóstico": [p["diagnostico"]],
            "Obra Social": [p["obra_social"]]
        })

        if st.button("Editar Información"):
            st.session_state.editing = True

    if 'editing' in st.session_state and st.session_state.editing:
        p = st.session_state.paciente_info
        with st.form(key="form_paciente"):
            nombre = st.text_input("Nombre", value=p["nombre"])
            apellido = st.text_input("Apellido", value=p["apellido"])
            habitacion = st.text_input("Habitación", value=p["habitacion"])
            alergias = st.text_area("Alergias", value=p["alergias"])
            contacto_telefonico = st.text_input("Contacto Telefónico", value=p["contacto_telefonico"])
            diagnostico = st.text_area("Diagnóstico", value=p["diagnostico"])
            obra_social = st.text_input("Obra Social", value=p["obra_social"])
            submit_button = st.form_submit_button(label="Actualizar Información")

            if submit_button:
                success = update_paciente_info(st.session_state.id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social)
                if success:
                    st.success("Información del paciente actualizada correctamente.")
                    st.session_state.paciente_info = get_paciente_info(st.session_state.id_paciente)
                    st.session_state.editing = False
                else:
                    st.error("Error al actualizar la información del paciente.")


def get_horario_area(id_empleado):
    try:
        response = db().table("empleado") \
            .select("horario_entrada, horario_salida, sector_geriatrico") \
            .eq("id_Empleado", id_empleado) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al obtener el horario y área del empleado: {e}")
        return None


def generar_id_aleatorio():
    return random.randint(100000000, 999999999)


def prescripcion_page():
    st.header("Prescripción")

    id_prescripcion = st.text_input("ID de la Prescripción:", value=str(generar_id_aleatorio()), key="add_prescripcion_id")
    nombre_medicamento = st.selectbox("Nombre del Medicamento", (
        "Paracetamol", "Ibuprofeno", "Amoxicilina", "Omeprazol", "Loratadina",
        "Diazepam", "Cetirizina", "Atorvastatina", "Metformina", "Simvastatina",
        "Ramipril", "Losartan", "Insulina", "Warfarina", "Levotiroxina",
        "Aspirina", "Enalapril", "Metoprolol", "Lisinopril", "Digoxina",
        "Amlodipino", "Pantoprazol", "Prednisona", "Metronidazol", "Macril",
        "Penicilina", "Betametasona", "Bactrim"
    ), index=None, placeholder="Seleccione una opción...")
    horario_administracion = st.time_input("Horario de Administración:", key="add_prescripcion_horario")
    dosis_gr = st.number_input("Dosis (gramos):", min_value=0.0, step=0.1, key="add_prescripcion_dosis")
    id_paciente = st.text_input("ID del Paciente:", key="add_prescripcion_paciente_id")

    if st.button("Añadir Prescripción", key="btn_add_prescripcion"):
        if id_prescripcion and nombre_medicamento and horario_administracion and dosis_gr and id_paciente:
            add_prescripcion(id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_paciente, st.session_state['user_id'])
        else:
            st.error("Por favor, complete todos los campos.")


def get_recordatorios():
    try:
        now_time = datetime.now()
        start_time = (now_time - timedelta(minutes=15)).strftime("%H:%M:%S")
        end_time = (now_time + timedelta(minutes=15)).strftime("%H:%M:%S")

        # Traemos prescripciones con horario en rango
        prescripciones = db().table("prescripcion") \
            .select("id_Prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_Pacientes") \
            .gte("horario_administracion", start_time) \
            .lte("horario_administracion", end_time) \
            .execute()

        if not prescripciones.data:
            return []

        result = []
        for p in prescripciones.data:
            paciente = db().table("pacientes") \
                .select("nombre, apellido") \
                .eq("id_Pacientes", p["id_Pacientes"]) \
                .execute()
            nombre_paciente = paciente.data[0]["nombre"] if paciente.data else "Desconocido"
            apellido_paciente = paciente.data[0]["apellido"] if paciente.data else ""
            result.append((
                p["id_Prescripcion"],
                p["nombre_medicamento"],
                p["horario_administracion"],
                p["dosis_gr"],
                p["id_Pacientes"],
                nombre_paciente,
                apellido_paciente
            ))
        return result
    except Exception as e:
        st.error(f"Error al obtener los recordatorios: {e}")
        return None


def recordatorios_medicamentos_page():
    st.header("Recordatorios de Medicamentos")
    recordatorios = get_recordatorios()

    if recordatorios:
        for rec in recordatorios:
            id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_Pacientes, nombre_paciente, apellido_paciente = rec
            st.warning(f"¡Recordatorio! Administrar {nombre_medicamento} ({dosis_gr}g) a ({id_Pacientes}) {nombre_paciente} {apellido_paciente} a las {horario_administracion}.")
    else:
        st.info("No hay recordatorios en este momento.")


def doctor_page():
    st.title("Página de Doctor")
    tab1, tab2, tab3 = st.tabs(["Ver Paciente", "Añadir Prescripción", "Prescripciones Asignadas"])

    with tab1:
        perfil_pacientes_page()

    with tab2:
        prescripcion_page()

    with tab3:
        st.header("Prescripciones Asignadas")
        id_prescripcion_eliminar = st.text_input("ID de la Prescripción a Eliminar:", key="delete_prescripcion_id")
        if st.button("Eliminar Prescripción", key="btn_delete_prescripcion"):
            if id_prescripcion_eliminar:
                delete_prescripcion(id_prescripcion_eliminar)
            else:
                st.error("Por favor, ingrese el ID de la prescripción a eliminar.")

        id_paciente = st.text_input("ID del Paciente:", key="view_prescripciones_paciente_id")
        if st.button("Ver Prescripciones", key="btn_view_prescripciones"):
            if id_paciente:
                prescripciones = get_prescripciones_de_paciente(id_paciente)
                if prescripciones:
                    for p in prescripciones:
                        st.write(f"ID: {p['id_Prescripcion']}")
                        st.write(f"Medicamento: {p['nombre_medicamento']}")
                        st.write(f"Horario: {p['horario_administracion']}")
                        st.write(f"Dosis: {p['dosis_gr']} g")
                        st.write(f"ID Doctor: {p['id_Doctor']}")
                        st.write("---")
                else:
                    st.error("No se encontraron prescripciones para ese paciente.")
            else:
                st.error("Por favor, ingrese el ID del paciente.")


def empleado_page():
    st.title("Página de Empleado")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Administración de Medicamentos",
        "Horarios de Trabajo",
        "Información del Paciente",
        "Ingresar Nuevo Paciente",
        "Recordatorio de Medicamentos"
    ])

    with tab1:
        admin_medicamentos_page()

    with tab2:
        st.header("Horarios de Trabajo")
        horario_area = get_horario_area(st.session_state['user_id'])
        if horario_area:
            st.write(f"Horario de Entrada: {horario_area['horario_entrada']}")
            st.write(f"Horario de Salida: {horario_area['horario_salida']}")
            st.write(f"Área: {horario_area['sector_geriatrico']}")
        else:
            st.info("No se encontraron datos de horario y área.")

    with tab3:
        perfil_pacientes_page()

    with tab4:
        alta_paciente_page()

    with tab5:
        recordatorios_medicamentos_page()


# Main
if st.session_state['estado'] == 'Autorizado':
    if 'user_id' not in st.session_state or not st.session_state['user_id']:
        id_input = st.text_input("Ingrese su ID:", key="login_id")
        if st.button("Ingresar", key="login_button"):
            if not id_input:
                st.error("Por favor, ingrese un ID válido.")
            else:
                empleado_details = check_id_in_empleado(id_input)
                doctor_details = check_id_in_doctor(id_input)
                if empleado_details:
                    st.session_state['estado'] = 'Autorizado'
                    st.session_state['user_role'] = 'Empleado'
                    st.session_state['user_id'] = id_input
                    st.success(f"Bienvenido {st.session_state['user_role']} ID: {st.session_state['user_id']}")
                    st.rerun()  # ✅ reemplaza experimental_rerun
                elif doctor_details:
                    st.session_state['estado'] = 'Autorizado'
                    st.session_state['user_role'] = 'Doctor'
                    st.session_state['user_id'] = id_input
                    st.success(f"Bienvenido {st.session_state['user_role']} ID: {st.session_state['user_id']}")
                    st.rerun()
                else:
                    st.error("El ID no existe en la base de datos.")
    else:
        st.success(f"Bienvenido {st.session_state['user_role']} ID: {st.session_state['user_id']}")
        if st.session_state['user_role'] == 'Empleado':
            empleado_page()
        elif st.session_state['user_role'] == 'Doctor':
            doctor_page()
else:
    st.error("Debes iniciar sesión primero.")