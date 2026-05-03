"""
Bot de Xadrez para Chess.com - VERSÃO ATUALIZADA 2.0
Com seletores robustos e múltiplas estratégias de localização
"""

import chess
import chess.engine
import chess.pgn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from pathlib import Path
import re


class ChessComBotV2:
    """
    Bot atualizado com múltiplas estratégias de localização de casas
    """
    
    def __init__(self, username, password, engine_path=None):
        self.username = username
        self.password = password
        self.driver = None
        self.board = chess.Board()
        self.engine = None
        self.engine_path = engine_path
        self.wait = None
        
    def setup_browser(self):
        """Configura o navegador Chrome"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        print("✓ Navegador configurado")
        
    def login(self):
        """Faz login no Chess.com"""
        try:
            self.driver.get("https://www.chess.com/login")
            time.sleep(2)
            
            # Preenche credenciais
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            
            time.sleep(5)
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
                print("  Continuando sem engine")
        else:
            print("⚠ Engine não configurado - usando movimentos aleatórios")
    
    def start_game(self, game_url=None):
        """Inicia uma partida"""
        if game_url:
            self.driver.get(game_url)
        else:
            self.driver.get("https://www.chess.com/play/online")
        
        time.sleep(5)
        print("✓ Na página de jogo")
        
    def find_square_element(self, square_name):
        """
        Encontra o elemento de uma casa usando múltiplas estratégias
        
        Args:
            square_name: Nome da casa em notação algébrica (ex: "e2")
            
        Returns:
            WebElement ou None
        """
        strategies = [
            # Estratégia 1: data-square attribute
            lambda: self.driver.find_element(By.CSS_SELECTOR, f"[data-square='{square_name}']"),
            
            # Estratégia 2: class contendo o nome da casa
            lambda: self.driver.find_element(By.CSS_SELECTOR, f".square-{square_name}"),
            
            # Estratégia 3: class com número da casa (a1=11, h8=88)
            lambda: self.driver.find_element(By.CSS_SELECTOR, f".square-{self._square_to_number(square_name)}"),
            
            # Estratégia 4: Procura por aria-label
            lambda: self.driver.find_element(By.CSS_SELECTOR, f"[aria-label*='{square_name}']"),
            
            # Estratégia 5: XPath genérico
            lambda: self.driver.find_element(By.XPATH, f"//*[contains(@class, 'square') and contains(@class, '{square_name}')]"),
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                element = strategy()
                if element:
                    print(f"  ✓ Casa {square_name} encontrada (estratégia {i})")
                    return element
            except:
                continue
        
        print(f"  ✗ Casa {square_name} não encontrada com nenhuma estratégia")
        return None
    
    def _square_to_number(self, square_name):
        """
        Converte notação algébrica para número (a1=11, h8=88)
        Chess.com às vezes usa este formato
        """
        file_map = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
        file_letter = square_name[0]
        rank = square_name[1]
        return int(str(file_map[file_letter]) + rank)
    
    def get_all_squares(self):
        """Debug: mostra todas as casas encontradas no tabuleiro"""
        try:
            # Tenta encontrar todas as casas possíveis
            squares = self.driver.find_elements(By.CSS_SELECTOR, "[class*='square']")
            print(f"\n🔍 Debug: Encontradas {len(squares)} casas")
            
            # Mostra as primeiras 5
            for i, sq in enumerate(squares[:5]):
                classes = sq.get_attribute("class")
                data_square = sq.get_attribute("data-square")
                print(f"  Casa {i+1}: class='{classes}' data-square='{data_square}'")
            
            return squares
        except Exception as e:
            print(f"Debug erro: {e}")
            return []
    
    def make_move_by_coordinates(self, move):
        """
        Faz o movimento clicando nas coordenadas das casas
        Método alternativo quando seletores CSS não funcionam
        """
        try:
            move_uci = move.uci()
            from_square = move_uci[:2]
            to_square = move_uci[2:4]
            
            print(f"🎯 Tentando movimento: {from_square} → {to_square}")
            
            # Primeiro tenta mostrar todas as casas (debug)
            if not hasattr(self, '_debug_shown'):
                self.get_all_squares()
                self._debug_shown = True
            
            # Encontra as casas
            from_element = self.find_square_element(from_square)
            to_element = self.find_square_element(to_square)
            
            if not from_element or not to_element:
                print("  ⚠ Não foi possível localizar as casas")
                return False
            
            # Executa o movimento
            actions = ActionChains(self.driver)
            
            # Método 1: Click → Click
            try:
                from_element.click()
                time.sleep(0.3)
                to_element.click()
                print(f"  ✓ Movimento executado: {move_uci} ({self.board.san(move)})")
                self.board.push(move)
                return True
            except:
                pass
            
            # Método 2: Drag and Drop
            try:
                actions.drag_and_drop(from_element, to_element).perform()
                print(f"  ✓ Movimento executado (drag): {move_uci}")
                self.board.push(move)
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"  ✗ Erro ao executar movimento: {e}")
            return False
    
    def get_move_from_notation(self):
        """
        Método alternativo: lê os movimentos da notação da partida
        ao invés de tentar ler o tabuleiro visual
        """
        try:
            # Chess.com geralmente mostra os movimentos em uma lista
            move_elements = self.driver.find_elements(By.CSS_SELECTOR, ".move-text-component, .node, .move")
            
            if move_elements:
                moves = [elem.text.strip() for elem in move_elements if elem.text.strip()]
                print(f"  📋 Movimentos lidos: {' '.join(moves[-5:])}")  # Últimos 5
                
                # Reconstrói o tabuleiro
                temp_board = chess.Board()
                for move_text in moves:
                    try:
                        # Remove números de movimento e caracteres extras
                        clean_move = re.sub(r'^\d+\.+\s*', '', move_text)
                        clean_move = clean_move.replace('+', '').replace('#', '').replace('!', '').replace('?', '')
                        
                        if clean_move:
                            move = temp_board.parse_san(clean_move)
                            temp_board.push(move)
                    except:
                        continue
                
                self.board = temp_board
                return True
                
        except Exception as e:
            print(f"  ⚠ Erro ao ler notação: {e}")
        
        return False
    
    def calculate_best_move(self, time_limit=1.0):
        """Calcula o melhor movimento"""
        if self.engine:
            result = self.engine.play(self.board, chess.engine.Limit(time=time_limit))
            return result.move
        else:
            import random
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                return random.choice(legal_moves)
        return None
    
    def wait_for_opponent(self, timeout=30):
        """Espera o oponente jogar"""
        print("⏳ Aguardando movimento do oponente...")
        
        old_move_count = self.board.fullmove_number
        
        for _ in range(timeout):
            time.sleep(1)
            
            # Tenta atualizar o tabuleiro pela notação
            self.get_move_from_notation()
            
            # Verifica se houve novo movimento
            if self.board.fullmove_number > old_move_count:
                print("  ✓ Oponente jogou!")
                return True
        
        print("  ⏱ Timeout esperando oponente")
        return False
    
    def play_game_interactive(self):
        """
        Modo interativo: você aprova cada movimento
        Mais seguro para testes
        """
        print("\n🎮 MODO INTERATIVO\n")
        print("O bot vai sugerir movimentos e você decide se executa\n")
        
        move_count = 0
        
        while not self.board.is_game_over() and move_count < 50:
            print(f"\n--- Turno {move_count + 1} ---")
            print(f"Posição atual: {self.board.fen()}")
            
            # Atualiza estado lendo a notação
            self.get_move_from_notation()
            
            # Mostra o tabuleiro
            print("\n" + str(self.board) + "\n")
            
            # Calcula melhor movimento
            best_move = self.calculate_best_move(time_limit=2.0)
            
            if not best_move:
                print("❌ Sem movimentos legais")
                break
            
            print(f"💡 Movimento sugerido: {best_move.uci()} ({self.board.san(best_move)})")
            
            choice = input("Executar? (s/n/sair): ").strip().lower()
            
            if choice == 'sair':
                break
            elif choice == 's':
                if self.make_move_by_coordinates(best_move):
                    move_count += 1
                    time.sleep(2)
                else:
                    print("❌ Falha ao executar - tente manualmente")
                    input("Pressione ENTER após jogar manualmente...")
            else:
                print("⏭ Movimento pulado")
        
        self.show_result()
    
    def show_result(self):
        """Mostra resultado final"""
        print("\n" + "="*50)
        if self.board.is_checkmate():
            winner = "Pretas" if self.board.turn == chess.WHITE else "Brancas"
            print(f"🏆 Xeque-mate! {winner} venceram!")
        elif self.board.is_stalemate():
            print("🤝 Empate por afogamento!")
        else:
            print("🏁 Jogo encerrado")
        print("="*50)
    
    def cleanup(self):
        """Limpa recursos"""
        if self.engine:
            self.engine.quit()
            print("✓ Engine encerrado")
        
        # Mantém navegador aberto para inspeção
        print("ℹ Navegador mantido aberto para você verificar")


def main():
    """Função principal"""
    print("="*60)
    print("🤖 BOT DE XADREZ V2.0 - CHESS.COM")
    print("="*60)
    
    # CONFIGURAÇÕES - ALTERE AQUI
    USERNAME = "pzww"  # ← MUDE AQUI
    PASSWORD = "Khvsarbx@120110"    # ← MUDE AQUI
    STOCKFISH_PATH = None     # ← Caminho do Stockfish (opcional)
    
    # Exemplo Windows: r"C:\stockfish\stockfish.exe"
    # Exemplo Linux: "/usr/games/stockfish"
    
    bot = ChessComBotV2(USERNAME, PASSWORD, STOCKFISH_PATH)
    
    try:
        bot.setup_browser()
        bot.login()
        bot.setup_engine()
        
        print("\n🎯 Instruções:")
        print("1. O navegador vai abrir no Chess.com")
        print("2. Inicie uma partida MANUALMENTE")
        print("3. Volte para este terminal e pressione ENTER")
        print("4. O bot vai operar em modo interativo")
        
        input("\n▶ Pressione ENTER quando estiver em uma partida...")
        
        bot.play_game_interactive()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrompido pelo usuário")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bot.cleanup()
        input("\nPressione ENTER para fechar o navegador...")
        if bot.driver:
            bot.driver.quit()


if __name__ == "__main__":
    main()