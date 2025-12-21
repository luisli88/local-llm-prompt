# Especificación: Aplicación Python para Gestión de Stack LLM

## 🎯 Visión General

Reescritura de la aplicación de terminal en Python para obtener información más precisa y veraz sobre el estado de Docker y los modelos, utilizando APIs nativas en lugar de parsing de comandos CLI.

## 🏗️ Arquitectura de la Aplicación

### Componentes Principales

#### 1. DockerManager (docker_manager.py)
**Responsabilidades:**
- Comunicación directa con Docker API via `docker-py`
- Gestión del ciclo de vida de contenedores
- Consulta de estado real-time de contenedores
- Información detallada: memoria, CPU, puertos, estado

**Métodos clave:**
```python
class DockerManager:
    def get_container_status(self, container_name: str) -> Dict[str, Any]:
        """Estado detallado del contenedor"""

    def start_container(self, container_name: str) -> bool:
        """Inicia contenedor con validación"""

    def stop_container(self, container_name: str) -> bool:
        """Detiene contenedor y libera recursos"""

    def get_container_stats(self, container_name: str) -> Dict[str, Any]:
        """Estadísticas de uso: CPU, memoria, GPU"""

    def validate_container_health(self, container_name: str) -> bool:
        """Verifica conectividad real con API del modelo"""
```

#### 2. ModelManager (model_manager.py)
**Responsabilidades:**
- Gestión de base de datos SQLite con SQLAlchemy
- Sincronización automática entre DB y estado Docker
- Tracking de versiones instaladas
- Operaciones CRUD para modelos

**Esquema de Base de Datos:**
```python
class Model(Base):
    __tablename__ = 'models'

    name = Column(String, primary_key=True)
    container_name = Column(String, unique=True)
    port = Column(Integer)
    installed_version = Column(String, nullable=True)
    status = Column(String, default='inactive')  # active/inactive
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Métodos clave:**
```python
class ModelManager:
    def sync_with_docker(self) -> None:
        """Sincroniza estado DB con contenedores reales"""

    def update_model_version(self, container_name: str, version: str) -> None:
        """Actualiza versión instalada"""

    def get_active_models(self) -> List[Dict[str, Any]]:
        """Modelos activos con URLs"""

    def set_model_status(self, container_name: str, status: str) -> None:
        """Actualiza estado del modelo"""
```

#### 3. OllamaClient (ollama_client.py)
**Responsabilidades:**
- Cliente para API de Ollama dentro de contenedores
- Gestión de modelos: pull, list, remove
- Validación de funcionamiento de modelos
- Tests de conectividad

**Métodos clave:**
```python
class OllamaClient:
    def pull_model(self, model_name: str, container_name: str) -> bool:
        """Descarga modelo en contenedor específico"""

    def list_models(self, container_name: str) -> List[str]:
        """Lista modelos disponibles en contenedor"""

    def test_model(self, model_name: str, container_name: str) -> Dict[str, Any]:
        """Test básico de funcionamiento"""

    def get_model_version(self, model_name: str, container_name: str) -> str:
        """Obtiene versión/tag del modelo"""
```

#### 4. CLI Interface (cli.py)
**Responsabilidades:**
- Interfaz de usuario con Rich para menús coloreados
- Manejo de entrada/salida
- Presentación de información en tiempo real
- Gestión de flujo de navegación

**Características:**
- Menús interactivos con indicadores visuales
- Tabla de modelos con estado y versiones
- Progress bars para operaciones largas
- Manejo de errores con mensajes informativos

## 📋 Dependencias Python

```toml
# requirements.txt
docker>=7.0.0
rich>=13.7.0
click>=8.1.0
sqlalchemy>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

## 🔧 Funcionalidades Avanzadas

### Sincronización Inteligente
- **Detección automática** de cambios en estado de contenedores
- **Actualización en tiempo real** de la interfaz
- **Validación cruzada** entre Docker API y base de datos

### Gestión de Recursos
- **Monitoreo de GPU**: Memoria usada, temperatura, utilization
- **Límites de recursos**: Configuración automática de límites por contenedor
- **Liberación automática**: Cleanup de recursos al detener contenedores

### Validación Robusta
- **Health checks**: Verificación de APIs de modelos
- **Connectivity tests**: Validación de puertos y endpoints
- **Dependency validation**: Chequeo completo de stack

## 🚀 API de Integración

### Endpoints para Scripts Externos
```python
# Para integración con otros scripts
from app import DockerManager, ModelManager

docker_mgr = DockerManager()
model_mgr = ModelManager()

# Estado del stack
status = docker_mgr.get_stack_status()
active_models = model_mgr.get_active_models()
```

### Configuración Extensible
- **YAML/JSON config**: Configuración externa de modelos y puertos
- **Environment variables**: Personalización vía variables de entorno
- **Plugins**: Sistema extensible para nuevos tipos de modelos

## 🧪 Testing y Calidad

### Estrategia de Testing
- **Unit tests**: Para cada componente individual
- **Integration tests**: Flujo completo con Docker
- **E2E tests**: Simulación de uso real

### Métricas de Calidad
- **Coverage**: >90% de código cubierto
- **Performance**: <2s para operaciones críticas
- **Reliability**: Manejo robusto de errores de Docker

## 📦 Distribución y Empaquetado

### Estructura del Proyecto
```
llm-stack-manager/
├── main.py                 # Entry point
├── cli.py                  # CLI interface
├── docker_manager.py       # Docker operations
├── model_manager.py        # Database operations
├── ollama_client.py        # Ollama API client
├── config.py              # Configuration
├── models.py              # SQLAlchemy models
├── utils.py               # Utilities
├── tests/                 # Test suite
├── requirements.txt       # Dependencies
└── pyproject.toml         # Package config
```

### Instalación
```bash
pip install -r requirements.txt
python main.py
```

## 🔄 Migración desde Bash

### Compatibilidad
- **Scripts existentes**: Mantener `.scripts/` para compatibilidad
- **Configuración**: Reutilizar `docker-compose.yml`
- **Interfaz**: Mantener UX similar con mejoras

### Beneficios de la Migración
- ✅ **Información precisa**: APIs nativas vs parsing CLI
- ✅ **Mejor error handling**: Excepciones específicas
- ✅ **Performance**: Operaciones más rápidas
- ✅ **Mantenibilidad**: Código más estructurado
- ✅ **Extensibilidad**: Fácil agregar nuevas funcionalidades