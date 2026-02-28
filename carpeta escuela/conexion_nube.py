from supabase import create_client, Client

# --- DATOS DE CONEXIÓN ---
# Asegúrate de que empiecen con " y terminen con "
URL_PROYECTO = "https://ecqjfkbo fhkjpbfnvecd.supabase.co" 
KEY_PROYECTO = "sb_publishable_cUHEtiaPg4y5MHsB8EXnAQ_LBEY99Ex"

# Inicializamos el cliente
supabase: Client = create_client(URL_PROYECTO, KEY_PROYECTO)

def enviar_nota_a_la_nube():
    try:
        alumno = {
            "nombre": "GABRIEL - PRUEBA EXITOSA",
            "seccion": "MQ-II",
            "n1": 20, "n2": 19, "n3": 18, "n4": 17, "n5": 20,
            "nota_final": 18.8
        }
        supabase.table("unefa_nube").insert(alumno).execute()
        print("🚀 ¡LOGRADO! El alumno ya está en internet.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    enviar_nota_a_la_nube()