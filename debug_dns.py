import socket
import requests
import os

domain = "notify-api.line.me"

print(f"Resolving {domain}...")
try:
    ip = socket.gethostbyname(domain)
    print(f"Resolved to: {ip}")
except Exception as e:
    print(f"Failed to resolve: {e}")

print("Resolving notify-bot.line.me...")
try:
    ip = socket.gethostbyname("notify-bot.line.me")
    print(f"Resolved to: {ip}")
except:
    pass
