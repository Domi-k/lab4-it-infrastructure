"""ЛР1. Автоматическая инвентаризация компьютера."""
import json
import platform
import socket
from datetime import datetime

import psutil


def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M"),
    }


def get_cpu_info():
    freq = psutil.cpu_freq()
    return {
        "model": platform.processor(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "max_freq_mhz": round(freq.max) if freq else None,
        "load_percent": psutil.cpu_percent(interval=1),
    }


def get_memory_info():
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / 1024 ** 3, 1),
        "used_percent": mem.percent,
        "available_gb": round(mem.available / 1024 ** 3, 1),
    }


def get_disk_info():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        disks.append({
            "device": part.device,
            "mountpoint": part.mountpoint,
            "fs": part.fstype,
            "total_gb": round(usage.total / 1024 ** 3, 1),
            "used_percent": usage.percent,
        })
    return disks


def get_network_info():
    """Задание 2: Сбор сетевых интерфейсов (имя, IPv4, маска, MAC)."""
    interfaces = {}
    net_addrs = psutil.net_if_addrs()

    for name, addrs in net_addrs.items():
        ipv4_addr = None
        netmask = None
        mac_addr = None

        for a in addrs:
            if a.family == socket.AF_INET:  # IPv4
                ipv4_addr = a.address
                netmask = a.netmask
            elif a.family == psutil.AF_LINK:  # MAC-адрес
                mac_addr = a.address

        # Пропускаем интерфейсы без IPv4
        if ipv4_addr:
            interfaces[name] = {
                "ipv4": ipv4_addr,
                "netmask": netmask,
                "mac": mac_addr
            }
    return interfaces


def analyze(passport):
    """Задание 3: Автоматический анализ паспорта и генерация рекомендаций."""
    recommendations = []

    ram_gb = passport["memory"]["total_gb"]
    phys_cores = passport["cpu"]["physical_cores"]

    # Правило 1
    if ram_gb < 8:
        recommendations.append("Недостаточно памяти для виртуальных машин и Docker")

    # Правило 2
    if ram_gb >= 16 and phys_cores >= 6:
        recommendations.append("Подходит для одновременной работы нескольких VM")

    # Правило 3
    for disk in passport["disks"]:
        if disk["used_percent"] > 85:
            recommendations.append(f"Освободить место на диске {disk['mountpoint']}")

    # Правило 4
    if phys_cores < 4:
        recommendations.append("Процессор может стать узким местом (bottleneck)")

    # Собственное правило (например, проверка загрузки CPU выше 80%)
    if passport["cpu"]["load_percent"] > 80:
        recommendations.append("Высокая текущая загрузка процессора")

    return recommendations


def main():
    passport = {
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system": get_system_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disks": get_disk_info(),
        "network": get_network_info(),
    }

    # Добавляем результаты анализа в паспорт
    passport["recommendations"] = analyze(passport)

    filename = f"passport_{passport['system']['hostname']}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(passport, f, indent=2, ensure_ascii=False)

    print(json.dumps(passport, indent=2, ensure_ascii=False))
    print(f"\nПаспорт сохранён в файл {filename}")


if __name__ == "__main__":
    main()