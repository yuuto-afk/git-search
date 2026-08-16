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
  document.getElementById("commitSelect").style.display = "none";
  document.getElementById("branchSelect").style.display = "none";
  document.getElementById("modeSelect").style.display = "none";

  const res = await fetch("/clone", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });

  const data = await res.json();
  document.getElementById("loading").style.display = "none";

  // clone 完了後にモード選択を表示
  document.getElementById("modeSelect").style.display = "block";

  // ブランチ一覧を保存（後で使う）
  window.branches = data.branches;
});

// モード切り替え
document.getElementById("mode").addEventListener("change", () => {
  const mode = document.getElementById("mode").value;

  document.getElementById("diffMode").style.display = "none";

  if (mode === "diff") {
    document.getElementById("diffMode").style.display = "block";

    // ▼ ブランチ一覧を表示
    const branchList = document.getElementById("branchList");
    branchList.innerHTML = "";
    window.branches.forEach(b => {
      const opt = document.createElement("option");
      opt.value = b;
      opt.textContent = b;
      branchList.appendChild(opt);
    });

    document.getElementById("branchSelect").style.display = "block";
  }
});

// ▼ ブランチ選択 → コミット一覧取得
document.getElementById("branchList").addEventListener("change", async () => {
  const branch = document.getElementById("branchList").value;

  const res = await fetch("/commits", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ branch })
  });

  const data = await res.json();

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

  document.getElementById("commitSelect").style.display = "block";
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

