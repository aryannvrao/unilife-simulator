from unilife import initialize_game_state, apply_stat_change


def test_initial_state_has_two_actions():
    state = initialize_game_state()
    assert state["actions_left"] == 2


def test_stat_clamps_to_100():
    state = initialize_game_state()
    state = apply_stat_change(state, "academic", 200)
    assert state["stats"]["academic"] == 100


def test_stat_clamps_to_0():
    state = initialize_game_state()
    state = apply_stat_change(state, "social", -200)
    assert state["stats"]["social"] == 0


def test_cash_increases():
    state = initialize_game_state()
    state["cash"] += 20
    assert state["cash"] == 40.00