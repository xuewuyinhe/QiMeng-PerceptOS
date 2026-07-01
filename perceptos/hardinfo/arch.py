#!/usr/bin/env python3
import os
import re
import platform
import psutil


def cpu_info() -> dict:
    info = {
        "arch": platform.machine(),
        "cores_physical": psutil.cpu_count(logical=False),
        "cores_logical": psutil.cpu_count(logical=True),
    }
    freq = psutil.cpu_freq()
    info["freq_MHz"] = round(freq.current, 1) if freq else "N/A"
    with open("/proc/cpuinfo") as f:
        m = re.search(r"model name\s*:\s*(.+)", f.read())
        info["model"] = m.group(1).strip() if m else "Unknown"
    return info


def mem_info() -> dict:
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    gb = 1024 ** 3
    return {
        "total_GB": round(vm.total / gb, 2),
        "available_GB": round(vm.available / gb, 2),
        "swap_GB": round(sm.total / gb, 2),
    }


def cache_info() -> dict:
    caches = {}
    cache_dir = "/sys/devices/system/cpu/cpu0/cache"
    if os.path.isdir(cache_dir):
        for entry in os.listdir(cache_dir):
            if entry.startswith("index"):
                level = open(f"{cache_dir}/{entry}/level").read().strip()
                ctype = open(f"{cache_dir}/{entry}/type").read().strip()   
                size  = open(f"{cache_dir}/{entry}/size").read().strip()  
                caches[f"L{level}_{ctype}"] = size
    return caches or {"note": "cache info not found"}


def fs_info() -> list:
    return [
        {
            "device": p.device,
            "mountpoint": p.mountpoint,
            "fstype": p.fstype,
        }
        for p in psutil.disk_partitions(all=False)
    ]

def get_arch() -> str:
    lines = []

    lines.append("=== CPU ===")
    for k, v in cpu_info().items():
        lines.append(f"{k:15}: {v}")

    lines.append("\n=== Memory (GB) ===")
    for k, v in mem_info().items():
        lines.append(f"{k:15}: {v}")

    lines.append("\n=== Cache ===")
    for k, v in cache_info().items():
        lines.append(f"{k:15}: {v}")

    lines.append("\n=== File-systems ===")
    for d in fs_info():
        lines.append(f"{d['mountpoint']:20} {d['fstype']:8} {d['device']}")

    return "\n".join(lines)


if __name__ == '__main__':
     print(get_arch())
