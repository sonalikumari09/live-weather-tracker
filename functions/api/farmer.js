/**
 * Cloudflare Pages Function: /api/farmer
 * Fetches agricultural metrics (soil temp, moisture, past 7 days rainfall) from Open-Meteo.
 */

export async function onRequestGet({ request }) {
  const url = new URL(request.url);
  const lat = url.searchParams.get("lat");
  const lon = url.searchParams.get("lon");

  if (!lat || !lon) {
    return new Response(JSON.stringify({ error: "Missing lat/lon parameters" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const openMeteoUrl = `https://api.open-meteo.com/v1/forecast?latitude=${encodeURIComponent(
    lat
  )}&longitude=${encodeURIComponent(
    lon
  )}&hourly=soil_temperature_6cm,soil_moisture_3_9cm,precipitation&daily=precipitation_sum,temperature_2m_max,temperature_2m_min,precipitation_probability_max&current=soil_temperature_6cm,soil_moisture_3_9cm&past_days=7&forecast_days=2&timezone=auto`;

  try {
    const resp = await fetch(openMeteoUrl, {
      headers: { "User-Agent": "LiveWeatherTracker/2.0 (Cloudflare)" },
    });

    if (!resp.ok) {
      return new Response(JSON.stringify({ error: "Provider error" }), {
        status: resp.status,
        headers: { "Content-Type": "application/json" },
      });
    }

    const data = await resp.json();

    return new Response(JSON.stringify(data), {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=600, s-maxage=600",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Network error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
