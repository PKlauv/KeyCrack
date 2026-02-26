import pytest

from keycrack.generator import CategorizedPasswords, PersonalInfo
from keycrack.pcfg import (
    build_grammar,
    case_expand,
    expand_template,
    generate_passwords_pcfg,
    make_mmdd_slot,
    make_name_slot,
)


@pytest.fixture
def info():
    return PersonalInfo("john", "doe", "03141983", "buddy")


@pytest.fixture
def info_no_pet():
    return PersonalInfo("john", "doe", "03141983")


# --- Slot expansion ---


class TestSlotExpansion:
    def test_name_slot_probs_sum_to_one(self, info):
        slot = make_name_slot(info)
        total = sum(sv.prob for sv in slot.values)
        assert abs(total - 1.0) < 0.01

    def test_name_slot_probs_sum_to_one_no_pet(self, info_no_pet):
        slot = make_name_slot(info_no_pet)
        total = sum(sv.prob for sv in slot.values)
        assert abs(total - 1.0) < 0.01

    def test_name_slot_with_pet_has_three_values(self, info):
        slot = make_name_slot(info)
        assert len(slot.values) == 3

    def test_name_slot_without_pet_has_two_values(self, info_no_pet):
        slot = make_name_slot(info_no_pet)
        assert len(slot.values) == 2

    def test_mmdd_slot_probs_sum_to_one(self, info):
        slot = make_mmdd_slot(info)
        total = sum(sv.prob for sv in slot.values)
        assert abs(total - 1.0) < 0.01

    def test_case_expand_probs_sum_to_one(self):
        results = case_expand("john")
        total = sum(p for _, p in results)
        assert abs(total - 1.0) < 0.01


# --- Template expansion ---


class TestTemplateExpansion:
    def test_templates_produce_passwords(self, info):
        templates = build_grammar(info)
        for template in templates[:5]:
            expansions = expand_template(template)
            assert len(expansions) > 0
            for pw, prob in expansions:
                assert isinstance(pw, str)
                assert prob > 0

    def test_expansion_probabilities_positive(self, info):
        templates = build_grammar(info)
        for template in templates:
            for pw, prob in expand_template(template):
                assert prob > 0, f"Non-positive probability for {pw}"


# --- Grammar builder ---


class TestGrammarBuilder:
    def test_template_probs_sum_near_one(self, info):
        templates = build_grammar(info)
        total = sum(t.base_prob for t in templates)
        assert abs(total - 1.0) < 0.05

    def test_all_categories_represented(self, info):
        templates = build_grammar(info)
        categories = {t.category for t in templates}
        expected = {"name_based", "leet_speak", "name_dob", "dob_name", "dob_only"}
        assert categories == expected

    def test_template_count(self, info):
        templates = build_grammar(info)
        assert len(templates) == 30


# --- End-to-end generation ---


class TestPCFGGeneration:
    def test_returns_categorized_passwords(self, info):
        result = generate_passwords_pcfg(info)
        assert isinstance(result, CategorizedPasswords)

    def test_top_passwords_max_30(self, info):
        result = generate_passwords_pcfg(info)
        assert len(result.top_passwords) <= 30

    def test_all_five_categories_populated(self, info):
        result = generate_passwords_pcfg(info)
        assert len(result.name_based) > 0
        assert len(result.leet_speak) > 0
        assert len(result.name_dob) > 0
        assert len(result.dob_name) > 0
        assert len(result.dob_only) > 0

    def test_known_patterns_present(self, info):
        result = generate_passwords_pcfg(info)
        all_pws = (
            result.name_based | result.leet_speak | result.name_dob
            | result.dob_name | result.dob_only
        )
        # john123 should appear (name + seq digits)
        assert "john123" in all_pws or "John123" in all_pws
        # john1983 should appear (name + birth year)
        assert "john1983" in all_pws or "John1983" in all_pws

    def test_min_length_enforced(self, info):
        result = generate_passwords_pcfg(info)
        for pw, _ in result.top_passwords:
            assert len(pw) >= 6, f"Password too short: {pw!r}"

    def test_works_without_pet(self, info_no_pet):
        result = generate_passwords_pcfg(info_no_pet)
        assert isinstance(result, CategorizedPasswords)
        assert len(result.top_passwords) > 0

    def test_top_passwords_are_tuples(self, info):
        result = generate_passwords_pcfg(info)
        for entry in result.top_passwords:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            assert isinstance(entry[0], str)
            assert isinstance(entry[1], float)

    def test_top_passwords_ordered_by_probability(self, info):
        result = generate_passwords_pcfg(info)
        probs = [prob for _, prob in result.top_passwords]
        for i in range(len(probs) - 1):
            assert probs[i] >= probs[i + 1], (
                f"Probability order violated at index {i}: "
                f"{probs[i]} before {probs[i + 1]}"
            )


# --- Probability math ---


class TestProbabilityMath:
    def test_no_negative_probabilities(self, info):
        result = generate_passwords_pcfg(info)
        for _, prob in result.top_passwords:
            assert prob > 0

    def test_highest_prob_is_name_variant(self, info):
        result = generate_passwords_pcfg(info)
        top_pw, _ = result.top_passwords[0]
        top_lower = top_pw.lower()
        # The highest probability password should contain a name or DOB component
        assert (
            "john" in top_lower
            or "doe" in top_lower
            or "buddy" in top_lower
            or "1983" in top_lower
        )
