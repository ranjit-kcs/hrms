export async function getRuntimeConfig() {
  const res = await fetch(
    "/api/method/hrms.api.runtime_config.get_frontend_config",
    {
      credentials: "include",
      cache: "no-cache"
    }
  );

  const data = await res.json();
  console.log(data, "data");
  
  return data.message || {};
}
