import streamlit as st
from supabase import create_client, Client
import unicodedata

# --- FUNCIÓN DE LIMPIEZA ---
def limpiar_texto(texto):
    if not texto: return ""
    texto = texto.strip().upper()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

# --- CONFIGURACIÓN SUPABASE ---
URL_NUBE = "https://ecqjfkbo fhkjpbfnvecd.supabase.co".replace(" ", "")
KEY_NUBE = "sb_publishable_cUHEtiaPg4y5MHsB8EXnAQ_LBEY99Ex"
supabase: Client = create_client(URL_NUBE, KEY_NUBE)

st.set_page_config(page_title="Consulta UNEFA", page_icon="🎓")
st.title("🎓 Sistema de Consulta de Notas")

nombre_raw = st.text_input("Nombre del Estudiante:")

if st.button("Buscar Notas"):
    if nombre_raw:
        nombre_buscado = limpiar_texto(nombre_raw)
        
        try:
            res = supabase.table("unefa_nube").select("*").ilike("nombre", f"%{nombre_buscado}%").execute()
            
            if res.data:
                alumno = res.data[0]
                st.session_state['alumno_actual'] = alumno # Guardamos los datos para editar
                
                st.success(f"### Estudiante: {alumno['nombre']}")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Sección", alumno['seccion'])
                c2.metric("Promedio", f"{alumno['nota_final']} / 20")
                estado = "APROBADO ✅" if alumno['nota_final'] >= 10 else "REPROBADO ❌"
                c3.write(f"**Estado:** \n### {estado}")

                st.write("---")
                detalles = {
                    "Evaluación": ["Nota 1", "Nota 2", "Nota 3", "Nota 4", "Nota 5"],
                    "Puntaje": [alumno['n1'], alumno['n2'], alumno['n3'], alumno['n4'], alumno['n5']]
                }
                st.table(detalles)
            else:
                st.error(f"No se encontró nada para: {nombre_buscado}")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Escribe un nombre.")

# --- SECCIÓN PARA MODIFICAR NOTAS (Solo visible si hay un alumno seleccionado) ---
if 'alumno_actual' in st.session_state:
    st.write("### 📝 Modificar Notas de este Estudiante")
    alumno = st.session_state['alumno_actual']
    
    with st.form("form_edicion"):
        col1, col2, col3, col4, col5 = st.columns(5)
        n1 = col1.number_input("N1", value=float(alumno['n1']), min_value=0.0, max_value=20.0)
        n2 = col2.number_input("N2", value=float(alumno['n2']), min_value=0.0, max_value=20.0)
        n3 = col3.number_input("N3", value=float(alumno['n3']), min_value=0.0, max_value=20.0)
        n4 = col4.number_input("N4", value=float(alumno['n4']), min_value=0.0, max_value=20.0)
        n5 = col5.number_input("N5", value=float(alumno['n5']), min_value=0.0, max_value=20.0)
        
        if st.form_submit_button("Guardar Cambios en la Nube"):
            nueva_final = round((n1 + n2 + n3 + n4 + n5) / 5, 2)
            
            # Actualizamos en Supabase usando el nombre como referencia
            datos_nuevos = {
                "n1": n1, "n2": n2, "n3": n3, "n4": n4, "n5": n5,
                "nota_final": nueva_final
            }
            
            try:
                supabase.table("unefa_nube").update(datos_nuevos).eq("nombre", alumno['nombre']).execute()
                st.success("✅ ¡Notas actualizadas con éxito! Refresca para ver los cambios.")
                del st.session_state['alumno_actual'] # Limpiamos para la próxima búsqueda
            except Exception as e:
                st.error(f"Error al actualizar: {e}")