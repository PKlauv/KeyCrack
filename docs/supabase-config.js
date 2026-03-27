// Supabase configuration for client-side API calls.
// The anon key is safe to expose — Row Level Security (RLS) policies
// on the database control what operations are allowed.

const SUPABASE_URL = "https://fdtsktbzshndnwiububp.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZkdHNrdGJ6c2huZG53aXVidWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3MzYwNDIsImV4cCI6MjA4NzMxMjA0Mn0.p1QU_Krf76umAu92xZDfnYHmnXIOqCpn7k3s_EgbpP4";

// Insert a bug report via Supabase REST API (anon can insert via RLS policy)
async function submitBug(description, category, email) {
    const body = { description, category };
    if (email) body.email = email;
    body.created_at = new Date().toISOString();

    const res = await fetch(`${SUPABASE_URL}/rest/v1/bugs`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": `Bearer ${SUPABASE_ANON_KEY}`,
            "Prefer": "return=representation",
        },
        body: JSON.stringify(body),
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || "Failed to submit bug report");
    }

    const rows = await res.json();
    return rows[0];
}

// Fetch all bug reports via Supabase REST API (requires authenticated session)
async function fetchBugs(accessToken) {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/bugs?order=id.desc`, {
        headers: {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": `Bearer ${accessToken}`,
        },
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || "Failed to fetch bugs");
    }

    return await res.json();
}

// Sign in with email/password via Supabase Auth
async function signIn(email, password) {
    const res = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "apikey": SUPABASE_ANON_KEY,
        },
        body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error_description || err.msg || "Login failed");
    }

    return await res.json();
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = { submitBug, fetchBugs, signIn, SUPABASE_URL, SUPABASE_ANON_KEY };
}
