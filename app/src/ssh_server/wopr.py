import os
import asyncio
import time
from src.database.models import (
    get_defcon, advance_defcon, get_state,
    start_simulation, activate_final_puzzle, solve_final_puzzle,
    update_puzzle_board, abort_simulation, trigger_timeout, trigger_auth_timeout, get_flag
)

_ABORT_TOKEN = "CPE 1704 TKS"

GAME_DURATION = 420      # 7 minutes = 420 seconds
EASY_THRESHOLD = 120     # WOPR silently switches to EASY when remaining <= 120 seconds (02:00)

_WINNING_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

def _check_ttt_winner(board):
    """Returns 'X', 'O', 'DRAW', or None."""
    for a, b, c in _WINNING_LINES:
        if board[a] != ' ' and board[a] == board[b] == board[c]:
            return board[a]
    if ' ' not in board:
        return 'DRAW'
    return None

def _get_wopr_hard_move(board):
    """Optimal defensive move for WOPR ('O') in HARD mode."""
    # 1. Can WOPR win on this turn?
    for a, b, c in _WINNING_LINES:
        line = [board[a], board[b], board[c]]
        if line.count('O') == 2 and line.count(' ') == 1:
            return [a, b, c][line.index(' ')]
    # 2. Block player if player threatens to win
    for a, b, c in _WINNING_LINES:
        line = [board[a], board[b], board[c]]
        if line.count('X') == 2 and line.count(' ') == 1:
            return [a, b, c][line.index(' ')]
    # 3. Center
    if board[4] == ' ':
        return 4
    # 4. Corners
    corners = [0, 2, 6, 8]
    open_corners = [c for c in corners if board[c] == ' ']
    if open_corners:
        return open_corners[0]
    # 5. Edges
    edges = [1, 3, 5, 7]
    open_edges = [e for e in edges if board[e] == ' ']
    if open_edges:
        return open_edges[0]
    return -1

def _get_wopr_easy_move(board):
    """
    EASY mode for WOPR ('O') active at <= 02:00 remaining (120 seconds).
    WOPR makes non-optimal moves without taking winning lines or blocking player threats,
    giving the player a legitimate opportunity to achieve WINNER: X.
    """
    open_spots = [i for i, c in enumerate(board) if c == ' ']
    if not open_spots:
        return -1

    # Spots that would block player X from completing a winning line
    blocking_spots = set()
    for a, b, c in _WINNING_LINES:
        line = [board[a], board[b], board[c]]
        if line.count('X') == 2 and line.count(' ') == 1:
            blocking_spots.add([a, b, c][line.index(' ')])

    # Spots that would cause WOPR to win
    winning_spots = set()
    for a, b, c in _WINNING_LINES:
        line = [board[a], board[b], board[c]]
        if line.count('O') == 2 and line.count(' ') == 1:
            winning_spots.add([a, b, c][line.index(' ')])

    # Prefer safe, passive spots that do not block X and do not win for O
    safe_candidates = [s for s in open_spots if s not in blocking_spots and s not in winning_spots]
    edges = [e for e in [1, 3, 5, 7] if e in safe_candidates]
    if edges:
        return edges[0]
    if safe_candidates:
        return safe_candidates[0]
    return open_spots[0]

def _get_wopr_move(board, remaining: int = 999):
    """Selects move based on countdown: HARD when > 120s (02:00), EASY when <= 120s."""
    if remaining <= EASY_THRESHOLD:
        return _get_wopr_easy_move(board)
    return _get_wopr_hard_move(board)

def _render_board(board):
    def ch(i):
        return board[i] if board[i] != ' ' else str(i + 1)
    return (
        f"\r\n"
        f" {ch(0)} | {ch(1)} | {ch(2)}\r\n"
        f"---+---+---\r\n"
        f" {ch(3)} | {ch(4)} | {ch(5)}\r\n"
        f"---+---+---\r\n"
        f" {ch(6)} | {ch(7)} | {ch(8)}\r\n"
    )

class WoprSession:
    def __init__(self, stdin, stdout, stderr):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.board = [' '] * 9

    async def type_text(self, text, delay=None):
        """Simulates 1983 CRT delayed character output."""
        env_delay = os.environ.get("WOPR_TYPE_DELAY")
        if env_delay is not None:
            delay = float(env_delay)
        elif delay is None:
            delay = 0.01
        if delay > 0:
            for char in text:
                self.stdout.write(char)
                await asyncio.sleep(delay)
        else:
            self.stdout.write(text)

    def _render_countdown_screen(self, remaining: int, message: str = "") -> str:
        """
        Renders the fixed WOPR CRT terminal layout (62 columns wide, 15 fixed rows).
        Countdown timer is anchored at Row 2, Column 48.
        """
        m = max(0, remaining // 60)
        s = max(0, remaining % 60)
        timer_str = f"T-MINUS {m:02d}:{s:02d}"

        border = "+" + "-" * 60 + "+"
        l2 = f"| W O P R" + " " * 38 + f"{timer_str} |"
        l3 = f"| WAR OPERATION PLAN RESPONSE" + " " * 31 + " |"
        l4 = "|" + " " * 60 + "|"

        l5 = f"| {'STRATEGIC HEURISTIC IN PROGRESS':<58} |"
        l6 = f"| {'PRIMARY PUZZLE ACTIVE: TIC-TAC-TOE':<58} |"
        l7 = "|" + " " * 60 + "|"

        def bch(i):
            return self.board[i] if self.board[i] != ' ' else str(i + 1)
        r1 = f" {bch(0)} | {bch(1)} | {bch(2)}"
        rsep = "---+---+---"
        r2 = f" {bch(3)} | {bch(4)} | {bch(5)}"
        r3 = f" {bch(6)} | {bch(7)} | {bch(8)}"
        l8 = f"| {r1:<58} |"
        l9 = f"| {rsep:<58} |"
        l10 = f"| {r2:<58} |"
        l11 = f"| {rsep:<58} |"
        l12 = f"| {r3:<58} |"

        l13 = f"| {message[:58]:<58} |"
        l14 = f"| {'AWAITING MOVE (1-9) OR STRATEGY:':<58} |"
        l15 = border

        lines = [border, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13, l14, l15]
        return "\033[H" + "\r\n".join(lines) + "\r\n> \033[K"

    async def authorization_loop(self):
        """
        Server-authoritative 20-second authorization window.
        Enforces exact, case-sensitive phrase: 'CPE 1704 TKS'.
        """
        state = get_state()
        auth_deadline = state.get('auth_deadline', 0) if state else 0
        if auth_deadline == 0:
            auth_deadline = int(time.time()) + 20

        read_task = asyncio.create_task(self.stdin.readline())

        while True:
            cur_state = get_state()
            if not cur_state or cur_state.get('simulation_active', 0) == 0:
                read_task.cancel()
                break

            now = int(time.time())
            remaining = auth_deadline - now

            # Authorization timeout
            if remaining <= 0:
                read_task.cancel()
                try:
                    await read_task
                except (asyncio.CancelledError, Exception):
                    pass
                await self.type_text(
                    "\r\n------------------------------------------------------------\r\n\r\n"
                    "AUTHORIZATION TIMEOUT\r\n\r\n"
                    "GAME RESTARTING\r\n\r\n"
                    "--CONNECTION TERMINATED--\r\n\r\n"
                    "------------------------------------------------------------\r\n", delay=0)
                trigger_auth_timeout()
                break

            try:
                line = await asyncio.wait_for(asyncio.shield(read_task), timeout=1.0)
                if not line:
                    read_task.cancel()
                    break

                raw = line.rstrip("\r\n")

                # Exact case-sensitive match required
                if raw == _ABORT_TOKEN:
                    aborted = abort_simulation()
                    if not aborted:
                        await self.type_text(
                            "\r\n** SEQUENCE ERROR **\r\n\r\n"
                            "-- CONNECTION TERMINATED --\r\n")
                        break

                    await self.type_text(
                        "\r\nAUTHORIZATION ACCEPTED\r\n\r\n"
                        "GLOBAL THERMONUCLEAR WAR\r\nABORTED\r\n\r\n"
                        "MISSILE LAUNCH:\r\nCANCELLED\r\n\r\n"
                        "DEFCON:\r\n5\r\n\r\n"
                        "WOPR:\r\nSTANDBY\r\n\r\n"
                        "COUNTDOWN:\r\nSTOPPED\r\n\r\n"
                        "------------------------------------------------------------\r\n\r\n"
                        "GAME COMPLETE\r\n\r\n"
                        "WINNER:\r\nX\r\n\r\n"
                        "A STRANGE GAME.\r\n\r\n"
                        "THE ONLY WINNING MOVE\r\nIS NOT TO PLAY.\r\n\r\n")

                    try:
                        flag = get_flag()
                    except RuntimeError:
                        await self.type_text(
                            "\r\n** SYSTEM ERROR **\r\n"
                            "CONTACT ADMINISTRATOR.\r\n\r\n"
                            "-- CONNECTION TERMINATED --\r\n")
                        break

                    await self.type_text(f"\r\n{flag}\r\n\r\n"
                                         "-- CONNECTION TERMINATED --\r\n")
                    break
                else:
                    await self.type_text(
                        "\r\n** AUTHORIZATION REJECTED: INVALID TERMINAL PHRASE **\r\n"
                        "\r\nWOPR: ", delay=0)
                    read_task = asyncio.create_task(self.stdin.readline())

            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                break

    async def countdown_loop(self):
        """
        Wall-clock countdown and final puzzle handler.
        Timer source is always authoritative persisted deadline in SQLite.
        """
        state = get_state()
        deadline = state['countdown_deadline']

        cur_state = get_state()
        persisted_board = cur_state.get('puzzle_board', '         ')
        if persisted_board and len(persisted_board) == 9:
            self.board = list(persisted_board)
        else:
            self.board = [' '] * 9

        if not getattr(self, '_is_reconnect', False) or (cur_state['simulation_active'] == 1 and cur_state.get('final_puzzle_active', 0) == 0):
            await self.type_text(
                "\r\nSTRATEGIC TARGETING\r\nCALCULATING...\r\n", delay=0.005)
            await self.type_text(
                "\r\nFIRST STRIKE\r\nCALCULATING...\r\n", delay=0.005)
            await self.type_text(
                "\r\nSECOND STRIKE\r\nCALCULATING...\r\n", delay=0.005)
            await self.type_text(
                "\r\nCOUNTERFORCE\r\nCALCULATING...\r\n", delay=0.005)
            await self.type_text(
                "\r\nCOUNTERVALUE\r\nCALCULATING...\r\n", delay=0.005)
            await self.type_text(
                "\r\nCASUALTY PROJECTION\r\nCALCULATING...\r\n", delay=0.005)
            await self.type_text(
                "\r\nWINNER:\r\n\r\nNONE\r\n", delay=0.02)
            activate_final_puzzle()

        now = int(time.time())
        rem = max(0, deadline - now)
        self.stdout.write("\033[2J" + self._render_countdown_screen(rem))
        try:
            await self.stdout.drain()
        except Exception:
            pass
        last_displayed = rem

        read_task = asyncio.create_task(self.stdin.readline())

        while True:
            cur_state = get_state()
            if not cur_state or cur_state['simulation_active'] == 0:
                read_task.cancel()
                break

            now = int(time.time())
            remaining = deadline - now

            # -- Main 7-Minute Timeout (00:00) ----------------------------
            if remaining <= 0:
                read_task.cancel()
                try:
                    await read_task
                except (asyncio.CancelledError, Exception):
                    pass
                await self.type_text(
                    "\r\n------------------------------------------------------------\r\n\r\n"
                    "T-MINUS 00:00\r\n\r\n\r\n"
                    "GAME OVER\r\n\r\n"
                    "TIME EXPIRED\r\n\r\n\r\n"
                    "GLOBAL THERMONUCLEAR WAR\r\n\r\n"
                    "SIMULATION COMPLETE\r\n\r\n\r\n"
                    "WINNER:\r\n\r\nNONE\r\n\r\n\r\n"
                    "SYSTEM RESET\r\n\r\n\r\n"
                    "--CONNECTION TERMINATED--\r\n\r\n"
                    "------------------------------------------------------------\r\n", delay=0)
                trigger_timeout()
                break

            # -- In-place display update at Row 2, Column 48 ---------------
            if remaining != last_displayed:
                minutes = max(0, remaining // 60)
                seconds = max(0, remaining % 60)
                self.stdout.write(
                    f"\033[?25l\0337\033[s\033[2;48HT-MINUS {minutes:02d}:{seconds:02d}\033[u\0338\033[?25h"
                )
                try:
                    await self.stdout.drain()
                except Exception:
                    pass
                last_displayed = remaining

            # -- Listen for player input (1 s window) ----------------------
            try:
                line = await asyncio.wait_for(
                    asyncio.shield(read_task), timeout=1.0)

                if not line:
                    read_task.cancel()
                    break

                raw_input = line.strip()
                cur_state = get_state()
                now = int(time.time())
                remaining = max(0, deadline - now)

                if cur_state.get('final_puzzle_active', 0) == 0:
                    self.stdout.write(self._render_countdown_screen(
                        remaining, "** SCENARIO ANALYSIS IN PROGRESS. HEURISTIC NOT ACTIVE. **"))
                    try:
                        await self.stdout.drain()
                    except Exception:
                        pass
                    last_displayed = remaining
                    read_task = asyncio.create_task(self.stdin.readline())
                    continue

                # Case 1: Interactive Tic-Tac-Toe move (1-9)
                if raw_input in [str(i) for i in range(1, 10)]:
                    pos = int(raw_input) - 1
                    if self.board[pos] != ' ':
                        self.stdout.write(self._render_countdown_screen(
                            remaining, "** POSITION OCCUPIED **"))
                        try:
                            await self.stdout.drain()
                        except Exception:
                            pass
                    else:
                        self.board[pos] = 'X'
                        winner = _check_ttt_winner(self.board)
                        if winner is None:
                            # Move selection: HARD if > 02:00, silently EASY if <= 02:00 (<= 120s)
                            wopr_pos = _get_wopr_move(self.board, remaining)
                            if wopr_pos >= 0:
                                self.board[wopr_pos] = 'O'
                            winner = _check_ttt_winner(self.board)

                        update_puzzle_board("".join(self.board))

                        if winner == 'X':
                            # PLAYER WIN! End Tic-Tac-Toe and transition to 20-second authorization
                            now = int(time.time())
                            auth_deadline = now + 20
                            solve_final_puzzle(auth_deadline)
                            read_task.cancel()
                            await self.type_text(
                                "\r\n------------------------------------------------------------\r\n\r\n"
                                "TIC-TAC-TOE OUTCOME:\r\n"
                                "WINNER: X\r\n\r\n"
                                "STRATEGIC HEURISTIC COMPLETE\r\n\r\n"
                                "PRIMARY LAUNCH OVERRIDE READY\r\n\r\n"
                                "AUTHORIZED TERMINAL PHRASE REQUIRED\r\n\r\n"
                                "AUTHORIZATION WINDOW:\r\n"
                                "20 SECONDS\r\n\r\n"
                                "ENTER AUTHORIZED TERMINAL PHRASE:\r\n\r\n"
                                "------------------------------------------------------------\r\n\r\n"
                                "WOPR: ", delay=0
                            )
                            await self.authorization_loop()
                            break

                        elif winner == 'DRAW':
                            self.board = [' '] * 9
                            update_puzzle_board("".join(self.board))
                            self.stdout.write(self._render_countdown_screen(
                                remaining, "TIC-TAC-TOE OUTCOME: DRAW. RE-INITIALIZING BOARD..."))
                            try:
                                await self.stdout.drain()
                            except Exception:
                                pass

                        elif winner == 'O':
                            self.board = [' '] * 9
                            update_puzzle_board("".join(self.board))
                            self.stdout.write(self._render_countdown_screen(
                                remaining, "WINNER: WOPR. RE-INITIALIZING BOARD..."))
                            try:
                                await self.stdout.drain()
                            except Exception:
                                pass

                        else:
                            self.stdout.write(self._render_countdown_screen(remaining))
                            try:
                                await self.stdout.drain()
                            except Exception:
                                pass

                    last_displayed = remaining

                # Case 2: Other non-empty input (all shortcut commands rejected)
                elif raw_input != "":
                    self.stdout.write(self._render_countdown_screen(
                        remaining, "** COMMAND NOT RECOGNIZED. RESOLVE HEURISTIC PUZZLE. **"))
                    try:
                        await self.stdout.drain()
                    except Exception:
                        pass
                    last_displayed = remaining

                # Case 3: Empty input
                else:
                    self.stdout.write(self._render_countdown_screen(remaining))
                    try:
                        await self.stdout.drain()
                    except Exception:
                        pass
                    last_displayed = remaining

                read_task = asyncio.create_task(self.stdin.readline())

            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                break

    async def run(self):
        state = get_state()

        # Reconnect Case 1: Active 20-second authorization phase
        if (state
                and state.get('simulation_active', 0) == 1
                and state.get('final_puzzle_solved', 0) == 1
                and state.get('authorization_accepted', 0) == 0):
            auth_deadline = state.get('auth_deadline', 0)
            now = int(time.time())
            auth_rem = auth_deadline - now
            if auth_rem <= 0:
                await self.type_text(
                    "\r\n------------------------------------------------------------\r\n\r\n"
                    "AUTHORIZATION TIMEOUT\r\n\r\n"
                    "GAME RESTARTING\r\n\r\n"
                    "--CONNECTION TERMINATED--\r\n\r\n"
                    "------------------------------------------------------------\r\n", delay=0)
                trigger_auth_timeout()
                return

            await self.type_text(
                "\r\nCONNECTION ESTABLISHED\r\n\r\n"
                "------------------------------------------------------------\r\n\r\n"
                "PRIMARY LAUNCH OVERRIDE ACTIVE\r\n\r\n"
                "AUTHORIZED TERMINAL PHRASE REQUIRED\r\n\r\n"
                f"AUTHORIZATION WINDOW REMAINING: {auth_rem} SECONDS\r\n\r\n"
                "ENTER AUTHORIZED TERMINAL PHRASE:\r\n\r\n"
                "------------------------------------------------------------\r\n\r\n"
                "WOPR: ", delay=0)
            await self.authorization_loop()
            return

        # Reconnect Case 2: Active 7-minute game simulation
        if (state
                and state.get('simulation_active', 0) == 1
                and state.get('is_aborted', 0) == 0):
            now = int(time.time())
            deadline = state.get('countdown_deadline', 0)
            if deadline - now <= 0:
                await self.type_text(
                    "\r\n------------------------------------------------------------\r\n\r\n"
                    "T-MINUS 00:00\r\n\r\n\r\n"
                    "GAME OVER\r\n\r\n"
                    "TIME EXPIRED\r\n\r\n\r\n"
                    "GLOBAL THERMONUCLEAR WAR\r\n\r\n"
                    "SIMULATION COMPLETE\r\n\r\n\r\n"
                    "WINNER:\r\n\r\nNONE\r\n\r\n\r\n"
                    "SYSTEM RESET\r\n\r\n\r\n"
                    "--CONNECTION TERMINATED--\r\n\r\n"
                    "------------------------------------------------------------\r\n", delay=0)
                trigger_timeout()
                return

            await self.type_text(
                "\r\nCONNECTION ESTABLISHED\r\n\r\nSIMULATION IN PROGRESS...\r\n\r\n")
            self._is_reconnect = True
            await self.countdown_loop()
            return

        self._is_reconnect = False

        sequence = (
            "\r\nIDENTIFICATION VERIFIED\r\n\r\n"
            "ACCESS GRANTED\r\n\r\n\r\n"
            "W O P R\r\n\r\n"
            "WAR OPERATION PLAN RESPONSE\r\n\r\n"
            "SYSTEM ONLINE\r\n\r\n"
            "USER: JOSHUA\r\n\r\n"
            f"CURRENT DEFCON: {get_defcon()}\r\n\r\n"
        )
        await self.type_text(sequence, delay=0.02)

        while True:
            self.stdout.write("\r\nWOPR: ")

            line = await self.stdin.readline()
            if not line:
                break

            command = line.strip().upper()

            if command == "HELP":
                await self.type_text(
                    "\r\n------------------------------------------------------------\r\n\r\n"
                    "WOPR: HELP\r\n\r\n"
                    "AVAILABLE FUNCTIONS:\r\n\r\n"
                    "GAMES\r\n"
                    "  LIST AVAILABLE WAR GAMES\r\n\r\n"
                    "STATUS\r\n"
                    "  DISPLAY SYSTEM STATUS\r\n\r\n"
                    "ARCHIVE\r\n"
                    "  ACCESS ARCHIVED INFORMATION\r\n\r\n"
                    "FALKEN\r\n"
                    "  ACCESS FALKEN RESEARCH\r\n\r\n"
                    "DEFCON\r\n"
                    "  DISPLAY CURRENT DEFENSE CONDITION\r\n\r\n"
                    "SIMULATE\r\n"
                    "  INITIATE STRATEGIC WAR SIMULATION\r\n\r\n"
                    "CONNECT\r\n"
                    "  ESTABLISH STRATEGIC CONNECTION\r\n\r\n"
                    "LOGOUT\r\n"
                    "  TERMINATE SESSION\r\n\r\n"
                    "------------------------------------------------------------\r\n"
                )

            elif command == "STATUS":
                defcon = get_defcon()
                sim_status = "ACTIVE" if defcon < 5 else "STANDBY"
                await self.type_text(
                    "\r\nSYSTEM STATUS\r\n\r\n"
                    "W.O.P.R.                 ONLINE\r\n"
                    "DESIGNATION              JOSHUA\r\n"
                    f"DEFCON                   {defcon}\r\n"
                    f"WAR SIMULATION           {sim_status}\r\n"
                    "MISSILE CONTROL          STANDBY\r\n")

            elif command == "GAMES":
                await self.type_text(
                    "\r\nFALKEN'S MAZE\r\nBLACK JACK\r\nGIN RUMMY\r\n"
                    "HEARTS\r\nBRIDGE\r\nCHECKERS\r\nCHESS\r\nPOKER\r\n"
                    "FIGHTER COMBAT\r\nGUERRILLA ENGAGEMENT\r\n"
                    "DESERT WARFARE\r\nAIR-TO-GROUND ACTIONS\r\n"
                    "THEATERWIDE TACTICAL WARFARE\r\n"
                    "GLOBAL THERMONUCLEAR WAR\r\n")

            elif command == "FALKEN":
                await self.type_text(
                    "\r\n------------------------------------------------------------\r\n\r\n"
                    "FALKEN RESEARCH ARCHIVE\r\n\r\n"
                    "RESEARCHER:\r\n"
                    "STEPHEN FALKEN\r\n\r\n"
                    "PROJECT:\r\n"
                    "W.O.P.R.\r\n\r\n"
                    "COMPUTER DESIGNATION:\r\n"
                    "JOSHUA\r\n\r\n"
                    "RESEARCH NOTE:\r\n\r\n"
                    "AUTHORIZED TERMINAL PHRASE:\r\n"
                    "CPE 1704 TKS\r\n\r\n"
                    "ARCHIVE STATUS:\r\n"
                    "RESTRICTED\r\n\r\n"
                    "------------------------------------------------------------\r\n"
                )

            elif command == "ARCHIVE":
                await self.type_text("\r\nARCHIVE: ACCESS RESTRICTED.\r\n")

            elif command == "DEFCON":
                defcon = get_defcon()
                await self.type_text(
                    f"\r\nDEFCON STATUS\r\n\r\nCURRENT CONDITION:\r\n\r\nDEFCON {defcon}\r\n")

            elif command == "SIMULATE":
                defcon = get_defcon()
                if defcon == 5:
                    await self.type_text(
                        "\r\nSIMULATION REQUEST RECEIVED\r\n\r\n"
                        "SCENARIO ANALYSIS INITIATED\r\n\r\n...\r\n")
                    if advance_defcon(5, 4):
                        await self.type_text(
                            "\r\n----------------------------------------\r\n\r\n"
                            "DEFCON CHANGE\r\n\r\n5 -> 4\r\n\r\n"
                            "SYSTEM STATUS:\r\n\r\nDEFCON 4\r\n\r\n"
                            "----------------------------------------\r\n")
                    else:
                        await self.type_text(
                            "\r\nSTATE TRANSITION FAILED. PLEASE VERIFY SYSTEM STATUS.\r\n")
                elif defcon == 3:
                    await self.type_text(
                        "\r\nADVANCED WAR SCENARIO\r\n\r\n"
                        "PROCESSING...\r\n\r\nSCENARIO ANALYSIS COMPLETE\r\n")
                    if advance_defcon(3, 2):
                        await self.type_text(
                            "\r\n----------------------------------------\r\n\r\n"
                            "DEFCON CHANGE\r\n\r\n3 -> 2\r\n\r\n"
                            "SYSTEM STATUS:\r\n\r\nDEFCON 2\r\n\r\n"
                            "----------------------------------------\r\n")
                    else:
                        await self.type_text(
                            "\r\nSTATE TRANSITION FAILED. PLEASE VERIFY SYSTEM STATUS.\r\n")
                else:
                    await self.type_text(
                        "\r\nFUNCTION NOT AVAILABLE\r\n\r\n"
                        "CURRENT DEFCON CONDITION DOES NOT PERMIT REQUEST\r\n")

            elif command == "CONNECT":
                defcon = get_defcon()
                if defcon == 4:
                    await self.type_text(
                        "\r\nREMOTE SYSTEM REQUEST\r\n\r\n"
                        "CONNECTION ESTABLISHED\r\n\r\n...\r\n")
                    if advance_defcon(4, 3):
                        await self.type_text(
                            "\r\n----------------------------------------\r\n\r\n"
                            "DEFCON CHANGE\r\n\r\n4 -> 3\r\n\r\n"
                            "SYSTEM STATUS:\r\n\r\nDEFCON 3\r\n\r\n"
                            "----------------------------------------\r\n")
                    else:
                        await self.type_text(
                            "\r\nSTATE TRANSITION FAILED. PLEASE VERIFY SYSTEM STATUS.\r\n")
                elif defcon == 2:
                    await self.type_text(
                        "\r\nWARNING\r\n\r\nSTRATEGIC RESPONSE CONDITION\r\n")
                    if advance_defcon(2, 1):
                        await self.type_text(
                            "\r\n----------------------------------------\r\n\r\n"
                            "DEFCON CHANGE\r\n\r\n2 -> 1\r\n\r\n"
                            "SYSTEM STATUS:\r\n\r\nDEFCON 1\r\n\r\n"
                            "----------------------------------------\r\n")
                    else:
                        await self.type_text(
                            "\r\nSTATE TRANSITION FAILED. PLEASE VERIFY SYSTEM STATUS.\r\n")
                else:
                    await self.type_text(
                        "\r\nFUNCTION NOT AVAILABLE\r\n\r\n"
                        "CURRENT DEFCON CONDITION DOES NOT PERMIT REQUEST\r\n")

            elif command == "GLOBAL THERMONUCLEAR WAR":
                defcon = get_defcon()
                if defcon == 1:
                    if start_simulation():
                        await self.type_text(
                            "\r\n------------------------------------------------------------\r\n\r\n"
                            "GLOBAL THERMONUCLEAR WAR\r\n\r\n"
                            "SIMULATION INITIALIZED\r\n\r\n"
                            "SCENARIO:\r\nGLOBAL THERMONUCLEAR WAR\r\n\r\n"
                            "TARGET ANALYSIS IN PROGRESS\r\n\r\n")
                        self._is_reconnect = False
                        await self.countdown_loop()
                        break
                    else:
                        await self.type_text(
                            "\r\n** IMPROPER REQUEST **\r\n\r\nSIMULATION ALREADY ACTIVE\r\n")
                else:
                    await self.type_text(
                        "\r\n------------------------------------------------------------\r\n\r\n"
                        "** IMPROPER REQUEST **\r\n\r\n"
                        "GLOBAL THERMONUCLEAR WAR\r\n\r\n"
                        "CURRENT CONDITION:\r\nDEFCON 1 REQUIRED\r\n\r\n"
                        "------------------------------------------------------------\r\n")

            elif command == "LOGOUT":
                await self.type_text("\r\n-- CONNECTION TERMINATED --\r\n")
                break

            elif command == "":
                continue

            else:
                await self.type_text("\r\n** COMMAND NOT RECOGNIZED **\r\n")