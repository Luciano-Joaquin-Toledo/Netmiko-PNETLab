# 🚀 TP Redes Integrador + Netmiko

**Autor:** Luciano Joaquín Toledo  
**Proyecto:** Automatización profesional de red segmentada con Python, Netmiko y MikroTik

---

## 🌐 Descripción

Este proyecto es un **script de automatización** para la configuración y verificación de una red segmentada, integrando switches Cisco y routers MikroTik. Utiliza Python y la librería Netmiko para aplicar cambios en VLANs, trunks, NAT, DHCP y realizar verificaciones en los dispositivos de red.  
Cada acción queda documentada tanto en la consola como en el archivo de log `netmiko_log.txt`.

---

## ✨ Características destacadas

- **Automatización completa:** Configura VLANs, trunks, NAT y DHCP en múltiples switches y routers.
- **Compatibilidad con Cisco legacy:** Parche SSH para conectar con switches antiguos (algoritmos legacy).
- **Registro detallado:** Todos los cambios, errores y verificaciones quedan documentados en un log con timestamp.
- **Verificaciones post-configuración:** Muestra el estado real de VLANs, trunks, NAT, IP y rutas.
- **Código modular y personalizable:** Parámetros y comandos fácilmente editables.
- **Soporte multi-vendor:** Funciona tanto en MikroTik RouterOS como en Cisco IOS.

---

## 🏗️ Topología sugerida

```
+------------------+      Trunk      +------------------+
|   Cisco Switch   |-----------------|   Cisco Switch   |
|   Principal      |                 |   Remoto         |
+--------+---------+                 +--------+---------+
         |                                  |
         |                                  |
     +---v---+                          +---v---+
     | Mikrotik|                        | Mikrotik|
     | Router  |                        | Router  |
     +--------+                        +--------+
```

---

## 🛠️ Tecnologías y dependencias

- **Python >= 3.8**
- **Netmiko >= 4.x**
- **Paramiko >= 3.x**
- **Switches Cisco IOS**
- **Routers MikroTik RouterOS**

---

## 📦 Instalación

1. **Instala Python 3 si no lo tienes.**
2. **Instala dependencias:**
   ```sh
   pip install netmiko paramiko
   ```
3. **Verifica conectividad SSH** en todos los equipos.

---

## ⚡ Ejecución rápida

1. **Clona el repositorio o descarga el script.**
2. **Edita los parámetros de usuario, contraseñas, IP y VLAN en el script si es necesario.**
3. **Ejecuta:**
   ```sh
   python script.py
   ```
4. **Analiza la consola y el archivo `netmiko_log.txt` para detalles, errores y resultados.**

---

## 🔧 Parámetros clave

- **Usuarios y contraseñas:** Configurados al inicio del script, cambia según tu infraestructura.
- **Lista de dispositivos:** Agrega/quita switches y routers fácilmente en las listas `switches` y `routers`.
- **Comandos personalizados:** Configura VLANs, trunks, NAT y DHCP editando las listas del script.

---

## 🛡️ Compatibilidad con Cisco legacy

¿Tu switch Cisco arroja errores de SSH como este?

```
Unable to negotiate ... no matching key exchange method found ...
```

¡No te preocupes!  
El script incluye un **parche Paramiko** para aceptar algoritmos legacy SSH.  
No necesitas actualizar IOS, sólo ejecuta el script y conecta sin problemas.

---

## 📝 ¿Qué automatiza el script?

- **VLANs:** Crea y nombra VLANs en switches Cisco.
- **Trunks:** Configura trunk principal para transportar varias VLANs.
- **Puertos:** Asigna puertos de acceso a VLANs.
- **MikroTik:** Automatiza la creación de VLANs, direcciones IP, reglas NAT y DHCP server.
- **Verificación:** Muestra el estado real de VLANs, trunks, NAT y rutas en consola.

---

## 📊 Ejemplo de salida en consola

```
=== Automatización de configuración de red ===

=== Configurando Switch 10.10.18.57 ===
✔ vlan 290
✔ name Ventas
...
-- Verificación --
VLAN Name Status Ports
...
```

---

## 🔎 Troubleshooting & Preguntas frecuentes

### 🔄 ¿No conecta por SSH al switch Cisco?
- Verifica usuario/contraseña.
- Asegúrate de que SSH está habilitado y la clave RSA generada.
- El parche SSH legacy resuelve problemas de negociación.

### 🛠️ ¿Cómo agrego más dispositivos?
- Añade nuevos diccionarios a las listas `switches` o `routers` en el script.

### 📝 ¿Dónde veo el historial de cambios?
- En el archivo `netmiko_log.txt` con fecha y hora.

---

## 💡 Personalización y escalabilidad

- **Cambia nombres de VLANs, IDs y puertos** en la lista `vlans`.
- **Agrega comandos adicionales** para nuevas configuraciones.
- **Adapta el log y las verificaciones** según tus necesidades de auditoría.

---

## 🏅 Créditos y agradecimientos

- **Netmiko:** [GitHub](https://github.com/ktbyers/netmiko)
- **Paramiko:** [GitHub](https://github.com/paramiko/paramiko)
- **Cisco y MikroTik CLI Reference**

---

## 📬 Contacto

¿Consultas, sugerencias o mejoras?  
**Autor:** Luciano Joaquín Toledo  
**Mail:** [luciano.toledo@email.com](mailto:luciano.toledo@email.com)

---

## 📝 Licencia

Proyecto entregado para usos educativos, académicos y profesionales.  
¡Si te fue útil, compártelo y mejoralo!