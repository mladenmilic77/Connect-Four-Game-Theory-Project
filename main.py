from human_agent import HumanAgent
from random_agent import RandomAgent
from match_runner import MatchRunner

def main():
    while True:
        print("=== Connect Four CLI ===")
        print("Choose mode:")
        print("1 - Human vs Human")
        print("2 - Human vs Random")
        print("3 - Random vs Random")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            name1 = input("Enter name for Human Player 1 | default: Paul Human: ").strip()
            name2 = input("Enter name for Human Player 2 | default: Paul Human: ").strip()
            runner = MatchRunner(HumanAgent(name1), HumanAgent(name2))
            break
        elif choice == "2":
            name1 = input("Enter name for Human Player 1 | default: Paul Human: ").strip()
            name2 = input("Enter name for Random Player 2 | default: Marlon Random: ").strip()
            runner = MatchRunner(HumanAgent(name1), RandomAgent(name2))
            break
        elif choice == "3":
            name1 = input("Enter name for Random Player 1 | default: Marlon Random: ").strip()
            name2 = input("Enter name for Random Player 2 | default: Marlon Random: ").strip()
            runner = MatchRunner(RandomAgent(name1), RandomAgent(name2))
            break
        else:
            print("Invalid choice.")

    result = runner.run()
    print("=== Game Over ===")
    if result == 0:
        print("Draw!")
    else:
        winner_agent = runner.agent1 if result == 1 else runner.agent2
        print(f"Winner: {winner_agent.name} (P{result})")

if __name__ == "__main__":
    main()