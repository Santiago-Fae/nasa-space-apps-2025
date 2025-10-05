/* ===== tiny DOM helpers ===== */
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));

/* ===== year ===== */
$("#year").textContent = new Date().getFullYear();

/* ===== simple carousel ===== */
const slides = [
    {
        text: "Explore hundreds of NASA bioscience articles. Filter, search, and map how topics connect.",
        img: "planet.png",
        alt: "Illustration of a ringed planet",
    },
    {
        text: "Build a visual map of overlapping categories and discover related work.",
        img: "saturn_rotating.gif",
        alt: "Saturn rotating on its axis",
    },
];
let slideIdx = 0;
function renderSlide(i) {
    $("#slideCopy").textContent = slides[i].text;
    $("#slideImg").src = slides[i].img;
    $("#slideImg").alt = slides[i].alt;
}
renderSlide(slideIdx);
$(".carousel-nav.prev").addEventListener("click", () => {
    slideIdx = (slideIdx - 1 + slides.length) % slides.length;
    renderSlide(slideIdx);
});
$(".carousel-nav.next").addEventListener("click", () => {
    slideIdx = (slideIdx + 1) % slides.length;
    renderSlide(slideIdx);
});

/* ===== view routing ===== */
const homeView = $("#home-view");
const explorerView = $("#explorer-view");
function routeTo(view) {
    if (view === "explorer") {
        homeView.classList.remove("active");
        explorerView.classList.add("active");
        history.replaceState(null, "", "#explorer");
    } else {
        explorerView.classList.remove("active");
        homeView.classList.add("active");
        history.replaceState(null, "", "#home");
    }
}
$("#startExploring").addEventListener("click", () => routeTo("explorer"));
$("#backHome").addEventListener("click", () => routeTo("home"));
if (location.hash === "#explorer") routeTo("explorer");

/* ===== Finder mock ===== */
const chipsWrap = $("#interestChips");
const interestInput = $("#interestInput");
$("#addInterest").addEventListener("click", () => {
    addChip(interestInput.value);
    interestInput.value = "";
    interestInput.focus();
});
interestInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        addChip(interestInput.value);
        interestInput.value = "";
    }
});
function addChip(label) {
    const val = (label || "").trim();
    if (!val) return;
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.innerHTML = `<span>${escapeHtml(
        val
    )}</span><button aria-label="Remove ${escapeHtml(
        val
    )}" title="Remove">×</button>`;
    chip.querySelector("button").addEventListener("click", () => chip.remove());
    chipsWrap.appendChild(chip);
}
$$(".chip-delete").forEach((btn) =>
    btn.addEventListener("click", () => btn.closest("li")?.remove())
);

$("#searchBtn").addEventListener("click", () => {
    const selectedKeywords = $$("#keywordGroup input:checked").map(
        (i) => i.value
    );
    const interests = $$("#interestChips .chip span").map((s) => s.textContent);
    const items = mockSearch({ keywords: selectedKeywords, interests });
    renderResults(items);
});
function renderResults(items) {
    const list = $("#resultsList");
    list.innerHTML = "";
    if (!items.length) {
        list.innerHTML = `<li>No results found. Try adjusting your filters.</li>`;
        return;
    }
    items.forEach((it, idx) => {
        const li = document.createElement("li");
        li.className = "result-row";
        li.innerHTML = `
      <div class="result-idx">${idx + 1}</div>
      <div class="result-meta">
        <div class="result-title">${escapeHtml(it.title)}</div>
        <div class="result-authors">${escapeHtml(it.authors)}</div>
        <div class="result-desc">${escapeHtml(it.snippet)}</div>
      </div>
      <button class="result-open" type="button">Open</button>
    `;
        li.querySelector(".result-open").addEventListener("click", () =>
            window.open(it.url, "_blank", "noopener")
        );
        list.appendChild(li);
    });
}
function mockSearch({ keywords, interests }) {
    const base = [
        {
            title: "Conservation of microgravity response in Enterobacteriaceae",
            authors: "A. Soni et al.",
            snippet: "Analysis of trp genes and microgravity response.",
            url: "https://example.com/1",
            tags: ["microgravity", "bacteria"],
        },
        {
            title: "Magnesium transport under modeled microgravity",
            authors: "J. Doe, A. Smith",
            snippet: "Ion transport regulation with magnesium focus.",
            url: "https://example.com/2",
            tags: ["magnesium", "microgravity"],
        },
        {
            title: "Mice muscle adaptation after spaceflight",
            authors: "R. Chen, K. Patel",
            snippet: "Skeletal muscle fiber changes in murine models.",
            url: "https://example.com/3",
            tags: ["mice", "physiology"],
        },
    ];
    let out = base.slice();
    if (keywords?.length)
        out = out.filter((it) =>
            keywords.some((k) =>
                it.tags.join(" ").toLowerCase().includes(k.toLowerCase())
            )
        );
    if (interests?.length)
        out = out.filter((it) =>
            interests.some((ch) =>
                (it.title + it.snippet).toLowerCase().includes(ch.toLowerCase())
            )
        );
    return out;
}
function escapeHtml(str) {
    return String(str).replace(
        /[&<>"']/g,
        (m) =>
            ({
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;",
            }[m])
    );
}

/* ===== Explorer page: PDF → keyword cloud ===== */
const pdfKeywords = [
    "Bioscience",
    "Synthetic Biology",
    "Drug Discovery",
    "Informatics",
    "Genetics",
    "CRISPR",
    "Genome",
    "Machine Learning",
];
const cloud = $("#keywordCloud");
pdfKeywords.forEach((kw, i) => {
    const span = document.createElement("span");
    span.className =
        "keyword" + (i % 3 === 0 ? " big" : i % 5 === 0 ? " alt" : "");
    span.textContent = kw;
    cloud.appendChild(span);
});

/* ===== Graph (Canvas + d3-force) ===== */
const canvas = $("#graphCanvas");
const ctx = canvas.getContext("2d");
let graph = { nodes: [], links: [] };
let sim,
    transform = { x: 0, y: 0, k: 1 };
let hovered = null;

/* ensure canvas has pixel size */
function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 800;
    const h = canvas.clientHeight || 500;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.resetTransform?.(); // clear any previous transforms
    transform = { x: canvas.width / 2, y: canvas.height / 2, k: 0.85 };
    draw();
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

/* pan/zoom */
let isPanning = false,
    last = { x: 0, y: 0 };
canvas.addEventListener("mousedown", (e) => {
    isPanning = true;
    last = { x: e.clientX, y: e.clientY };
});
window.addEventListener("mouseup", () => (isPanning = false));
window.addEventListener("mousemove", (e) => {
    if (isPanning) {
        const dx = e.clientX - last.x,
            dy = e.clientY - last.y;
        last = { x: e.clientX, y: e.clientY };
        transform.x += dx;
        transform.y += dy;
        draw();
    }
});
canvas.addEventListener(
    "wheel",
    (e) => {
        e.preventDefault();
        const dpr = window.devicePixelRatio || 1;
        const offsetX = e.offsetX * dpr,
            offsetY = e.offsetY * dpr;
        const k = Math.exp(-e.deltaY * 0.001);
        const x = (offsetX - transform.x) / transform.k;
        const y = (offsetY - transform.y) / transform.k;
        transform.k *= k;
        transform.x = offsetX - x * transform.k;
        transform.y = offsetY - y * transform.k;
        draw();
    },
    { passive: false }
);

/* hover + click */
canvas.addEventListener("mousemove", (e) => {
    const dpr = window.devicePixelRatio || 1;
    const p = screenToWorld(e.offsetX * dpr, e.offsetY * dpr);
    hovered = pickNode(p.x, p.y);
    const tip = $("#tooltip");
    if (hovered) {
        tip.hidden = false;
        tip.style.left = e.offsetX + 14 + "px";
        tip.style.top = e.offsetY + 14 + "px";
        tip.innerHTML = `<strong>${escapeHtml(hovered.title)}</strong><br>${(
            hovered.categories || []
        ).join(", ")}`;
    } else {
        tip.hidden = true;
    }
    draw();
});
canvas.addEventListener("click", () => {
    if (hovered && hovered.link)
        window.open(hovered.link, "_blank", "noopener");
});

function screenToWorld(sx, sy) {
    return {
        x: (sx - transform.x) / transform.k,
        y: (sy - transform.y) / transform.k,
    };
}

/* node lookup */
function nodeIndex() {
    return new Map(graph.nodes.map((n) => [n.id, n]));
}
function linkXY(l, map) {
    const s = typeof l.source === "object" ? l.source : map.get(l.source);
    const t = typeof l.target === "object" ? l.target : map.get(l.target);
    return s && t ? { sx: s.x, sy: s.y, tx: t.x, ty: t.y } : null;
}

function pickNode(x, y) {
    const map = nodeIndex();
    for (const n of graph.nodes) {
        const r = nodeRadius(n, map);
        const dx = x - (n.x || 0),
            dy = y - (n.y || 0);
        if (dx * dx + dy * dy <= r * r) return n;
    }
    return null;
}

function nodeRadius(n, map) {
    const base = 10;
    let deg = 0;
    for (const l of graph.links) {
        const s = typeof l.source === "object" ? l.source : map.get(l.source);
        const t = typeof l.target === "object" ? l.target : map.get(l.target);
        if (s === n || t === n) deg++;
    }
    return base + Math.min(10, deg * 1.5);
}

/* start simulation */
function startSim() {
    if (sim) sim.stop();
    sim = d3
        .forceSimulation(graph.nodes)
        .force(
            "link",
            d3
                .forceLink(graph.links)
                .id((d) => d.id)
                .distance((l) => 160 + (l.weight || 1) * 40)
                .strength(0.05)
        )
        .force("charge", d3.forceManyBody().strength(-240))
        .force(
            "collide",
            d3
                .forceCollide()
                .radius((d) => nodeRadius(d, nodeIndex()) + 4)
                .iterations(2)
        )
        .force("center", d3.forceCenter(canvas.width / 2, canvas.height / 2))
        .alpha(1)
        .alphaDecay(0.02)
        .on("tick", draw);
}

/* draw function */
function draw() {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.k, transform.k);

    const map = nodeIndex();

    // draw links
    ctx.globalAlpha = 0.25;
    ctx.lineWidth = 1.2;
    for (const l of graph.links) {
        const xy = linkXY(l, map);
        if (!xy) continue;
        ctx.beginPath();
        ctx.moveTo(xy.sx, xy.sy);
        ctx.lineTo(xy.tx, xy.ty);
        ctx.strokeStyle =
            l.weight >= 3 ? "#eab308" : l.weight >= 2 ? "#7dd3fc" : "#93c5fd";
        ctx.stroke();
    }

    // draw nodes
    ctx.globalAlpha = 1;
    for (const n of graph.nodes) {
        const r = nodeRadius(n, map);
        ctx.beginPath();
        ctx.arc(n.x || 0, n.y || 0, r, 0, Math.PI * 2);
        const col = colorFromCategory(n.categories && n.categories[0]);
        ctx.fillStyle = hovered && hovered.id === n.id ? "#f97316" : col;
        ctx.fill();
    }
}

/* deterministic color */
function colorFromCategory(cat) {
    const str = cat || "uncategorized";
    let h = 0;
    for (let i = 0; i < str.length; i++)
        h = ((h << 5) - h + str.charCodeAt(i)) | 0;
    const hue = Math.abs(h) % 360;
    return `hsl(${hue},70%,55%)`;
}

/* build links */
function buildLinks(nodes, minShared = 1, allowCats = null) {
    const links = [];
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            const A = allowCats
                ? nodes[i].categories.filter((c) => allowCats.has(c))
                : nodes[i].categories;
            const B = allowCats
                ? nodes[j].categories.filter((c) => allowCats.has(c))
                : nodes[j].categories;
            const shared = A.filter((c) => B.includes(c));
            if (shared.length >= minShared)
                links.push({
                    source: nodes[i].id,
                    target: nodes[j].id,
                    weight: shared.length,
                    shared,
                });
        }
    }
    return links;
}

/* UI controls */
const $thresh = $("#threshold");
const $threshVal = $("#threshVal");
const $cat = $("#categoryFilter");
const $q = $("#searchBox");

$thresh.addEventListener("input", refreshGraph);
$cat.addEventListener("change", refreshGraph);
$q.addEventListener("input", draw);

/* load data & initialize */
let RAW = [];
fetch("categorized.json")
    .then((r) => r.json())
    .then((data) => {
        RAW = data.map((d) => ({
            id: d.id,
            title: d.title || `Article ${d.id}`,
            link: d.link || "#",
            categories: Array.isArray(d.categories)
                ? d.categories
                      .map((c) => String(c).toLowerCase().trim())
                      .filter(Boolean)
                : [],
        }));
        const allCats = [...new Set(RAW.flatMap((n) => n.categories))].sort();
        for (const c of allCats) {
            const o = document.createElement("option");
            o.value = c;
            o.textContent = c;
            $cat.appendChild(o);
        }
        refreshGraph();
    })
    .catch((err) => {
        console.error("categorized.json load failed", err);
        alert(
            "Could not load categorized.json. If running locally, start a server, e.g. `python -m http.server`."
        );
    });

function refreshGraph() {
    const minShared = parseInt($thresh.value || "1", 10);
    $threshVal.textContent = String(minShared);
    const selected = $cat.value;
    const allow = selected ? new Set([selected]) : null;

    const nodes = selected
        ? RAW.filter((n) => n.categories.includes(selected))
        : RAW.slice();
    const links = buildLinks(nodes, minShared, allow);
    graph = {
        nodes: nodes.map((n) => ({ ...n })),
        links: links.map((l) => ({ ...l })),
    };

    transform = { x: canvas.width / 2, y: canvas.height / 2, k: 0.85 };
    startSim();
}

/* title search highlight layer */
const _drawOrig = draw;
draw = function () {
    _drawOrig();
    const q = $q.value.trim().toLowerCase();
    if (!q) return;

    ctx.save();
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.k, transform.k);
    ctx.globalAlpha = 0.9;

    for (const n of graph.nodes) {
        if ((n.title || "").toLowerCase().includes(q)) {
            ctx.beginPath();
            ctx.arc(
                n.x || 0,
                n.y || 0,
                nodeRadius(n, nodeIndex()) + 5,
                0,
                Math.PI * 2
            );
            ctx.strokeStyle = "#f97316";
            ctx.lineWidth = 2.5;
            ctx.stroke();
        }
    }
    ctx.restore();
};
