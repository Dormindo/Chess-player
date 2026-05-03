#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chess.com Bot Autonomo V3.0
Funciona com wc-chess-board (2025/2026)

Sistema de coordenadas Chess.com:
- Casas numeradas de 11 a 88
- Primeiro digito: coluna (a=1, b=2, ..., h=8)
- Segundo digito: linha (1-8)
- Exemplo: e2 = 51, e4 = 54
"""

import chess
import chess.engine
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from pathlib import Path
from datetime import datetime


class ChessComAutonomousBot:
    FILE_MAP = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    REVERSE_FILE_MAP = {v: k for k, v in FILE_MAP.items()}

    def __init__(self, username, password, engine_path=None, headless=False):
        self.username = username
        self.password = password
        self.engine_path = engine_path
        self.headless = headless
        self.driver = None
        self.wait = None
        self.engine = None
        self.board = chess.Board()
        self.my_color = None
        self.game_active = False
        self.last_fen = None
        self.move_count = 0

    def setup_browser(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        )
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 1,
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.wait = WebDriverWait(self.driver, 15)
        print("[OK] Navegador configurado")

    def setup_engine(self):
        if self.engine_path and Path(self.engine_path).exists():
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
                self.engine.configure({"Hash": 128, "Threads": 2, "Skill Level": 20})
                print(f"[OK] Stockfish: {self.engine_path}")
                return True
            except Exception as e:
                print(f"[!] Erro Stockfish: {e}")
        print("[!] Sem engine - usando movimentos aleatorios")
        return False

    def login(self):
        print("[*] Fazendo login...")
        self.driver.get("https://www.chess.com/login")
        time.sleep(3)
        try:
            self._accept_cookies()
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_field = self.driver.find_element(By.ID, "password")
            username_field.clear()
            username_field.send_keys(self.username)
            time.sleep(0.5)
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(0.5)
            login_btn = self.driver.find_element(By.ID, "login")
            login_btn.click()
            time.sleep(5)
            if "login" not in self.driver.current_url:
                print("[OK] Login realizado!")
                return True
            else:
                print("[ERRO] Falha no login")
                return False
        except Exception as e:
            print(f"[ERRO] Login: {e}")
            return False

    def _accept_cookies(self):
        try:
            cookie_btn = self.driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler")
            cookie_btn.click()
            time.sleep(1)
        except:
            pass

    def go_to_play_computer(self):
        print("[*] Indo para Play vs Computer...")
        self.driver.get("https://www.chess.com/play/computer")
        time.sleep(5)
        self._close_modals()
        if "play/computer" in self.driver.current_url:
            print("[OK] Na pagina de jogo")
            return True
        return False

    def _close_modals(self):
        selectors = ["[data-cy='close-button']", ".modal-close-button", "button[aria-label='Close']"]
        for selector in selectors:
            try:
                for elem in self.driver.find_elements(By.CSS_SELECTOR, selector):
                    if elem.is_displayed():
                        elem.click()
                        time.sleep(0.5)
            except:
                pass

    @classmethod
    def algebraic_to_chesscom(cls, square):
        if isinstance(square, str) and len(square) == 2:
            file_num = cls.FILE_MAP[square[0].lower()]
            rank = int(square[1])
            return int(f"{file_num}{rank}")
        return square

    @classmethod
    def chesscom_to_algebraic(cls, number):
        num_str = str(number)
        if len(num_str) == 2:
            return f"{cls.REVERSE_FILE_MAP[int(num_str[0])]}{num_str[1]}"
        return str(number)

    @classmethod
    def uci_to_chesscom_squares(cls, uci_move):
        return (cls.algebraic_to_chesscom(uci_move[:2]),
                cls.algebraic_to_chesscom(uci_move[2:4]))

    def get_board_state_js(self):
        script = """
        function getBoardState() {
            const board = document.querySelector('wc-chess-board');
            if (!board) return null;
            const pieces = board.querySelectorAll('.piece');
            const state = {};
            pieces.forEach(piece => {
                const classes = piece.className.split(' ');
                const pieceClass = classes.find(c => c.length === 2 &&
                    (c.startsWith('w') || c.startsWith('b')));
                const squareClass = classes.find(c => c.startsWith('square-'));
                if (pieceClass && squareClass) {
                    state[squareClass.replace('square-', '')] = pieceClass;
                }
            });
            const coords = board.querySelector('.coordinates');
            const isFlipped = coords ? coords.classList.contains('flipped') : false;
            return {pieces: state, isFlipped: isFlipped, pieceCount: pieces.length};
        }
        return getBoardState();
        """
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            print(f"[!] Erro ao ler tabuleiro: {e}")
            return None

    def get_board_fen(self):
        state = self.get_board_state_js()
        if not state or not state.get('pieces'):
            return None
        pieces = state['pieces']
        is_flipped = state.get('isFlipped', False)
        board_array = [['' for _ in range(8)] for _ in range(8)]
        for square_num, piece in pieces.items():
            num = int(square_num)
            file_idx = (num // 10) - 1
            rank_idx = (num % 10) - 1
            if is_flipped:
                file_idx = 7 - file_idx
                rank_idx = 7 - rank_idx
            if 0 <= file_idx < 8 and 0 <= rank_idx < 8:
                color = piece[0]
                ptype = piece[1]
                fen_char = ptype.upper() if color == 'w' else ptype.lower()
                board_array[7 - rank_idx][file_idx] = fen_char
        fen_rows = []
        for row in board_array:
            fen_row = ''
            empty = 0
            for cell in row:
                if cell == '':
                    empty += 1
                else:
                    if empty > 0:
                        fen_row += str(empty)
                        empty = 0
                    fen_row += cell
            if empty > 0:
                fen_row += str(empty)
            fen_rows.append(fen_row)
        return '/'.join(fen_rows)

    def detect_my_color(self):
        state = self.get_board_state_js()
        if not state:
            return None
        pieces = state['pieces']
        is_flipped = state.get('isFlipped', False)
        white_bottom = 0
        black_bottom = 0
        for square_num, piece in pieces.items():
            num = int(square_num)
            rank = num % 10
            if not is_flipped:
                if rank <= 2 and piece.startswith('w'):
                    white_bottom += 1
                elif rank <= 2 and piece.startswith('b'):
                    black_bottom += 1
            else:
                if rank <= 2 and piece.startswith('b'):
                    black_bottom += 1
                elif rank <= 2 and piece.startswith('w'):
                    white_bottom += 1
        if white_bottom >= 6:
            self.my_color = 'white'
        elif black_bottom >= 6:
            self.my_color = 'black'
        else:
            self.my_color = 'white'
        print(f"[INFO] Cor: {self.my_color.upper()}")
        return self.my_color

    def is_my_turn(self):
        current_fen = self.get_board_fen()
        if not current_fen:
            return False
        try:
            temp_board = chess.Board(current_fen)
            if not self.my_color:
                self.detect_my_color()
            is_white_turn = temp_board.turn == chess.WHITE
            return is_white_turn if self.my_color == 'white' else not is_white_turn
        except Exception as e:
            print(f"[!] Erro turno: {e}")
            return False

    def click_square(self, square_num):
        script = "return (function(sq){" +             "var b=document.querySelector('wc-chess-board');" +             "if(!b)return false;" +             "var s=b.querySelector('.square-'+sq);" +             "if(!s)return false;" +             "var r=s.getBoundingClientRect();" +             "var cx=r.left+r.width/2;" +             "var cy=r.top+r.height/2;" +             "['mousedown','mouseup','click'].forEach(function(et){" +             "var ev=new MouseEvent(et,{bubbles:true,cancelable:true,view:window,clientX:cx,clientY:cy,button:0});" +             "s.dispatchEvent(ev);" +             "});" +             "return true;" +             "})(" + str(square_num) + ")"
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            print(f"[!] Erro click {square_num}: {e}")
            return False

    def make_move(self, move_uci):
        from_sq, to_sq = self.uci_to_chesscom_squares(move_uci)
        print(f"[MOVE] {move_uci} ({from_sq}->{to_sq})")
        if not self.click_square(from_sq):
            print(f"[ERRO] Origem {from_sq}")
            return False
        time.sleep(0.3)
        if not self.click_square(to_sq):
            print(f"[ERRO] Destino {to_sq}")
            return False
        time.sleep(0.5)
        if len(move_uci) == 5:
            self._handle_promotion(move_uci[4].upper())
        print(f"[OK] Movimento: {move_uci}")
        return True

    def _handle_promotion(self, piece):
        piece_map = {'Q': 'queen', 'R': 'rook', 'B': 'bishop', 'N': 'knight'}
        piece_name = piece_map.get(piece, 'queen')
        try:
            promo = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"[data-piece='{piece_name}'], .promotion-piece")))
            promo.click()
            time.sleep(0.5)
        except:
            print(f"[!] Promocao {piece} falhou")

    def calculate_best_move(self, time_limit=1.0):
        if not self.engine:
            return self._get_random_move()
        try:
            current_fen = self.get_board_fen()
            if not current_fen:
                return self._get_random_move()
            self.board.set_fen(current_fen)
            result = self.engine.play(self.board, chess.engine.Limit(time=time_limit))
            return result.move
        except Exception as e:
            print(f"[!] Engine erro: {e}")
            return self._get_random_move()

    def _get_random_move(self):
        try:
            current_fen = self.get_board_fen()
            if current_fen:
                self.board.set_fen(current_fen)
            legal = list(self.board.legal_moves)
            if legal:
                import random
                return random.choice(legal)
        except:
            pass
        return None

    def wait_for_game_start(self, timeout=60):
        print("[*] Aguardando partida...")
        for i in range(timeout):
            state = self.get_board_state_js()
            if state and state.get('pieceCount', 0) >= 32:
                print("[OK] Partida detectada!")
                time.sleep(2)
                self.detect_my_color()
                self.game_active = True
                return True
            time.sleep(1)
        print("[TIMEOUT]")
        return False

    def play_turn(self, think_time=1.0):
        if not self.is_my_turn():
            return False
        print(f"\n[*] Minha vez! (#{self.move_count + 1})")
        move = self.calculate_best_move(time_limit=think_time)
        if not move:
            print("[ERRO] Sem movimento")
            return False
        move_uci = move.uci()
        move_san = self.board.san(move)
        print(f"[ENGINE] {move_san} ({move_uci})")
        if self.make_move(move_uci):
            self.board.push(move)
            self.move_count += 1
            self.last_fen = self.board.fen()
            return True
        return False

    def wait_opponent_move(self, timeout=30):
        print("[*] Aguardando oponente...")
        initial_fen = self.get_board_fen()
        for i in range(timeout):
            time.sleep(1)
            current_fen = self.get_board_fen()
            if current_fen and current_fen != initial_fen:
                print("[OK] Oponente jogou!")
                try:
                    self.board.set_fen(current_fen)
                except:
                    pass
                return True
        print("[TIMEOUT] Oponente")
        return False

    def check_game_over(self):
        try:
            modals = self.driver.find_elements(By.CSS_SELECTOR,
                "[data-cy='game-over-modal'], .game-over-modal")
            for m in modals:
                if m.is_displayed():
                    return True
            script = "return document.querySelector('.game-over, .result') !== null;"
            return self.driver.execute_script(script)
        except:
            return False

    def run_game_loop(self, think_time=1.0, max_moves=100):
        print("\n" + "="*60)
        print("[*] MODO AUTONOMO")
        print("="*60)
        if not self.wait_for_game_start():
            print("[ERRO] Sem partida")
            return
        while self.move_count < max_moves:
            if self.check_game_over():
                print("[FIM] Jogo terminou!")
                break
            if self.is_my_turn():
                self.play_turn(think_time=think_time)
                time.sleep(1)
            else:
                if not self.wait_opponent_move(timeout=60):
                    if self.is_my_turn():
                        continue
                    else:
                        time.sleep(2)
            time.sleep(0.5)
        print("\n" + "="*60)
        print(f"[STATS] Movimentos: {self.move_count}")
        print("="*60)

    def take_screenshot(self, filename=None):
        if not filename:
            filename = f"chess_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.driver.save_screenshot(filename)
        print(f"[SCREEN] {filename}")
        return filename

    def cleanup(self):
        print("\n[*] Limpando...")
        if self.engine:
            try:
                self.engine.quit()
                print("[OK] Engine")
            except:
                pass
        if self.driver:
            try:
                self.driver.quit()
                print("[OK] Browser")
            except:
                pass

    def __del__(self):
        self.cleanup()


def main():
    print("="*70)
    print("[*] CHESS.COM BOT AUTONOMO V3.0")
    print("="*70)
    print()

    USERNAME = "none"
    PASSWORD = "none"
    STOCKFISH_PATH = None
    TEMPO_PENSAMENTO = 1.0
    MODO_HEADLESS = False

    if USERNAME == "seu_usuario" or PASSWORD == "sua_senha":
        print("[ERRO] Configure usuario e senha!")
        return

    bot = ChessComAutonomousBot(
        username=USERNAME,
        password=PASSWORD,
        engine_path=STOCKFISH_PATH,
        headless=MODO_HEADLESS
    )

    try:
        bot.setup_browser()
        bot.driver.get("https://www.chess.com/login")
        print("\n[*] Faça login manualmente no navegador...")
        input("Pressione ENTER após concluir o login...")
        bot.setup_engine()

        print("\n" + "="*70)
        print("MODO:")
        print("1. Play vs Computer")
        print("2. Play Online")
        print("3. URL especifica")
        print()

        choice = input("Opcao (1/2/3): ").strip()

        if choice == "1":
            bot.go_to_play_computer()
            print("\n[*] Selecione bot e inicie manualmente...")
            input("Pressione ENTER quando pronto...")
        elif choice == "2":
            bot.driver.get("https://www.chess.com/play/online")
            print("\n[*] Inicie partida online...")
            input("Pressione ENTER quando comecar...")
        elif choice == "3":
            url = input("URL: ").strip()
            bot.driver.get(url)
            input("Pressione ENTER quando ativa...")
        else:
            print("[ERRO] Invalido")
            return

        bot.run_game_loop(think_time=TEMPO_PENSAMENTO)

        while True:
            again = input("\n[*] Novamente? (s/n): ").strip().lower()
            if again == 's':
                bot.board = chess.Board()
                bot.move_count = 0
                bot.run_game_loop(think_time=TEMPO_PENSAMENTO)
            else:
                break

    except KeyboardInterrupt:
        print("\n\n[!] Interrompido")
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
    finally:
        bot.cleanup()
        print("\n[*] Tchau!")


if __name__ == "__main__":
    main()
