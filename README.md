# Gestión Escolar (script)

Archivo: `school_manager.py`

Requisitos: Python 3 (sin dependencias externas).

Cómo ejecutar:

```bash
# Desde tu directorio home
chmod +x ~/school_manager.py
./school_manager.py
# o
python3 ~/school_manager.py
```

Opciones del menú:
- 1) Registrar Alumno
- 2) Ver Listado
- 3) Reporte por Materia (suma de notas)
- 4) Eliminar Alumno (por ID)
- 5) Exportar a CSV (crea `students_export.csv`)
- 6) Salir

Notas:
- La base de datos SQLite se crea como `school.db` en el mismo directorio.
- `students_export.csv` se genera con las columnas `id,nombre,cedula,materia,nota`.
