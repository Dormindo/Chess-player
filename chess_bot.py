"""
Bot de Xadrez para Chess.com
Trabalho Escolar - Inteligência Artificial aplicada a jogos
"""

import chess
import chess.engine
import chess.pgn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from pathlib import Path


class ChessComBot:
    """
    Bot automatizado para jogar xadrez no Chess.com
    """
    
    def __init__(self, username, password, engine_path=None):
        """
        Inicializa o bot
        
        Args:
            username: Seu usuário do Chess.com
            password: Sua senha do Chess.com
            engine_path: Caminho para o engine Stockfish (opcional)
        """
        self.username = username
        self.password = password
        self.driver = None
        self.board = chess.Board()
        self.engine = None
        self.engine_path = engine_path
        
    def setup_browser(self):
        """Configura o navegador Chrome"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # Descomente para rodar em modo headless (sem interface gráfica)
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        print("✓ Navegador configurado")
        
    def login(self):
        """Faz login no Chess.com"""
        try:
            self.driver.get("https://www.chess.com/login")
            time.sleep(2)
            
            # Preenche credenciais
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            
            time.sleep(3)
            print("✓ Login realizado")
            
        except Exception as e:
            print(f"✗ Erro no login: {e}")
            
    def setup_engine(self):
        """Configura o engine de xadrez (Stockfish)"""
        if self.engine_path and Path(self.engine_path).exists():
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
                print("✓ Engine Stockfish carregado")
            except Exception as e:
                print(f"✗ Erro ao carregar engine: {e}")
                print("  Continuando sem engine (apenas movimentos legais aleatórios)")
        else:
            print("⚠ Engine não configurado - usando movimentos aleatórios")
    
    def start_game(self, game_url=None):
        """
        Inicia uma partida
        
        Args:
            game_url: URL de uma partida específica (opcional)
        """
        if game_url:
            self.driver.get(game_url)
        else:
            # Vai para a página de jogar online
            self.driver.get("https://www.chess.com/play/online")
        
        time.sleep(3)
        print("✓ Partida iniciada")
        
    def get_board_state(self):
        """
        Lê o estado atual do tabuleiro do Chess.com
        Retorna a posição FEN
        """
        try:
            # Chess.com usa classes específicas para as peças
            # Este é um exemplo - você precisará adaptar aos seletores atuais
            
            # Método alternativo: capturar os movimentos da partida
            moves_element = self.driver.find_elements(By.CLASS_NAME, "move")
            
            # Reconstrói o tabuleiro a partir dos movimentos
            self.board = chess.Board()
            for move_elem in moves_element:
                move_text = move_elem.text
                try:
                    move = self.board.parse_san(move_text)
                    self.board.push(move)
                except:
                    continue
                    
            return self.board.fen()
            
        except Exception as e:
            print(f"⚠ Erro ao ler tabuleiro: {e}")
            return None
    
    def calculate_best_move(self, time_limit=1.0):
        """
        Calcula o melhor movimento
        
        Args:
            time_limit: Tempo em segundos para pensar
            
        Returns:
            Objeto chess.Move com o melhor movimento
        """
        if self.engine:
            # Usa o Stockfish para calcular
            result = self.engine.play(self.board, chess.engine.Limit(time=time_limit))
            return result.move
        else:
            # Sem engine: escolhe movimento legal aleatório
            import random
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                return random.choice(legal_moves)
        return None
    
    def make_move(self, move):
        """
        Executa o movimento no Chess.com
        
        Args:
            move: Objeto chess.Move
        """
        try:
            # Converte o movimento para formato UCI (ex: "e2e4")
            move_uci = move.uci()
            from_square = move_uci[:2]
            to_square = move_uci[2:4]
            
            # Encontra e clica na casa de origem
            from_selector = f"[data-square='{from_square}']"
            from_element = self.driver.find_element(By.CSS_SELECTOR, from_selector)
            from_element.click()
            
            time.sleep(0.3)
            
            # Encontra e clica na casa de destino
            to_selector = f"[data-square='{to_square}']"
            to_element = self.driver.find_element(By.CSS_SELECTOR, to_selector)
            to_element.click()
            
            # Atualiza o tabuleiro interno
            self.board.push(move)
            
            print(f"✓ Movimento executado: {move_uci} ({self.board.san(move)})")
            
        except Exception as e:
            print(f"✗ Erro ao executar movimento: {e}")
    
    def wait_for_opponent(self, timeout=30):
        """Espera o oponente jogar"""
        print("⏳ Aguardando movimento do oponente...")
        time.sleep(3)  # Tempo básico de espera
        
    def play_game(self):
        """Loop principal do jogo"""
        print("\n🎮 Iniciando partida automática!\n")
        
        move_count = 0
        max_moves = 100  # Limite de segurança
        
        while not self.board.is_game_over() and move_count < max_moves:
            # Verifica de quem é a vez
            if self.board.turn == chess.WHITE:
                print(f"\n--- Movimento {move_count + 1} (Brancas) ---")
            else:
                print(f"\n--- Movimento {move_count + 1} (Pretas) ---")
            
            # Atualiza estado do tabuleiro
            self.get_board_state()
            
            # Calcula e executa movimento
            best_move = self.calculate_best_move(time_limit=2.0)
            
            if best_move:
                self.make_move(best_move)
                move_count += 1
                
                # Espera o oponente
                self.wait_for_opponent()
            else:
                print("⚠ Nenhum movimento legal encontrado")
                break
        
        # Fim da partida
        print("\n" + "="*50)
        if self.board.is_checkmate():
            winner = "Pretas" if self.board.turn == chess.WHITE else "Brancas"
            print(f"🏆 Xeque-mate! {winner} venceram!")
        elif self.board.is_stalemate():
            print("🤝 Empate por afogamento!")
        elif self.board.is_insufficient_material():
            print("🤝 Empate por material insuficiente!")
        else:
            print("🏁 Partida encerrada")
        print("="*50)
    
    def cleanup(self):
        """Limpa recursos"""
        if self.engine:
            self.engine.quit()
            print("✓ Engine encerrado")
        
        if self.driver:
            # Não fecha o navegador automaticamente para você ver o resultado
            # self.driver.quit()
            print("ℹ Navegador mantido aberto")


def main():
    """Função principal"""
    print("="*50)
    print("🤖 BOT DE XADREZ - CHESS.COM")
    print("="*50)
    
    # Configurações
    USERNAME = "seu_usuario"  # ALTERE AQUI
    PASSWORD = "sua_senha"    # ALTERE AQUI
    
    # Caminho para o Stockfish (baixe em https://stockfishchess.org/)
    # Exemplos:
    # Windows: r"C:\stockfish\stockfish.exe"
    # Linux/Mac: "/usr/local/bin/stockfish"
    STOCKFISH_PATH = None  # Ou coloque o caminho
    
    # Cria e configura o bot
    bot = ChessComBot(USERNAME, PASSWORD, STOCKFISH_PATH)
    
    try:
        bot.setup_browser()
        bot.login()
        bot.setup_engine()
        bot.start_game()
        bot.play_game()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrompido pelo usuário")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
    finally:
        bot.cleanup()


if __name__ == "__main__":
    main()
