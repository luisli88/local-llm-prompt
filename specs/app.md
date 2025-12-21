# Especificación: Aplicación Python para Gestión de Stack LLM

## 🎯 Visión General

Reescritura de la aplicación de terminal en Python para obtener información más precisa y veraz sobre el estado de Docker y los modelos, utilizando APIs nativas en lugar de parsing de comandos CLI.

## 🎯 Arquitectura Simplificada: Ollama Local Nativo

### Arquitectura Principal
- **Ollama Local**: Instalado nativamente en el sistema host
- **Configuración Externa**: Modelos definidos en archivos YAML (`config/models.yml`)
- **Gestión Directa**: Comandos CLI sin contenedores Docker
- **RTX 2070 SUPER**: Optimizado para 8GB VRAM con gestión inteligente

### Gestión de Modelos
- **Activación/Desactivación**: Via `ollama pull/rm/stop` directo
- **Sin Prioridades**: Gestión simple por orden de uso
- **Sin Base de Datos**: Configuración en archivos YAML

## 🏗️ Arquitectura de la Aplicación

### Componentes Principales

#### 0. ConfigManager (config_manager.py)
**Responsabilidades:**
- Gestión de configuración de modos de despliegue
- Validación de dependencias por modo
- Configuración automática de parámetros
- Detección automática del modo actual

**Métodos clave:**
```python
class ConfigManager:
    def detect_deployment_mode(self) -> str:
        """Auto-detecta: single/local/multi"""

    def validate_dependencies(self, mode: str) -> Dict[str, bool]:
        """Valida Docker/Ollama según modo"""

    def get_deployment_config(self, mode: str) -> Dict[str, Any]:
        """Configuración específica por modo"""
```

#### 1. DockerManager (docker_manager.py) - *Opcional*
**Responsabilidades:**
- Comunicación directa con Docker API via `docker-py`
- Gestión del ciclo de vida de contenedores (solo para modos single/multi)
- Consulta de estado real-time de contenedores
- Información detallada: memoria, CPU, puertos, estado

**Métodos clave:**
```python
class DockerManager:
    def __init__(self, deployment_mode: str):
        self.deployment_mode = deployment_mode

    def get_container_status(self, container_name: str) -> Dict[str, Any]:
        """Estado detallado del contenedor"""

    def start_container(self, container_name: str) -> bool:
        """Inicia contenedor con validación (solo single/multi)"""

    def stop_container(self, container_name: str) -> bool:
        """Detiene contenedor y libera recursos"""

    def get_container_stats(self, container_name: str) -> Dict[str, Any]:
        """Estadísticas de uso: CPU, memoria, GPU"""

    def validate_container_health(self, container_name: str) -> bool:
        """Verifica conectividad real con API del modelo"""

    def exec_ollama_command(self, container_name: str, command: str) -> str:
        """Ejecuta comandos ollama dentro del contenedor"""
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
    container_name = Column(String, nullable=True)  # None para local mode
    port = Column(Integer, default=11434)
    installed_version = Column(String, nullable=True)
    status = Column(String, default='inactive')  # active/inactive
    priority = Column(Integer, default=5)  # 1-10, mayor = más prioridad
    deployment_mode = Column(String, default='single')  # single/local/multi
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Métodos clave:**
```python
class ModelManager:
    def __init__(self, deployment_mode: str = 'single'):
        self.deployment_mode = deployment_mode  # single/local/multi

    def sync_with_deployment(self) -> None:
        """Sincroniza estado DB con contenedores reales o Ollama local"""

    def update_model_version(self, model_name: str, version: str) -> None:
        """Actualiza versión instalada"""

    def get_active_models(self) -> List[Dict[str, Any]]:
        """Modelos activos con URLs"""

    def set_model_status(self, model_name: str, status: str) -> None:
        """Actualiza estado del modelo"""

    def set_model_priority(self, model_name: str, priority: int) -> None:
        """Establece prioridad 1-10 (mayor = más importante)"""

    def get_primary_model(self) -> Optional[Dict[str, Any]]:
        """Obtiene modelo con mayor prioridad activa"""

    def deactivate_lower_priority_models(self, keep_active: str) -> None:
        """Desactiva modelos de menor prioridad para liberar VRAM"""
```

#### 3. OllamaClient (ollama_client.py)
**Responsabilidades:**
- Cliente unificado para API de Ollama (contenedor/local)
- Gestión de modelos: pull, list, remove, stop
- Validación de funcionamiento de modelos
- Tests de conectividad y health checks
- Gestión de memoria GPU con prioridad

**Métodos clave:**
```python
class OllamaClient:
    def __init__(self, deployment_mode: str = 'single', container_name: str = None):
        self.deployment_mode = deployment_mode
        self.container_name = container_name

    def pull_model(self, model_name: str) -> bool:
        """Descarga modelo (via docker exec o CLI directo)"""

    def list_models(self) -> List[str]:
        """Lista modelos disponibles"""

    def remove_model(self, model_name: str) -> bool:
        """Elimina modelo"""

    def stop_model(self, model_name: str) -> bool:
        """Detiene modelo cargado (libera VRAM)"""

    def test_model(self, model_name: str) -> Dict[str, Any]:
        """Test básico de funcionamiento"""

    def get_running_models(self) -> List[str]:
        """Modelos actualmente cargados en memoria"""

    def get_vram_usage(self) -> Dict[str, float]:
        """Uso de VRAM por modelo"""
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
- **Actualizaciones automáticas**: Detección y aplicación de updates de modelos

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
├── config/                 # 📁 Configuración externa
│   ├── models.yml         # Modelos disponibles
│   └── app.yml           # Configuración de aplicación
├── lib/                   # 📁 Código fuente
│   ├── main.py           # Entry point principal
│   ├── cli.py            # Interfaz CLI simplificada
│   ├── config_manager.py # Gestión de configuración YAML
│   └── ollama_manager.py # Cliente directo Ollama
├── specs/                # 📁 Documentación técnica
├── requirements.txt      # Dependencias Python
└── README.md            # Documentación usuario
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