// script.js for login page notification fadeout

document.addEventListener('DOMContentLoaded', function() {
  // Auto-hide messages after 2.5 seconds
  var messages = document.querySelectorAll('.message.show');
  if (messages.length) {
    messages.forEach(function(msg) {
      // OTP messages stay longer (7s); others hide earlier (2.5s)
      var timeout = msg.classList.contains('otp') ? 7000 : 2500;
      setTimeout(function() {
        msg.classList.remove('show');
        msg.style.display = 'none';
      }, timeout);
    });
  }
});
