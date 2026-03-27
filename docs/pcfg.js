// Probabilistic Context-Free Grammar (PCFG) password generator.
// JavaScript port of keycrack/generator.py and keycrack/pcfg.py.
// Defines a grammar of 30 templates, expands every combination via Cartesian
// product, scores them by probability, and returns a diverse top-30 list plus
// full categorized results.

// -- Constants & utilities (from generator.py) --

const LEET_MAP = {
    a: "@", e: "3", i: "1", o: "0", s: "$", t: "7", l: "1",
};

const MIN_LENGTH = 6;

function validateDob(dob) {
    if (!/^\d{8}$/.test(dob)) {
        throw new Error("DOB must be exactly 8 digits (MMDDYYYY).");
    }
    const mm = parseInt(dob.slice(0, 2), 10);
    const dd = parseInt(dob.slice(2, 4), 10);
    if (mm < 1 || mm > 12) {
        throw new Error(`Invalid month: ${String(mm).padStart(2, "0")}. Must be 01-12.`);
    }
    if (dd < 1 || dd > 31) {
        throw new Error(`Invalid day: ${String(dd).padStart(2, "0")}. Must be 01-31.`);
    }
    return dob;
}

function stripToAlpha(name) {
    return name.replace(/[^a-zA-Z]/g, "");
}

function leetSpeak(word) {
    return word.split("").map(c => LEET_MAP[c.toLowerCase()] || c).join("");
}

function capitalize(s) {
    if (s.length === 0) return s;
    return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

// -- Case expansion --

function caseExpand(value) {
    const results = [[value.toLowerCase(), 0.50], [capitalize(value), 0.40]];
    if (value.toLowerCase() !== value.toUpperCase()) {
        results.push([value.toUpperCase(), 0.10]);
    }
    return results;
}

// -- Slot factory functions --

function makeNameSlot(info) {
    let values;
    if (info.petName) {
        values = [
            { value: info.firstName, prob: 0.50 },
            { value: info.lastName, prob: 0.20 },
            { value: info.petName, prob: 0.30 },
        ];
    } else {
        values = [
            { value: info.firstName, prob: 0.70 },
            { value: info.lastName, prob: 0.30 },
        ];
    }
    return { name: "name", values, applyCase: true };
}

function makeCompoundSlot(info) {
    const first = info.firstName;
    const last = info.lastName;
    const pet = info.petName;

    let values;
    if (pet) {
        values = [
            { value: first + last, prob: 0.30 },
            { value: first[0] + last, prob: 0.25 },
            { value: first + last[0], prob: 0.15 },
            { value: first + pet, prob: 0.20 },
            { value: pet + first, prob: 0.10 },
        ];
    } else {
        values = [
            { value: first + last, prob: 0.45 },
            { value: first[0] + last, prob: 0.35 },
            { value: first + last[0], prob: 0.20 },
        ];
    }
    return { name: "compound", values, applyCase: true };
}

function makeInitialsSlot(info) {
    const initials = info.firstName[0] + info.lastName[0];
    return { name: "initials", values: [{ value: initials, prob: 1.0 }], applyCase: true };
}

function makeLeetNameSlot(info) {
    let values;
    if (info.petName) {
        values = [
            { value: leetSpeak(info.firstName), prob: 0.50 },
            { value: leetSpeak(info.lastName), prob: 0.20 },
            { value: leetSpeak(info.petName), prob: 0.30 },
        ];
    } else {
        values = [
            { value: leetSpeak(info.firstName), prob: 0.70 },
            { value: leetSpeak(info.lastName), prob: 0.30 },
        ];
    }
    return { name: "leet_name", values, applyCase: true };
}

function makeBirthYear4Slot(info) {
    const yyyy = info.dob.slice(4, 8);
    return { name: "birth_year_4", values: [{ value: yyyy, prob: 1.0 }], applyCase: false };
}

function makeBirthYear2Slot(info) {
    const yy = info.dob.slice(6, 8);
    return { name: "birth_year_2", values: [{ value: yy, prob: 1.0 }], applyCase: false };
}

function makeMmddSlot(info) {
    const mm = info.dob.slice(0, 2);
    const dd = info.dob.slice(2, 4);
    return {
        name: "mmdd",
        values: [
            { value: mm + dd, prob: 0.70 },
            { value: dd + mm, prob: 0.30 },
        ],
        applyCase: false,
    };
}

function makeMmddyySlot(info) {
    const mm = info.dob.slice(0, 2);
    const dd = info.dob.slice(2, 4);
    const yy = info.dob.slice(6, 8);
    return {
        name: "mmddyy",
        values: [
            { value: mm + dd + yy, prob: 0.50 },
            { value: dd + mm + yy, prob: 0.30 },
            { value: mm + yy, prob: 0.20 },
        ],
        applyCase: false,
    };
}

function makeMmddyyyySlot(info) {
    const mm = info.dob.slice(0, 2);
    const dd = info.dob.slice(2, 4);
    const yyyy = info.dob.slice(4, 8);
    return {
        name: "mmddyyyy",
        values: [
            { value: mm + dd + yyyy, prob: 0.50 },
            { value: dd + mm + yyyy, prob: 0.30 },
            { value: mm + yyyy, prob: 0.20 },
        ],
        applyCase: false,
    };
}

function makeCurrentYearSlot() {
    const now = new Date();
    return {
        name: "current_year",
        values: [
            { value: String(now.getFullYear()), prob: 0.70 },
            { value: String(now.getFullYear() + 1), prob: 0.30 },
        ],
        applyCase: false,
    };
}

function makeSeparatorSlot() {
    return {
        name: "separator",
        values: [
            { value: "_", prob: 0.45 },
            { value: ".", prob: 0.35 },
            { value: "-", prob: 0.20 },
        ],
        applyCase: false,
    };
}

// -- Static slots --

const SEQ_123 = { name: "seq_123", values: [{ value: "123", prob: 1.0 }], applyCase: false };
const SEQ_1234 = { name: "seq_1234", values: [{ value: "1234", prob: 1.0 }], applyCase: false };
const SEQ_12345 = { name: "seq_12345", values: [{ value: "12345", prob: 1.0 }], applyCase: false };

const SEQ_DIGITS = {
    name: "seq_digits",
    values: [
        { value: "123", prob: 0.55 },
        { value: "1234", prob: 0.30 },
        { value: "12345", prob: 0.15 },
    ],
    applyCase: false,
};

const BANG_SLOT = {
    name: "bang",
    values: [
        { value: "!", prob: 0.65 },
        { value: "!!", prob: 0.35 },
    ],
    applyCase: false,
};

const LITERAL_123_BANG = { name: "123_bang", values: [{ value: "123!", prob: 1.0 }], applyCase: false };
const LITERAL_4EVER = { name: "4ever", values: [{ value: "4ever", prob: 1.0 }], applyCase: false };

const SPECIAL_SUFFIX_SLOT = {
    name: "special_suffix",
    values: [
        { value: "69", prob: 0.25 },
        { value: "420", prob: 0.25 },
        { value: "007", prob: 0.20 },
        { value: "99", prob: 0.15 },
        { value: "01", prob: 0.15 },
    ],
    applyCase: false,
};

const DIGIT_1_SLOT = { name: "digit_1", values: [{ value: "1", prob: 1.0 }], applyCase: false };

const ILOVE_PREFIX = {
    name: "ilove_prefix",
    values: [
        { value: "ilove", prob: 0.60 },
        { value: "iLove", prob: 0.40 },
    ],
    applyCase: false,
};

// -- Grammar builder --

function buildGrammar(info) {
    const name = makeNameSlot(info);
    const compound = makeCompoundSlot(info);
    const initials = makeInitialsSlot(info);
    const leetName = makeLeetNameSlot(info);
    const birthYear4 = makeBirthYear4Slot(info);
    const birthYear2 = makeBirthYear2Slot(info);
    const mmdd = makeMmddSlot(info);
    const mmddyy = makeMmddyySlot(info);
    const mmddyyyy = makeMmddyyyySlot(info);
    const currentYear = makeCurrentYearSlot();
    const separator = makeSeparatorSlot();

    const templates = [
        // Category: name_based
        { name: "name_seq", slots: [name, SEQ_DIGITS], baseProb: 0.105, category: "name_based" },           // T01
        { name: "name_digit1", slots: [name, DIGIT_1_SLOT], baseProb: 0.050, category: "name_based" },      // T02
        { name: "name_bang", slots: [name, BANG_SLOT], baseProb: 0.037, category: "name_based" },            // T03
        { name: "name_123bang", slots: [name, LITERAL_123_BANG], baseProb: 0.025, category: "name_based" },  // T04
        { name: "name_double", slots: [name, name], baseProb: 0.018, category: "name_based" },              // T05
        { name: "compound", slots: [compound], baseProb: 0.025, category: "name_based" },                   // T06
        { name: "name_4ever", slots: [name, LITERAL_4EVER], baseProb: 0.012, category: "name_based" },      // T07
        { name: "ilove_name", slots: [ILOVE_PREFIX, name], baseProb: 0.031, category: "name_based" },       // T08
        { name: "name_special", slots: [name, SPECIAL_SUFFIX_SLOT], baseProb: 0.018, category: "name_based" }, // T09
        { name: "initials_year4", slots: [initials, birthYear4], baseProb: 0.050, category: "name_based" },    // T10
        { name: "initials_mmdd", slots: [initials, mmdd], baseProb: 0.031, category: "name_based" },           // T11
        { name: "initials_mmddyyyy", slots: [initials, mmddyyyy], baseProb: 0.018, category: "name_based" },   // T12
        { name: "initials_seq", slots: [initials, SEQ_DIGITS], baseProb: 0.025, category: "name_based" },      // T13

        // Category: name_dob
        { name: "name_year4", slots: [name, birthYear4], baseProb: 0.111, category: "name_dob" },             // T14
        { name: "name_year2", slots: [name, birthYear2], baseProb: 0.068, category: "name_dob" },             // T15
        { name: "name_mmdd", slots: [name, mmdd], baseProb: 0.068, category: "name_dob" },                    // T16
        { name: "name_mmddyy", slots: [name, mmddyy], baseProb: 0.037, category: "name_dob" },               // T17
        { name: "name_mmddyyyy", slots: [name, mmddyyyy], baseProb: 0.025, category: "name_dob" },           // T18
        { name: "name_curyear", slots: [name, currentYear], baseProb: 0.031, category: "name_dob" },          // T19
        { name: "name_sep_year4", slots: [name, separator, birthYear4], baseProb: 0.018, category: "name_dob" }, // T20
        { name: "name_sep_mmdd", slots: [name, separator, mmdd], baseProb: 0.012, category: "name_dob" },        // T21

        // Category: dob_name
        { name: "mmdd_name", slots: [mmdd, name], baseProb: 0.037, category: "dob_name" },                    // T22
        { name: "year4_name", slots: [birthYear4, name], baseProb: 0.018, category: "dob_name" },             // T23
        { name: "mmddyy_name", slots: [mmddyy, name], baseProb: 0.012, category: "dob_name" },               // T24

        // Category: dob_only
        { name: "dob_mmddyyyy", slots: [mmddyyyy], baseProb: 0.019, category: "dob_only" },                  // T25
        { name: "dob_mmddyy", slots: [mmddyy], baseProb: 0.013, category: "dob_only" },                      // T26
        { name: "dob_mmdd_seq", slots: [mmdd, SEQ_DIGITS], baseProb: 0.013, category: "dob_only" },           // T27

        // Category: leet_speak
        { name: "leet_seq", slots: [leetName, SEQ_DIGITS], baseProb: 0.037, category: "leet_speak" },         // T28
        { name: "leet_year4", slots: [leetName, birthYear4], baseProb: 0.025, category: "leet_speak" },       // T29
        { name: "leet_bang", slots: [leetName, BANG_SLOT], baseProb: 0.012, category: "leet_speak" },          // T30
    ];

    return templates;
}

// -- Template expansion --

function expandTemplate(template) {
    let expansions = [["", template.baseProb]];

    for (const slot of template.slots) {
        const newExpansions = [];
        for (const [prefix, prefixProb] of expansions) {
            for (const sv of slot.values) {
                if (slot.applyCase) {
                    for (const [cased, caseProb] of caseExpand(sv.value)) {
                        newExpansions.push([prefix + cased, prefixProb * sv.prob * caseProb]);
                    }
                } else {
                    newExpansions.push([prefix + sv.value, prefixProb * sv.prob]);
                }
            }
        }
        expansions = newExpansions;
    }

    return expansions;
}

// -- Diverse top-N selection --

function selectDiverseTop(scored, n, maxPerTemplate) {
    n = n || 30;
    maxPerTemplate = maxPerTemplate || 2;

    const seenLower = new Set();
    const templateCounts = {};
    const result = [];

    for (const [pw, prob, tname] of scored) {
        const key = pw.toLowerCase();
        if (seenLower.has(key)) continue;
        if ((templateCounts[tname] || 0) >= maxPerTemplate) continue;
        seenLower.add(key);
        templateCounts[tname] = (templateCounts[tname] || 0) + 1;
        result.push([pw, prob]);
        if (result.length === n) break;
    }

    return result;
}

// -- Category metadata (from app.py) --

const CATEGORY_META = {
    name_based: {
        label: "Name-Based",
        description: "Name combinations with common suffixes",
    },
    leet_speak: {
        label: "Leet Speak",
        description: "Letter substitutions (a=@, e=3, s=$, etc.) with suffixes",
    },
    name_dob: {
        label: "Name + DOB",
        description: "Name followed by date-of-birth patterns",
    },
    dob_name: {
        label: "DOB + Name",
        description: "Date-of-birth patterns followed by name",
    },
    dob_only: {
        label: "DOB Only",
        description: "Date-of-birth patterns with common suffixes",
    },
};

// -- Main generation function --

function generatePasswords(firstName, lastName, dob, petName) {
    const cleanDob = validateDob(dob.trim());
    const cleanFirst = stripToAlpha(firstName.trim());
    const cleanLast = stripToAlpha(lastName.trim());
    const cleanPet = petName ? stripToAlpha(petName.trim()) : "";

    if (!cleanFirst) {
        throw new Error("First name must contain at least one letter.");
    }
    if (!cleanLast) {
        throw new Error("Last name must contain at least one letter.");
    }

    const info = {
        firstName: cleanFirst,
        lastName: cleanLast,
        dob: cleanDob,
        petName: cleanPet || null,
    };

    const start = performance.now();
    const templates = buildGrammar(info);

    // Expand all templates
    const allPasswords = [];
    for (const template of templates) {
        for (const [pw, prob] of expandTemplate(template)) {
            if (pw.length >= MIN_LENGTH) {
                allPasswords.push([pw, prob, template.category, template.name]);
            }
        }
    }

    // Deduplicate: keep highest probability per password
    const best = {};
    for (const [pw, prob, cat, tname] of allPasswords) {
        if (!best[pw] || prob > best[pw][0]) {
            best[pw] = [prob, cat, tname];
        }
    }

    // Build category sets
    const categories = {
        name_based: new Set(),
        leet_speak: new Set(),
        name_dob: new Set(),
        dob_name: new Set(),
        dob_only: new Set(),
    };
    const scored = [];
    for (const pw of Object.keys(best)) {
        const [prob, cat, tname] = best[pw];
        categories[cat].add(pw);
        scored.push([pw, prob, tname]);
    }

    // Sort by probability descending, then alphabetically
    scored.sort((a, b) => {
        if (b[1] !== a[1]) return b[1] - a[1];
        return a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0;
    });

    // Diverse top 30: max 2 per template name
    const top30 = selectDiverseTop(scored, 30, 2);

    const elapsed = (performance.now() - start) / 1000;

    // Format response to match the API shape the frontend expects
    const categoryResponse = {};
    let totalCount = 0;
    const categoryOrder = ["name_based", "leet_speak", "name_dob", "dob_name", "dob_only"];
    for (const key of categoryOrder) {
        const meta = CATEGORY_META[key];
        const passwords = Array.from(categories[key]).sort();
        categoryResponse[key] = {
            label: meta.label,
            description: meta.description,
            passwords: passwords,
            count: passwords.length,
        };
        totalCount += passwords.length;
    }

    return {
        categories: categoryResponse,
        top_passwords: top30.map(([password, probability]) => ({ password, probability })),
        total_count: totalCount,
        elapsed_seconds: Math.round(elapsed * 10000) / 10000,
    };
}

// Node.js exports for testing
if (typeof module !== "undefined" && module.exports) {
    module.exports = {
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
    };
}
