// 主端末（Primary）でのみ動く: /state をポーリングし、customer_state が "Serving" なら /customer に遷移
let attendanceInterval = null;

function startPollingAttendance() {
  attendanceInterval = setInterval(() => {
    fetch('/state')
      .then(resp => resp.json())
      .then(data => {
        if (data.customer_state === "Serving") {
          clearInterval(attendanceInterval); // ここで止める
          window.location.href = "http://192.168.24.62:8000/welcome/";
        }
      })
      .catch(err => console.log(err));
  }, 1000);
}
window.addEventListener("load", startPollingAttendance);

