function formatTime(t) {
  return t ? t.split(" ")[1].slice(0,5) : "--:--";
}



function showHistory(history, now_unixtime) {
  let html = "";
  for (const name in history) {
    const logs = history[name].slice().reverse(); // 古い→新しい
    html += `<div class="scan-user-block"><span class="scan-user">${name}</span><div class="scan-times">`;

    logs.forEach((entry, idx) => {
      html += `<span class="scan-time">${formatTime(entry.time)}`;
      // 右端（最新）・打刻が2つの時だけ
      if (idx === logs.length - 1 && logs.length === 2 && entry.timestamp) {
        const elapsed = now_unixtime - entry.timestamp;
        if (elapsed < 3600) {
          const left = 3600 - elapsed;
          const min = Math.floor(left / 60);
          const sec = Math.floor(left % 60);
          html += ` <span class="break-label">休憩中: 残り${min}分${sec.toString().padStart(2, "0")}秒</span>`;
        }
      }
      html += "</span>";
    });
    html += "</div></div>";
  }
  return html || "<div>（本日まだスキャンはありません）</div>";
}





// --- ここから「時刻補正付きリアルタイム表示」実装 ---

let latestHistory = {};
let lastServerTime = 0;      // サーバーから取得したUNIX秒
let lastClientNow = 0;       // 取得時のクライアントのDate.now()値（ms）
let lastNowStr = "--:--";    // サーバーから取得した日付文字列

function updateAttendance() {
  fetch("/data").then(r => r.json()).then(d => {
    // サーバー時刻を取得
    lastServerTime = d.now_unixtime;
    lastClientNow = Date.now();
    lastNowStr = d.now;

    document.getElementById("uid").textContent = d.uid;
    document.getElementById("name").textContent = d.name;
    document.getElementById("scan_time").textContent = d.scan_time;

    // --- 状態表示・色分け ---
    const statusElem = document.getElementById("status");
    statusElem.textContent = d.status;
    statusElem.classList.remove("status-error", "status-break", "status-normal");
    if (d.status.includes("エラー") || d.status.includes("未登録") || d.status.includes("注意")) {
      statusElem.classList.add("status-error");
    } else if (d.status.includes("休憩")) {
      statusElem.classList.add("status-break");
    } else {
      statusElem.classList.add("status-normal");
    }

    latestHistory = d.history || {};
    document.getElementById("scan-history").innerHTML = showHistory(latestHistory, lastServerTime);
  });
}

// 1秒ごとに「補正付き現在時刻」を表示
setInterval(() => {
  if (lastServerTime) {
    const elapsed = Math.floor((Date.now() - lastClientNow) / 1000);
    const virtualUnixtime = lastServerTime + elapsed;
    const dt = new Date(virtualUnixtime * 1000);
    // サーバーから日付文字列が取得できていれば「日付部分」はそれに揃える
    let nowText = lastNowStr;
    if (nowText.length > 10) {
      // "YYYY/MM/DD " までの部分だけ差し替えて後半はクライアント時刻で
      nowText = nowText.slice(0, 11) + 
        ("0" + dt.getHours()).slice(-2) + ":" +
        ("0" + dt.getMinutes()).slice(-2) + ":" +
        ("0" + dt.getSeconds()).slice(-2);
    } else {
      nowText = dt.getFullYear() + "/" +
        ("0" + (dt.getMonth()+1)).slice(-2) + "/" +
        ("0" + dt.getDate()).slice(-2) + " " +
        ("0" + dt.getHours()).slice(-2) + ":" +
        ("0" + dt.getMinutes()).slice(-2) + ":" +
        ("0" + dt.getSeconds()).slice(-2);
    }
    document.getElementById("now").textContent = nowText;

    // 履歴の休憩残り時間もズレなく表示
    document.getElementById("scan-history").innerHTML = showHistory(latestHistory, virtualUnixtime);
  }
}, 1000);

// 3秒ごとにサーバー値で「大補正」
setInterval(updateAttendance, 1000);

// 初回実行
updateAttendance();

