from board import Board
from agents.human_agent import HumanAgent
from agents.random_agent import RandomAgent
from match_runner import MatchRunner
from agents.heuristic_agent import OffensiveAgent, DefensiveAgent

# TODO take constants from constants.py
MIN_RC, MAX_RC = 4, 30
AGENT_CLASSES = {
    "Human": HumanAgent,
    "Random": RandomAgent,
    "Offensive": OffensiveAgent,
    "Defensive": DefensiveAgent,
}

def choose_agent(player_num: int) -> object:
    """"""
    print(f"\nSelect Agent type for player {player_num}:")
    for i, agent_type in enumerate(AGENT_CLASSES.keys(), start = 1):
        print(f"{i} - {agent_type}")

    while True:
        choice = input(f"Enter choice for player {player_num}: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(AGENT_CLASSES):
            agent_type = list(AGENT_CLASSES.keys())[int(choice) - 1]
            break
        print("Invalid choice. Try again.")

    default_name = {
        "Human": "Paul Human",
        "Random": "Marlon Random",
        "Offensive": "Rowan Attackinson",
        "Defensive": "Samuel L. Blockson",
    }[agent_type]
    name = input(f"Enter name for {agent_type} Player {player_num} | default: {default_name}: ").strip() or default_name

    return AGENT_CLASSES[agent_type](name)

def ask_helper(prompt: str, min_v = MIN_RC, max_v = MAX_RC) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            val = int(raw)
            if not(min_v <= val <= max_v):
                print(f"Please enter a number in [{min_v}, {max_v}].")
                continue
            return val
        except ValueError:
            print("Not a valid integer. Try again.")
    return min_v #not reachable


def main():
    print("=== Connect Four CLI ===")
    print(f"\nChoose board dimensions (MIN: {MIN_RC}, MAX: {MAX_RC})")
    rows = ask_helper("Enter number of rows: ")
    cols = ask_helper("Enter number of cols: ")

    print(f"Enter the number of tokens needed to win (MIN: 3, MAX: {max(rows, cols)}).")
    chips = ask_helper("Your choice: ", 3, max(rows, cols))

    try:
        board = Board(rows, cols, chips)
    except ValueError as e:
        print(f"Board error: {e}")
        print("Let's try again...\n")
        return

    agent1 = choose_agent(1)
    agent2 = choose_agent(2)

    runner = MatchRunner(agent1, agent2, board)
    result = runner.run()

    print("=== Game Over ===")
    if result == 0:
        print("Draw!")
    else:
        winner_agent = runner.agent1 if result == 1 else runner.agent2
        print(f"Winner: {winner_agent.name} (P{result})")

if __name__ == "__main__":
    main()