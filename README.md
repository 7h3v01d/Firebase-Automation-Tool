# 🔥 Firebase Automation Tool (Archived)

A desktop GUI for running **Firebase CLI workflows without living in the terminal**.

This project is currently **on ice**, preserved as a functional prototype and design reference.

---

## 🚀 What is this?

Firebase is powerful — but the CLI can be:
- easy to misconfigure
- easy to forget flags
- unfriendly to newcomers
- tedious for repeated workflows

This tool wraps common Firebase Hosting operations in a **safe, guided GUI** while still using the official Firebase CLI under the hood.

---

## ✨ What it can do

- 🔐 **Firebase login**
- 🧰 **Install Firebase CLI** (via npm)
- 📁 **Initialize Firebase Hosting**
- 🚀 **Deploy to Firebase Hosting**
- 🧵 **Threaded execution** (no frozen UI)
- 📜 **Live output logging**
- ⚠️ **Helpful error detection & messaging**

All actions are executed using the official Firebase CLI — nothing proprietary.

---

## 🖥️ How it works

- Built with **Tkinter**
- Runs Firebase CLI commands via `subprocess`
- Captures stdout/stderr and displays it in real time
- Executes long-running commands in background threads
- Guards against common misconfiguration errors

---

## 🗂️ Project structure

firebase-automation-tool/
├── main.py # Tkinter GUI + command orchestration
├── Roadmap.md # Planned improvements and features
└── firebase-debug.log (example output)

yaml
Copy code

---

## ▶️ Requirements

- Python 3.x
- Node.js + npm
- Firebase CLI (`npm install -g firebase-tools`)

---

## ▶️ Running the tool

```bash
python main.py
```
From there, the GUI guides you through:

- logging in
- selecting a project
- initializing hosting
- deploying your site

## ⚠️ Project status
Archived / Prototype

- Core functionality works
- No installer or packaging
- No automated tests
- UI polish and cross-platform refinement incomplete

The roadmap documents how this could evolve into a production-grade tool.

## 🧭 Roadmap highlights

Planned (but not implemented):

- persistent settings
- progress indicators
- cancelable operations
- Firebase emulator support
- project management
- OAuth-based login
- plugin architecture

See Roadmap.md for full details.

## 📜 License
Unlicensed (personal archive).

## 🏷️ Status
On ice — but useful.

This project exists as a practical snapshot of a real-world developer tooling experiment.
