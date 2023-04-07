#!/usr/bin/python3
import threading


def setInterval(func, temps):
    e = threading.Event()
    while not e.wait(temps/1000):
        func()
