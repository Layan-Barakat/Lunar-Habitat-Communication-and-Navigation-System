# Lunar Habitat Communication and Navigation System 🛰️

This project simulates a communication and navigation network for a lunar habitat.
It includes encrypted transmission, Hamming (12,8) error correction, GNSS-style positioning with beacons, packet loss and latency simulation, and an emergency system for astronauts and rovers.

## Features
- XOR encryption (key = 23)
- Parity + checksum + Hamming (12,8) error handling
- GNSS-style positioning via virtual beacons
- Simulated rover/astronaut movement
- Emergency alerts and transmission logging (latency, attempts, status)

## Files
- `Comms system trial-Layan.py` — main communication simulation
- `GNSS_Symulation.py` — GNSS positioning + rover/astronaut movement

## How to Run
1) Run `Comms system trial-Layan.py`
2) Pick a sender (Astronaut 1–4)
3) Type a message or commands like `emergency`, `encryption`, `positions`, `log`

## Example Log
[2025-04-30 19:12:58] Message 4 by Astronaut-2 at (32.4, -18.6): Success after 5 attempt(s) | Encrypted: True | Emergency: False | Latency: 6.4s

**Author:** Layan Barakat — University of Birmingham Dubai
