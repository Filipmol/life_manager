# Ultimate Daily Life Manager

A cross-platform desktop app (Windows & Linux) for managing your daily life — tasks, recipes, workouts — with a local AI assistant powered by Ollama.

**Dark mode, modern Flutter-like UI, 100% local, no cloud APIs.**

---

## Prerequisites (install these FIRST)

### 1. Python 3.10+

| OS | How to install |
|---|---|
| **Windows** | Download from [python.org/downloads](https://www.python.org/downloads/). **Check "Add Python to PATH"** during installation. |
| **Ubuntu/Debian** | `sudo apt install python3 python3-pip python3-venv` |
| **Fedora** | `sudo dnf install python3 python3-pip` |
| **Arch** | `sudo pacman -S python python-pip` |

### 2. Ollama (for AI features — optional but recommended)

| OS | How to install |
|---|---|
| **Windows** | Download from [ollama.com](https://ollama.com) and run the installer. |
| **Linux** | `curl -fsSL https://ollama.com/install.sh \| sh` |

After installing Ollama, pull a model:

```bash
ollama pull llama3.2
```

Keep Ollama running in the background while using the app.

> **Note:** The app works without Ollama — task management is fully functional. Only recipe generation and workout plan generation require Ollama.

---

## How to Run (1-click)

### Windows

1. Double-click **`run_windows.bat`**
2. The script checks Python, installs dependencies, and launches the app.

### Linux

1. Open a terminal in the project folder.
2. Run:
   ```bash
   ./run_linux.sh
   ```
   (or `bash run_linux.sh` if permissions aren't set)

---

## Features

### Dashboard
- Greeting based on time of day
- Live stats: total tasks, recipes, workouts, overdue items
- Ollama connection status indicator
- Quick-access navigation cards
- Mini Kanban preview

### Food & Recipes
- Enter ingredients you have on hand
- AI generates a detailed recipe with prep time, steps, nutrition notes
- Choose which Ollama model to use
- Full recipe history with expand/collapse and delete
- Streaming AI output — see the recipe appear word-by-word

### Fitness & Running
- Describe any fitness goal (5km run, gym day, HIIT, stretching)
- Quick-start template chips for common workouts
- AI generates a specific plan with warm-up, main workout, cool-down
- Saved workout history

### Task Manager (Kanban)
- Three-column board: To Do → Doing → Done
- Add tasks with title, description, category, priority, due date
- Move tasks between columns with arrow buttons
- Filter by category (Work / School / Personal)
- Priority indicators (color-coded dots)
- Overdue date highlighting
- Delete tasks

---

## Project Structure

```
life-manager/
├── main.py                  # App entry point
├── requirements.txt         # Python dependencies
├── run_windows.bat          # 1-click Windows launcher
├── run_linux.sh             # 1-click Linux launcher
├── README.md                # This file
├── core/
│   ├── __init__.py
│   ├── database.py          # SQLite — auto-creates DB and tables
│   ├── ollama_client.py     # Local LLM communication (streaming)
│   └── theme.py             # Dark mode color palette & UI helpers
└── views/
    ├── __init__.py
    ├── dashboard.py          # Dashboard view
    ├── food.py               # Food & Recipes view
    ├── fitness.py            # Fitness & Running view
    └── tasks.py              # Task Manager / Kanban view
```

---

## Data Storage

All data is stored in a local SQLite database at:

- **Windows:** `C:\Users\<you>\.life_manager\life_manager.db`
- **Linux:** `~/.life_manager/life_manager.db`

The database and all tables are created automatically on first launch.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "Python is not installed" | Install Python 3.10+ and ensure it's in your PATH |
| App window doesn't open | Check the terminal for error messages |
| AI features say "Ollama offline" | Start Ollama and make sure you've pulled a model (`ollama pull llama3.2`) |
| "Cannot reach Ollama" during generation | Ollama may have stopped — restart it |
| Flet install fails | Try `pip install flet` manually, or update pip: `python -m pip install --upgrade pip` |
