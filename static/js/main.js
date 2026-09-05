const renderDiff = (text) => {
  const diffHtml = Diff2Html.html(text, {
    drawFileList: true,
    matching: "lines",
    outputFormat: "line-by-line"
  });
  document.getElementById("diff").innerHTML = diffHtml;
};

// clone → ブランチ一覧取得
document.getElementById("loadBtn").addEventListener("click", async () => {
  const url = document.getElementById("repoUrl").value;

  document.getElementById("loading").style.display = "block";
  document.getElementById("diff").innerHTML = "";
  document.getElementById("branchSelect").style.display = "none";
  document.getElementById("modeSelect").style.display = "none";
  document.getElementById("commitSelect").style.display = "none";

  const res = await fetch("/clone", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });

  const data = await res.json();
  document.getElementById("loading").style.display = "none";

  // ▼ clone 完了後にまずブランチ選択を表示
  const branchList = document.getElementById("branchList");
  branchList.innerHTML = "";
  data.branches.forEach(b => {
    const opt = document.createElement("option");
    opt.value = b;
    opt.textContent = b;
    branchList.appendChild(opt);
  });

  document.getElementById("branchSelect").style.display = "block";
});

// ▼ ブランチ選択 → コミット一覧取得 → モード選択を表示
document.getElementById("branchList").addEventListener("change", async () => {
  const branch = document.getElementById("branchList").value;

  const res = await fetch("/commits", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ branch })
  });

  const data = await res.json();

  // ▼ コミット一覧をセット
  const commitA = document.getElementById("commitA");
  const commitB = document.getElementById("commitB");
  commitA.innerHTML = "";
  commitB.innerHTML = "";

  data.commits.forEach(c => {
    const optA = document.createElement("option");
    optA.value = c.hash;
    optA.textContent = `${c.hash.slice(0,7)} — ${c.message} (${c.date})`;
    commitA.appendChild(optA);

    const optB = document.createElement("option");
    optB.value = c.hash;
    optB.textContent = `${c.hash.slice(0,7)} — ${c.message} (${c.date})`;
    commitB.appendChild(optB);
  });

  // ▼ ブランチ選択後にモード選択を表示（ここが重要）
  document.getElementById("modeSelect").style.display = "block";
});

// ▼ モード選択 → 差分モードを表示
document.getElementById("mode").addEventListener("change", () => {
  const mode = document.getElementById("mode").value;

  document.getElementById("diffMode").style.display = "none";

  if (mode === "diff") {
    document.getElementById("diffMode").style.display = "block";
    document.getElementById("commitSelect").style.display = "block";
  }
});

// ▼ 差分表示
document.getElementById("diffBtn").addEventListener("click", async () => {
  const a = document.getElementById("commitA").value;
  const b = document.getElementById("commitB").value;

  const res = await fetch("/diff", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ a, b })
  });

  const data = await res.json();
  renderDiff(data.diff);
});

let searchResults = [];
let currentPage = 1;
const perPage = 20;   // 1ページあたりの件数
let currentKeyword = "";

function highlight(text, keyword) {
  const safeKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); // 正規表現エスケープ
  const regex = new RegExp(safeKeyword, "gi");
  return text.replace(regex, match => `<mark>${match}</mark>`);
}

// ▼ ページを描画する関数
function renderSearchPage() {
  const resultsDiv = document.getElementById("searchResults");
  resultsDiv.innerHTML = "";

  const start = (currentPage - 1) * perPage;
  const end = start + perPage;

  const pageItems = searchResults.slice(start, end);

  pageItems.forEach(file => {
    const fileBox = document.createElement("div");
    fileBox.style.marginBottom = "30px";

    fileBox.innerHTML = `<h4>${file.path}</h4>`;

    file.hunks.forEach((hunk, index) => {
      const contextHtml = hunk.context
        .map((line, i) => {
          const lineNumber = hunk.start + i;
          const highlighted = highlight(line, currentKeyword);
          return `<span style="color:#888;" class="linejump" data-path="${file.path}" data-line="${lineNumber}">${lineNumber}</span>  ${highlighted}`;
        })
        .join("\n");

      const hunkBox = document.createElement("div");
      hunkBox.innerHTML = `
        <pre class="code-block">${contextHtml}</pre>
      `;

      fileBox.appendChild(hunkBox);

      // ▼ 次のまとまりがあるなら “…” を挟む
      if (index < file.hunks.length - 1) {
        const sep = document.createElement("div");
        sep.textContent = "...";
        sep.style.color = "#999";
        sep.style.margin = "10px 0";
        fileBox.appendChild(sep);
      }
    });

    resultsDiv.appendChild(fileBox);
  });

  // ▼ 行番号クリックイベント
  document.querySelectorAll(".linejump").forEach(el => {
    el.addEventListener("click", () => {
      const path = el.dataset.path;
      const line = el.dataset.line;

      const repoUrl = document.getElementById("repoUrl").value;
      const branch = document.getElementById("branchList").value;

      // ▼ GitHub の repo 部分を抽出
      const m = repoUrl.match(/github\.com\/([^\/]+\/[^\/]+?)(?:\.git)?$/);
      if (!m) return;

      const repo = m[1];

      // ▼ GitHub の行番号ジャンプ URL を組み立てる
      const githubUrl =
        `https://github.com/${repo}/blob/${branch}/${path}#L${line}`;

      window.open(githubUrl, "_blank");
    });
  });

  const totalPages = Math.ceil(searchResults.length / perPage);
  document.getElementById("pageInfo").textContent =
    `${currentPage} / ${totalPages}`;

  document.getElementById("pagination").style.display =
    searchResults.length > perPage ? "block" : "none";
}

// ▼ 検索ボタン
document.getElementById("searchBtn").addEventListener("click", async () => {
  currentKeyword = document.getElementById("searchKeyword").value;

  const res = await fetch("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keyword: currentKeyword })
  });

  const data = await res.json();
  searchResults = data.results;
  currentPage = 1;

  if (searchResults.length === 0) {
    document.getElementById("searchResults").innerHTML =
      "<p>検索結果はありません。</p>";
    document.getElementById("pagination").style.display = "none";
    return;
  }

  renderSearchPage();
});

// ▼ 前へ
document.getElementById("prevPage").addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage--;
    renderSearchPage();
  }
});

// ▼ 次へ
document.getElementById("nextPage").addEventListener("click", () => {
  const totalPages = Math.ceil(searchResults.length / perPage);
  if (currentPage < totalPages) {
    currentPage++;
    renderSearchPage();
  }
});

// ▼ モード選択 → diffMode or searchMode を表示
document.getElementById("mode").addEventListener("change", () => {
  const mode = document.getElementById("mode").value;

  // 全モードを非表示
  document.getElementById("diffMode").style.display = "none";
  document.getElementById("searchMode").style.display = "none";
  document.getElementById("commitSelect").style.display = "none";

  if (mode === "diff") {
    document.getElementById("diffMode").style.display = "block";
    document.getElementById("commitSelect").style.display = "block";
  }

  if (mode === "search") {
    document.getElementById("searchMode").style.display = "block";
  }
});

