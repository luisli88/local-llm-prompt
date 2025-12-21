# LLM Local Stack Manager

Aplicación para gestionar modelos de lenguaje locales usando Docker y Ollama con interfaz Python moderna.

## ✅ Estado del Proyecto

**🟢 COMPLETAMENTE FUNCIONAL** - Aplicación Python lista para uso en producción.

### Problemas Resueltos (v2.0.0)
- ✅ Validación de instalación funciona correctamente
- ✅ Instalación del stack inicia contenedores con Docker Compose
- ✅ Activación/desactivación de modelos funciona perfectamente
- ✅ Actualización de modelos con lógica corregida
- ✅ Interfaz moderna con Rich y navegación fluida
- ✅ Sincronización automática DB ↔ Docker
- ✅ Suite completa de pruebas unitarias (13/13)

### Mejoras vs Versión Bash
- **Precisión**: APIs nativas de Docker vs parsing de CLI
- **Robustez**: Manejo avanzado de errores y recuperación automática
- **Mantenibilidad**: Arquitectura modular y testable
- **UX**: Interfaz moderna con colores, tablas y progreso
- **Confiabilidad**: Validación automática de dependencias y estado

## 🚀 Características

- **Interfaz Moderna**: CLI interactiva con Rich para una experiencia de usuario mejorada
- **Gestión Inteligente**: Estado automático de contenedores y modelos
- **Base de Datos SQLite**: Persistencia de configuraciones y versiones
- **Sincronización en Tiempo Real**: Estado actualizado automáticamente
- **Validación Robusta**: Verificación completa de dependencias y conectividad
- **Actualizaciones Automáticas**: Pull de nuevas versiones de modelos

## 📋 Requisitos

- **Ubuntu 25.10** (o compatible)
- **Docker** con NVIDIA Container Toolkit
- **Python 3.11+** con entorno virtual
- **RTX 2070 SUPER** o GPU NVIDIA compatible (8GB+ VRAM)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd llm-local-stack
```

### 2. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Instalar stack base
```bash
# Ejecutar instalación inicial
python main.py
# Seleccionar opción 2: "Instalar Stack"
```

## 🎯 Uso

### Interfaz Interactiva
```bash
python main.py
```

### Menú Principal
1. **Validar Instalación**: Verifica estado completo del stack
2. **Instalar Stack**: Configuración inicial de contenedores
3. **Activar Modelo**: Inicia contenedor de modelo específico
4. **Desactivar Modelo**: Detiene contenedor de modelo
5. **Actualizar Modelos**: Descarga últimas versiones
6. **Desactivar Stack Completo**: Detiene todos los contenedores

### Modelos Disponibles

| Modelo | Contenedor | Puerto | Uso |
|--------|------------|--------|-----|
| Qwen2.5-Coder | ollama-qwen | 11434 | Code completion |
| DeepSeek-Coder | ollama-deepseek | 11435 | Technical reasoning |
| Mistral | ollama-mistral | 11436 | Documentation |

## 🏗️ Arquitectura

### Componentes Principales

#### DockerManager (`docker_manager.py`)
- Comunicación directa con Docker API
- Gestión del ciclo de vida de contenedores
- Estadísticas de uso en tiempo real
- Validación de salud de servicios

#### ModelManager (`model_manager.py`)
- Base de datos SQLite con SQLAlchemy
- Sincronización automática DB ↔ Docker
- Tracking de versiones instaladas
- Operaciones CRUD de modelos

#### OllamaClient (`ollama_client.py`)
- Cliente para operaciones con Ollama
- Gestión de modelos: pull, list, test
- Validación de funcionamiento
- Actualizaciones automáticas

#### CLI Interface (`main.py`)
- Interfaz de usuario con Rich
- Menús interactivos y coloreados
- Gestión de flujo de navegación
- Presentación de información en tiempo real

### Base de Datos

```sql
-- Esquema de la base de datos
CREATE TABLE models (
    name TEXT PRIMARY KEY,
    container_name TEXT UNIQUE,
    port INTEGER,
    installed_version TEXT,
    status TEXT DEFAULT 'inactive',
    last_updated DATETIME,
    created_at DATETIME
);
```

## 🧪 Testing

### Ejecutar Pruebas
```bash
# Todas las pruebas
pytest tests.py -v

# Pruebas específicas
pytest tests.py::TestDockerManager -v

# Con coverage
pytest --cov=. --cov-report=html
```

### Tipos de Pruebas
- **Unitarias**: Funciones individuales
- **Integración**: Flujo completo con Docker
- **Mocks**: Simulación de APIs externas

## 📁 Estructura del Proyecto

```
llm-stack-manager/
├── main.py                 # CLI principal
├── docker_manager.py       # Gestión Docker
├── model_manager.py        # Gestión modelos/DB
├── ollama_client.py        # Cliente Ollama
├── models.py              # Modelos SQLAlchemy
├── config.py              # Configuración
├── utils.py               # Utilidades
├── tests.py               # Pruebas unitarias
├── requirements.txt       # Dependencias Python
├── .models.db            # Base de datos SQLite
├── docker-compose.yml    # Configuración Docker
└── .scripts/             # Scripts auxiliares
    ├── setup.sh
    ├── verify-install.sh
    └── model_manager.sh
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Personalizar rutas
export LLM_DB_PATH="/custom/path/.models.db"
export LLM_SCRIPTS_DIR="/custom/scripts"

# Configuración Docker
export DOCKER_HOST="unix:///var/run/docker.sock"
```

### Configuración de Modelos
Editar `config.py` para agregar nuevos modelos:

```python
MODELS_CONFIG.update({
    "nuevo-modelo": {
        "name": "Nuevo Modelo",
        "container_name": "ollama-nuevo",
        "port": 11437,
        "description": "Descripción del modelo"
    }
})
```

## 🚨 Solución de Problemas

### Problemas Comunes

#### Docker no disponible
```bash
# Verificar servicio Docker
sudo systemctl status docker
sudo systemctl start docker

# Verificar permisos de usuario
sudo usermod -aG docker $USER
# Reiniciar sesión
```

#### GPU no detectada
```bash
# Verificar NVIDIA drivers
nvidia-smi

# Verificar toolkit
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

#### Puertos ocupados
```bash
# Verificar puertos en uso
netstat -tlnp | grep :11434

# Cambiar puertos en config.py
```

### Logs y Debugging
```bash
# Ver logs de contenedores
docker compose logs ollama-qwen

# Ver estado detallado
docker compose ps -a

# Debug de la aplicación
python -c "from docker_manager import DockerManager; dm = DockerManager(); print(dm.get_stack_status())"
```

## 📊 Métricas y Monitoreo

### Información de Rendimiento
- **Uso de GPU**: Memoria, temperatura, utilization
- **Uso de CPU/RAM**: Por contenedor
- **Latencia**: Tiempo de respuesta de modelos
- **Tokens/segundo**: Rendimiento de inferencia

### Comandos de Monitoreo
```bash
# Estado del stack
python -c "from main import LLMStackApp; app = LLMStackApp(); print(app._show_menu())"

# Estadísticas de contenedores
docker stats

# Uso de GPU
nvidia-smi --query-gpu=utilization.gpu,utilization.memory --format=csv
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Guías de Desarrollo
- **Tests**: Todas las funciones deben tener tests unitarios
- **Documentación**: Actualizar README y docstrings
- **Commits**: Mensajes descriptivos en inglés
- **Style**: Seguir PEP 8

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [Ollama](https://ollama.ai/) - Motor de inferencia
- [Docker](https://docker.com/) - Contenedorización
- [NVIDIA](https://nvidia.com/) - Aceleración GPU
- [Rich](https://rich.readthedocs.io/) - CLI moderna
- [SQLAlchemy](https://sqlalchemy.org/) - ORM de base de datos

**Code Completion:**
- Base URL: `http://localhost:11434/v1`
- Model: `qwen2.5-coder:7b-instruct-q4_K_M`

**Technical Reasoning:**
- Base URL: `http://localhost:11435/v1`
- Model: `deepseek-coder-v2-lite-instruct-q4_K_M`

**Documentation:**
- Base URL: `http://localhost:11436/v1`
- Model: `mistral:7b-instruct-v0.3-q4_K_M`

API Key: `ollama` (para todos)

## Archivos

- `main.sh`: **Aplicación principal** - Punto de entrada único
- `.scripts/`: Scripts de automatización (ocultos)
- `specs/`: Especificaciones técnicas
- `docker-compose.yml`: Configuración multi-contenedor
- `README.md`: Esta documentación