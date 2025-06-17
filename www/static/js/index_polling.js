// 主端末（Primary）でのみ動く: /state をポーリングし、customer_state が "Serving" なら /welcome へリダイレクト
let pollingIndexInterval = null;

function startPollingIndex() {
  pollingIndexInterval = setInterval(() => {
    fetch('/state')
      .then(resp => resp.json())
      .then(data => {
        if (data.customer_state === "Serving") {
          clearInterval(pollingIndexInterval); // ここで必ず止める
          window.location.href = "http://192.168.24.62:8000/welcome/";
        }
      })
      .catch(err => console.log(err));
  }, 1000);
}
window.addEventListener("load", startPollingIndex);
