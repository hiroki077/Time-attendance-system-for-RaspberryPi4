let pollingIndexInterval = null;

function startPollingIndex() {
  pollingIndexInterval = setInterval(() => {
    fetch('/state')
      .then(resp => resp.json())
      .then(data => {
        if (data.customer_state === "Serving") {
          clearInterval(pollingIndexInterval);
          // window.API_BASEを使う（console.logで必ず確認！）
          console.log("リダイレクト先", window.API_BASE + "/welcome/");
          window.location.href = window.API_BASE + "/welcome/";

        }
      })
      .catch(err => console.log(err));
  }, 1000);
}

window.addEventListener("load", startPollingIndex);
