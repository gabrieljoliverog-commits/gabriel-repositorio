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
        # Limpiamos el nombre
        nombre_buscado = limpiar_texto(nombre_raw)
        
        try:
            # CAMBIO CLAVE: Usamos .ilike() con % para que busque coincidencias aunque haya espacios
            res = supabase.table("unefa_nube").select("*").ilike("nombre", f"%{nombre_buscado}%").execute()
            
            if res.data:
                # Si hay varios parecidos, mostramos el primero
                alumno = res.data[0]
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