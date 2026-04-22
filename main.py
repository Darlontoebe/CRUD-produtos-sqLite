import sqlite3

class Produto:
    def __init__(self, codigo: str, nome: str, preco: float, estoque: int, categoria: str = "Geral"):
        self.codigo = codigo.upper().strip()
        self.nome = nome.strip()
        self.preco = round(preco, 2)
        self.estoque = estoque
        self.categoria = categoria.strip() or "Geral"

    def __str__(self):
        return f"{self.codigo:<6} | {self.nome:<25} | R${self.preco:>8.2f} | Estoque: {self.estoque:>4} | {self.categoria}"


class GerenciadorProdutos:
    def __init__(self):
        self.conn = sqlite3.connect('produtos.db')
        self.criar_tabela()

    def criar_tabela(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                codigo TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                preco REAL NOT NULL,
                estoque INTEGER NOT NULL,
                categoria TEXT
            )
        ''')
        self.conn.commit()

    def adicionar(self, produto: Produto):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO produtos (codigo, nome, preco, estoque, categoria)
                VALUES (?, ?, ?, ?, ?)
            ''', (produto.codigo, produto.nome, produto.preco, produto.estoque, produto.categoria))
            self.conn.commit()
            print(f"✅ Produto {produto.codigo} adicionado com sucesso!")
        except sqlite3.IntegrityError:
            print(f"❌ Erro: Código {produto.codigo} já existe!")

    def listar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM produtos ORDER BY codigo")
        produtos = cursor.fetchall()
        
        if not produtos:
            print("Nenhum produto cadastrado ainda.")
            return
        
        print("\n" + "="*80)
        print("LISTA DE PRODUTOS")
        print("="*80)
        print(f"{'Código':<6} | {'Nome':<25} | {'Preço':>10} | {'Estoque':>8} | Categoria")
        print("-"*80)
        for p in produtos:
            print(f"{p[0]:<6} | {p[1]:<25} | R${p[2]:>8.2f} | {p[3]:>8} | {p[4]}")
        print("="*80)

    def buscar(self, codigo: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo.upper().strip(),))
        produto = cursor.fetchone()
        
        if produto:
            print(f"\nProduto encontrado:")
            print(f"Código: {produto[0]}")
            print(f"Nome: {produto[1]}")
            print(f"Preço: R${produto[2]:.2f}")
            print(f"Estoque: {produto[3]}")
            print(f"Categoria: {produto[4]}")
        else:
            print(f"❌ Produto com código {codigo} não encontrado.")

    def alterar(self, codigo: str, novo_preco: float = None, novo_estoque: int = None):
        cursor = self.conn.cursor()
        atualizado = False
        
        if novo_preco is not None:
            cursor.execute("UPDATE produtos SET preco = ? WHERE codigo = ?", (novo_preco, codigo.upper().strip()))
            atualizado = True
        if novo_estoque is not None:
            cursor.execute("UPDATE produtos SET estoque = ? WHERE codigo = ?", (novo_estoque, codigo.upper().strip()))
            atualizado = True
            
        if atualizado:
            self.conn.commit()
            print(f"✅ Produto {codigo} alterado com sucesso!")
        else:
            print("Nenhuma alteração realizada.")

    def remover(self, codigo: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE codigo = ?", (codigo.upper().strip(),))
        if cursor.rowcount > 0:
            self.conn.commit()
            print(f"✅ Produto {codigo} removido com sucesso!")
        else:
            print(f"❌ Produto {codigo} não encontrado.")

    def estoque_baixo(self, limite=10):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE estoque <= ? ORDER BY estoque", (limite,))
        produtos = cursor.fetchall()
        
        if produtos:
            print(f"\n=== PRODUTOS COM ESTOQUE BAIXO (<= {limite}) ===")
            for p in produtos:
                print(f"{p[0]} | {p[1]} | R${p[2]:.2f} | Estoque: {p[3]} | {p[4]}")
        else:
            print(f"Nenhum produto com estoque baixo (<= {limite}).")

    def fechar(self):
        self.conn.close()


# ==================== MENU ====================
def menu():
    gerenciador = GerenciadorProdutos()
    
    while True:
        print("\n" + "="*50)
        print("   SISTEMA DE GERENCIAMENTO DE PRODUTOS")
        print("="*50)
        print("1. Adicionar produto")
        print("2. Listar todos os produtos")
        print("3. Buscar produto por código")
        print("4. Alterar produto")
        print("5. Remover produto")
        print("6. Relatório - Estoque baixo")
        print("0. Sair")
        print("="*50)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            codigo = input("Código: ").strip()
            nome = input("Nome do produto: ").strip()
            
            # Input inteligente de preço
            while True:
                preco_str = input("Preço (ex: 52.90 ou 52,90): R$").strip()
                try:
                    preco = float(preco_str.replace(",", "."))
                    if preco <= 0:
                        print("❌ Preço deve ser maior que zero.")
                        continue
                    break
                except ValueError:
                    print("❌ Preço inválido! Use apenas números.")
            
            # Input de estoque
            while True:
                estoque_str = input("Estoque inicial: ").strip()
                try:
                    estoque = int(estoque_str)
                    if estoque < 0:
                        print("❌ Estoque não pode ser negativo.")
                        continue
                    break
                except ValueError:
                    print("❌ Estoque inválido! Digite apenas números inteiros.")
            
            categoria = input("Categoria (Enter para 'Geral'): ").strip() or "Geral"
            
            produto = Produto(codigo, nome, preco, estoque, categoria)
            gerenciador.adicionar(produto)
            
        elif opcao == "2":
            gerenciador.listar_todos()
            
        elif opcao == "3":
            codigo = input("Digite o código: ").strip()
            gerenciador.buscar(codigo)
            
        elif opcao == "4":
            codigo = input("Código do produto a alterar: ").strip()
            print("Deixe em branco se não quiser alterar.")
            preco_str = input("Novo preço (ex: 52.90): R$").strip()
            estoque_str = input("Novo estoque: ").strip()
            
            novo_preco = float(preco_str.replace(",", ".")) if preco_str else None
            novo_estoque = int(estoque_str) if estoque_str else None
            gerenciador.alterar(codigo, novo_preco, novo_estoque)
            
        elif opcao == "5":
            codigo = input("Código do produto a remover: ").strip()
            confirmar = input(f"Tem certeza que quer remover {codigo}? (s/n): ").strip().lower()
            if confirmar == "s":
                gerenciador.remover(codigo)
                
        elif opcao == "6":
            gerenciador.estoque_baixo()
            
        elif opcao == "0":
            gerenciador.fechar()
            print("👋 Sistema encerrado. Até mais!")
            break
            
        else:
            print("❌ Opção inválida! Tente novamente.")


if __name__ == "__main__":
    menu()