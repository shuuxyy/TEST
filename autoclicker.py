#!/usr/bin/env python3
"""Simple Windows autoclicker using ctypes."""
from __future__ import annotations

import argparse
import platform
import threading
import time
from dataclasses import dataclass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Windows-Autoclicker per Kommandozeile."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.1,
        help="Sekunden zwischen Klicks (Standard: 0.1)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Anzahl der Klicks (0 = unendlich)",
    )
    parser.add_argument(
        "--button",
        choices=("left", "right"),
        default="left",
        help="Maustaste (left/right)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Startverzögerung in Sekunden (Standard: 3.0)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Overlay öffnen, um Klicks interaktiv zu konfigurieren.",
    )
    return parser


@dataclass
class ClickConfig:
    interval_ms: int
    count: int
    button: str
    delay_s: float = 0.0


def validate_config(config: ClickConfig) -> None:
    if config.interval_ms <= 0:
        raise ValueError("Interval muss größer als 0 sein.")

    if config.delay_s < 0:
        raise ValueError("Delay darf nicht negativ sein.")

    if config.count < 0:
        raise ValueError("Count darf nicht negativ sein.")


def validate_config_cli(config: ClickConfig, parser: argparse.ArgumentParser) -> None:
    try:
        validate_config(config)
    except ValueError as exc:
        parser.error(str(exc))


def resolve_flags(button: str) -> tuple[int, int]:
    # Windows API constants
    left_down = 0x0002
    left_up = 0x0004
    right_down = 0x0008
    right_up = 0x0010

    if button == "left":
        return left_down, left_up
    return right_down, right_up


def run_click_loop(
    config: ClickConfig,
    stop_event: threading.Event | None = None,
) -> None:
    import ctypes  # noqa: WPS433 - Windows-only dependency

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    down_flag, up_flag = resolve_flags(config.button)
    interval_s = config.interval_ms / 1000.0

    if config.delay_s:
        time.sleep(config.delay_s)

    clicks_done = 0
    while config.count == 0 or clicks_done < config.count:
        if stop_event and stop_event.is_set():
            break
        user32.mouse_event(down_flag, 0, 0, 0, 0)
        user32.mouse_event(up_flag, 0, 0, 0, 0)
        clicks_done += 1
        time.sleep(interval_s)


def run_cli(config: ClickConfig) -> None:
    print(
        "Autoclicker startet in "
        f"{config.delay_s:.2f}s (Stop mit Strg+C)..."
    )
    try:
        run_click_loop(config)
    except KeyboardInterrupt:
        print("Autoclicker gestoppt.")


def run_gui(parser: argparse.ArgumentParser) -> None:
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Autoclicker Overlay")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    interval_var = tk.StringVar(value="100")
    count_var = tk.StringVar(value="0")
    button_var = tk.StringVar(value="left")

    status_var = tk.StringVar(value="Bereit")
    stop_event = threading.Event()
    worker: threading.Thread | None = None

    def set_status(text: str) -> None:
        status_var.set(text)

    def build_config() -> ClickConfig | None:
        try:
            interval_ms = int(interval_var.get())
            count = int(count_var.get())
        except ValueError:
            set_status("Bitte gültige Zahlen eingeben.")
            return None

        config = ClickConfig(
            interval_ms=interval_ms,
            count=count,
            button=button_var.get(),
            delay_s=0.0,
        )
        try:
            validate_config(config)
        except ValueError as exc:
            set_status(str(exc))
            return None
        return config

    def start_clicking() -> None:
        nonlocal worker
        if worker and worker.is_alive():
            set_status("Autoclicker läuft bereits.")
            return

        config = build_config()
        if not config:
            return

        stop_event.clear()
        set_status("Läuft...")
        worker = threading.Thread(
            target=run_click_loop,
            args=(config, stop_event),
            daemon=True,
        )
        worker.start()

    def stop_clicking() -> None:
        stop_event.set()
        set_status("Gestoppt")

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frame, text="Clicks (0 = unendlich)").grid(
        row=0, column=0, sticky="w"
    )
    ttk.Entry(frame, textvariable=count_var, width=12).grid(
        row=0, column=1, padx=(8, 0)
    )

    ttk.Label(frame, text="Abstand (ms)").grid(
        row=1, column=0, sticky="w", pady=(6, 0)
    )
    ttk.Entry(frame, textvariable=interval_var, width=12).grid(
        row=1, column=1, padx=(8, 0), pady=(6, 0)
    )

    ttk.Label(frame, text="Taste").grid(
        row=2, column=0, sticky="w", pady=(6, 0)
    )
    ttk.OptionMenu(frame, button_var, button_var.get(), "left", "right").grid(
        row=2, column=1, padx=(8, 0), pady=(6, 0), sticky="ew"
    )

    button_row = ttk.Frame(frame)
    button_row.grid(row=3, column=0, columnspan=2, pady=(10, 0))
    ttk.Button(button_row, text="Start", command=start_clicking).grid(
        row=0, column=0, padx=(0, 6)
    )
    ttk.Button(button_row, text="Stop", command=stop_clicking).grid(
        row=0, column=1
    )

    ttk.Label(frame, textvariable=status_var).grid(
        row=4, column=0, columnspan=2, pady=(8, 0), sticky="w"
    )

    root.mainloop()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if platform.system() != "Windows":
        parser.error("Dieses Skript unterstützt nur Windows.")

    config = ClickConfig(
        interval_ms=int(args.interval * 1000),
        count=args.count,
        button=args.button,
        delay_s=args.delay,
    )
    validate_config_cli(config, parser)

    if args.gui:
        run_gui(parser)
        return 0

    run_cli(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
