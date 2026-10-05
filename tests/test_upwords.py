from infrastructure.upwords import make


def test_inline_small_letters():
    assert make("красивая", "луна") == "кⷧрꙷаⷩсⷶивая"


def test_star_moves_small_letters_after_word():
    assert make("слово*", "луна") == "слово ⷧ ꙷ ⷩ ⷶ"


def test_non_letters_are_removed_from_upper_text():
    assert make("тест", "а!б?") == make("тест", "аб")
