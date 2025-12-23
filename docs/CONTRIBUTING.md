# Guía de Contribución

Gracias por tu interés en contribuir a Akitoi.

## Configuración del entorno de desarrollo

1. Fork y clona el repositorio
2. Crea un entorno virtual: `python -m venv venv`
3. Activa el entorno virtual: `source venv/bin/activate`
4. Instala las dependencias de desarrollo: `pip install -e ".[dev]"`

## Estándares de código

Este proyecto utiliza:

- **Black** para formateo de código
- **Ruff** para linting
- **MyPy** para verificación de tipos
- **pytest** para testing

Antes de hacer commit, asegúrate de que tu código pase todas las verificaciones:

```bash
# Formatear código
black src/ tests/

# Verificar linting
ruff check src/ tests/

# Verificar tipos
mypy src/

# Ejecutar tests
pytest
```

## Proceso de contribución

1. Crea una issue describiendo el cambio propuesto
2. Espera feedback antes de empezar a trabajar
3. Crea una rama desde `main`: `git checkout -b feature/tu-feature`
4. Haz tus cambios siguiendo los estándares de código
5. Agrega tests para tu código
6. Actualiza la documentación si es necesario
7. Haz commit con mensajes claros y descriptivos
8. Push a tu fork
9. Crea un Pull Request

## Mensajes de commit

Usa mensajes claros y descriptivos:

- `feat: agregar nueva funcionalidad X`
- `fix: corregir bug en Y`
- `docs: actualizar documentación de Z`
- `test: agregar tests para W`
- `refactor: mejorar implementación de V`

## Tests

Todos los cambios deben incluir tests apropiados. Los tests deben:

- Ser claros y descriptivos
- Probar un solo comportamiento
- Ser independientes entre sí
- Tener alta cobertura

## Preguntas

Si tienes preguntas, abre una issue o contacta al equipo en team@akitoi.dev
