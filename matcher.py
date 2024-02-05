"""
SAMPLE USAGE
from matcher import is_similar, Matcher

# Use 1
boolean = is_similar("im crying", [["im", "crying"], ["i", "am", "crying"]])
print(boolean)

# Use 2
is_match = Matcher([["im", "crying"], ["i", "am", "crying"]])
assert(is_match("im crying"))
assert(is_match("i am crying"))
"""

import string
from typing import Callable

SIMILARITY_THRESHOLD = 0.8
INTERRUPT_THRESHOLD = 1

Word = str
Phrase = list[Word]
SimilarityFunc = Callable[[Word, Word], float]

def default_similarity(a: Word, b: Word) -> float:
    def levenshtein_distance(a: Word, b: Word) -> int:
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif a[i - 1] == b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        return dp[m][n]

    distance = levenshtein_distance(a, b)
    similarity = 1.0 - (distance / max(len(a), len(b)))
    return similarity

def match_phrase(words: list[Word], phrase: Phrase, similarity_threshold: float, interrupt_threshold: float, similarity_func: SimilarityFunc) -> bool:
    word_index = 0
    phrase_index = 0
    latest_interrupt_index = -1

    while word_index < len(words):
        if similarity_func(words[word_index], phrase[phrase_index]) >= similarity_threshold:
            latest_interrupt_index = word_index
            phrase_index += 1

        if latest_interrupt_index > -1 and latest_interrupt_index + interrupt_threshold < word_index:
            word_index = latest_interrupt_index
            phrase_index = 0
            latest_interrupt_index = -1

        if phrase_index == len(phrase):
            return True

        word_index += 1

    return False

def to_words(content: str) -> list[Word]:
    words = content.split()
    cleaned_words = []
    for word in words:
        word = ''.join(c.lower() for c in word if c not in string.punctuation)
        cleaned_words.append(word)
    return cleaned_words

def is_similar(phrase_have: Phrase,
               phrases_want: list[Phrase],
               similarity_threshold: float | None = SIMILARITY_THRESHOLD,
               interrupt_threshold: int | None = INTERRUPT_THRESHOLD,
               similarity_func: SimilarityFunc | None = default_similarity) -> bool:
    words = to_words(phrase_have)
    return any(match_phrase(words, phrase, similarity_threshold, interrupt_threshold, similarity_func) for phrase in phrases_want)

def Matcher(phrase_want: Phrase,
            similarity_threshold: float | None = SIMILARITY_THRESHOLD,
            interrupt_threshold: int | None = INTERRUPT_THRESHOLD,
            similarity_func: SimilarityFunc | None = default_similarity):
        def match(phrase_have: Phrase) -> bool:
            return is_similar(phrase_have, phrase_want, similarity_threshold, interrupt_threshold, similarity_func)
        return match


def test_equality(test: str, got: bool, expected: bool) -> None:
    try:
        assert got == expected
        print(f"Pass: {test}")
    except AssertionError:
        print(f"Fail: {test}")



def test_all() -> None:
    def make_default(phrase_want: Phrase):
        def f(phrase_have: Phrase) -> bool:
            return is_similar(phrase_have, phrase_want)
        return f
    is_match = make_default([["im", "crying"], ["i", "am", "crying"]])

    test_equality("exact match", is_match("im crying"), True)
    test_equality("exact match", is_match("i am crying"), True)
    test_equality("exact match", is_match("in crying"), False)
    test_equality("exact match", is_match("x am crying"), False)

    test_equality("partial match", is_match("im cryjing"), True)
    test_equality("partial match", is_match("im crayoning"), False)
    test_equality("partial match", is_match("im cringe"), False)
    test_equality("partial match", is_match("im cring"), True)
    test_equality("partial match", is_match("im crazy"), False)
    test_equality("partial match", is_match("in cryo"), False)
    test_equality("partial match", is_match("i-am-crying"), False)
    test_equality("partial match", is_match("im-crying"), False)

    test_equality("punctuation", is_match("i'm crying"), True)
    test_equality("punctuation", is_match("i'm crying..."), True)
    test_equality("punctuation", is_match("im crying! xd"), True)
    test_equality("punctuation", is_match("~im ~crying~"), True)
    test_equality("punctuation", is_match("i am cry!ng"), True)

    test_equality("interruption thres", is_match("im literally crying"), True)
    test_equality("interruption thres", is_match("i am so so so crying"), False)

    test_equality("other", is_match("red books"), False)
    test_equality("other", is_match("crying am i"), False)
    test_equality("other", is_match("u are crying"), False)
    test_equality("other", is_match("i are crying"), False)


if __name__ == "__main__":
    test_all()
