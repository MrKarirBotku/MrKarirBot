const state = { query: "", remote: false, offset: 0, limit: 20, loading: false };

const form = document.querySelector("#search-form");
const input = document.querySelector("#search-input");
const remoteOnly = document.querySelector("#remote-only");
const list = document.querySelector("#job-list");
const summary = document.querySelector("#result-summary");
const loadMore = document.querySelector("#load-more");
const template = document.querySelector("#job-template");

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
  [job.location, job.is_remote ? "Remote" : null, job.job_type, job.salary_text]
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

  try {
    const response = await fetch(`/api/v1/jobs?${params}`);
    if (!response.ok) throw new Error("API tidak tersedia");
    const jobs = await response.json();
    if (!append) list.replaceChildren();
    jobs.forEach(renderJob);

    const shown = list.querySelectorAll(".job-card").length;
    summary.textContent = shown
      ? `${shown} lowongan ditampilkan${state.query ? ` untuk “${state.query}”` : ""}.`
      : "Belum ada lowongan yang cocok dengan pencarian ini.";
    if (!shown) list.innerHTML = '<div class="empty">Coba kata kunci atau filter yang berbeda.</div>';
    loadMore.hidden = jobs.length < state.limit;
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
