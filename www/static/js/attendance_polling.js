let attendanceInterval = null;

function startPollingAttendance() {
  attendanceInterval = setInterval(() => {
    fetch('/state')
      .then(resp => resp.json())
      .then(data => {
        if (data.customer_state === "Serving") {
          clearInterval(attendanceInterval);
          window.location.href = window.API_BASE + "/welcome/";
        }
      })
      .catch(err => console.log(err));
  }, 1000);
}
window.addEventListener("load", startPollingAttendance);
