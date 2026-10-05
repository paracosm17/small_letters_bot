small_letters = {
    chr(1072): chr(11766),
    chr(1073): chr(11744),
    chr(1074): chr(11745),
    chr(1075): chr(11746),
    chr(1076): chr(11747),
    chr(1077): chr(11767),
    chr(1105): chr(11767),
    chr(1078): chr(11748),
    chr(1079): chr(11749),
    chr(1080): chr(42613),
    chr(1081): chr(42613),
    chr(1082): chr(11750),
    chr(1083): chr(11751),
    chr(1084): chr(11752),
    chr(1085): chr(11753),
    chr(1086): chr(11754),
    chr(1087): chr(11755),
    chr(1088): chr(11756),
    chr(1089): chr(11757),
    chr(1090): chr(11758),
    chr(1091): chr(42615),
    chr(1092): chr(42654),
    chr(1093): chr(11759),
    chr(1094): chr(11760),
    chr(1095): chr(11761),
    chr(1096): chr(11762),
    chr(1097): chr(11763),
    chr(1098): chr(42616),
    chr(1099): chr(42617),
    chr(1100): chr(42618),
    chr(1101): chr(42612),
    chr(1102): chr(11771),
    chr(1103): chr(11769),
}


def make(text: str, uptext: str) -> str:
    text_words = text.split()

    filtered_uptext = "".join(
        character for character in uptext.lower() if character.isalpha() or character == " "
    )
    uptext_words = filtered_uptext.translate(filtered_uptext.maketrans(small_letters)).split()

    for index, upword in enumerate(uptext_words):
        result_word = ""
        if index < len(text_words):
            word = text_words[index].ljust(len(upword))
            if len(text_words[index]) >= len(upword):
                word = text_words[index]

            if text_words[index].endswith("*"):
                result_word = text_words[index][:-1]
                for upper_character in upword:
                    result_word += " " + upper_character
                text_words[index] = result_word
            else:
                for lower_character, upper_character in zip(word, upword, strict=False):
                    result_word += lower_character + upper_character
                if len(word) > len(upword):
                    result_word += word[len(upword) :]
                text_words[index] = result_word
        else:
            for upper_character in upword:
                result_word += " " + upper_character
            text_words.append(result_word)

    return " ".join(text_words)
