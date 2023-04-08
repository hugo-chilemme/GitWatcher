#!/usr/bin/python3
import threading


def setTimeout(func, temps):
    e = threading.Event()
    e.wait(temps/1000)
    func()
