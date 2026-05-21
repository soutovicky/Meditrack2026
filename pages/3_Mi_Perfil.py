import streamlit as st
import random
import sys
import os
from datetime import datetime, timedelta, timezone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import db

favicon = "https://github.com/soutovicky/Meditrack2/blob/main/Imagenes/Icon.png?raw=true"
st.set_page_config(page_title='Meditrack', page_icon=favicon, layout='wide')

st.title("Mi Perfil")

if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None


# ── AUTENTICACIÓN ──────────────────────────────────────────────────────────────

def check_id_in_empleado(id_to_check):
    try:
        response = db().table("empleado") \
            .select("id_empleado, nombre, apellido") \
            .eq("id_empleado", id_to_check) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al consultar empleado: {e}")
        return None


def check_id_in_doctor(id_to_check):
    try:
        response = db().table("doctor") \
            .select("id_doctor, nombre, apellido") \
            .eq("id_doctor", id_to_check) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al consultar doctor: {e}")
        return None


# ── PACIENTES ──────────────────────────────────────────────────────────────────

def get_paciente_info(id_paciente):
    try:
        response = db().table("pacientes") \
            .select("id_pacientes, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social") \
            .eq("id_pacientes", id_paciente) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al obtener información del paciente: {e}")
        return None


def get_paciente_alergias(id_paciente):
    try:
        response = db().table("pacientes") \
            .select("alergias") \
            .eq("id_pacientes", id_paciente) \
            .execute()
        return response.data[0]["alergias"] if response.data else None
    except Exception as e:
        st.error(f"Error al obtener las alergias del paciente: {e}")
        return None


def insertar_paciente(id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social):
    try:
        db().table("pacientes").insert({
            "id_pacientes":        id_paciente,
            "nombre":              nombre,
            "apellido":            apellido,
            "habitacion":          habitacion,
            "alergias":            alergias,
            "contacto_telefonico": contacto_telefonico,
            "diagnostico":         diagnostico,
            "obra_social":         obra_social
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al insertar el paciente: {e}")
        return False


def update_paciente_info(id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social):
    try:
        db().table("pacientes").update({
            "nombre":              nombre,
            "apellido":            apellido,
            "habitacion":          habitacion,
            "alergias":            alergias,
            "contacto_telefonico": contacto_telefonico,
            "diagnostico":         diagnostico,
            "obra_social":         obra_social
        }).eq("id_pacientes", id_paciente).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la información del paciente: {e}")
        return False


# ── PRESCRIPCIONES ─────────────────────────────────────────────────────────────

def add_prescripcion(id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_paciente, id_doctor):
    try:
        alergias = get_paciente_alergias(id_paciente)
        if alergias and nombre_medicamento.lower() in alergias.lower():
            st.warning(f"⚠️ El paciente es alérgico a {nombre_medicamento}. No se puede recetar este medicamento.")
            return None

        db().table("prescripcion").insert({
            "id_prescripcion":        id_prescripcion,
            "nombre_medicamento":     nombre_medicamento,
            "horario_administracion": str(horario_administracion),
            "dosis_gr":               dosis_gr,
            "id_pacientes":           id_paciente,
            "id_doctor":              id_doctor
        }).execute()
        st.success("✅ Prescripción añadida correctamente.")
    except Exception as e:
        st.error(f"Error al añadir prescripción: {e}")


def delete_prescripcion(id_prescripcion):
    try:
        db().table("prescripcion") \
            .delete() \
            .eq("id_prescripcion", id_prescripcion) \
            .execute()
        st.success("Prescripción eliminada correctamente.")
    except Exception as e:
        st.error(f"Error al eliminar la prescripción: {e}")


def get_prescripciones_de_paciente(id_paciente):
    try:
        response = db().table("prescripcion") \
            .select("id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_doctor") \
            .eq("id_pacientes", id_paciente) \
            .execute()
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error al obtener las prescripciones: {e}")
        return None


def get_prescripciones_paciente(id_paciente):
    """Obtiene prescripciones con estado de administración del empleado actual."""
    try:
        prescripciones = db().table("prescripcion") \
            .select("id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr") \
            .eq("id_pacientes", id_paciente) \
            .execute()

        if not prescripciones.data:
            return None

        result = []
        for p in prescripciones.data:
            administra = db().table("administra") \
                .select("administrado") \
                .eq("id_prescripcion", p["id_prescripcion"]) \
                .eq("id_empleado", st.session_state['user_id']) \
                .execute()
            administrado = administra.data[0]["administrado"] if administra.data else False
            result.append((
                p["id_prescripcion"],
                p["nombre_medicamento"],
                p["horario_administracion"],
                p["dosis_gr"],
                administrado
            ))
        return result
    except Exception as e:
        st.error(f"Error al obtener las prescripciones: {e}")
        return None


# ── ADMINISTRA ─────────────────────────────────────────────────────────────────

def update_administracion(id_empleado, selected_prescripciones):
    try:
        for prescripcion_id, estado in selected_prescripciones.items():
            check = db().table("administra") \
                .select("id_administra") \
                .eq("id_empleado", id_empleado) \
                .eq("id_prescripcion", prescripcion_id) \
                .execute()

            if check.data:
                db().table("administra") \
                    .update({"administrado": estado}) \
                    .eq("id_empleado", id_empleado) \
                    .eq("id_prescripcion", prescripcion_id) \
                    .execute()
            else:
                db().table("administra").insert({
                    "id_prescripcion": prescripcion_id,
                    "id_empleado":     id_empleado,
                    "administrado":    estado
                }).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la administración: {e}")
        return False


# ── EMPLEADO ───────────────────────────────────────────────────────────────────

def get_horario_sector(id_empleado):
    try:
        response = db().table("empleado") \
            .select("horario_entrada, horario_salida, sector_hospitalario, cargo") \
            .eq("id_empleado", id_empleado) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al obtener el horario del empleado: {e}")
        return None


# ── RECORDATORIOS ──────────────────────────────────────────────────────────────

def get_recordatorios():
    try:
        now_time  = datetime.now()
        start_str = (now_time - timedelta(minutes=15)).strftime("%H:%M:%S")
        end_str   = (now_time + timedelta(minutes=15)).strftime("%H:%M:%S")

        prescripciones = db().table("prescripcion") \
            .select("id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_pacientes") \
            .gte("horario_administracion", start_str) \
            .lte("horario_administracion", end_str) \
            .execute()

        if not prescripciones.data:
            return []

        result = []
        for p in prescripciones.data:
            paciente = db().table("pacientes") \
                .select("nombre, apellido") \
                .eq("id_pacientes", p["id_pacientes"]) \
                .execute()
            nombre_p   = paciente.data[0]["nombre"]   if paciente.data else "Desconocido"
            apellido_p = paciente.data[0]["apellido"]  if paciente.data else ""
            result.append((
                p["id_prescripcion"],
                p["nombre_medicamento"],
                p["horario_administracion"],
                p["dosis_gr"],
                p["id_pacientes"],
                nombre_p,
                apellido_p
            ))
        return result
    except Exception as e:
        st.error(f"Error al obtener los recordatorios: {e}")
        return []


# ── PÁGINAS ────────────────────────────────────────────────────────────────────

def perfil_pacientes_page():
    st.header("Perfil del Paciente")

    if 'paciente_info' not in st.session_state:
        st.session_state.paciente_info = None
    if 'id_paciente' not in st.session_state:
        st.session_state.id_paciente = ""

    id_paciente = st.text_input("ID del Paciente:", key="perfil_paciente_id", value=st.session_state.id_paciente)

    if st.button("Buscar Paciente", key="btn_buscar_paciente"):
        if id_paciente:
            info = get_paciente_info(id_paciente)
            if info:
                st.success("Paciente encontrado.")
                st.session_state.paciente_info = info
                st.session_state.id_paciente   = id_paciente
            else:
                st.warning("No se encontró ningún paciente con ese ID.")
        else:
            st.error("Por favor, ingrese el ID del paciente.")

    if st.session_state.paciente_info:
        p = st.session_state.paciente_info
        st.table({
            "ID":                 [p["id_pacientes"]],
            "Nombre":             [p["nombre"]],
            "Apellido":           [p["apellido"]],
            "Habitación":         [p["habitacion"]],
            "Alergias":           [p["alergias"]],
            "Contacto":           [p["contacto_telefonico"]],
            "Diagnóstico":        [p["diagnostico"]],
            "Obra Social":        [p["obra_social"]]
        })

        if st.button("Editar Información"):
            st.session_state.editing = True

    if st.session_state.get('editing'):
        p = st.session_state.paciente_info
        with st.form(key="form_paciente"):
            nombre             = st.text_input("Nombre",             value=p["nombre"])
            apellido           = st.text_input("Apellido",           value=p["apellido"])
            habitacion         = st.text_input("Habitación",         value=p["habitacion"])
            alergias           = st.text_area("Alergias",            value=p["alergias"])
            contacto_telefonico= st.text_input("Contacto Telefónico",value=p["contacto_telefonico"])
            diagnostico        = st.text_area("Diagnóstico",         value=p["diagnostico"])
            obra_social        = st.text_input("Obra Social",        value=p["obra_social"])
            submit             = st.form_submit_button("Actualizar Información")

            if submit:
                if update_paciente_info(st.session_state.id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social):
                    st.success("Información actualizada correctamente.")
                    st.session_state.paciente_info = get_paciente_info(st.session_state.id_paciente)
                    st.session_state.editing = False
                else:
                    st.error("Error al actualizar la información.")


def alta_paciente_page():
    st.header("Alta de Paciente")
    id_paciente = random.randint(100000000, 999999999)
    st.info(f"ID generado automáticamente: **PAC{id_paciente}**")

    with st.form("alta_paciente_form"):
        nombre              = st.text_input("Nombre *")
        apellido            = st.text_input("Apellido *")
        habitacion          = st.text_input("Habitación")
        alergias            = st.text_area("Alergias (separadas por coma)")
        contacto_telefonico = st.text_input("Contacto Telefónico")
        diagnostico         = st.text_area("Diagnóstico")
        obra_social         = st.text_input("Obra Social")
        submitted           = st.form_submit_button("Dar de Alta")

        if submitted:
            if not nombre or not apellido:
                st.error("Nombre y Apellido son obligatorios.")
            elif insertar_paciente(f"PAC{id_paciente}", nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social):
                st.success(f"Paciente dado de alta. ID asignado: PAC{id_paciente}")
            else:
                st.error("Error al dar de alta al paciente.")


def admin_medicamentos_page():
    st.header("Administración de Medicamentos")

    if 'paciente_encontrado' not in st.session_state:
        st.session_state['paciente_encontrado'] = False
    if 'selected_prescripciones' not in st.session_state:
        st.session_state['selected_prescripciones'] = {}
    if 'admin_id_paciente' not in st.session_state:
        st.session_state['admin_id_paciente'] = ''

    id_paciente = st.text_input("ID del Paciente:", key="admin_paciente_id")

    if st.button("Buscar Prescripciones", key="btn_buscar_prescripciones"):
        if id_paciente:
            prescripciones = get_prescripciones_paciente(id_paciente)
            if prescripciones:
                st.session_state['paciente_encontrado']     = True
                st.session_state['admin_id_paciente']       = id_paciente
                st.session_state['selected_prescripciones'] = {p[0]: p[4] for p in prescripciones}
                st.success("Prescripciones encontradas.")
            else:
                st.warning("No se encontraron prescripciones para este paciente.")
                st.session_state['paciente_encontrado'] = False
        else:
            st.error("Por favor, ingrese el ID del paciente.")

    if st.session_state['paciente_encontrado']:
        prescripciones = get_prescripciones_paciente(st.session_state['admin_id_paciente'])
        if prescripciones:
            st.write("Marque los medicamentos que ya fueron administrados:")
            for p in prescripciones:
                info = f"💊 {p[1]} — Horario: {p[2]} — Dosis: {p[3]} g"
                st.session_state['selected_prescripciones'][p[0]] = st.checkbox(
                    info,
                    value=st.session_state['selected_prescripciones'].get(p[0], False),
                    key=f"chk_{p[0]}"
                )

    if st.button("Guardar Cambios", key="btn_guardar_cambios"):
        if st.session_state['selected_prescripciones']:
            if update_administracion(st.session_state['user_id'], st.session_state['selected_prescripciones']):
                st.success("Cambios guardados correctamente.")
            else:
                st.error("Error al guardar los cambios.")
        st.session_state['paciente_encontrado']     = False
        st.session_state['selected_prescripciones'] = {}


def prescripcion_page():
    st.header("Nueva Prescripción")

    id_prescripcion    = st.text_input("ID de la Prescripción:", value=f"PRE{random.randint(100000, 999999)}", key="add_prescripcion_id")
    nombre_medicamento = st.selectbox("Medicamento:", (
        "Paracetamol", "Ibuprofeno", "Amoxicilina", "Omeprazol", "Loratadina",
        "Diazepam", "Cetirizina", "Atorvastatina", "Metformina", "Simvastatina",
        "Ramipril", "Losartan", "Insulina", "Warfarina", "Levotiroxina",
        "Aspirina", "Enalapril", "Metoprolol", "Lisinopril", "Digoxina",
        "Amlodipino", "Pantoprazol", "Prednisona", "Metronidazol",
        "Penicilina", "Betametasona", "Bactrim", "Furosemida", "Salbutamol",
        "Levodopa", "Donepezilo", "Risperidona", "Sertralina"
    ), index=None, placeholder="Seleccione un medicamento...")
    horario_administracion = st.time_input("Horario de Administración:", key="add_prescripcion_horario")
    dosis_gr               = st.number_input("Dosis (gramos):", min_value=0.0, step=0.001, format="%.3f", key="add_prescripcion_dosis")
    id_paciente            = st.text_input("ID del Paciente:", key="add_prescripcion_paciente_id")

    if st.button("Añadir Prescripción", key="btn_add_prescripcion"):
        if id_prescripcion and nombre_medicamento and horario_administracion and dosis_gr and id_paciente:
            add_prescripcion(id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_paciente, st.session_state['user_id'])
        else:
            st.error("Por favor, complete todos los campos.")


def recordatorios_medicamentos_page():
    st.header("Recordatorios de Medicamentos")
    st.caption("Muestra las prescripciones con horario en los próximos/últimos 15 minutos.")
    recordatorios = get_recordatorios()

    if recordatorios:
        for rec in recordatorios:
            _, nombre_med, horario, dosis, id_pac, nombre_p, apellido_p = rec
            st.warning(f"⏰ Administrar **{nombre_med}** ({dosis}g) a **{nombre_p} {apellido_p}** (ID: {id_pac}) — Horario: {horario}")
    else:
        st.info("No hay recordatorios pendientes en este momento.")


def doctor_page():
    st.title("Panel del Doctor")
    tab1, tab2, tab3 = st.tabs(["👤 Ver Paciente", "💊 Nueva Prescripción", "📋 Gestionar Prescripciones"])

    with tab1:
        perfil_pacientes_page()

    with tab2:
        prescripcion_page()

    with tab3:
        st.header("Gestionar Prescripciones")

        st.subheader("Eliminar Prescripción")
        id_prescripcion_eliminar = st.text_input("ID de la Prescripción a Eliminar:", key="delete_prescripcion_id")
        if st.button("Eliminar Prescripción", key="btn_delete_prescripcion"):
            if id_prescripcion_eliminar:
                delete_prescripcion(id_prescripcion_eliminar)
            else:
                st.error("Ingrese el ID de la prescripción.")

        st.subheader("Ver Prescripciones de un Paciente")
        id_paciente = st.text_input("ID del Paciente:", key="view_prescripciones_paciente_id")
        if st.button("Ver Prescripciones", key="btn_view_prescripciones"):
            if id_paciente:
                prescripciones = get_prescripciones_de_paciente(id_paciente)
                if prescripciones:
                    for p in prescripciones:
                        st.write(f"**ID:** {p['id_prescripcion']} | **Medicamento:** {p['nombre_medicamento']} | **Horario:** {p['horario_administracion']} | **Dosis:** {p['dosis_gr']} g")
                        st.write("---")
                else:
                    st.warning("No se encontraron prescripciones para ese paciente.")
            else:
                st.error("Ingrese el ID del paciente.")


def empleado_page():
    st.title("Panel del Empleado")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💊 Administrar Medicamentos",
        "🕐 Mi Horario",
        "👤 Información del Paciente",
        "➕ Nuevo Paciente",
        "⏰ Recordatorios"
    ])

    with tab1:
        admin_medicamentos_page()

    with tab2:
        st.header("Mi Horario y Sector")
        horario = get_horario_sector(st.session_state['user_id'])
        if horario:
            col1, col2, col3 = st.columns(3)
            col1.metric("Horario de Entrada", horario['horario_entrada'])
            col2.metric("Horario de Salida",  horario['horario_salida'])
            col3.metric("Sector",             horario['sector_hospitalario'])
            st.write(f"**Cargo:** {horario['cargo']}")
        else:
            st.info("No se encontraron datos de horario.")

    with tab3:
        perfil_pacientes_page()

    with tab4:
        alta_paciente_page()

    with tab5:
        recordatorios_medicamentos_page()


# ── MAIN ───────────────────────────────────────────────────────────────────────

if st.session_state['estado'] == 'Autorizado':
    if not st.session_state.get('user_id'):
        id_input = st.text_input("Ingrese su ID:", key="login_id")
        if st.button("Ingresar", key="login_button"):
            if not id_input:
                st.error("Por favor, ingrese un ID válido.")
            else:
                emp = check_id_in_empleado(id_input)
                doc = check_id_in_doctor(id_input)
                if emp:
                    st.session_state['user_role'] = 'Empleado'
                    st.session_state['user_id']   = id_input
                    st.rerun()
                elif doc:
                    st.session_state['user_role'] = 'Doctor'
                    st.session_state['user_id']   = id_input
                    st.rerun()
                else:
                    st.error("El ID no existe en la base de datos.")
    else:
        st.success(f"Bienvenido/a — {st.session_state['user_role']} | ID: {st.session_state['user_id']}")
        if st.session_state['user_role'] == 'Empleado':
            empleado_page()
        elif st.session_state['user_role'] == 'Doctor':
            doctor_page()
else:
    st.error("Debes iniciar sesión primero.")