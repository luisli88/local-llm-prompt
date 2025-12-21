#!/usr/bin/env python3
"""
LLM Stack Manager - Arquitectura Local Nativa
Gestión simplificada de modelos Ollama para RTX 2070 SUPER

Uso:
    python main.py              # Inicia interfaz interactiva
    python main.py --help       # Muestra ayuda
"""

import sys
from pathlib import Path
import subprocess

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from config_manager import config_manager
from ollama_manager import ollama_manager


class LLMStackApp:
    """Aplicación principal para gestión del stack LLM local."""

    def __init__(self):
        self.console = Console()

    def run(self):
        """Ejecuta el bucle principal de la aplicación."""
        while True:
            self._clear_screen()
            self._show_header()
            self._validate_dependencies()
            self._show_menu()

            choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5", "6", "7", "8", "0"])

            if choice == "0":
                self._print_success("¡Hasta luego!")
                break
            elif choice == "1":
                self._validate_installation()
            elif choice == "2":
                self._install_dependencies()
            elif choice == "3":
                self._activate_model()
            elif choice == "4":
                self._deactivate_model()
            elif choice == "5":
                self._update_models()
            elif choice == "6":
                self._check_updates()
            elif choice == "7":
                self._show_status()
            elif choice == "8":
                self._show_config()

            if choice != "0":
                self._wait_for_continue()

    def _clear_screen(self):
        """Limpia la pantalla."""
        self.console.clear()

    def _show_header(self):
        """Muestra el encabezado de la aplicación."""
        header = Panel.fit(
            "[bold blue]🤖 LLM Stack Manager v0.0.1 - Local Native[/bold blue]\n"
            "[dim]Arquitectura simplificada para RTX 2070 SUPER[/dim]",
            border_style="blue"
        )
        self.console.print(header)
        self.console.print()

    def _validate_dependencies(self):
        """Valida las dependencias del sistema."""
        self.console.print("[bold]Validando Dependencias[/bold]")

        # Verificar Python
        self._print_success(f"Python: {sys.version.split()[0]}")

        # Verificar dependencias Python esenciales (pyyaml se instala automáticamente)
        required_packages = ['rich', 'requests']
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self._print_error(f"Dependencias faltantes: {', '.join(missing_packages)}")
            self._print_info("Usa opción 2 para instalar automáticamente")
        else:
            self._print_success("Dependencias Python: OK")

        # Verificar Ollama
        if ollama_manager.check_ollama_installed():
            self._print_success("Ollama: OK")
        else:
            self._print_error("Ollama: NO instalado")
            self._print_info("Usa opción 2 para instalar automáticamente")

        # Verificar configuración
        errors = config_manager.validate_config()
        if errors:
            self._print_warning("Configuración: Advertencias")
            for error in errors:
                self._print_info(f"  • {error}")
        else:
            self._print_success("Configuración: OK")

        self.console.print()

    def _show_menu(self):
        """Muestra el menú principal."""
        self.console.print("[bold]Menú Principal:[/bold]")
        self.console.print("  1. 🔍 Validar Instalación Completa")
        self.console.print("  2. 📦 Instalar Dependencias")
        self.console.print("  3. 🟢 Activar Modelo")
        self.console.print("  4. 🛑 Desactivar Modelo")
        self.console.print("  5. 📥 Actualizar Modelos")
        self.console.print("  6. 🔄 Verificar Actualizaciones")
        self.console.print("  7. � Estado del Sistema")
        self.console.print("  8. ⚙️  Configuración")
        self.console.print("  0. 🚪 Salir")
        self.console.print()

    def _validate_installation(self):
        """Valida la instalación completa."""
        self.console.print("[bold]🔍 Validando Instalación Completa[/bold]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Verificando componentes...", total=100)

            # Verificar Python
            progress.update(task, advance=20, description="Python: OK")

            # Verificar dependencias (pyyaml se instala automáticamente)
            required_packages = ['rich', 'requests']
            missing = []
            for package in required_packages:
                try:
                    __import__(package.replace('-', '_'))
                except ImportError:
                    missing.append(package)

            if missing:
                progress.update(task, advance=20, description=f"Dependencias: FALTAN ({len(missing)})")
                self._print_error(f"Dependencias faltantes: {', '.join(missing)}")
                return
            else:
                progress.update(task, advance=20, description="Dependencias: OK")

            # Verificar Ollama
            if ollama_manager.check_ollama_installed():
                progress.update(task, advance=20, description="Ollama: OK")
            else:
                progress.update(task, advance=20, description="Ollama: FALTA")
                self._print_error("Ollama no está instalado")
                return

            # Verificar configuración
            errors = config_manager.validate_config()
            if errors:
                progress.update(task, advance=20, description="Configuración: ADVERTENCIAS")
                self._print_warning("Configuración tiene advertencias")
            else:
                progress.update(task, advance=20, description="Configuración: OK")

            # Verificar servicio Ollama
            if ollama_manager.check_ollama_running():
                progress.update(task, advance=20, description="Servicio Ollama: ACTIVO")
            else:
                progress.update(task, advance=20, description="Servicio Ollama: INACTIVO")

        self._print_success("✅ Validación completa - Sistema listo!")

    def _install_dependencies(self):
        """Instala dependencias automáticamente."""
        self.console.print("[bold]📦 Instalando Dependencias[/bold]")

        # Menú de instalación
        self.console.print("Selecciona qué instalar:")
        self.console.print("  1. Todas las dependencias (recomendado)")
        self.console.print("  2. Solo dependencias Python")
        self.console.print("  3. Solo Ollama")
        self.console.print("  4. Solo entorno virtual")
        self.console.print()

        choice = Prompt.ask("Opción", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            self._install_all_dependencies()
        elif choice == "2":
            self._install_python_deps()
        elif choice == "3":
            self._install_ollama()
        elif choice == "4":
            self._create_venv()

    def _install_all_dependencies(self):
        """Instala todas las dependencias."""
        self.console.print("🚀 Instalando todas las dependencias...")

        steps = [
            ("Creando entorno virtual", self._create_venv),
            ("Instalando dependencias Python", self._install_python_deps),
            ("Instalando Ollama", self._install_ollama),
        ]

        for step_name, step_func in steps:
            self.console.print(f"📋 {step_name}...")
            if not step_func():
                self._print_error(f"Error en: {step_name}")
                return
            self._print_success(f"{step_name} completado")

        self._print_success("🎉 ¡Todas las dependencias instaladas!")

    def _create_venv(self):
        """Crea entorno virtual."""
        if Path('.venv').exists():
            self._print_info("Entorno virtual ya existe")
            return True

        try:
            result = subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
            self._print_success("Entorno virtual creado en .venv/")
            return True
        except subprocess.CalledProcessError as e:
            self._print_error(f"Error creando venv: {e}")
            return False

    def _install_python_deps(self):
        """Instala dependencias Python."""
        pip_cmd = '.venv/bin/pip' if Path('.venv/bin/pip').exists() else sys.executable

        try:
            result = subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
            self._print_success("Dependencias Python instaladas")
            return True
        except subprocess.CalledProcessError as e:
            self._print_error(f"Error instalando dependencias: {e}")
            return False

    def _install_ollama(self):
        """Instala Ollama."""
        if ollama_manager.check_ollama_installed():
            self._print_info("Ollama ya está instalado")
            return True

        self.console.print("📥 Descargando e instalando Ollama...")

        try:
            # Descargar script de instalación
            result = subprocess.run([
                'curl', '-fsSL', 'https://ollama.com/install.sh'
            ], capture_output=True, text=True, check=True)

            # Ejecutar script
            result2 = subprocess.run(['sh', '-c', result.stdout], check=True)

            self._print_success("Ollama instalado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            self._print_error(f"Error instalando Ollama: {e}")
            return False

    def _activate_model(self):
        """Activa un modelo."""
        self.console.print("[bold]🟢 Activando Modelo[/bold]")

        models = config_manager.get_models_list()

        if not models:
            self._print_error("No hay modelos configurados")
            return

        # Mostrar modelos disponibles
        table = Table(title="Modelos disponibles")
        table.add_column("N°", style="cyan", no_wrap=True)
        table.add_column("Modelo", style="green")
        table.add_column("Estado", style="magenta", justify="center")

        running_models = ollama_manager.get_running_models()

        for i, model in enumerate(models, 1):
            status = "🟢 Activo" if model.name in running_models else "⚪ Inactivo"
            table.add_row(str(i), model.name, status)

        self.console.print(table)
        self.console.print()

        choices = [str(i) for i in range(1, len(models) + 1)]
        choice = Prompt.ask("Selecciona modelo para activar", choices=choices)

        try:
            index = int(choice) - 1
            selected_model = models[index]

            with self.console.status(f"Activando {selected_model.name}..."):
                success = ollama_manager.smart_activate_model(list(config_manager.get_models().keys())[index])

            if success:
                self._print_success(f"✅ {selected_model.name} activado exitosamente")
            else:
                self._print_error(f"❌ Error activando {selected_model.name}")

        except (ValueError, IndexError):
            self._print_error("Selección inválida")

    def _deactivate_model(self):
        """Desactiva un modelo."""
        self.console.print("[bold]🛑 Desactivando Modelo[/bold]")

        running = ollama_manager.get_running_models()
        if not running:
            self._print_warning("No hay modelos activos")
            return

        # Mostrar modelos activos
        table = Table(title="Modelos activos")
        table.add_column("N°", style="cyan", no_wrap=True)
        table.add_column("Modelo", style="green")

        for i, model_name in enumerate(running, 1):
            table.add_row(str(i), model_name)

        self.console.print(table)
        self.console.print()

        choices = [str(i) for i in range(1, len(running) + 1)]
        choice = Prompt.ask("Selecciona modelo para desactivar", choices=choices)

        try:
            index = int(choice) - 1
            model_name = running[index]

            with self.console.status(f"Desactivando {model_name}..."):
                success = ollama_manager.stop_model(model_name)

            if success:
                self._print_success(f"✅ {model_name} desactivado - VRAM liberada")
            else:
                self._print_error(f"❌ Error desactivando {model_name}")

        except (ValueError, IndexError):
            self._print_error("Selección inválida")

    def _check_updates(self):
        """Verifica y aplica actualizaciones de modelos."""
        self.console.print("[bold]🔄 Verificando Actualizaciones[/bold]")

        with self.console.status("[bold green]Consultando registry de Ollama...") as status:
            updates = ollama_manager.check_model_updates()

        if not updates:
            self._print_success("✅ Todos los modelos están actualizados")
            return

        # Mostrar actualizaciones disponibles
        self.console.print(f"📦 {len(updates)} actualizaciones disponibles:")
        self.console.print()

        updates_table = Table(title="Actualizaciones Disponibles")
        updates_table.add_column("Modelo Actual", style="cyan")
        updates_table.add_column("Nueva Versión", style="green")
        updates_table.add_column("Acción", style="yellow")

        for model_name, update_info in updates.items():
            updates_table.add_row(
                update_info["current"],
                update_info["latest"],
                "Pendiente"
            )

        self.console.print(updates_table)
        self.console.print()

        # Preguntar qué hacer
        self.console.print("Opciones:")
        self.console.print("  1. Actualizar todos los modelos")
        self.console.print("  2. Seleccionar modelos específicos")
        self.console.print("  3. Ver detalles de cambios")
        self.console.print("  0. Cancelar")
        self.console.print()

        choice = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "0"], default="0")

        if choice == "0":
            self._print_info("Operación cancelada")
            return

        elif choice == "1":
            # Actualizar todos
            if Confirm.ask(f"¿Actualizar {len(updates)} modelos?"):
                updated = 0
                for model_name, update_info in updates.items():
                    self.console.print(f"📥 Actualizando {update_info['current']}...")
                    if ollama_manager.update_model_if_available(update_info["current"]):
                        updated += 1
                    else:
                        self._print_error(f"❌ Error actualizando {update_info['current']}")

                self._print_success(f"✅ {updated}/{len(updates)} modelos actualizados")

        elif choice == "2":
            # Seleccionar específicos
            self.console.print("Modelos disponibles para actualizar:")
            model_list = list(updates.keys())

            for i, model_name in enumerate(model_list, 1):
                update_info = updates[model_name]
                self.console.print(f"  {i}. {update_info['current']} → {update_info['latest']}")

            self.console.print()
            try:
                choice = Prompt.ask("Número del modelo", choices=[str(i) for i in range(1, len(model_list) + 1)])
                index = int(choice) - 1
                selected_model = model_list[index]
                update_info = updates[selected_model]

                if Confirm.ask(f"¿Actualizar {update_info['current']} → {update_info['latest']}?"):
                    if ollama_manager.update_model_if_available(update_info["current"]):
                        self._print_success("✅ Modelo actualizado exitosamente")
                    else:
                        self._print_error("❌ Error en la actualización")

            except (ValueError, IndexError):
                self._print_error("Selección inválida")

        elif choice == "3":
            # Ver detalles (por ahora solo mostrar info básica)
            self.console.print("ℹ️  Información de actualizaciones:")
            for model_name, update_info in updates.items():
                self.console.print(f"  • {update_info['base_name']}: {update_info['current']} → {update_info['latest']}")
            self.console.print()
            self._print_info("Las actualizaciones incluyen mejoras de rendimiento, corrección de bugs y nuevas características")

    def _update_models(self):
        """Actualiza modelos."""
        self.console.print("[bold]📥 Actualizando Modelos[/bold]")

        models = config_manager.get_models()

        if Confirm.ask("¿Actualizar todos los modelos instalados?"):
            updated = 0
            for key, model in models.items():
                self.console.print(f"📥 Actualizando {model.name}...")
                if ollama_manager.pull_model(model.name, show_progress=False):
                    self._print_success(f"✅ {model.name} actualizado")
                    updated += 1
                else:
                    self._print_error(f"❌ Error actualizando {model.name}")

            self._print_success(f"📊 {updated}/{len(models)} modelos actualizados")
        else:
            self._print_info("Operación cancelada")

    def _show_status(self):
        """Muestra estado detallado del sistema."""
        self.console.print("[bold]📊 Estado del Sistema[/bold]")

        status = ollama_manager.get_status_summary()
        vram = ollama_manager.get_vram_usage()

        # Panel de estado
        status_table = Table(title="Estado General")
        status_table.add_column("Componente", style="cyan")
        status_table.add_column("Estado", style="green")

        status_table.add_row("Servicio Ollama", "✅ Activo" if status["ollama_running"] else "❌ Inactivo")
        status_table.add_row("Modelos Instalados", f"📦 {status['models_installed']}")
        status_table.add_row("Modelos Cargados", f"🧠 {status['models_running']}")
        status_table.add_row("VRAM Usada", f"💾 {vram.used_vram} / {vram.total_vram}")

        if status["models_with_updates"] > 0:
            status_table.add_row("Actualizaciones", f"🔄 {status['models_with_updates']} disponibles")

        self.console.print(status_table)
        self.console.print()

        # Modelos cargados
        if status["running_models"]:
            running_panel = Panel(
                "\n".join(f"• {model}" for model in status["running_models"]),
                title="🟢 Modelos Activos",
                border_style="green"
            )
            self.console.print(running_panel)
            self.console.print()

        # Actualizaciones disponibles
        if status["available_updates"]:
            updates_list = []
            for model_name, update_info in status["available_updates"].items():
                updates_list.append(f"• {update_info['current']} → {update_info['latest']}")

            updates_panel = Panel(
                "\n".join(updates_list),
                title=f"🔄 {len(status['available_updates'])} Actualizaciones Disponibles",
                border_style="yellow"
            )
            self.console.print(updates_panel)

    def _show_config(self):
        """Muestra configuración actual."""
        self.console.print("[bold]⚙️ Configuración Actual[/bold]")

        config = config_manager.get_config()

        config_table = Table(title="Configuración del Sistema")
        config_table.add_column("Opción", style="cyan")
        config_table.add_column("Valor", style="green")

        config_table.add_row("Directorio configuración", str(config_manager.config_dir))
        config_table.add_row("Host Ollama", config.ollama_host)
        config_table.add_row("Máx modelos simultáneos", str(config.max_loaded_models))
        config_table.add_row("Auto-stop inactivo", str(config.auto_stop_inactive))
        config_table.add_row("Timeout inactivo (min)", str(config.inactive_timeout_minutes))

        self.console.print(config_table)
        self.console.print()

        # Modelos configurados
        models = config_manager.get_models_list()
        if models:
            models_table = Table(title="Modelos Configurados")
            models_table.add_column("Modelo", style="green")
            models_table.add_column("Descripción", style="white")

            for model in models:
                models_table.add_row(model.name, model.description)

            self.console.print(models_table)

    def _wait_for_continue(self):
        """Espera a que el usuario presione Enter."""
        self.console.print()
        Prompt.ask("Presiona Enter para continuar")

    def _print_success(self, message: str):
        """Imprime mensaje de éxito."""
        self.console.print(f"[green]✅ {message}[/green]")

    def _print_error(self, message: str):
        """Imprime mensaje de error."""
        self.console.print(f"[red]❌ {message}[/red]")

    def _print_warning(self, message: str):
        """Imprime mensaje de advertencia."""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")

    def _print_info(self, message: str):
        """Imprime mensaje informativo."""
        self.console.print(f"[cyan]ℹ {message}[/cyan]")


def show_welcome():
    """Muestra mensaje de bienvenida"""
    print("🤖 LLM Stack Manager v0.0.1 - Local Native")
    print("=======================================")
    print("Arquitectura simplificada para desarrollo local")
    print("• Ollama nativo (sin contenedores)")
    print("• RTX 2070 SUPER optimizado")
    print("• Gestión inteligente de VRAM")
    print()


def main():
    """Función principal."""
    try:
        app = LLMStackApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()