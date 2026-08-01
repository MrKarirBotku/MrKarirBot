const apiBase = "https://api.cloudflare.com/client/v4";
const zoneName = "mrkarirai.web.id";
const token = process.env.CLOUDFLARE_API_TOKEN;
const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;

if (!token || !accountId) {
  throw new Error("Cloudflare credentials are not configured");
}

async function cloudflare(path, init = {}) {
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...init.headers,
    },
  });
  const payload = await response.json();
  if (!response.ok || !payload.success) {
    throw new Error(`Cloudflare API request failed: ${response.status}`);
  }
  return payload.result;
}

const zones = await cloudflare(
  `/zones?name=${encodeURIComponent(zoneName)}&account.id=${encodeURIComponent(accountId)}`,
);

if (zones.length !== 1 || zones[0].status !== "active") {
  throw new Error(`Expected one active zone for ${zoneName}`);
}

const zoneId = zones[0].id;
const records = await cloudflare(`/zones/${zoneId}/dns_records?per_page=100`);
const conflictingTypes = new Set(["A", "AAAA", "CNAME"]);
const conflicts = records.filter(
  (record) => record.name === zoneName && conflictingTypes.has(record.type),
);

console.log(
  JSON.stringify(
    {
      zone: zoneName,
      conflicts: conflicts.map(({ id, type, name, content, proxied }) => ({
        id,
        type,
        name,
        content,
        proxied,
      })),
    },
    null,
    2,
  ),
);

for (const record of conflicts) {
  await cloudflare(`/zones/${zoneId}/dns_records/${record.id}`, { method: "DELETE" });
  console.log(`Deleted conflicting ${record.type} record for ${record.name}`);
}

console.log(`DNS reconciliation complete; deleted ${conflicts.length} conflicting record(s)`);
