from board import Board
from human_agent import HumanAgent
from random_agent import RandomAgent
from match_runner import MatchRunner

# TODO take constants from constants.py
MIN_RC, MAX_RC = 4, 30

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
    runner = None

    while True:
        print("=== Connect Four CLI ===")
        print("Choose mode:")
        print("1 - Human vs Human")
        print("2 - Human vs Random")
        print("3 - Random vs Random")
        choice = input("Enter choice: ").strip()

        if choice not in {"1", "2", "3"}:
            print("Invalid choice.\n")
            continue

        print(f"\nChoose board dimensions (MIN: {MIN_RC}, MAX: {MAX_RC})")
        rows = ask_helper("Enter number of rows: ")
        cols = ask_helper("Enter number of cols: ")

        try:
            board = Board(rows, cols)
        except ValueError as e:
            print(f"Board error: {e}")
            print("Let's try again...\n")
            continue

        if choice == "1":
            name1 = input("Enter name for Human Player 1 | default: Paul Human: ").strip()
            name2 = input("Enter name for Human Player 2 | default: Paul Human: ").strip()
            runner = MatchRunner(HumanAgent(name1), HumanAgent(name2), board)
        elif choice == "2":
            name1 = input("Enter name for Human Player 1 | default: Paul Human: ").strip()
            name2 = input("Enter name for Random Player 2 | default: Marlon Random: ").strip()
            runner = MatchRunner(HumanAgent(name1), RandomAgent(name2), board)
        else:
            name1 = input("Enter name for Random Player 1 | default: Marlon Random: ").strip()
            name2 = input("Enter name for Random Player 2 | default: Marlon Random: ").strip()
            runner = MatchRunner(RandomAgent(name1), RandomAgent(name2), board)

        break


    result = runner.run()
    print("=== Game Over ===")
    if result == 0:
        print("Draw!")
    else:
        winner_agent = runner.agent1 if result == 1 else runner.agent2
        print(f"Winner: {winner_agent.name} (P{result})")

if __name__ == "__main__":
    main()