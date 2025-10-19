// register.js — basic client-side validation for registration form

document.addEventListener('DOMContentLoaded', function() {
  var form = document.querySelector('form[action="' + window.location.pathname + '"]');
  if (!form) {
    form = document.querySelector('form');
  }
  if (!form) return;

  form.addEventListener('submit', function(e) {
    var username = (form.querySelector('input[name="username"]') || {}).value || '';
    var email = (form.querySelector('input[name="email"]') || {}).value || '';
    var pwd = (form.querySelector('input[name="password"]') || {}).value || '';
    var cpwd = (form.querySelector('input[name="confirm_password"]') || {}).value || '';

    // Basic client-side checks
    if (!username.trim() || !email.trim() || !pwd) {
      e.preventDefault();
      showMessage('Please fill all required fields.', 'error');
      return false;
    }

    if (pwd !== cpwd) {
      e.preventDefault();
      showMessage('Passwords do not match.', 'error');
      return false;
    }

    // Allow submit
    return true;
  });

  function showMessage(text, type) {
    var area = document.querySelector('.message-area') || document.querySelector('.auth-card');
    var div = document.createElement('div');
    div.className = 'message show ' + (type || 'error');
    div.textContent = text;
    area.appendChild(div);
    setTimeout(function() { div.classList.remove('show'); div.style.display = 'none'; }, 2500);
  }
});
