import pytest

from keycrack.generator import (
    CategorizedPasswords,
    PersonalInfo,
    _classify_password,
    _score_password,
    generate_passwords,
    generate_passwords_categorized,
    strip_to_alpha,
    validate_dob,
)


@pytest.fixture
def info():
    return PersonalInfo("john", "doe", "03141983", "buddy")


@pytest.fixture
def info_no_pet():
    return PersonalInfo("john", "doe", "03141983")


# --- validate_dob ---


class TestValidateDob:
    def test_valid_dob_returns_string(self):
        assert validate_dob("03141983") == "03141983"

    def test_valid_dob_edge_month_day(self):
        assert validate_dob("12311999") == "12311999"

    def test_invalid_length_short(self):
        with pytest.raises(ValueError, match="8 digits"):
            validate_dob("031483")

    def test_invalid_length_long(self):
        with pytest.raises(ValueError, match="8 digits"):
            validate_dob("031419830")

    def test_invalid_non_digits(self):
        with pytest.raises(ValueError, match="8 digits"):
            validate_dob("0314abcd")

    def test_invalid_month_zero(self):
        with pytest.raises(ValueError, match="Invalid month"):
            validate_dob("00141983")

    def test_invalid_month_thirteen(self):
        with pytest.raises(ValueError, match="Invalid month"):
            validate_dob("13141983")

    def test_invalid_day_zero(self):
        with pytest.raises(ValueError, match="Invalid day"):
            validate_dob("03001983")

    def test_invalid_day_thirtytwo(self):
        with pytest.raises(ValueError, match="Invalid day"):
            validate_dob("03321983")


# --- strip_to_alpha ---


class TestStripToAlpha:
    def test_normal_name_unchanged(self):
        assert strip_to_alpha("john") == "john"

    def test_strips_digits(self):
        assert strip_to_alpha("john123") == "john"

    def test_strips_symbols(self):
        assert strip_to_alpha("jo!h@n#") == "john"

    def test_strips_spaces(self):
        assert strip_to_alpha("jo hn") == "john"

    def test_all_digits_returns_empty(self):
        assert strip_to_alpha("12345") == ""

    def test_mixed_case_preserved(self):
        assert strip_to_alpha("JoHn") == "JoHn"


# --- generate_passwords ---


class TestGeneratePasswords:
    def test_returns_non_empty_set(self, info):
        result = generate_passwords(info)
        assert isinstance(result, set)
        assert len(result) > 0

    def test_all_items_min_length(self, info):
        result = generate_passwords(info)
        for pw in result:
            assert len(pw) >= 6, f"Password too short: {pw!r}"

    def test_no_empty_strings(self, info):
        result = generate_passwords(info)
        assert "" not in result

    def test_known_pattern_name123(self, info):
        result = generate_passwords(info)
        assert "john123" in result

    def test_known_pattern_capitalized(self, info):
        result = generate_passwords(info)
        assert "John123" in result

    def test_known_pattern_name_year(self, info):
        result = generate_passwords(info)
        assert "john1983" in result

    def test_without_pet_still_works(self, info_no_pet):
        result = generate_passwords(info_no_pet)
        assert len(result) > 0
        assert "john123" in result


# --- generate_passwords_categorized ---


class TestGeneratePasswordsCategorized:
    def test_returns_categorized_passwords(self, info):
        result = generate_passwords_categorized(info)
        assert isinstance(result, CategorizedPasswords)

    def test_top_passwords_max_30(self, info):
        result = generate_passwords_categorized(info)
        assert len(result.top_passwords) <= 30

    def test_top_passwords_ordered_by_score(self, info):
        result = generate_passwords_categorized(info)
        scores = [_score_password(pw, info) for pw in result.top_passwords]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], (
                f"Score order violated: {result.top_passwords[i]} "
                f"({scores[i]}) before {result.top_passwords[i+1]} ({scores[i+1]})"
            )

    def test_all_five_categories_populated(self, info):
        result = generate_passwords_categorized(info)
        assert len(result.name_based) > 0
        assert len(result.leet_speak) > 0
        assert len(result.name_dob) > 0
        assert len(result.dob_name) > 0
        assert len(result.dob_only) > 0

    def test_top_passwords_are_strings(self, info):
        result = generate_passwords_categorized(info)
        for pw in result.top_passwords:
            assert isinstance(pw, str)
            assert len(pw) >= 6


# --- _score_password ---


class TestScorePassword:
    def test_name123_scores_high(self, info):
        score = _score_password("john123", info)
        assert score > 40

    def test_name123_beats_reversed(self, info):
        score_normal = _score_password("john123", info)
        score_reversed = _score_password("nhoj123", info)
        assert score_normal > score_reversed

    def test_name123_beats_leet(self, info):
        score_normal = _score_password("john123", info)
        score_leet = _score_password("j0hn123", info)
        assert score_normal > score_leet

    def test_simple_pattern_beats_longer_variant(self, info):
        # name123 (the most common pattern) should outscore name12345
        score_123 = _score_password("john123", info)
        score_12345 = _score_password("john12345", info)
        assert score_123 > score_12345


# --- _classify_password ---


class TestClassifyPassword:
    def test_name123_is_seq_123(self, info):
        assert _classify_password("john123", info) == "seq_123"

    def test_ilove_pattern(self, info):
        assert _classify_password("ilovejohn", info) == "ilove"

    def test_name_bang(self, info):
        assert _classify_password("john!!", info) == "bang_double"

    def test_name_4ever(self, info):
        assert _classify_password("john4ever", info) == "name_4ever"

    def test_name_repeat(self, info):
        assert _classify_password("johnjohn", info) == "name_repeat"

    def test_separator(self, info):
        assert _classify_password("john_1983", info) == "separator"

    def test_compound(self, info):
        assert _classify_password("johndoe", info) == "compound"
