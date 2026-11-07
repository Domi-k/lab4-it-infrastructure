"""ЛР1. Мониторинг нагрузки с порогами и журналом в CSV (Вариант 2)."""
import csv
import time
from datetime import datetime

import psutil

INTERVAL = 2  # секунд между замерами
SAMPLES = 20  # количество замеров
THRESHOLDS = {"cpu": 75, "ram": 85, "disk": 90}
LOG_FILE = "monitor_log.csv"


def take_sample():
    swap_val = psutil.swap_memory().percent
    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "swap": swap_val,
    }


def check_alerts(sample):
    alerts = []
    for metric, limit in THRESHOLDS.items():
        if sample[metric] >= limit:
            alerts.append(f"{metric.upper()} = {sample[metric]}% (порог {limit}%)")
    return alerts


def main():
    psutil.cpu_percent(interval=None)  # «прогреваем» счетчик CPU

    samples_data = []

    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["time", "cpu", "ram", "disk", "swap", "alert"])
        writer.writeheader()

        for _ in range(SAMPLES):
            time.sleep(INTERVAL)
            s = take_sample()
            alerts = check_alerts(s)
            s["alert"] = "; ".join(alerts)
            writer.writerow(s)
            samples_data.append(s)

            mark = "  <-- ВНИМАНИЕ: " + s["alert"] if alerts else ""
            print(
                f"{s['time']}  CPU {s['cpu']:5.1f}%  RAM {s['ram']:5.1f}%  DISK {s['disk']:5.1f}%  SWAP {s['swap']:5.1f}%{mark}")

    print(f"\nЖурнал сохранён в {LOG_FILE}")

    # Расчет и вывод среднего, максимума и минимума по метрикам
    if samples_data:
        cpu_vals = [d["cpu"] for d in samples_data]
        ram_vals = [d["ram"] for d in samples_data]
        disk_vals = [d["disk"] for d in samples_data]
        swap_vals = [d["swap"] for d in samples_data]

        print("\n--- Итоговая статистика мониторинга ---")
        print(
            f"CPU  -> Мин: {min(cpu_vals):.1f}%, Макс: {max(cpu_vals):.1f}%, Среднее: {sum(cpu_vals) / len(cpu_vals):.1f}%")
        print(
            f"RAM  -> Мин: {min(ram_vals):.1f}%, Макс: {max(ram_vals):.1f}%, Среднее: {sum(ram_vals) / len(ram_vals):.1f}%")
        print(
            f"DISK -> Мин: {min(disk_vals):.1f}%, Макс: {max(disk_vals):.1f}%, Среднее: {sum(disk_vals) / len(disk_vals):.1f}%")
        print(
            f"SWAP -> Мин: {min(swap_vals):.1f}%, Макс: {max(swap_vals):.1f}%, Среднее: {sum(swap_vals) / len(swap_vals):.1f}%")


if __name__ == "__main__":
    main()