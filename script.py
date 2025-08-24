"""
TP Redes Integrador + Netmiko
Script de automatización de configuración y verificación de red segmentada
Autor: Luciano Joaquín Toledo

Descripción:
Este script automatiza la configuración de VLANs, trunk, NAT, DHCP y realiza verificaciones en switches Cisco y routers MikroTik. 
Marca los cambios realizados, indica errores en comandos y documenta las acciones realizadas en consola y en el archivo netmiko_log.txt.

Actualización 2024:
- Parche para switches Cisco antiguos: fuerza algoritmos SSH legacy en Paramiko para compatibilidad con dispositivos que solo ofrecen diffie-hellman-group14-sha1.
- Recomendación: Usar Netmiko >=4.x y Paramiko >=3.x. Si sigue fallando, este parche lo soluciona.
"""

from netmiko import ConnectHandler
from datetime import datetime

# --- Parche Paramiko para switches Cisco con SSH legacy ---
import paramiko
paramiko.transport.Transport._preferred_kex = (
    'diffie-hellman-group14-sha1',
    'diffie-hellman-group-exchange-sha1',
    'diffie-hellman-group1-sha1',
)
paramiko.transport.Transport._preferred_keys = (
    'ssh-rsa',
)

# ---- Parámetros globales ----
SWITCH_USER = "netadmin"
SWITCH_PASS_PRINCIPAL = "P4ssw0rdNet"
SWITCH_SECRET_PRINCIPAL = "P4ssw0rdNet"
SWITCH_PASS_REMOTO = "P4ssw0rdNet"
SWITCH_SECRET_REMOTO = "P4ssw0rdNet"
ROUTER_USER = "admin"
ROUTER_PASS = "admin"

LOG_FILE = "netmiko_log.txt"

switches = [
    {
        'device_type': 'cisco_ios',
        'ip': '10.10.18.57',
        'username': SWITCH_USER,
        'password': SWITCH_PASS_PRINCIPAL,
        'secret': SWITCH_SECRET_PRINCIPAL,
        'allow_agent': False,
        'use_keys': False,
    },
    {
        'device_type': 'cisco_ios',
        'ip': '10.10.18.58',
        'username': SWITCH_USER,
        'password': SWITCH_PASS_REMOTO,
        'secret': SWITCH_SECRET_REMOTO,
        'allow_agent': False,
        'use_keys': False,
    }
]

routers = [
    {
        'device_type': 'mikrotik_routeros',
        'ip': '10.10.18.59',  # MikroTik Principal
        'username': ROUTER_USER,
        'password': ROUTER_PASS,
    },
    {
        'device_type': 'mikrotik_routeros',
        'ip': '10.10.18.60',  # MikroTik Remoto
        'username': ROUTER_USER,
        'password': ROUTER_PASS,
    }
]

vlans = [
    {'id': 290, 'name': 'Ventas', 'ports': ['e0/1']},
    {'id': 291, 'name': 'Tecnica', 'ports': ['e0/2']},
    {'id': 292, 'name': 'Visitantes', 'ports': ['e0/3']}
]
TRUNK_IF = "e0/0"
ALLOWED_VLANS = [str(v['id']) for v in vlans] + ["1899"]

def log_event(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {event}\n")

def ejecutar_comandos(conn, comandos, device_ip):
    cambios = []
    errores = []
    for cmd in comandos:
        try:
            resultado = conn.send_config_set([cmd])
            if "Invalid input" in resultado or "Error" in resultado:
                errores.append((cmd, resultado.strip()))
                log_event(f"ERROR en {device_ip}: {cmd} -> {resultado.strip()}")
            else:
                cambios.append((cmd, resultado.strip()))
                log_event(f"OK en {device_ip}: {cmd} -> {resultado.strip()}")
        except Exception as e:
            errores.append((cmd, str(e)))
            log_event(f"EXCEPCIÓN en {device_ip}: {cmd} -> {str(e)}")
    return cambios, errores

def configurar_switch(switch):
    print(f"\n=== Configurando Switch {switch['ip']} ===")
    log_event(f"Inicio configuración Switch {switch['ip']}")
    try:
        conn = ConnectHandler(**switch)
        conn.enable()
        comandos = []
        # Crear y nombrar VLANs
        for vlan in vlans:
            comandos += [
                f"vlan {vlan['id']}",
                f"name {vlan['name']}"
            ]
        # Asignar puertos de acceso
        for vlan in vlans:
            for port in vlan['ports']:
                comandos += [
                    f"interface {port}",
                    "switchport mode access",
                    f"switchport access vlan {vlan['id']}",
                    "no shutdown"
                ]
        # Configurar trunk principal
        comandos += [
            f"interface {TRUNK_IF}",
            "switchport trunk encapsulation dot1q",
            "switchport mode trunk",
            f"switchport trunk allowed vlan {','.join(ALLOWED_VLANS)}",
            "no shutdown"
        ]
        cambios, errores = ejecutar_comandos(conn, comandos, switch['ip'])

        print("\n-- Cambios realizados --")
        for cmd, out in cambios:
            print(f"✔ {cmd}")

        if errores:
            print("\n-- Errores encontrados --")
            for cmd, err in errores:
                print(f"✘ {cmd} -> {err}")

        print("\n-- Verificación --")
        print(conn.send_command("show vlan brief"))
        print(conn.send_command("show interfaces trunk"))
        conn.disconnect()
        log_event(f"Fin configuración Switch {switch['ip']}")
    except Exception as e:
        print(f"!! Error al conectar con el switch {switch['ip']}: {str(e)}")
        log_event(f"ERROR de conexión Switch {switch['ip']}: {str(e)}")

def configurar_mikrotik(router):
    print(f"\n=== Configurando MikroTik {router['ip']} ===")
    log_event(f"Inicio configuración MikroTik {router['ip']}")
    try:
        conn = ConnectHandler(**router)
        comandos = [
            # Ventas
            '/interface vlan add name=Ventas vlan-id=290 interface=ether2',
            '/ip address add address=10.10.18.65/27 interface=Ventas',
            # Técnica
            '/interface vlan add name=Tecnica vlan-id=291 interface=ether2',
            '/ip address add address=10.10.18.97/28 interface=Tecnica',
            # Visitantes
            '/interface vlan add name=Visitantes vlan-id=292 interface=ether2',
            '/ip address add address=10.10.18.113/29 interface=Visitantes',
            # NAT solo para Ventas y Técnica
            '/ip firewall nat add chain=srcnat src-address=10.10.18.64/27 action=masquerade comment="NAT Ventas"',
            '/ip firewall nat add chain=srcnat src-address=10.10.18.96/28 action=masquerade comment="NAT Tecnica"',
            # DHCP para Ventas
            '/ip pool add name=pool_ventas ranges=10.10.18.66-10.10.18.94',
            '/ip dhcp-server add name=dhcp_ventas interface=Ventas address-pool=pool_ventas lease-time=1h disabled=no',
            '/ip dhcp-server network add address=10.10.18.64/27 gateway=10.10.18.65 dns-server=8.8.8.8',
        ]
        cambios = []
        errores = []
        for cmd in comandos:
            try:
                resultado = conn.send_command(cmd)
                if "failure" in resultado or "error" in resultado or "invalid" in resultado:
                    errores.append((cmd, resultado.strip()))
                    log_event(f"ERROR en {router['ip']}: {cmd} -> {resultado.strip()}")
                else:
                    cambios.append((cmd, resultado.strip()))
                    log_event(f"OK en {router['ip']}: {cmd} -> {resultado.strip()}")
            except Exception as e:
                errores.append((cmd, str(e)))
                log_event(f"EXCEPCIÓN en {router['ip']}: {cmd} -> {str(e)}")

        print("\n-- Cambios realizados --")
        for cmd, out in cambios:
            print(f"✔ {cmd}")

        if errores:
            print("\n-- Errores encontrados --")
            for cmd, err in errores:
                print(f"✘ {cmd} -> {err}")

        print("\n-- Verificación --")
        print(conn.send_command('/interface vlan print'))
        print(conn.send_command('/ip address print'))
        print(conn.send_command('/ip route print'))
        # Verificación específica de NAT en el MikroTik principal
        if router['ip'] == "10.10.18.59":
            print(conn.send_command('/ip firewall nat print'))
        conn.disconnect()
        log_event(f"Fin configuración MikroTik {router['ip']}")
    except Exception as e:
        print(f"!! Error al conectar con el router {router['ip']}: {str(e)}")
        log_event(f"ERROR de conexión MikroTik {router['ip']}: {str(e)}")

def main():
    print("=== Automatización de configuración de red ===")
    log_event("=== EJECUCIÓN GENERAL INICIADA ===")
    for sw in switches:
        configurar_switch(sw)
    for rt in routers:
        configurar_mikrotik(rt)
    log_event("=== EJECUCIÓN GENERAL FINALIZADA ===")

if __name__ == "__main__":
    main()
