/**
 * A fetch wrapper that handles non-standard JSON values (NaN, Infinity, -Infinity)
 * which the Python/Flask API can emit but the browser's JSON.parse() rejects.
 */
export async function fetchJson(url, options) {
    const res = await fetch(url, options);
    const text = await res.text();
    // Replace bare NaN / Infinity tokens with null before parsing
    const sanitized = text
        .replace(/:\s*NaN\b/g, ': null')
        .replace(/:\s*Infinity\b/g, ': null')
        .replace(/:\s*-Infinity\b/g, ': null');
    const data = JSON.parse(sanitized);
    return { ok: res.ok, status: res.status, data };
}
