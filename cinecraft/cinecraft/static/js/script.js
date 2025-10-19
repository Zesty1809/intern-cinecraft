// script.js for login page notification fadeout

document.addEventListener('DOMContentLoaded', function() {
  // Auto-hide messages after 2.5 seconds
  var messages = document.querySelectorAll('.message.show');
  if (messages.length) {
    setTimeout(function() {
      messages.forEach(function(msg) {
        msg.classList.remove('show');
        msg.style.display = 'none';
      });
    }, 2500);
  }
});
