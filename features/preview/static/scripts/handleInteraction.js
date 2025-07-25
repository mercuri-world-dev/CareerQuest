if (!window.__applyNowListenerAdded) {
  window.__applyNowListenerAdded = true;
  document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.apply-now-btn').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        const jobId = btn.getAttribute('data-job-id');
        fetch('/api/job_click', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ job_id: jobId })
        });
      });
    });
  });
}