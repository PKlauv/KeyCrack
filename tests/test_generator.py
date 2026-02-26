import pytest

from keycrack.generator import strip_to_alpha, validate_dob

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
