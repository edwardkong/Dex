import pytest
from unittest.mock import patch, Mock
from src.main import UCI

@pytest.fixture
def mock_gamestate():
    with patch('src.gamestate.GameState') as MockGameState:
        yield MockGameState.return_value

@pytest.fixture
def mock_evaluate():
    with patch('src.evaluate.evaluate_board') as mock:
        yield mock

@pytest.fixture
def mock_tools():
    with patch('src.tools') as mock:
        yield mock

@pytest.fixture
def uci():
    return UCI()

def test_UCI_init():
    uci = UCI()
    assert uci is not None

def test_UCI_quit(monkeypatch):
    uci = UCI()

    with pytest.raises(SystemExit) as e:
        monkeypatch.setattr('builtins.input', lambda: 'quit')
        uci.coms()

    assert e.type == SystemExit
    assert e.value.code == 0

def test_UCI_uci(monkeypatch, capsys):
    uci = UCI()
    inputs = iter(['uci', 'quit'])
    with pytest.raises(SystemExit) as e:
        monkeypatch.setattr('builtins.input', lambda: next(inputs))
        uci.coms()
    captured = capsys.readouterr()

    assert captured.out == "id name Dex 0.0\nid author Edward Kong\nuciok\n"
    assert e.type == SystemExit
    assert e.value.code == 0

def test_UCI_isready(monkeypatch, capsys):
    uci = UCI()
    inputs = iter(['isready', 'quit'])
    with pytest.raises(SystemExit) as e:
        monkeypatch.setattr('builtins.input', lambda: next(inputs))
        uci.coms()
    captured = capsys.readouterr()

    assert captured.out == "readyok\n"
    assert e.type == SystemExit
    assert e.value.code == 0

def test_UCI_ucinewgame(monkeypatch, mock_gamestate, uci):
    inputs = iter(['ucinewgame', 'quit'])
    monkeypatch.setattr('builtins.input', lambda: next(inputs))
    with pytest.raises(SystemExit) as e:
        uci.coms()
        mock_gamestate.newGameUCI.assert_called()
    
def test_UCI_setupgame(monkeypatch, mock_gamestate, uci, capsys):
    inputs = iter(['uci', 'isready', 'ucinewgame', 'quit'])
    monkeypatch.setattr('builtins.input', lambda: next(inputs))
    with pytest.raises(SystemExit) as e:
        uci.coms()
        mock_gamestate.newGameUCI.assert_called()
    captured = capsys.readouterr()

    assert captured.out == "id name Dex 0.0\nid author Edward Kong\nuciok\nreadyok\n"
    assert e.type == SystemExit
    assert e.value.code == 0


if __name__ == "__main__":
    pytest.main(['-v'])