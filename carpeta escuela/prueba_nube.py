from supabase import create_client, Client

# --- CONFIGURACIÓN LIMPIA ---
# He unido la URL para que no tenga espacios accidentales
URL_NUBE = "https://ecqjfkbo fhkjpbfnvecd.supabase.co".replace(" ", "")
KEY_NUBE = "sb_publishable_cUHEtiaPg4y5MHsB8EXnAQ_LBEY99Ex"

supabase: Client = create_client(URL_NUBE, KEY_NUBE)

def guardar_en_la_nube(nombre, seccion, notas):
    try:
        promedio = round(sum(notas) / len(notas), 2)
        datos = {
            "nombre": nombre.upper(),
            "seccion": seccion.upper(),
            "n1": notas[0], "n2": notas[1], "n3": notas[2], 
            "n4": notas[3], "n5": notas[4],
            "nota_final": promedio
        }
        # Enviamos a la tabla que ya tienes creada
        supabase.table("unefa_nube").insert(datos).execute()
        print("✅ ¡DATOS GUARDADOS EN LA NUBE CON ÉXITO!")
    except Exception as e:
        print(f"❌ Error al guardar: {e}")

if __name__ == "__main__":
    mis_notas = [15.0, 18.0, 12.0, 20.0, 14.0]
    print("Conectando con Supabase...")
    guardar_en_la_nube("GABRIEL PRUEBA FINAL", "A1", mis_notas)