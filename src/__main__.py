# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import fire
from src.interface.cli import RAGCLI


def main():
    fire.Fire(RAGCLI)

if __name__ == '__main__':
    main()
