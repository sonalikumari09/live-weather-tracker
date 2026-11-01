/**
 * Cloudflare Pages Function: /api/suggest
 * Fast autocomplete search across Indian districts, villages, towns, and PIN codes.
 * Backed by Cloudflare D1 (edge SQLite) with live OSM/Photon fallback.
 */

const DISTRICT_KEYWORDS = new Set(["district", "districts", "dist", "dt", "jila", "jilla", "zila"]);
const VILLAGE_KEYWORDS = new Set(["village", "villages", "vill", "vil", "gaon", "gao", "gram", "grama", "kheda"]);
const SUBDISTRICT_KEYWORDS = new Set(["subdistrict", "tehsil", "tahsil", "taluk", "taluka", "block", "mandal"]);
const CITY_KEYWORDS = new Set(["city", "town", "nagar"]);
const NOISE_KEYWORDS = new Set(["in", "of", "all", "the", "near"]);

const FEATURE_LABELS = {
  PPLC: "capital",
  PPLA: "city",
  PPLA2: "city",
  PPLA3: "town",
  PPLA4: "town",
  PPLA5: "town",
  PPL: "village",
  PPLX: "locality",
  PPLQ: "abandoned place",
  PPLL: "locality",
  PPLF: "farm",
  PPLR: "religious place",
  PPLS: "place",
  ADM1: "state",
  ADM2: "district",
  ADM3: "subdistrict",
};

const FEATURE_PRIORITY = {
  PPLC: 0,
  PPLA: 1,
  PPLA2: 1,
  ADM2: 2,
  PPLA3: 3,
  PPLA4: 3,
  PPLA5: 3,
  PPL: 4,
  ADM3: 5,
  PPLL: 5,
  PPLX: 6,
  PPLF: 6,
  PPLR: 6,
  PPLS: 6,
  ADM1: 7,
};

function normalize(text) {
  return (text || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function cleanDistrictName(name) {
  if (!name) return "";
  return name
    .replace(/^(District|Zila)\s+/i, "")
    .replace(/\s+(District|district|Zila|zila|Division|division)$/i, "")
    .trim();
}

function buildLabel(place) {
  const typ = place.type_label || place.type || "place";
  let name = place.name || "";
  if (typ === "district") {
    name = cleanDistrictName(name);
  }
  const parts = [];
  const admin3 = place.admin3 || "";
  const admin2 = cleanDistrictName(place.admin2 || "");
  const admin1 = place.admin1 || "";

  for (const item of [name, admin3, admin2, admin1]) {
    if (item && !parts.some((p) => normalize(p) === normalize(item))) {
      parts.push(item);
    }
  }
  const extra = typ && typ !== "place" ? ` [${typ}]` : "";
  return parts.join(", ") + extra;
}

function jsonResponse(data, maxAgeSec = 3600) {
  return new Response(JSON.stringify(data), {
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": `public, max-age=${maxAgeSec}, s-maxage=${maxAgeSec}`,
      "Access-Control-Allow-Origin": "*",
    },
  });
}

// ----------------- Cloudflare D1 Search -----------------
async function searchD1(db, query, limit) {
  const norm = normalize(query);
  if (!norm) return [];
  const words = norm.split(/\s+/);

  let targetType = null;
  if (words.some((w) => DISTRICT_KEYWORDS.has(w))) targetType = "district";
  else if (words.some((w) => VILLAGE_KEYWORDS.has(w))) targetType = "village";
  else if (words.some((w) => SUBDISTRICT_KEYWORDS.has(w))) targetType = "subdistrict";
  else if (words.some((w) => CITY_KEYWORDS.has(w))) targetType = "city";

  const contentWords = words.filter(
    (w) =>
      !DISTRICT_KEYWORDS.has(w) &&
      !VILLAGE_KEYWORDS.has(w) &&
      !SUBDISTRICT_KEYWORDS.has(w) &&
      !CITY_KEYWORDS.has(w) &&
      !NOISE_KEYWORDS.has(w)
  );
  const coreTerm = contentWords.length ? contentWords.join(" ") : words.join(" ");

  let rows = [];

  // Pattern: "villages in <District>"
  if (
    targetType === "village" &&
    (words.some((w) => w === "in" || w === "of") ||
      (words.length >= 2 && VILLAGE_KEYWORDS.has(words[words.length - 1])))
  ) {
    const stmt = db.prepare(`
      SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population
      FROM places
      WHERE feature_code IN ('PPL', 'PPLL', 'PPLF', 'PPLR', 'PPLS')
        AND (admin2 LIKE ? OR admin1 LIKE ?)
      ORDER BY population DESC, name
      LIMIT ?
    `);
    const res = await stmt.bind(`${coreTerm}%`, `${coreTerm}%`, limit * 3).all();
    rows.push(...(res.results || []));
  }
  // Pattern: "districts in <State>"
  else if (
    targetType === "district" &&
    (words.some((w) => w === "in" || w === "of") ||
      (words.length >= 2 && DISTRICT_KEYWORDS.has(words[words.length - 1])))
  ) {
    const stmt = db.prepare(`
      SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population
      FROM places
      WHERE feature_code = 'ADM2'
        AND admin1 LIKE ?
      ORDER BY name
      LIMIT ?
    `);
    const res = await stmt.bind(`${coreTerm}%`, limit * 3).all();
    rows.push(...(res.results || []));
  }
  // Pattern: Multi-word query (e.g. "Bajpatti Sitamarhi" or "Sitamarhi Bajpatti")
  else if (contentWords.length >= 2) {
    const w0 = contentWords[0];
    const w1 = contentWords.slice(1).join(" ");
    const stmt = db.prepare(`
      SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population
      FROM places
      WHERE (name LIKE ? AND (admin2 LIKE ? OR admin1 LIKE ? OR admin3 LIKE ?))
         OR (name LIKE ? AND (admin2 LIKE ? OR admin1 LIKE ? OR admin3 LIKE ?))
      ORDER BY population DESC, name
      LIMIT ?
    `);
    const res = await stmt
      .bind(
        `${w0}%`,
        `%${w1}%`,
        `%${w1}%`,
        `%${w1}%`,
        `${w1}%`,
        `%${w0}%`,
        `%${w0}%`,
        `%${w0}%`,
        limit * 3
      )
      .all();
    rows.push(...(res.results || []));
  }

  // Standard prefix matching
  if (targetType === "district") {
    const stmt = db.prepare(`
      SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population
      FROM places
      WHERE feature_code = 'ADM2' AND (name LIKE ? OR admin2 LIKE ?)
      ORDER BY population DESC
      LIMIT ?
    `);
    const res = await stmt.bind(`${coreTerm}%`, `${coreTerm}%`, limit * 3).all();
    rows.push(...(res.results || []));
  } else if (targetType === "village") {
    const stmt = db.prepare(`
      SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population
      FROM places
      WHERE feature_code IN ('PPL', 'PPLL', 'PPLF', 'PPLR', 'PPLS') AND name LIKE ?
      ORDER BY population DESC, name
      LIMIT ?
    `);
    const res = await stmt.bind(`${coreTerm}%`, limit * 3).all();
    rows.push(...(res.results || []));
  } else {
    const stmt = db.prepare(`
      SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population
      FROM places
      WHERE name LIKE ?
      ORDER BY population DESC, name
      LIMIT ?
    `);
    const res = await stmt.bind(`${coreTerm}%`, limit * 3).all();
    rows.push(...(res.results || []));

    if (coreTerm.length >= 3) {
      const stmtDist = db.prepare(`
        SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population
        FROM places
        WHERE feature_code = 'ADM2' AND (name LIKE ? OR admin2 LIKE ?)
        LIMIT 5
      `);
      const resDist = await stmtDist.bind(`${coreTerm}%`, `${coreTerm}%`).all();
      rows.push(...(resDist.results || []));
    }
  }

  // Substring fallback if few results
  if (rows.length < 2 && coreTerm.length >= 3) {
    const stmtSub = db.prepare(`
      SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population
      FROM places
      WHERE name LIKE ?
      ORDER BY population DESC, name
      LIMIT ?
    `);
    const res = await stmtSub.bind(`%${coreTerm}%`, limit * 2).all();
    rows.push(...(res.results || []));
  }

  // Deduplicate by ID
  const unique = new Map();
  for (const r of rows) {
    if (!unique.has(r.id)) {
      unique.set(r.id, r);
    }
  }

  const qClean = coreTerm.toLowerCase();

  const sorted = Array.from(unique.values()).sort((a, b) => {
    const nameA = cleanDistrictName(a.name || "").toLowerCase();
    const nameB = cleanDistrictName(b.name || "").toLowerCase();

    const scoreA =
      nameA === qClean ? 0 : nameA.startsWith(qClean) ? 1 : nameA.includes(qClean) ? 2 : 3;
    const scoreB =
      nameB === qClean ? 0 : nameB.startsWith(qClean) ? 1 : nameB.includes(qClean) ? 2 : 3;
    if (scoreA !== scoreB) return scoreA - scoreB;

    let prioA = FEATURE_PRIORITY[a.feature_code] ?? 8;
    let prioB = FEATURE_PRIORITY[b.feature_code] ?? 8;
    if (targetType === "district") {
      prioA = a.feature_code === "ADM2" ? 0 : 10;
      prioB = b.feature_code === "ADM2" ? 0 : 10;
    } else if (targetType === "village") {
      prioA = ["PPL", "PPLL", "PPLF", "PPLR", "PPLS"].includes(a.feature_code) ? 0 : 10;
      prioB = ["PPL", "PPLL", "PPLF", "PPLR", "PPLS"].includes(b.feature_code) ? 0 : 10;
    }
    if (prioA !== prioB) return prioA - prioB;

    const popA = a.population || 0;
    const popB = b.population || 0;
    if (popB !== popA) return popB - popA;

    return nameA.length - nameB.length;
  });

  return sorted.slice(0, limit).map((r) => {
    const pop = r.population || 0;
    let displayType = "village";
    if (r.feature_code === "PPL") {
      displayType = pop >= 100000 ? "city" : pop >= 10000 ? "town" : "village";
    } else {
      displayType = FEATURE_LABELS[r.feature_code] || "place";
    }

    const item = {
      name: r.feature_code === "ADM2" ? cleanDistrictName(r.name) : r.name,
      latitude: parseFloat(r.latitude),
      longitude: parseFloat(r.longitude),
      admin1: r.admin1 || "",
      admin2: cleanDistrictName(r.admin2 || ""),
      admin3: r.admin3 || "",
      country: "India",
      type: displayType,
      type_label: displayType,
      population: pop,
      source: "d1",
    };
    item.label = buildLabel(item);
    return item;
  });
}

// ----------------- Live Geocoding Fallback -----------------
async function searchLive(query, limit) {
  try {
    const photonUrl = `https://photon.komoot.io/api/?q=${encodeURIComponent(
      query
    )}&limit=${limit * 2}&lang=en`;
    const resp = await fetch(photonUrl, {
      headers: { "User-Agent": "LiveWeatherTracker/2.0 (Cloudflare)" },
    });
    if (!resp.ok) return [];
    const data = await resp.json();
    const out = [];

    for (const f of data.features || []) {
      const p = f.properties || {};
      if (p.countrycode && p.countrycode !== "IN") continue;
      const coords = (f.geometry && f.geometry.coordinates) || [];
      if (coords.length < 2) continue;

      const name = p.name || query;
      let typ = p.osm_value || p.type || "place";
      if (p.osm_key === "boundary" && p.osm_value === "administrative") {
        typ = "district";
      }

      const item = {
        name,
        latitude: coords[1],
        longitude: coords[0],
        admin1: p.state || "",
        admin2: cleanDistrictName(p.district || p.county || p.city || ""),
        admin3: "",
        country: "India",
        type: typ,
        type_label: typ,
        source: "photon",
      };
      item.label = buildLabel(item);
      out.push(item);
      if (out.length >= limit) break;
    }
    return out;
  } catch (e) {
    return [];
  }
}

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const q = (url.searchParams.get("q") || "").trim();
  const limit = Math.min(parseInt(url.searchParams.get("limit") || "8", 10), 20);

  if (q.length < 2) {
    return jsonResponse([]);
  }

  if (/^\d{6}$/.test(q)) {
    const live = await searchLive(q, limit);
    return jsonResponse(live, 3600);
  }

  if (env && env.DB) {
    try {
      const d1Results = await searchD1(env.DB, q, limit);
      if (d1Results && d1Results.length > 0) {
        return jsonResponse(d1Results, 3600);
      }
    } catch (e) {
      console.error("D1 error:", e);
    }
  }

  const fallback = await searchLive(q, limit);
  return jsonResponse(fallback, 3600);
}
