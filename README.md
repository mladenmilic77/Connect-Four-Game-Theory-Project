# 🎮 Connect-N Game Theory Project

A Python implementation of the **Connect-N** game featuring multiple intelligent agents for AI and game theory experimentation.

---

## 🧩 Features

✅ Play via **GUI (Pygame)** or **CLI mode**  
✅ Modular design – easily add new agents  
✅ Adjustable board size and connect-length  
✅ Multiple AI strategies for comparison  
✅ Clear, object-oriented architecture

---

## 🚀 Installation & Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/mladenmilic77/Connect-Four-Game-Theory-Project.git
cd Connect-Four-Game-Theory-Project
pip install -r requirements.txt
```

---

## 🕹️ Running the Game

### Run GUI version:
```bash
python gui_main.py
```

### Run CLI version:
```bash
python cli_main.py
```

---

## 🧠 Agent Overview

| Agent | Description |
|--------|-------------|
| `HumanAgent` | Manual input through GUI or terminal |
| `RandomAgent` | Plays random legal moves |
| `OffensiveAgent` | Heuristic: prefers winning opportunities |
| `DefensiveAgent` | Heuristic: focuses on blocking opponent |
| `MinimaxAgent` | Classic minimax algorithm with heuristic evaluation |
| `MCTSAgent` | Monte Carlo Tree Search with UCT and smart rollouts |

---

## ⚙️ Project Structure

```
/GameTheory/
│
├── board.py               # Board logic and win detection
├── game_controller.py     # Game loop and state management
├── match_runner.py        # Automates matches between agents
│
├── agents/
│   ├── human_agent.py
│   ├── random_agent.py
│   ├── heuristic_agent.py
│   ├── minimax_agent.py
│   └── mcts_agent.py
│
├── gui_main.py            # Pygame-based GUI launcher
├── cli_main.py            # Command-line version
│
├── gui/
│   ├── scene.py           # GUI components
│   ├── main_menu.py
│   ├── window_manager.py
│   ├── ui_element.py
│
├── requirements.txt
└── README.md
```

---

## 📜 License

This project is open-source under the **MIT License**.  
Feel free to fork, modify, and extend it.

---

## 👤 Author

**Mladen Milić**  
Computing & Control Engineering Student  
University of Novi Sad – Faculty of Technical Sciences

www.linkedin.com/in/mladen-milic-resume
