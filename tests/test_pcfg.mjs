// JavaScript tests for the client-side PCFG engine (docs/pcfg.js).
// Uses Node.js built-in assert — zero dependencies.

import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const {
    generatePasswords,
    validateDob,
    stripToAlpha,
    leetSpeak,
    caseExpand,
    buildGrammar,
    expandTemplate,
    selectDiverseTop,
    LEET_MAP,
    MIN_LENGTH,
    CATEGORY_META,
} = require("../docs/pcfg.js");

let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        passed++;
        console.log(`  PASS  ${name}`);
    } catch (err) {
        failed++;
        console.log(`  FAIL  ${name}`);
        console.log(`        ${err.message}`);
    }
}

console.log("\n=== KeyCrack JS PCFG Tests ===\n");

// -- validateDob --

test("validateDob accepts valid DOB", () => {
    assert.equal(validateDob("01151990"), "01151990");
    assert.equal(validateDob("12312000"), "12312000");
});

test("validateDob rejects non-8-digit input", () => {
    assert.throws(() => validateDob("1234567"), { message: /8 digits/ });
    assert.throws(() => validateDob("123456789"), { message: /8 digits/ });
    assert.throws(() => validateDob("abcdefgh"), { message: /8 digits/ });
});

test("validateDob rejects invalid month", () => {
    assert.throws(() => validateDob("00151990"), { message: /Invalid month/ });
    assert.throws(() => validateDob("13151990"), { message: /Invalid month/ });
});

test("validateDob rejects invalid day", () => {
    assert.throws(() => validateDob("01001990"), { message: /Invalid day/ });
    assert.throws(() => validateDob("01321990"), { message: /Invalid day/ });
});

// -- stripToAlpha --

test("stripToAlpha removes non-alpha chars", () => {
    assert.equal(stripToAlpha("John123"), "John");
    assert.equal(stripToAlpha("O'Brien"), "OBrien");
    assert.equal(stripToAlpha("Mary-Jane"), "MaryJane");
    assert.equal(stripToAlpha(""), "");
});

// -- leetSpeak --

test("leetSpeak applies LEET_MAP correctly", () => {
    assert.equal(leetSpeak("password"), "p@$$w0rd");
    assert.equal(leetSpeak("test"), "73$7");
    assert.equal(leetSpeak("Alice"), "@l1c3");
});

test("leetSpeak preserves unmapped characters", () => {
    assert.equal(leetSpeak("xyz"), "xyz");
    assert.equal(leetSpeak("123"), "123");
});

// -- caseExpand --

test("caseExpand returns 3 variants for alpha strings", () => {
    const result = caseExpand("john");
    assert.equal(result.length, 3);
    assert.equal(result[0][0], "john");
    assert.equal(result[1][0], "John");
    assert.equal(result[2][0], "JOHN");
});

test("caseExpand probabilities sum to 1.0", () => {
    const result = caseExpand("test");
    const sum = result.reduce((s, [, p]) => s + p, 0);
    assert.ok(Math.abs(sum - 1.0) < 0.001, `Sum was ${sum}`);
});

// -- buildGrammar --

test("buildGrammar produces 30 templates", () => {
    const info = { firstName: "John", lastName: "Smith", dob: "01151990", petName: null };
    const templates = buildGrammar(info);
    assert.equal(templates.length, 30);
});

test("buildGrammar probabilities sum near 1.0", () => {
    const info = { firstName: "John", lastName: "Smith", dob: "01151990", petName: null };
    const templates = buildGrammar(info);
    const sum = templates.reduce((s, t) => s + t.baseProb, 0);
    assert.ok(Math.abs(sum - 1.0) < 0.05, `Sum was ${sum}`);
});

test("buildGrammar covers all 5 categories", () => {
    const info = { firstName: "John", lastName: "Smith", dob: "01151990", petName: null };
    const templates = buildGrammar(info);
    const categories = new Set(templates.map(t => t.category));
    assert.deepEqual(categories, new Set(["name_based", "name_dob", "dob_name", "dob_only", "leet_speak"]));
});

test("buildGrammar works with pet name", () => {
    const info = { firstName: "John", lastName: "Smith", dob: "01151990", petName: "Rex" };
    const templates = buildGrammar(info);
    assert.equal(templates.length, 30);
});

// -- expandTemplate --

test("expandTemplate produces non-empty results", () => {
    const info = { firstName: "John", lastName: "Smith", dob: "01151990", petName: null };
    const templates = buildGrammar(info);
    for (const t of templates) {
        const expanded = expandTemplate(t);
        assert.ok(expanded.length > 0, `Template ${t.name} produced no expansions`);
    }
});

test("expandTemplate probabilities are positive", () => {
    const info = { firstName: "John", lastName: "Smith", dob: "01151990", petName: null };
    const templates = buildGrammar(info);
    for (const t of templates) {
        for (const [pw, prob] of expandTemplate(t)) {
            assert.ok(prob > 0, `Password "${pw}" has prob ${prob}`);
        }
    }
});

// -- selectDiverseTop --

test("selectDiverseTop respects max_per_template", () => {
    const scored = [
        ["a", 0.5, "t1"], ["b", 0.4, "t1"], ["c", 0.3, "t1"],
        ["d", 0.2, "t2"], ["e", 0.1, "t2"],
    ];
    const result = selectDiverseTop(scored, 5, 2);
    const t1Count = result.filter(([, , t]) => false).length; // count from result
    // Result should have max 2 from t1
    const fromT1 = result.filter(([pw]) => ["a", "b", "c"].includes(pw));
    assert.ok(fromT1.length <= 2);
});

test("selectDiverseTop deduplicates case-insensitively", () => {
    const scored = [
        ["John", 0.5, "t1"], ["john", 0.4, "t2"], ["JOHN", 0.3, "t3"],
    ];
    const result = selectDiverseTop(scored, 10, 5);
    assert.equal(result.length, 1);
    assert.equal(result[0][0], "John");
});

// -- generatePasswords (full integration) --

test("generatePasswords returns correct shape", () => {
    const result = generatePasswords("John", "Smith", "01151990", null);
    assert.ok(result.categories);
    assert.ok(result.top_passwords);
    assert.ok(typeof result.total_count === "number");
    assert.ok(typeof result.elapsed_seconds === "number");
    assert.ok(result.total_count > 0);
});

test("generatePasswords top_passwords max 30 and ordered", () => {
    const result = generatePasswords("John", "Smith", "01151990", null);
    assert.ok(result.top_passwords.length <= 30);
    assert.ok(result.top_passwords.length > 0);
    for (let i = 1; i < result.top_passwords.length; i++) {
        assert.ok(
            result.top_passwords[i - 1].probability >= result.top_passwords[i].probability,
            `Not sorted: ${result.top_passwords[i - 1].probability} < ${result.top_passwords[i].probability}`
        );
    }
});

test("generatePasswords enforces MIN_LENGTH", () => {
    const result = generatePasswords("John", "Smith", "01151990", null);
    for (const entry of result.top_passwords) {
        assert.ok(entry.password.length >= MIN_LENGTH, `"${entry.password}" is too short`);
    }
    for (const key of Object.keys(result.categories)) {
        for (const pw of result.categories[key].passwords) {
            assert.ok(pw.length >= MIN_LENGTH, `"${pw}" in ${key} is too short`);
        }
    }
});

test("generatePasswords populates all 5 categories", () => {
    const result = generatePasswords("John", "Smith", "01151990", null);
    for (const key of ["name_based", "leet_speak", "name_dob", "dob_name", "dob_only"]) {
        assert.ok(result.categories[key], `Missing category: ${key}`);
        assert.ok(result.categories[key].count > 0, `Empty category: ${key}`);
        assert.ok(result.categories[key].label, `Missing label for: ${key}`);
        assert.ok(result.categories[key].description, `Missing description for: ${key}`);
    }
});

test("generatePasswords works with pet name", () => {
    const result = generatePasswords("Sarah", "Miller", "07221993", "Luna");
    assert.ok(result.total_count > 0);
    // Pet name should appear in some passwords
    const allPws = Object.values(result.categories).flatMap(c => c.passwords);
    const hasLuna = allPws.some(pw => pw.toLowerCase().includes("luna"));
    assert.ok(hasLuna, "Expected pet name 'Luna' in generated passwords");
});

test("generatePasswords works without pet name", () => {
    const result = generatePasswords("Harold", "Patterson", "08171948", null);
    assert.ok(result.total_count > 0);
});

test("generatePasswords validates empty first name", () => {
    assert.throws(() => generatePasswords("", "Smith", "01151990", null), { message: /First name/ });
    assert.throws(() => generatePasswords("123", "Smith", "01151990", null), { message: /First name/ });
});

test("generatePasswords validates empty last name", () => {
    assert.throws(() => generatePasswords("John", "", "01151990", null), { message: /Last name/ });
});

test("generatePasswords validates DOB", () => {
    assert.throws(() => generatePasswords("John", "Smith", "invalid", null), { message: /8 digits/ });
});

test("generatePasswords category passwords are sorted", () => {
    const result = generatePasswords("John", "Smith", "01151990", null);
    for (const key of Object.keys(result.categories)) {
        const pws = result.categories[key].passwords;
        for (let i = 1; i < pws.length; i++) {
            assert.ok(pws[i - 1] <= pws[i], `${key} not sorted: "${pws[i - 1]}" > "${pws[i]}"`);
        }
    }
});

test("generatePasswords total_count matches sum of category counts", () => {
    const result = generatePasswords("John", "Smith", "01151990", null);
    const sum = Object.values(result.categories).reduce((s, c) => s + c.count, 0);
    assert.equal(result.total_count, sum);
});

// -- Summary --

console.log(`\n${passed + failed} tests: ${passed} passed, ${failed} failed\n`);
if (failed > 0) process.exit(1);
