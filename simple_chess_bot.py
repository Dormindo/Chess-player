"""
Bot de Xadrez Simplificado - Versão para Testes Locais
Jogue contra o Stockfish no terminal antes de testar online
"""

import chess
import chess.engine
import random
from pathlib import Path


class SimpleChessBot:
    """Bot simples para testes locais"""
    
    def __init__(self, engine_path=None):
        self.board = chess.Board()
        self.engine = None
        self.engine_path = engine_path
        
    def setup_engine(self):
        """Configura o Stockfish"""
        if self.engine_path and Path(self.engine_path).exists():
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
                print("✓ Stockfish carregado!")
                return True
            except Exception as e:
                print(f"✗ Erro ao carregar engine: {e}")
        return False
    
    def display_board(self):
        """Mostra o tabuleiro no terminal"""
        print("\n" + "="*40)
        print(self.board)
        print("="*40)
        print(f"FEN: {self.board.fen()}")
        print(f"Vez de: {'Brancas' if self.board.turn else 'Pretas'}")
        print()
    
    def get_player_move(self):
        """Pede movimento ao jogador humano"""
        while True:
            try:
                move_input = input("Seu movimento (ex: e2e4) ou 'sair': ").strip().lower()
                
                if move_input == 'sair':
                    return None
                
                # Tenta interpretar como UCI
                move = chess.Move.from_uci(move_input)
                
                if move in self.board.legal_moves:
                    return move
                else:
                    print("❌ Movimento ilegal! Tente novamente.")
                    self.show_legal_moves()
                    
            except ValueError:
                print("❌ Formato inválido! Use formato UCI (ex: e2e4)")
                print("   Origem e destino com letras minúsculas")
    
    def show_legal_moves(self):
        """Mostra alguns movimentos legais"""
        legal = list(self.board.legal_moves)[:10]
        print(f"Exemplos de movimentos legais: {', '.join([m.uci() for m in legal])}")
    
    def get_bot_move(self, difficulty=1.0):
        """
        Calcula movimento do bot
        
        Args:
            difficulty: Tempo de pensamento (segundos)
        """
        if self.engine:
            print(f"🤖 Bot pensando... ({difficulty}s)")
            result = self.engine.play(
                self.board, 
                chess.engine.Limit(time=difficulty)
            )
            return result.move
        else:
            # Sem engine: movimento aleatório
            legal_moves = list(self.board.legal_moves)
            return random.choice(legal_moves) if legal_moves else None
    
    def play_vs_human(self, bot_plays_white=False):
        """Joga contra humano"""
        print("\n🎮 PARTIDA: Humano vs Bot")
        print(f"Você joga com as {'Pretas' if bot_plays_white else 'Brancas'}")
        print("-" * 40)
        
        while not self.board.is_game_over():
            self.display_board()
            
            # Determina quem joga
            is_bot_turn = (self.board.turn == chess.WHITE) == bot_plays_white
            
            if is_bot_turn:
                # Turno do bot
                move = self.get_bot_move(difficulty=2.0)
                if move:
                    print(f"🤖 Bot jogou: {move.uci()} ({self.board.san(move)})")
                    self.board.push(move)
            else:
                # Turno do humano
                move = self.get_player_move()
                if move is None:
                    print("\n👋 Partida encerrada pelo jogador")
                    return
                self.board.push(move)
        
        # Fim de jogo
        self.display_board()
        self.show_result()
    
    def play_bot_vs_bot(self, time_per_move=1.0):
        """Dois bots jogam entre si"""
        print("\n🤖 PARTIDA: Bot vs Bot")
        print("-" * 40)
        
        move_count = 0
        
        while not self.board.is_game_over() and move_count < 100:
            self.display_board()
            
            move = self.get_bot_move(difficulty=time_per_move)
            if move:
                player = "Brancas" if self.board.turn else "Pretas"
                print(f"🤖 {player}: {move.uci()} ({self.board.san(move)})")
                self.board.push(move)
                move_count += 1
                
                input("Pressione ENTER para continuar...")
            else:
                break
        
        self.display_board()
        self.show_result()
    
    def show_result(self):
        """Mostra o resultado final"""
        print("\n" + "="*40)
        print("🏁 FIM DE JOGO")
        print("="*40)
        
        if self.board.is_checkmate():
            winner = "Pretas" if self.board.turn == chess.WHITE else "Brancas"
            print(f"🏆 Xeque-mate! {winner} venceram!")
        elif self.board.is_stalemate():
            print("🤝 Empate por afogamento!")
        elif self.board.is_insufficient_material():
            print("🤝 Empate por material insuficiente!")
        elif self.board.is_fifty_moves():
            print("🤝 Empate pela regra dos 50 movimentos!")
        elif self.board.is_repetition():
            print("🤝 Empate por repetição!")
        else:
            print("Partida encerrada")
        
        print(f"\nTotal de movimentos: {self.board.fullmove_number}")
        print("="*40)
    
    def cleanup(self):
        """Encerra o engine"""
        if self.engine:
            self.engine.quit()


def main():
    """Menu principal"""
    print("="*50)
    print("♟️  BOT DE XADREZ - TESTE LOCAL")
    print("="*50)
    
    # Caminho do Stockfish (ajuste conforme necessário)
    stockfish_path = None  # Ou: "/usr/local/bin/stockfish"
    
    bot = SimpleChessBot(stockfish_path)
    
    # Tenta carregar o engine
    has_engine = bot.setup_engine()
    if not has_engine:
        print("\n⚠️  Stockfish não encontrado - usando movimentos aleatórios")
        print("   Baixe em: https://stockfishchess.org/download/\n")
    
    # Menu
    print("\nMODOS DE JOGO:")
    print("1 - Jogar contra o bot (você: Brancas)")
    print("2 - Jogar contra o bot (você: Pretas)")
    print("3 - Bot vs Bot (demonstração)")
    print("0 - Sair")
    
    try:
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            bot.play_vs_human(bot_plays_white=False)
        elif choice == "2":
            bot.play_vs_human(bot_plays_white=True)
        elif choice == "3":
            bot.play_bot_vs_bot(time_per_move=0.5)
        else:
            print("👋 Até logo!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido")
    finally:
        bot.cleanup()


if __name__ == "__main__":
    main()
