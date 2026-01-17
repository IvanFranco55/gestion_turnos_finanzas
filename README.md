# 🦷 Sistema de Gestión para Consultorio Odontológico

Sistema integral desarrollado para la administración de turnos, pacientes y finanzas de un consultorio dental real. Diseñado para funcionar offline y desplegado mediante contenedores para fácil instalación.

## 🚀 Funcionalidades Principales
- **Gestión de Turnos:** Agenda interactiva con ordenamiento cronológico inteligente.
- **Historia Clínica:** ABM (Alta, Baja, Modificación) completo de pacientes y tratamientos.
- **Finanzas:** Control de ingresos y gastos del consultorio.
- **UX/UI:** Interfaz moderna con **Modo Oscuro** automático y persistente.
- **Seguridad:** Sistema de Login/Logout y usuarios administradores.

## 🛠 Tecnologías Utilizadas
- **Backend:** Python 3.11, Django 4.2.
- **Frontend:** HTML5, CSS3, Bootstrap 5 (Jinja2 Templates).
- **Infraestructura:** Docker & Docker Compose.
- **Base de Datos:** SQLite (Optimizado para uso local/monousuario).

## 📦 Instalación y Despliegue
El proyecto está dockerizado para un despliegue "One-Click".
```bash
docker-compose up -d
