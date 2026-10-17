export async function getRuntimeURLConfig() {
  const res = await fetch(
    "/api/method/hrms.api.runtime_config.get_map_urls",
    {
      credentials: "include",
      cache: "no-cache"
    }
  );

  const data = await res.json();
  // console.log(data, "data");
  
  return data.message || {};
}
