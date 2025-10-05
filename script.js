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
const interestList = $("#interestList");
const interestInput = $("#interestInput");
$("#addInterest").addEventListener("click", () => {
    addInterestItem(interestInput.value);
    interestInput.value = "";
    interestInput.focus();
});
interestInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        addInterestItem(interestInput.value);
        interestInput.value = "";
    }
});

function addInterestItem(label) {
    const val = (label || "").trim();
    if (!val) return;
    const li = document.createElement("li");
    const span = document.createElement("span");
    span.textContent = val;
    const btn = document.createElement("button");
    btn.className = "chip-delete";
    btn.textContent = "Delete";
    btn.type = "button";
    li.appendChild(span);
    li.appendChild(btn);
    interestList.appendChild(li);
}

// event delegation for delete buttons inside the interest list
interestList.addEventListener("click", (e) => {
    const btn = e.target.closest("button.chip-delete");
    if (!btn) return;
    const li = btn.closest("li");
    if (li) li.remove();
});

$("#searchBtn").addEventListener("click", () => {
    const selectedKeywords = $$("#keywordGroup input:checked").map(
        (i) => i.value
    );
    const interests = $$("#interestList li span").map((s) => s.textContent);
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

/* ===== Explorer keyword cloud removed (title retained) ===== */

/* ===== Graph (Canvas + d3-force) ===== */
const canvas = $("#graphCanvas");
const ctx = canvas.getContext("2d");
let graph = { nodes: [], links: [] };
let sim,
    transform = { x: 0, y: 0, k: 1 };
let hovered = null;
let selectedKeywords = new Set();

/* ensure canvas has pixel size */
function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
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
        const { offsetX, offsetY, deltaY } = e;
        const k = Math.exp(-deltaY * 0.001);
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
    const rect = canvas.getBoundingClientRect();
    const scale = canvas.width / rect.width;
    const sx = (e.clientX - rect.left) * scale;
    const sy = (e.clientY - rect.top) * scale;
    const p = screenToWorld(sx, sy);
    hovered = pickNode(p.x, p.y);
    const tip = $("#tooltip");
    if (hovered) {
        tip.hidden = false;
        tip.style.left = e.clientX + 14 + "px";
        tip.style.top = e.clientY + 14 + "px";
        tip.innerHTML = `<strong>${escapeHtml(hovered.title)}</strong><br>${(
            hovered.categories || []
        ).join(", ")}`;
    } else tip.hidden = true;
    draw();
});
canvas.addEventListener("click", (e) => {
    if (hovered && hovered.link)
        window.open(hovered.link, "_blank", "noopener");
});

function screenToWorld(sx, sy) {
    return {
        x: (sx - transform.x) / transform.k,
        y: (sy - transform.y) / transform.k,
    };
}

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
            d3.forceCollide().radius((d) => nodeRadius(d, nodeIndex()) + 4)
        )
        .force("center", d3.forceCenter(canvas.width / 2, canvas.height / 2))
        .alpha(1)
        .alphaDecay(0.02)
        .on("tick", draw);
}

function draw() {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.k, transform.k);

    const map = nodeIndex();

    ctx.globalAlpha = 0.25;
    ctx.lineWidth = 1.2;
    const hasSelection = selectedKeywords && selectedKeywords.size > 0;
    for (const l of graph.links) {
        const xy = linkXY(l, map);
        if (!xy) continue;
        const shared = l.shared || [];
        const intersect = [...selectedKeywords].some((k) => shared.includes(k));
        // If user selected keywords, only draw links that match (hide others)
        if (hasSelection && !intersect) continue;
        ctx.beginPath();
        ctx.moveTo(xy.sx, xy.sy);
        ctx.lineTo(xy.tx, xy.ty);
        ctx.strokeStyle = intersect ? "#FFD166" : "#A3C08F";
        ctx.lineWidth = intersect ? 3 : 1.2;
        ctx.stroke();
    }

    ctx.globalAlpha = 1;
    for (const n of graph.nodes) {
        const r = nodeRadius(n, map);
        ctx.beginPath();
        ctx.arc(n.x || 0, n.y || 0, r, 0, Math.PI * 2);
        const col = colorFromCategory(n.categories && n.categories[0]);
        ctx.fillStyle = hovered && hovered.id === n.id ? "#FFD166" : col;
        ctx.fill();
    }
}

/* === Green palette === */
const PALETTE = ["#4D7C0F", "#8CBE4A", "#B2D683"];
function colorFromCategory(cat) {
    const str = cat || "uncategorized";
    let h = 0;
    for (let i = 0; i < str.length; i++)
        h = ((h << 5) - h + str.charCodeAt(i)) | 0;
    return PALETTE[Math.abs(h) % PALETTE.length];
}

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
        // assign stable pseudo-random launch years for timeline
        assignRandomYears(RAW);
        buildTimelineIndex(RAW);
        renderTimeline();
        const allCats = [...new Set(RAW.flatMap((n) => n.categories))].sort();
        for (const c of allCats) {
            const o = document.createElement("option");
            o.value = c;
            o.textContent = c;
            $cat.appendChild(o);
        }
        // populate searchable checkbox list for keyword highlighting
        const kf = $("#keywordFilter");
        const kfList = $("#kfList");
        const kfSearch = $("#kfSearch");
        if (kf && kfList) {
            // helper to render list items based on a filter
            function renderKfList(filter = "") {
                kfList.innerHTML = "";
                const f = String(filter || "").toLowerCase();
                for (const c of allCats) {
                    if (f && !c.toLowerCase().includes(f)) continue;
                    const id = `kf_${c.replace(/[^a-z0-9]+/gi, "_")}`;
                    const lbl = document.createElement("label");
                    lbl.htmlFor = id;
                    const cb = document.createElement("input");
                    cb.type = "checkbox";
                    cb.id = id;
                    cb.value = c;
                    cb.addEventListener("change", () => {
                        updateSelectedKeywords();
                    });
                    lbl.appendChild(cb);
                    const txt = document.createTextNode(c);
                    lbl.appendChild(txt);
                    kfList.appendChild(lbl);
                }
            }

            function updateSelectedKeywords() {
                const checked = Array.from(
                    kfList.querySelectorAll("input:checked")
                ).map((i) => i.value);
                selectedKeywords = new Set(checked);
                draw();
            }

            kfSearch.addEventListener("input", (e) =>
                renderKfList(e.target.value)
            );
            renderKfList();
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
            ctx.strokeStyle = "#FFD166";
            ctx.lineWidth = 2.5;
            ctx.stroke();
        }
    }
    ctx.restore();
};

/* ===== Timeline (projects per randomized year) ===== */
let TIMELINE = { years: [], byYear: new Map() };

function seededYearFor(item, min = 2010, max = new Date().getFullYear()) {
    // simple string hash on title+id, stable across sessions
    const str = `${item.title}|${item.id}`;
    let h = 2166136261; // FNV-1a base
    for (let i = 0; i < str.length; i++) {
        h ^= str.charCodeAt(i);
        h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
    }
    const rng = Math.abs(h >>> 0) / 2 ** 32; // [0,1)
    const year = Math.floor(min + rng * (max - min + 1));
    return Math.max(min, Math.min(max, year));
}

function assignRandomYears(items) {
    const min = 2010;
    const max = new Date().getFullYear();
    for (const it of items) it.year = seededYearFor(it, min, max);
}

function buildTimelineIndex(items) {
    const by = new Map();
    for (const it of items) {
        const y = it.year;
        if (!by.has(y)) by.set(y, []);
        by.get(y).push(it);
    }
    const years = Array.from(by.keys()).sort((a, b) => a - b);
    TIMELINE = { years, byYear: by };
}

function renderTimeline() {
    const wrap = document.getElementById("timelineChart");
    if (!wrap) return;
    wrap.innerHTML = "";

    const width = Math.max(320, wrap.clientWidth || 800);
    const height = 240;
    const margin = { top: 10, right: 20, bottom: 32, left: 36 };
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", String(height));

    const g = document.createElementNS(svg.namespaceURI, "g");
    g.setAttribute("transform", `translate(${margin.left},${margin.top})`);
    svg.appendChild(g);

    const years = TIMELINE.years;
    if (years.length === 0) {
        wrap.textContent = "No data";
        return;
    }
    const counts = years.map((y) => ({ year: y, count: TIMELINE.byYear.get(y).length }));
    const minY = Math.min(...years);
    const maxY = Math.max(...years);
    const x = (yr) => {
        const t = (yr - minY) / (maxY - minY || 1);
        return Math.round(t * innerW);
    };
    const maxCount = Math.max(1, ...counts.map((d) => d.count));
    const y = (c) => innerH - Math.round((c / maxCount) * innerH);

    // axes
    const axis = document.createElementNS(svg.namespaceURI, "g");
    axis.setAttribute("fill", "#636363");
    axis.setAttribute("font-size", "10");
    // x-axis: show all years
    for (let t = minY; t <= maxY; t++) {
        const tx = x(t);
        const line = document.createElementNS(svg.namespaceURI, "line");
        line.setAttribute("x1", String(tx));
        line.setAttribute("x2", String(tx));
        line.setAttribute("y1", String(innerH + 2));
        line.setAttribute("y2", String(innerH + 6));
        line.setAttribute("stroke", "#cfd8dc");
        g.appendChild(line);

        const label = document.createElementNS(svg.namespaceURI, "text");
        label.setAttribute("x", String(tx));
        label.setAttribute("y", String(innerH + 18));
        label.setAttribute("text-anchor", "middle");
        label.textContent = String(t);
        g.appendChild(label);
    }
    // y-axis: ticks every 2 (0,2,4,... up to next even ≥ maxCount)
    // draw baseline at 0 (no label)
    {
        const gy = y(0);
        const gl = document.createElementNS(svg.namespaceURI, "line");
        gl.setAttribute("x1", "0");
        gl.setAttribute("x2", String(innerW));
        gl.setAttribute("y1", String(gy));
        gl.setAttribute("y2", String(gy));
        gl.setAttribute("stroke", "#90a4ae");
        g.appendChild(gl);
    }
    // Build ticks every 2 and ensure last odd max is included
    const ticks = [];
    for (let v = 2; v <= Math.ceil(maxCount / 2) * 2; v += 2) ticks.push(v);
    if (maxCount % 2 === 1 && !ticks.includes(maxCount)) ticks.push(maxCount);
    for (const gv of ticks) {
        const gy = y(gv);
        const gl = document.createElementNS(svg.namespaceURI, "line");
        gl.setAttribute("x1", "0");
        gl.setAttribute("x2", String(innerW));
        gl.setAttribute("y1", String(gy));
        gl.setAttribute("y2", String(gy));
        gl.setAttribute("stroke", "#e0e0e0");
        gl.setAttribute("stroke-dasharray", "4 4");
        g.appendChild(gl);
        const tl = document.createElementNS(svg.namespaceURI, "text");
        tl.setAttribute("x", String(-8));
        tl.setAttribute("y", String(gy + 3));
        tl.setAttribute("text-anchor", "end");
        tl.textContent = String(gv);
        g.appendChild(tl);
    }

    // line path
    const path = document.createElementNS(svg.namespaceURI, "path");
    const d = counts
        .map((pt, i) => `${i ? "L" : "M"}${x(pt.year)},${y(pt.count)}`)
        .join(" ");
    path.setAttribute("d", d);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "#1f4ba6");
    path.setAttribute("stroke-width", "2");
    g.appendChild(path);

    // points
    counts.forEach((pt) => {
        const cx = x(pt.year);
        const cy = y(pt.count);
        const c = document.createElementNS(svg.namespaceURI, "circle");
        c.setAttribute("cx", String(cx));
        c.setAttribute("cy", String(cy));
        c.setAttribute("r", "4");
        c.setAttribute("fill", "#5b7f2a");
        c.setAttribute("style", "cursor:pointer");
        c.addEventListener("mouseenter", (e) => {
            c.style.filter = "brightness(1.15)";
            showTimelineTooltip(e, pt.year, pt.count);
        });
        c.addEventListener("mouseleave", () => {
            c.style.filter = "";
            hideTimelineTooltip();
        });
        // click opens list (kept)
        c.addEventListener("click", () => showYearProjects(pt.year));
        // touch hold support
        let holdTimer = null;
        c.addEventListener("touchstart", (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            holdTimer = window.setTimeout(() => {
                showTimelineTooltip(touch, pt.year, pt.count);
            }, 350);
        }, { passive: false });
        c.addEventListener("touchend", () => {
            window.clearTimeout(holdTimer);
            hideTimelineTooltip();
        });
        g.appendChild(c);

        const title = document.createElementNS(svg.namespaceURI, "title");
        title.textContent = `${pt.year}: ${pt.count} projects`;
        c.appendChild(title);
    });

    wrap.appendChild(svg);
}

function showYearProjects(year) {
    const host = document.getElementById("timelineDetails");
    if (!host) return;
    const items = TIMELINE.byYear.get(year) || [];
    const header = `<div class="year-header"><strong>${year}</strong> — ${items.length} project(s)</div>`;
    if (!items.length) {
        host.innerHTML = header + `<div class="empty">No projects found.</div>`;
        return;
    }
    const list = items
        .map(
            (it) =>
                `<li><a href="${escapeHtml(it.link)}" target="_blank" rel="noopener">${escapeHtml(
                    it.title
                )}</a></li>`
        )
        .join("");
    host.innerHTML = header + `<ol class="year-list">${list}</ol>`;
}

window.addEventListener("resize", () => renderTimeline());

// floating tooltip for timeline points
let timelineTip = null;
function ensureTimelineTip() {
    if (timelineTip) return timelineTip;
    timelineTip = document.createElement("div");
    timelineTip.className = "tooltip timeline-tip";
    timelineTip.hidden = true;
    const host = document.getElementById("timelineChart");
    host?.appendChild(timelineTip);
    return timelineTip;
}
function showTimelineTooltip(evt, year, count) {
    const tip = ensureTimelineTip();
    tip.hidden = false;
    tip.innerHTML = `<strong>${year}</strong><br>${count} project(s)`;
    const bounds = document.getElementById("timelineChart").getBoundingClientRect();
    const x = (evt.clientX || 0) - bounds.left + 12;
    const y = (evt.clientY || 0) - bounds.top + 12;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
}
function hideTimelineTooltip() {
    if (timelineTip) timelineTip.hidden = true;
}
