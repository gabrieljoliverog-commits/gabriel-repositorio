import unicodedata, sqlite3, tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client
from fpdf import FPDF

# --- LIMPIEZA DE TEXTO ---
def limpiar(t):
    if not t: return ""
    t = t.strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')

# --- CONFIGURACIÓN NUBE ---
URL = "https://ecqjfkbo fhkjpbfnvecd.supabase.co".replace(" ", "")
KEY = "sb_publishable_cUHEtiaPg4y5MHsB8EXnAQ_LBEY99Ex"
sb: Client = create_client(URL, KEY)

# --- BASE DE DATOS LOCAL ---
def conectar_db():
    conn = sqlite3.connect("notas_unefa.db")
    conn.execute("CREATE TABLE IF NOT EXISTS configuracion (id INTEGER PRIMARY KEY, e1 TEXT, e2 TEXT, e3 TEXT, e4 TEXT, e5 TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS unefa (id INTEGER PRIMARY KEY, nombre TEXT, seccion TEXT, n1 REAL, n2 REAL, n3 REAL, n4 REAL, n5 REAL, nota_final REAL)")
    if conn.execute("SELECT COUNT(*) FROM configuracion").fetchone()[0] == 0:
        conn.execute("INSERT INTO configuracion VALUES (1, 'HERIDAS', 'NUTRICION', 'DRENES', 'OSTOMIAS', 'REVISTA')")
    conn.commit()
    return conn

id_edit = None

# --- FUNCIONES ---
def cargar_para_editar(e):
    global id_edit
    item = tabla.focus()
    if not item: return
    v = tabla.item(item)['values']
    id_edit = v[0]
    ent_nom.delete(0, tk.END); ent_nom.insert(0, v[1])
    ent_sec.delete(0, tk.END); ent_sec.insert(0, v[2])
    for i in range(5):
        entradas_notas[i].delete(0, tk.END); entradas_notas[i].insert(0, v[3+i])
    btn_guardar.config(text="ACTUALIZAR NOTA", bg="#3498db")

def guardar():
    global id_edit
    try:
        n, s = limpiar(ent_nom.get()), limpiar(ent_sec.get())
        if not n or not s: return messagebox.showwarning("¡OJO!", "Nombre y Sección son obligatorios")
        notas = [float(x.get()) if x.get().strip() else 0.0 for x in entradas_notas]
        p = round(sum(notas)/5, 2)
        conn = conectar_db()
        if id_edit is None:
            conn.execute("INSERT INTO unefa (nombre,seccion,n1,n2,n3,n4,n5,nota_final) VALUES (?,?,?,?,?,?,?,?)",(n,s,*notas,p))
        else:
            conn.execute("UPDATE unefa SET nombre=?,seccion=?,n1=?,n2=?,n3=?,n4=?,n5=?,nota_final=? WHERE id=?",(n,s,*notas,p,id_edit))
        conn.commit(); conn.close()
        try:
            sb.table("unefa_nube").upsert({"nombre":n,"seccion":s,"n1":notas[0],"n2":notas[1],"n3":notas[2],"n4":notas[3],"n5":notas[4],"nota_final":p}, on_conflict="nombre").execute()
        except: pass
        id_edit = None; btn_guardar.config(text="GUARDAR NUEVO", bg="#2ecc71")
        for e in [ent_nom, ent_sec] + entradas_notas: e.delete(0, tk.END)
        cargar_datos()
        messagebox.showinfo("ÉXITO", "DATOS SINCRONIZADOS")
    except: messagebox.showerror("ERROR", "Revisa que las notas sean números (usa punto para decimal)")

def cargar_datos():
    for i in tabla.get_children(): tabla.delete(i)
    conn = conectar_db()
    conf = conn.execute("SELECT e1, e2, e3, e4, e5 FROM configuracion WHERE id=1").fetchone()
    for i, v in enumerate(conf):
        etiq_vars[i].delete(0, tk.END); etiq_vars[i].insert(0, v)
    for f in conn.execute("SELECT * FROM unefa ORDER BY id DESC"):
        tabla.insert("", tk.END, values=f, tags=("aprobado" if f[8]>=10 else "reprobado"))
    conn.close()

def generar_pdf():
    try:
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "UNEFA - REPORTE DE NOTAS", 0, 1, 'C')
        pdf.ln(5)
        titulos = [x.get() for x in etiq_vars]
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(50, 8, "NOMBRE", 1); pdf.cell(15, 8, "SEC", 1)
        for t in titulos: pdf.cell(18, 8, t[:7], 1)
        pdf.cell(15, 8, "FIN", 1); pdf.ln()
        conn = conectar_db()
        for f in conn.execute("SELECT nombre, seccion, n1, n2, n3, n4, n5, nota_final FROM unefa"):
            pdf.cell(50, 7, str(f[0])[:25], 1); pdf.cell(15, 7, str(f[1]), 1)
            for i in range(2, 8): pdf.cell(18, 7, str(f[i]), 1)
            pdf.ln()
        conn.close(); pdf.output("Reporte_Notas.pdf")
        messagebox.showinfo("PDF", "REPORTE GENERADO")
    except Exception as e: messagebox.showerror("ERROR PDF", str(e))

# --- INTERFAZ GRÁFICA ---
root = tk.Tk(); root.title("ADMINISTRACIÓN UNEFA - GABRIEL"); root.geometry("1100x750")

# Títulos de materias
f_mats = tk.LabelFrame(root, text=" NOMBRES DE MATERIAS (EDITABLES) ", fg="blue")
f_mats.pack(fill="x", padx=10, pady=5)
etiq_vars = [tk.Entry(f_mats, width=15, justify="center") for _ in range(5)]
for i, ev in enumerate(etiq_vars): ev.grid(row=0, column=i, padx=5, pady=5)

# Formulario de entrada
f_ent = tk.Frame(root); f_ent.pack(pady=10)
tk.Label(f_ent, text="NOMBRE COMPLETO").grid(row=0, column=0)
ent_nom = tk.Entry(f_ent, width=30); ent_nom.grid(row=1, column=0, padx=5)
tk.Label(f_ent, text="SECCIÓN").grid(row=0, column=1)
ent_sec = tk.Entry(f_ent, width=10); ent_sec.grid(row=1, column=1, padx=5)

entradas_notas = []
for i in range(5):
    tk.Label(f_ent, text=f"NOTA {i+1}").grid(row=0, column=i+2)
    en = tk.Entry(f_ent, width=7); en.grid(row=1, column=i+2, padx=3)
    entradas_notas.append(en)

# Botones
f_btns = tk.Frame(root); f_btns.pack(pady=10)
btn_guardar = tk.Button(f_btns, text="GUARDAR NUEVO", command=guardar, bg="#2ecc71", fg="white", width=20, font=('Arial', 10, 'bold'))
btn_guardar.pack(side=tk.LEFT, padx=10)
tk.Button(f_btns, text="GENERAR PDF", command=generar_pdf, bg="#9b59b6", fg="white", width=20, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

# Tabla de resultados
cols = ("ID", "ALUMNO", "SECCIÓN", "N1", "N2", "N3", "N4", "N5", "FINAL")
tabla = ttk.Treeview(root, columns=cols, show='headings', height=18)
for c in cols: 
    tabla.heading(c, text=c)
    tabla.column(c, width=100, anchor="center")
tabla.column("ALUMNO", width=250, anchor="w")
tabla.pack(fill="both", expand=True, padx=10, pady=10)
tabla.tag_configure("aprobado", foreground="green")
tabla.tag_configure("reprobado", foreground="red")

# Evento Doble Clic
tabla.bind("<Double-1>", cargar_para_editar)

cargar_datos()
root.mainloop()