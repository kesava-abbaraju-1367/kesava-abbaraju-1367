#!/usr/bin/env python3
"""
tictactoe_bot.py - Interactive GitHub README Tic-Tac-Toe Bot Engine

How it works:
1. Triggered when an issue is opened with title: "tictactoe|move|<cell_index>" or "tictactoe|reset"
2. Reads current board from README.md
3. Validates and applies user move (X)
4. Checks if user won -> Displays Winner Banner & Confetti Animation!
5. If game continues, AI Bot plays move (O)
6. Checks if Bot won or Draw
7. Rewrites README.md with new board state, links, and banners
8. Closes the GitHub Issue
"""

import sys
import os
import re
import random

# Winning combinations on 3x3 board (0-indexed)
WINNING_COMBOS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
    (0, 4, 8), (2, 4, 6)               # Diagonals
]

def parse_board_from_readme(readme_content):
    """Extracts 9-element array representing the board from README.md."""
    # Look for the Tic-Tac-Toe table in README
    match = re.search(r'<!-- TICTACTOE_BOARD_START -->.*?<!-- TICTACTOE_BOARD_END -->', readme_content, re.DOTALL)
    if not match:
        return ["⬜"] * 9
    
    table_text = match.group(0)
    cells = []
    # Find all occurrences of ❌, ⭕, or ⬜
    for symbol in re.findall(r'[❌⭕⬜]', table_text):
        cells.append(symbol)
        if len(cells) == 9:
            break
            
    while len(cells) < 9:
        cells.append("⬜")
    return cells

def check_winner(board):
    for a, b, c in WINNING_COMBOS:
        if board[a] != "⬜" and board[a] == board[b] == board[c]:
            return board[a]
    if "⬜" not in board:
        return "DRAW"
    return None

def get_best_bot_move(board):
    """Smart AI Bot logic using Minimax/Priority."""
    # 1. Can Bot (⭕) win on this move?
    for i in range(9):
        if board[i] == "⬜":
            temp_board = list(board)
            temp_board[i] = "⭕"
            if check_winner(temp_board) == "⭕":
                return i

    # 2. Can User (❌) win on next move? Block them!
    for i in range(9):
        if board[i] == "⬜":
            temp_board = list(board)
            temp_board[i] = "❌"
            if check_winner(temp_board) == "❌":
                return i

    # 3. Take Center if available
    if board[4] == "⬜":
        return 4

    # 4. Take Corners
    corners = [i for i in [0, 2, 6, 8] if board[i] == "⬜"]
    if corners:
        return random.choice(corners)

    # 5. Take any remaining empty cell
    empty = [i for i in range(9) if board[i] == "⬜"]
    if empty:
        return random.choice(empty)
    return None

def generate_board_markdown(board, repo_owner, status_message=""):
    """Generates the Markdown table with clickable issue links for empty cells."""
    base_url = f"https://github.com/{repo_owner}/{repo_owner}/issues/new"
    
    rows = []
    for r in range(3):
        row_cells = []
        for c in range(3):
            idx = r * 3 + c
            symbol = board[idx]
            if symbol == "⬜":
                cell_link = f'{base_url}?title=tictactoe%7Cmove%7C{idx + 1}&body=Click+%22Submit+new+issue%22+to+make+this+move!'
                row_cells.append(f'<a href="{cell_link}">⬜</a>')
            else:
                row_cells.append(symbol)
        rows.append(f"| {' | '.join(row_cells)} |")

    table_md = "\n".join(rows)
    reset_url = f'{base_url}?title=tictactoe%7Creset&body=Click+%22Submit+new+issue%22+to+reset+the+game!'

    banner_html = ""
    if status_message:
        banner_html = f"\n{status_message}\n"

    new_section = f"""<!-- TICTACTOE_BOARD_START -->
<div align="center">

## `~/` 🎮 tic-tac-toe (play against bot!)

{banner_html}
| | | |
| :-: | :-: | :-: |
{table_md}

<br>

<a href="{reset_url}">🔄 **Reset / Play Again**</a>

</div>
<!-- TICTACTOE_BOARD_END -->"""
    return new_section

def main():
    repo_owner = os.environ.get("REPO_OWNER", "kesava-abbaraju-1367")
    issue_title = os.environ.get("ISSUE_TITLE", "").strip()

    print(f"Processing Tic-Tac-Toe action for issue: '{issue_title}'")

    readme_path = "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    # Reset game command
    if "reset" in issue_title.lower():
        board = ["⬜"] * 9
        status_msg = "🎮 *Game reset! You are ❌. Click any empty square (⬜) to start!*"
        new_board_md = generate_board_markdown(board, repo_owner, status_msg)
        updated_readme = re.sub(r'<!-- TICTACTOE_BOARD_START -->.*?<!-- TICTACTOE_BOARD_END -->', new_board_md, readme_content, flags=re.DOTALL)
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_readme)
        print("Game reset successfully.")
        return

    # Parse move index (1-9)
    move_match = re.search(r'(\d+)', issue_title)
    if not move_match:
        print("No valid move index found in title.")
        return

    move_idx = int(move_match.group(1)) - 1  # Convert to 0-indexed
    if move_idx < 0 or move_idx > 8:
        print("Move index out of range.")
        return

    board = parse_board_from_readme(readme_content)

    # Check if cell is empty
    if board[move_idx] != "⬜":
        print(f"Cell {move_idx + 1} is already occupied.")
        return

    # 1. Apply User Move (❌)
    board[move_idx] = "❌"
    result = check_winner(board)

    status_msg = ""
    if result == "❌":
        # WINNER ANIMATION!
        status_msg = """
<a href="https://github.com/kesava-abbaraju-1367">
  <img src="assets/winner-animation.svg" width="85%" alt="Winner Animation">
</a>
<br>
<h3>🎉 🏆 <b>VICTORY! CONGRATULATIONS!</b> 🏆 🎉</h3>
"""
    elif result == "DRAW":
        status_msg = "<h3>🤝 <b>IT'S A DRAW! GREAT GAME!</b> 🤝</h3>"
    else:
        # 2. AI Bot Move (⭕)
        bot_move = get_best_bot_move(board)
        if bot_move is not None:
            board[bot_move] = "⭕"
            bot_result = check_winner(board)
            if bot_result == "⭕":
                status_msg = "<h3>🤖 <b>BOT WON THIS ROUND! TRY AGAIN!</b> 🤖</h3>"
            elif bot_result == "DRAW":
                status_msg = "<h3>🤝 <b>IT'S A DRAW!</b> 🤝</h3>"
            else:
                status_msg = "🎮 *Your turn! Click an empty square (⬜) to place your move ❌!*"

    # Generate updated README section
    new_board_md = generate_board_markdown(board, repo_owner, status_msg)
    updated_readme = re.sub(r'<!-- TICTACTOE_BOARD_START -->.*?<!-- TICTACTOE_BOARD_END -->', new_board_md, readme_content, flags=re.DOTALL)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_readme)

    print("Tic-Tac-Toe board updated successfully!")

if __name__ == "__main__":
    main()
