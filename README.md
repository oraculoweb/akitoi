# Akitoi

Un proyecto Python profesional diseñado para escalar.

## Propósito

Akitoi es una base sólida para desarrollar aplicaciones Python modernas y escalables. El proyecto está configurado con las mejores prácticas de la industria, incluyendo:

- Gestión moderna de dependencias con `pyproject.toml`
- Herramientas de calidad de código (Ruff, Black, MyPy)
- Framework de testing con pytest
- Estructura modular y mantenible

## Requisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)

## Instalación

### Instalación básica

```bash
# Clonar el repositorio
git clone https://github.com/oraculoweb/akitoi.git
cd akitoi

# Crear un entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar el paquete
pip install -e .
```

### Instalación para desarrollo

```bash
# Instalar con dependencias de desarrollo
pip install -e ".[dev]"
```

## Uso básico

```python
# Importar el paquete
import akitoi

# El proyecto está listo para que agregues tu lógica de negocio
```

## Estructura del proyecto

```
akitoi/
├── src/
│   └── akitoi/          # Código fuente principal
│       └── __init__.py
├── tests/               # Tests unitarios y de integración
│   └── __init__.py
├── docs/                # Documentación adicional
├── .gitignore          # Archivos ignorados por git
├── pyproject.toml      # Configuración del proyecto y dependencias
└── README.md           # Este archivo
```

## Desarrollo

### Ejecutar tests

```bash
pytest
```

### Ejecutar linting

```bash
# Verificar código con Ruff
ruff check src/ tests/

# Formatear código con Black
black src/ tests/

# Verificar tipos con MyPy
mypy src/
```

### Formatear código automáticamente

```bash
black src/ tests/
ruff check --fix src/ tests/
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Roadmap

- [ ] Implementar módulos core
- [ ] Agregar documentación completa
- [ ] Configurar CI/CD
- [ ] Publicar en PyPI

## Licencia

MIT License - ver archivo LICENSE para más detalles.

## Contacto

Akitoi Team - team@akitoi.dev

Project Link: [https://github.com/oraculoweb/akitoi](https://github.com/oraculoweb/akitoi)
