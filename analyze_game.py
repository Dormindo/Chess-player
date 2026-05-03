"""
Analisador de Partidas de Xadrez
Ferramenta educacional para estudar e analisar jogos
"""

import chess
import chess.pgn
import chess.engine
from pathlib import Path
import io


class ChessAnalyzer:
    """Analisa partidas de xadrez usando Stockfish"""
    
    def __init__(self, engine_path):
        self.engine_path = engine_path
        self.engine = None
        
    def setup_engine(self):
        """Inicializa o Stockfish"""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            print("✓ Stockfish pronto para análise")
            return True
        except Exception as e:
            print(f"✗ Erro ao carregar engine: {e}")
            return False
    
    def analyze_position(self, board, time_limit=1.0):
        """
        Analisa uma posição específica
        
        Returns:
            dict com: melhor movimento, avaliação, variante principal
        """
        if not self.engine:
            return None
        
        info = self.engine.analyse(board, chess.engine.Limit(time=time_limit))
        
        result = {
            'best_move': info.get('pv', [None])[0],
            'score': info.get('score'),
            'depth': info.get('depth'),
            'pv': info.get('pv', [])  # Principal variation
        }
        
        return result
    
    def analyze_game_from_pgn(self, pgn_string):
        """
        Analisa uma partida completa a partir de PGN
        
        Args:
            pgn_string: String com a notação PGN da partida
        """
        pgn = io.StringIO(pgn_string)
        game = chess.pgn.read_game(pgn)
        
        if not game:
            print("❌ Erro ao ler PGN")
            return
        
        # Informações da partida
        print("\n" + "="*60)
        print("📊 ANÁLISE DE PARTIDA")
        print("="*60)
        print(f"Brancas: {game.headers.get('White', 'Desconhecido')}")
        print(f"Pretas: {game.headers.get('Black', 'Desconhecido')}")
        print(f"Resultado: {game.headers.get('Result', '*')}")
        print(f"Data: {game.headers.get('Date', 'N/A')}")
        print("="*60)
        
        board = game.board()
        mistakes = []
        
        print("\n🔍 Analisando jogadas...\n")
        
        for move_num, move in enumerate(game.mainline_moves(), 1):
            # Analisa posição ANTES do movimento
            analysis_before = self.analyze_position(board, time_limit=0.5)
            
            if analysis_before:
                best_move = analysis_before['best_move']
                score_before = analysis_before['score']
                
                # Faz o movimento
                board.push(move)
                
                # Analisa posição DEPOIS do movimento
                analysis_after = self.analyze_position(board, time_limit=0.5)
                
                if analysis_after:
                    score_after = analysis_after['score']
                    
                    # Detecta erros (mudança significativa na avaliação)
                    if score_before and score_after:
                        # Converte scores para perspectiva das brancas
                        eval_before = self._score_to_cp(score_before, not board.turn)
                        eval_after = self._score_to_cp(score_after, not board.turn)
                        
                        diff = eval_before - eval_after
                        
                        # Se perdeu mais de 100 centipawns = erro
                        if abs(diff) > 100:
                            player = "Pretas" if board.turn else "Brancas"
                            mistakes.append({
                                'move_num': move_num,
                                'player': player,
                                'played': move,
                                'best': best_move,
                                'eval_loss': diff
                            })
                            
                            status = "❌ ERRO" if abs(diff) > 300 else "⚠️  Imprecisão"
                            print(f"Movimento {move_num}: {board.san(move)} - {status}")
                            print(f"  Melhor seria: {board.san(best_move) if best_move else 'N/A'}")
                            print(f"  Perda de avaliação: {diff:.0f} centipawns\n")
        
        # Resumo final
        print("\n" + "="*60)
        print("📈 RESUMO DA ANÁLISE")
        print("="*60)
        print(f"Total de movimentos: {move_num}")
        print(f"Erros detectados: {len(mistakes)}")
        
        if mistakes:
            print("\n🎯 Principais erros:")
            for i, mistake in enumerate(sorted(mistakes, key=lambda x: abs(x['eval_loss']), reverse=True)[:5], 1):
                print(f"\n{i}. Movimento {mistake['move_num']} ({mistake['player']})")
                print(f"   Jogou: {mistake['played'].uci()}")
                print(f"   Melhor: {mistake['best'].uci() if mistake['best'] else 'N/A'}")
                print(f"   Perda: {abs(mistake['eval_loss']):.0f} centipawns")
        
        print("="*60)
    
    def _score_to_cp(self, score, white_pov):
        """Converte Score para centipawns do ponto de vista das brancas"""
        if score.is_mate():
            # Mate em X movimentos
            mate_score = 10000 - abs(score.mate()) * 100
            return mate_score if score.mate() > 0 else -mate_score
        else:
            cp = score.score()
            return cp if white_pov else -cp
    
    def cleanup(self):
        """Fecha o engine"""
        if self.engine:
            self.engine.quit()


def example_analysis():
    """Exemplo de análise de uma partida famosa"""
    
    # PGN de exemplo: "Imortal" - Anderssen vs Kieseritzky (1851)
    pgn_example = """
[Event "London"]
[Site "London ENG"]
[Date "1851.06.21"]
[Round "?"]
[White "Adolf Anderssen"]
[Black "Lionel Adalbert Bagration Felix Kieseritzky"]
[Result "1-0"]

1. e4 e5 2. f4 exf4 3. Bc4 Qh4+ 4. Kf1 b5 5. Bxb5 Nf6 6. Nf3 Qh6 
7. d3 Nh5 8. Nh4 Qg5 9. Nf5 c6 10. g4 Nf6 11. Rg1 cxb5 12. h4 Qg6 
13. h5 Qg5 14. Qf3 Ng8 15. Bxf4 Qf6 16. Nc3 Bc5 17. Nd5 Qxb2 
18. Bd6 Bxg1 19. e5 Qxa1+ 20. Ke2 Na6 21. Nxg7+ Kd8 22. Qf6+ Nxf6 
23. Be7# 1-0
"""
    
    print("🎓 Exemplo: Analisando a 'Partida Imortal' (1851)")
    print("   Uma das partidas mais famosas da história do xadrez\n")
    
    # Configure o caminho do seu Stockfish aqui
    stockfish_path = None  # Ex: "/usr/local/bin/stockfish"
    
    if not stockfish_path:
        print("⚠️  Configure o caminho do Stockfish na variável 'stockfish_path'")
        return
    
    analyzer = ChessAnalyzer(stockfish_path)
    
    if analyzer.setup_engine():
        analyzer.analyze_game_from_pgn(pgn_example)
        analyzer.cleanup()


def analyze_your_game():
    """Analisa uma partida fornecida pelo usuário"""
    print("="*60)
    print("🎯 ANALISADOR DE PARTIDAS")
    print("="*60)
    print("\nCole o PGN da sua partida (Ctrl+D ou Ctrl+Z para finalizar):")
    print("(Você pode exportar PGN de qualquer partida no Chess.com)")
    print("-"*60)
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    pgn_text = "\n".join(lines)
    
    if not pgn_text.strip():
        print("\n❌ Nenhum PGN fornecido")
        return
    
    # Configure seu Stockfish
    stockfish_path = input("\nCaminho do Stockfish: ").strip()
    
    if not Path(stockfish_path).exists():
        print("❌ Stockfish não encontrado neste caminho")
        return
    
    analyzer = ChessAnalyzer(stockfish_path)
    
    if analyzer.setup_engine():
        analyzer.analyze_game_from_pgn(pgn_text)
        analyzer.cleanup()


if __name__ == "__main__":
    print("\n♟️  ANALISADOR DE XADREZ")
    print("\n1 - Analisar exemplo (Partida Imortal)")
    print("2 - Analisar sua partida (cole PGN)")
    print("0 - Sair")
    
    choice = input("\nEscolha: ").strip()
    
    if choice == "1":
        example_analysis()
    elif choice == "2":
        analyze_your_game()
    else:
        print("👋 Até logo!")
