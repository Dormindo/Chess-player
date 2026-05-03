"""
Ferramenta de Diagnóstico - Chess.com
Inspeciona a estrutura do site para ajudar a corrigir seletores
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


class ChessComInspector:
    """Inspeciona a estrutura HTML do Chess.com"""
    
    def __init__(self):
        self.driver = None
        
    def setup_browser(self):
        """Configura navegador"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=options)
        print("✓ Navegador aberto")
        
    def inspect_board(self):
        """Analisa a estrutura do tabuleiro"""
        print("\n" + "="*70)
        print("🔍 INSPEÇÃO DO TABULEIRO")
        print("="*70)
        
        # Procura por diferentes tipos de containers
        selectors = [
            "div[class*='board']",
            "div[class*='chess']",
            "div[id*='board']",
            "svg[class*='board']",
            ".board",
            "#board-layout-main",
            ".game-board",
            "[class*='chessboard']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\n✓ Encontrado: {selector} ({len(elements)} elemento(s))")
                    
                    # Mostra atributos do primeiro elemento
                    elem = elements[0]
                    print(f"  - Tag: {elem.tag_name}")
                    print(f"  - ID: {elem.get_attribute('id')}")
                    print(f"  - Classes: {elem.get_attribute('class')}")
            except Exception as e:
                print(f"✗ {selector}: {e}")
        
    def inspect_squares(self):
        """Analisa as casas do tabuleiro"""
        print("\n" + "="*70)
        print("🎯 INSPEÇÃO DAS CASAS")
        print("="*70)
        
        # Diferentes padrões de seletores para casas
        square_selectors = [
            "[data-square]",
            "[class*='square']",
            "div[class*='square']",
            "rect[class*='square']",
            ".square",
            "[id*='square']",
        ]
        
        for selector in square_selectors:
            try:
                squares = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if squares:
                    print(f"\n✓ {selector}: {len(squares)} casas encontradas")
                    
                    # Analisa as primeiras 3 casas
                    for i, sq in enumerate(squares[:3], 1):
                        print(f"\n  Casa {i}:")
                        print(f"    Tag: {sq.tag_name}")
                        print(f"    ID: {sq.get_attribute('id')}")
                        print(f"    Classes: {sq.get_attribute('class')}")
                        print(f"    data-square: {sq.get_attribute('data-square')}")
                        print(f"    aria-label: {sq.get_attribute('aria-label')}")
                        
                        # Tenta pegar coordenadas
                        try:
                            location = sq.location
                            size = sq.size
                            print(f"    Posição: x={location['x']}, y={location['y']}")
                            print(f"    Tamanho: {size['width']}x{size['height']}px")
                        except:
                            pass
                    
                    # Se encontrou casas válidas, para
                    if len(squares) >= 64:
                        print(f"\n  ✅ Tabuleiro completo encontrado!")
                        return selector
                        
            except Exception as e:
                pass
        
        print("\n  ⚠ Nenhum seletor padrão funcionou")
        return None
    
    def inspect_pieces(self):
        """Analisa as peças"""
        print("\n" + "="*70)
        print("♟️  INSPEÇÃO DAS PEÇAS")
        print("="*70)
        
        piece_selectors = [
            "[class*='piece']",
            "div[class*='piece']",
            "img[class*='piece']",
            "svg[class*='piece']",
            ".piece"
        ]
        
        for selector in piece_selectors:
            try:
                pieces = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if pieces:
                    print(f"\n✓ {selector}: {len(pieces)} peças encontradas")
                    
                    # Mostra primeiras 3
                    for i, piece in enumerate(pieces[:3], 1):
                        print(f"\n  Peça {i}:")
                        print(f"    Tag: {piece.tag_name}")
                        print(f"    Classes: {piece.get_attribute('class')}")
                        print(f"    data-piece: {piece.get_attribute('data-piece')}")
                        print(f"    src: {piece.get_attribute('src')}")
                        
            except Exception as e:
                pass
    
    def inspect_move_list(self):
        """Analisa a lista de movimentos"""
        print("\n" + "="*70)
        print("📋 INSPEÇÃO DA LISTA DE MOVIMENTOS")
        print("="*70)
        
        move_selectors = [
            ".move",
            "[class*='move']",
            ".node",
            "[class*='notation']",
            ".move-text",
            "[class*='move-text']"
        ]
        
        for selector in move_selectors:
            try:
                moves = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if moves:
                    print(f"\n✓ {selector}: {len(moves)} elementos")
                    
                    # Mostra primeiros movimentos
                    move_texts = [m.text for m in moves[:10] if m.text.strip()]
                    if move_texts:
                        print(f"  Movimentos: {' '.join(move_texts)}")
                        
            except Exception as e:
                pass
    
    def save_page_source(self):
        """Salva o HTML da página para análise offline"""
        try:
            html = self.driver.page_source
            filename = f"chesscom_page_{int(time.time())}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"\n💾 HTML salvo em: {filename}")
            print("   Você pode abrir este arquivo em um editor para analisar")
            
        except Exception as e:
            print(f"✗ Erro ao salvar: {e}")
    
    def run_full_inspection(self):
        """Executa inspeção completa"""
        print("\n🚀 Iniciando inspeção do Chess.com...")
        print("\nInstruções:")
        print("1. O navegador vai abrir Chess.com")
        print("2. Faça login manualmente")
        print("3. Inicie uma partida (qualquer modo)")
        print("4. Volte aqui e pressione ENTER")
        
        self.driver.get("https://www.chess.com")
        
        input("\n▶ Pressione ENTER quando estiver em uma partida ativa...")
        
        print("\n🔍 Analisando estrutura da página...")
        time.sleep(2)
        
        # Executa todas as inspeções
        self.inspect_board()
        self.inspect_squares()
        self.inspect_pieces()
        self.inspect_move_list()
        self.save_page_source()
        
        print("\n" + "="*70)
        print("✅ INSPEÇÃO COMPLETA!")
        print("="*70)
        print("\nUse as informações acima para atualizar os seletores no bot.")
        print("O arquivo HTML foi salvo para análise detalhada.")
        
    def cleanup(self):
        """Fecha navegador"""
        input("\n▶ Pressione ENTER para fechar o navegador...")
        if self.driver:
            self.driver.quit()


def main():
    """Executa diagnóstico"""
    print("="*70)
    print("🔧 DIAGNÓSTICO CHESS.COM")
    print("="*70)
    
    inspector = ChessComInspector()
    
    try:
        inspector.setup_browser()
        inspector.run_full_inspection()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrompido")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        inspector.cleanup()


if __name__ == "__main__":
    main()