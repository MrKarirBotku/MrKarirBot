const initialParams = new URLSearchParams(window.location.search);
const state = {
  query: initialParams.get("q") || "",
  remote: initialParams.get("remote") === "true",
  location: initialParams.get("location") || "",
  workSystem: initialParams.get("work_system") || "",
  employmentType: initialParams.get("employment_type") || "",
  sort: initialParams.get("sort") || "newest",
  offset: 0,
  limit: 20,
  loading: false,
};

const form = document.querySelector("#search-form");
const input = document.querySelector("#search-input");
const remoteOnly = document.querySelector("#remote-only");
const list = document.querySelector("#job-list");
const summary = document.querySelector("#result-summary");
const loadMore = document.querySelector("#load-more");
const template = document.querySelector("#job-template");
const locationFilter = document.querySelector("#location-filter");
const workSystemFilter = document.querySelector("#work-system-filter");
const employmentFilter = document.querySelector("#employment-filter");
const sortFilter = document.querySelector("#sort-filter");

input.value = state.query;
remoteOnly.checked = state.remote;
locationFilter.value = state.location;
workSystemFilter.value = state.workSystem;
employmentFilter.value = state.employmentType;
sortFilter.value = state.sort;

function formatDate(value) {
  if (!value) return "Baru diperbarui";
  return new Intl.DateTimeFormat("id-ID", { day: "numeric", month: "short", year: "numeric" })
    .format(new Date(value));
}

function renderJob(job) {
  const node = template.content.cloneNode(true);
  node.querySelector(".company-avatar").textContent = job.company.charAt(0).toUpperCase();
  node.querySelector(".source-badge").textContent = job.source_name;
  node.querySelector("time").textContent = formatDate(job.published_at);
  node.querySelector("h3").textContent = job.title;
  node.querySelector(".company").textContent = job.company;

  const meta = node.querySelector(".job-meta");
  const salary = job.salary_is_visible && (job.salary_min || job.salary_max)
    ? `${job.salary_currency || ""} ${job.salary_min || ""}${job.salary_max ? `–${job.salary_max}` : ""}`.trim()
    : null;
  [job.location, job.is_remote ? "Remote" : job.work_system, job.job_type, salary]
    .filter(Boolean)
    .forEach((value) => {
      const chip = document.createElement("span");
      chip.textContent = value;
      meta.appendChild(chip);
    });

  const link = node.querySelector(".apply-link");
  link.href = job.source_url;
  list.appendChild(node);
}

async function loadJobs({ append = false } = {}) {
  if (state.loading) return;
  state.loading = true;
  summary.textContent = "Memuat lowongan terbaru…";
  loadMore.hidden = true;

  const params = new URLSearchParams({
    q: state.query,
    remote: String(state.remote),
    limit: String(state.limit),
    offset: String(state.offset),
  });
  if (state.location) params.set("location", state.location);
  if (state.workSystem) params.set("work_system", state.workSystem);
  if (state.employmentType) params.set("employment_type", state.employmentType);
  params.set("sort", state.sort);
  const shareParams = new URLSearchParams(params);
  shareParams.delete("offset");
  shareParams.delete("limit");
  if (!state.query) shareParams.delete("q");
  if (!state.remote) shareParams.delete("remote");
  window.history.replaceState({}, "", `${window.location.pathname}${shareParams.size ? `?${shareParams}` : ""}`);

  try {
    const response = await fetch(`/api/v1/jobs?${params}`);
    if (!response.ok) throw new Error("API tidak tersedia");
    const page = await response.json();
    if (!append) list.replaceChildren();
    page.items.forEach(renderJob);

    const shown = list.querySelectorAll(".job-card").length;
    summary.textContent = shown
      ? `${shown} lowongan ditampilkan${state.query ? ` untuk “${state.query}”` : ""}.`
      : "Belum ada lowongan yang cocok dengan pencarian ini.";
    if (!shown) list.innerHTML = '<div class="empty">Coba kata kunci atau filter yang berbeda.</div>';
    loadMore.hidden = !page.has_more;
  } catch (error) {
    if (!append) list.innerHTML = '<div class="empty">Lowongan belum dapat dimuat. Silakan coba kembali.</div>';
    summary.textContent = error.message;
  } finally {
    state.loading = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  state.query = input.value.trim();
  state.offset = 0;
  document.querySelector("#lowongan").scrollIntoView();
  loadJobs();
});

remoteOnly.addEventListener("change", () => {
  state.remote = remoteOnly.checked;
  state.offset = 0;
  loadJobs();
});

let debounceTimer;
input.addEventListener("input", () => {
  window.clearTimeout(debounceTimer);
  debounceTimer = window.setTimeout(() => {
    state.query = input.value.trim();
    state.offset = 0;
    loadJobs();
  }, 350);
});

function applyFilters() {
  state.location = locationFilter.value.trim();
  state.workSystem = workSystemFilter.value;
  state.employmentType = employmentFilter.value;
  state.sort = sortFilter.value;
  state.offset = 0;
  loadJobs();
}

locationFilter.addEventListener("input", () => {
  window.clearTimeout(debounceTimer);
  debounceTimer = window.setTimeout(applyFilters, 350);
});
[workSystemFilter, employmentFilter, sortFilter].forEach((element) => {
  element.addEventListener("change", applyFilters);
});

loadMore.addEventListener("click", () => {
  state.offset += state.limit;
  loadJobs({ append: true });
});

document.querySelectorAll("[data-query]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.query;
    state.query = button.dataset.query;
    state.offset = 0;
    document.querySelector("#lowongan").scrollIntoView();
    loadJobs();
  });
});

loadJobs();
