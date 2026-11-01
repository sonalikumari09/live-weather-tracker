/**
 * Cloudflare Pages Function: /api/weather
 * Fetches current weather and 7-day forecast from Open-Meteo with edge caching.
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
  )}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,is_day&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m,apparent_temperature&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,sunrise,sunset&timezone=auto&forecast_days=7`;

  try {
    const resp = await fetch(openMeteoUrl, {
      headers: { "User-Agent": "LiveWeatherTracker/2.0 (Cloudflare)" },
    });

    if (!resp.ok) {
      return new Response(JSON.stringify({ error: "Weather provider unavailable" }), {
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
    return new Response(JSON.stringify({ error: "Network or server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
