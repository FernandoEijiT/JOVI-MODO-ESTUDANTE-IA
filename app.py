# Importando a classe responsável pelo modo estudante
from sistema.modo_estudante import ModoEstudante

def main():
    """Cria o Modo Estudante e inicia o programa."""
    sistema = ModoEstudante()
    sistema.executar()

if __name__ == "__main__":
    main()
