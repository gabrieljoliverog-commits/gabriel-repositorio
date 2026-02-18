#!/usr/bin/env python3
"""
Programa sencillo de gestión escolar (un solo archivo).

Características:
- Usa sqlite3 para persistencia en 'school.db'.
- Permite registrar alumno, ver listado, reporte por materia (suma de notas), eliminar y exportar CSV.

Ejecutar: ./school_manager.py  (o `python3 school_manager.py`)
"""

import sqlite3
import os
import sys
import csv

# Nombre del archivo de la base de datos SQLite
DB_FILE = "school.db"


def get_connection():
    """Crear (o abrir) la conexión a la base de datos."""
    return sqlite3.connect(DB_FILE)


def init_db():
    """Crear la tabla `students` si no existe."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT NOT NULL,
            materia TEXT NOT NULL,
            nota REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def register_student(nombre, cedula, materia, nota):
    """Insertar un nuevo alumno en la tabla."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (nombre, cedula, materia, nota) VALUES (?, ?, ?, ?)",
        (nombre, cedula, materia, float(nota)),
    )
    conn.commit()
    conn.close()


def delete_student_by_id(student_id):
    """Eliminar un alumno por su ID. Devuelve número de filas borradas."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted


def fetch_all_students():
    """Devolver todos los alumnos registrados como lista de tuplas."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, cedula, materia, nota FROM students ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def report_by_materia():
    """Devolver lista de (materia, suma_notas) agrupadas por materia."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT materia, SUM(nota) FROM students GROUP BY materia")
    rows = cur.fetchall()
    conn.close()
    return rows


def export_to_csv(path="students_export.csv"):
    """Exportar todos los registros a un archivo CSV y devolver la ruta escrita."""
    rows = fetch_all_students()
    if not rows:
        return None
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "nombre", "cedula", "materia", "nota"])
        for r in rows:
            writer.writerow(r)
    return os.path.abspath(path)


def input_nonempty(prompt):
    """Pedir al usuario hasta que ingrese una cadena no vacía."""
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("Entrada vacía — inténtalo de nuevo.")


def input_float(prompt):
    """Pedir al usuario un número (float) válido."""
    while True:
        v = input(prompt).strip()
        try:
            return float(v)
        except ValueError:
            print("Valor no válido. Introduce un número (por ejemplo: 7.5).")


def print_table(rows, headers):
    """Imprimir una tabla de texto con ajuste de columnas sencillo."""
    if not rows:
        # Mostrar solo cabecera si no hay filas
        widths = [len(h) for h in headers]
    else:
        cols = list(zip(*rows))
        widths = []
        for i, h in enumerate(headers):
            maxw = len(h)
            if cols and i < len(cols):
                maxw = max(maxw, max(len(str(x)) for x in cols[i]))
            widths.append(maxw)

    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * widths[i] for i in range(len(headers)))
    print(header_line)
    print(sep_line)

    for r in rows:
        print(" | ".join(str(r[i]).ljust(widths[i]) for i in range(len(headers))))


def cmd_register():
    """Comando: registrar un nuevo alumno pidiendo los campos."""
    print("--- Registrar Alumno ---")
    nombre = input_nonempty("Nombre: ")
    cedula = input_nonempty("Cédula de Identidad: ")
    materia = input_nonempty("Materia: ")
    nota = input_float("Nota (número): ")
    register_student(nombre, cedula, materia, nota)
    print("Alumno registrado correctamente.\n")


def cmd_list():
    """Comando: mostrar listado de alumnos en tabla."""
    rows = fetch_all_students()
    if not rows:
        print("No hay alumnos registrados.\n")
        return
    headers = ["ID", "Nombre", "Cédula", "Materia", "Nota"]
    print_table(rows, headers)
    print()


def cmd_report():
    """Comando: mostrar suma de notas por materia."""
    rows = report_by_materia()
    if not rows:
        print("No hay datos para reportar.\n")
        return
    headers = ["Materia", "Suma de Notas"]
    formatted = [(m, f"{s:.2f}") for m, s in rows]
    print_table(formatted, headers)
    print()


def cmd_delete():
    """Comando: eliminar un registro pidiendo el ID."""
    print("--- Eliminar Alumno ---")
    sid = input_nonempty("ID del alumno a eliminar: ")
    try:
        sid_i = int(sid)
    except ValueError:
        print("ID no válido. Debe ser un número entero.\n")
        return
    deleted = delete_student_by_id(sid_i)
    if deleted:
        print(f"Alumno con ID {sid_i} eliminado correctamente.\n")
    else:
        print(f"No se encontró alumno con ID {sid_i}.\n")


def cmd_export():
    """Comando: exportar todos los registros a CSV."""
    path = export_to_csv()
    if not path:
        print("No hay datos para exportar.\n")
    else:
        print(f"Exportado a: {path}\n")


def main():
    """Bucle principal del menú de texto."""
    init_db()
    while True:
        print("--- Gestión Escolar ---")
        print("1) Registrar Alumno")
        print("2) Ver Listado")
        print("3) Reporte por Materia (suma de notas)")
        print("4) Eliminar Alumno (por ID)")
        print("5) Exportar a CSV")
        print("6) Salir")
        choice = input("Elige una opción (1-6): ").strip()
        if choice == "1":
            cmd_register()
        elif choice == "2":
            cmd_list()
        elif choice == "3":
            cmd_report()
        elif choice == "4":
            cmd_delete()
        elif choice == "5":
            cmd_export()
        elif choice == "6":
            print("Saliendo. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intenta de nuevo.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario. Saliendo.")
        sys.exit(0)
