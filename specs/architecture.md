# Arquitectura del Stack (Docker + Ollama + GPU + SQLite)

```mermaid
graph TB
    subgraph "Host Ubuntu 25.10"
        A[NVIDIA Driver<br/>580.95 + CUDA 13.0]
        B[Docker Engine<br/>+ NVIDIA Container Toolkit]
        C[RTX 2070 SUPER<br/>8GB VRAM]
    end

    subgraph "Interfaz de Usuario"
        D[Terminal App<br/>main.sh / main.py]
        E[Scripts Ocultos<br/>.scripts/]
    end

    subgraph "Base de Datos Local"
        L[SQLite Database<br/>.models.db<br/>Estado + Versiones]
    end

    subgraph "Contenedores Ollama (puertos 11434-11436)"
        F[Ollama Qwen<br/>11434: Code Completion]
        G[Ollama DeepSeek<br/>11435: Technical Reasoning]
        H[Ollama Mistral<br/>11436: Docs/Architecture]
        I[llama.cpp backend<br/>CUDA acceleration]
    end

    subgraph "Integraciones Desarrollo"
        J[VSCode + Kilo Code<br/>OpenAI API Client]
        K[CLI Tools<br/>ollama CLI]
    end

    D -->|Valida dependencias| A
    D -->|Gestiona contenedores| F
    D -->|Gestiona contenedores| G
    D -->|Gestiona contenedores| H
    D -->|Sincroniza estado| L
    E -->|Automatización| B
    A -->|GPU Runtime| B
    B -.->|--gpus all| F
    B -.->|--gpus all| G
    B -.->|--gpus all| H
    C -->|VRAM + Compute| I
    L -->|Estado modelos| D
    F -->|HTTP API| J
    G -->|HTTP API| J
    H -->|HTTP API| J
    F -->|CLI| K
    G -->|CLI| K
    H -->|CLI| K

    style A fill:#e1f5fe
    style C fill:#fff3e0
    style D fill:#c8e6c9
    style L fill:#fff9c4
    style F fill:#e8f5e8
    style G fill:#e8f5e8
    style H fill:#e8f5e8
```

## Componentes Actualizados

### 🗄️ Base de Datos SQLite (.models.db)
- **Propósito**: Persistencia del estado de modelos y versiones instaladas
- **Esquema**:
  ```sql
  CREATE TABLE models (
      name TEXT PRIMARY KEY,
      container_name TEXT,
      port INTEGER,
      installed_version TEXT,
      status TEXT DEFAULT 'inactive',
      last_updated TEXT
  );
  ```
- **Funciones**:
  - Sincronización automática con estado real de contenedores
  - Tracking de versiones instaladas
  - Estado activo/inactivo por modelo

### 🔄 Sincronización de Estado
- **Mecanismo**: Consulta directa a Docker API para verificar contenedores activos
- **Frecuencia**: Automática en cada visualización del menú principal
- **Beneficios**: Información siempre actualizada sin intervención manual

### 📦 Scripts Ocultos (.scripts/)
- **model_manager.sh**: Gestión de base de datos y estados
- **setup.sh**: Instalación inicial del stack
- **verify-install.sh**: Validación de dependencias y configuración

### 🚀 Funcionalidades Avanzadas
- **Actualización de Modelos**: Pull automático desde Ollama registry
- **Gestión de Estado**: Activación/desactivación individual por modelo
- **Validación Automática**: Verificación de dependencias al inicio
- **Interfaz Mejorada**: Menú interactivo con indicadores visuales

---

## ✅ Estado de Implementación v2.0.0

### 🎯 Migración Completada: Bash → Python

Se ha completado exitosamente la migración de la aplicación de gestión de stack LLM de Bash a Python, proporcionando una solución más robusta, mantenible y precisa.

#### 📦 Entregables Completados

**Aplicación Python Completa** (`main.py`)
- ✅ Interfaz CLI moderna con Rich
- ✅ Gestión inteligente de estado de contenedores
- ✅ Sincronización automática con base de datos
- ✅ Validación robusta de dependencias
- ✅ Funcionalidad completa de gestión de modelos

**Arquitectura Modular** (`lib/`)
- ✅ `DockerManager`: API nativa de Docker
- ✅ `ModelManager`: Gestión SQLite con SQLAlchemy
- ✅ `OllamaClient`: Cliente para operaciones con modelos
- ✅ `Config`: Configuración centralizada
- ✅ `Utils`: Utilidades del sistema

**Base de Datos SQLite**
- ✅ Esquema completo para modelos
- ✅ Sincronización automática DB ↔ Docker
- ✅ Tracking de versiones y estados
- ✅ Persistencia de configuraciones

**Suite de Pruebas Completa** (`lib/tests.py`)
- ✅ 13 pruebas unitarias pasando
- ✅ Cobertura de componentes principales
- ✅ Mocks para APIs externas
- ✅ Tests de integración

#### 🔄 Mejoras Obtenidas

**Precisión Mejorada**
- APIs nativas de Docker vs parsing de comandos CLI
- Estado preciso de contenedores y modelos
- Validación automática de conectividad HTTP

**Robustez Superior**
- Manejo avanzado de errores y recuperación automática
- Excepciones específicas y logging detallado
- Validación de dependencias al inicio

**Mantenibilidad**
- Arquitectura modular y testable
- Código Python moderno con type hints
- Separación clara de responsabilidades

**Experiencia de Usuario**
- Interfaz moderna con Rich (colores, tablas, progreso)
- Menú interactivo con navegación fluida
- Mensajes informativos y estados visuales

#### 🧪 Validación Final
- ✅ **13/13 pruebas unitarias pasan**
- ✅ **Funcionalidad completa verificada**
- ✅ **Interfaz moderna implementada**
- ✅ **Sincronización automática DB ↔ Docker**

**Estado: COMPLETAMENTE FUNCIONAL** 🚀

