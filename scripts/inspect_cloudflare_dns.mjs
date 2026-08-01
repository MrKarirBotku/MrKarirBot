const apiBase = "https://api.cloudflare.com/client/v4";
const zoneName = "mrkarirai.web.id";
const token = process.env.CLOUDFLARE_API_TOKEN;
const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;

if (!token || !accountId) {
  throw new Error("Cloudflare credentials are not configured");
}

async function cloudflare(path) {
  const response = await fetch(`${apiBase}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
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

if (zones.length !== 1) {
  throw new Error(`Expected one active zone for ${zoneName}, found ${zones.length}`);
}

const records = await cloudflare(`/zones/${zones[0].id}/dns_records?per_page=100`);
const relevantNames = new Set([
  zoneName,
  `www.${zoneName}`,
  `_openai-site-verification.${zoneName}`,
]);

const relevantRecords = records
  .filter((record) => relevantNames.has(record.name))
  .map(({ id, type, name, content, proxied, ttl }) => ({ id, type, name, content, proxied, ttl }));

console.log(JSON.stringify({ zone: zoneName, status: zones[0].status, records: relevantRecords }, null, 2));
