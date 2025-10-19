document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(btn => {
    btn.addEventListener('click', (event) => {
      tabs.forEach(t => t.classList.remove('active'));
      event.currentTarget.classList.add('active');

      const targetId = event.currentTarget.getAttribute('data-target');
      document.querySelectorAll('.af-section').forEach(sec => sec.classList.remove('active'));
      const targetSection = document.getElementById(targetId);
      if (targetSection) targetSection.classList.add('active');
    });
  });

  const toastEl = document.getElementById('af-toast');
  const statsEls = {
    total: document.querySelector('[data-stat="total"]'),
    pending: document.querySelector('[data-stat="pending"]'),
    approved: document.querySelector('[data-stat="approved"]'),
  };
  const allSubmissionTables = () => Array.from(document.querySelectorAll('.submissions-table tbody'));
  const usersActiveGrid = document.querySelector('#tab-users .users-grid.active-users');
  const usersInactiveGrid = document.querySelector('#tab-users .users-grid.inactive-users');

  const statusLabels = {
    approved: 'Approved',
    active: 'Active',
    pending: 'Pending',
    rejected: 'Rejected',
    inactive: 'Inactive',
    draft: 'Draft',
    unknown: 'Unknown',
  };

  function showToast(message, variant = 'info') {
    if (!toastEl) {
      if (variant === 'error') {
        alert(message);
      }
      return;
    }
    toastEl.textContent = message;
    toastEl.classList.remove('hide', 'info', 'success', 'error');
    toastEl.classList.add('show', variant);
    setTimeout(() => {
      toastEl.classList.remove('show');
      toastEl.classList.add('hide');
    }, 2500);
  }

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  const hiddenToken = document.getElementById('csrf-token');
  const csrftoken = getCookie('csrftoken') || (hiddenToken ? hiddenToken.value : '');

  function updateStats() {
    const bodies = allSubmissionTables();
    if (!bodies.length) return;
    let total = 0;
    let pending = 0;
    let approved = 0;

    bodies.forEach(tbody => {
      tbody.querySelectorAll('tr[data-status-key]').forEach((row) => {
        total += 1;
        const key = row.dataset.statusKey || '';
        if (key === 'pending') pending += 1;
        if (key === 'approved' || key === 'active') approved += 1;
      });
    });

    if (statsEls.total) statsEls.total.textContent = total;
    if (statsEls.pending) statsEls.pending.textContent = pending;
    if (statsEls.approved) statsEls.approved.textContent = approved;
  }

  function setRowStatus(row, statusKey) {
    if (!row) return;
    row.dataset.statusKey = statusKey;

    const pill = row.querySelector('.status-pill');
    if (pill) {
      Object.keys(statusLabels).forEach(k => pill.classList.remove(k));
      pill.classList.remove('unknown');
      pill.classList.add(statusKey || 'unknown');
      const label = statusLabels[statusKey] || (statusKey ? statusKey.charAt(0).toUpperCase() + statusKey.slice(1) : 'Unknown');
      pill.textContent = label;
    }

    const approveBtn = row.querySelector('.approve-btn');
    const rejectBtn = row.querySelector('.reject-btn');
    if (approveBtn) {
      approveBtn.disabled = statusKey === 'approved' || statusKey === 'active';
    }
    if (rejectBtn) {
      rejectBtn.disabled = statusKey === 'rejected';
    }
  }

  function findUserCard(pk) {
    if (!pk) return null;
    const cards = document.querySelectorAll(`#tab-users .users-grid .user-card[data-pk="${pk}"]`);
    return cards.length ? cards[0] : null;
  }

  function removeUserCard(pk) {
    const card = findUserCard(pk);
    if (card) card.remove();
  }

  function addOrUpdateUserCardFromRow(row, forceActive = false) {
    if (!row) return;
    const pk = row.dataset.pk;
    const name = row.dataset.name || (row.querySelector('td:first-child')?.textContent || '').trim();
    const role = row.dataset.role || '';
    const contact = row.dataset.contact || '';
    const statusKey = forceActive ? 'active' : (row.dataset.statusKey || 'unknown');
    const statusLabel = statusKey === 'active' || statusKey === 'approved' ? 'Active' : (statusKey.charAt(0).toUpperCase() + statusKey.slice(1));

    // First, ensure no duplicate cards exist for this pk
    const existingCards = usersGrid.querySelectorAll(`.user-card[data-pk="${pk}"]`);
    existingCards.forEach(card => card.remove());

    // Now create a fresh card
    const card = document.createElement('div');
    card.className = 'user-card';
    card.dataset.pk = pk;
    card.innerHTML = `
      <div class="user-name">${name || 'Unknown'}</div>
      <div class="user-role" style="display:${role ? '' : 'none'}">${role || ''}</div>
      <div class="user-meta" style="display:${contact ? '' : 'none'}">${contact || ''}</div>
      <div class="user-status ${statusKey === 'approved' ? 'active' : statusKey}">${statusKey === 'approved' ? 'Active' : statusLabel}</div>
    `;
    // Choose container based on status
    if ((statusKey === 'active' || statusKey === 'approved') && usersActiveGrid) {
      usersActiveGrid.prepend(card);
    } else if (statusKey === 'inactive' && usersInactiveGrid) {
      usersInactiveGrid.prepend(card);
    } else if (usersActiveGrid) {
      usersActiveGrid.prepend(card);
    }
  }

  async function postAction(row, action) {
    const pk = row?.dataset.pk;
    if (!pk) return;

    try {
      const resp = await fetch(`/admin/front/submission/${pk}/action/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrftoken,
        },
        body: `action=${encodeURIComponent(action)}`,
      });

      let data = { ok: false, error: 'Unexpected response' };
      const isJson = resp.headers.get('content-type')?.includes('application/json');
      if (isJson) {
        data = await resp.json();
      } else if (!resp.ok) {
        throw new Error(`Server responded with ${resp.status}`);
      }

      if (data.ok) {
        setRowStatus(row, data.status);
        updateStats();
        const successLabel = action === 'approve' ? 'approved' : 'rejected';
        showToast(`Submission ${successLabel} successfully`, 'success');

        // Live update Users tab
        try {
          const pk = row?.dataset.pk;
          if (action === 'approve') {
            addOrUpdateUserCardFromRow(row, true);
            setTimeout(() => showToast('Users tab updated', 'info'), 1000);
          } else if (action === 'reject') {
            removeUserCard(pk);
            setTimeout(() => showToast('User removed from Users tab', 'info'), 1000);
          }
        } catch (e) {
          console.warn('Users tab live update failed:', e);
        }
      } else {
        showToast(`Action failed: ${data.error || 'unknown'}`, 'error');
      }
    } catch (error) {
      console.error(error);
      showToast('Request failed', 'error');
    }
  }

  // Row selection functionality
  let selectedRow = null;
  const allTables = document.querySelectorAll('.submissions-table');
  
  allTables.forEach(table => {
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    tbody.addEventListener('click', (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      
      // Check if clicked on a button - if so, don't select row
      if (target.closest('button')) return;
      
      const row = target.closest('tr');
      if (!row || !row.dataset.pk) return;
      
      // Toggle selection
      if (selectedRow === row) {
        row.classList.remove('selected');
        selectedRow = null;
        updateActionButtons(null);
      } else {
        // Remove previous selection
        if (selectedRow) {
          selectedRow.classList.remove('selected');
        }
        row.classList.add('selected');
        selectedRow = row;
        updateActionButtons(row);
      }
    });
  });
  
  function updateActionButtons(row) {
    const sections = document.querySelectorAll('.action-buttons-section');
    sections.forEach(section => {
      const editBtn = section.querySelector('.edit-btn');
      const approveBtn = section.querySelector('.approve-btn');
      const rejectBtn = section.querySelector('.reject-btn');
      const deactivateBtn = section.querySelector('.deactivate-btn');
      const activateBtn = section.querySelector('.activate-btn');
      const deleteBtn = section.querySelector('.delete-btn');
      
      if (!row) {
        if (editBtn) editBtn.disabled = true;
        if (approveBtn) approveBtn.disabled = true;
        if (rejectBtn) rejectBtn.disabled = true;
        if (deactivateBtn) deactivateBtn.disabled = true;
        if (activateBtn) activateBtn.disabled = true;
        if (deleteBtn) deleteBtn.disabled = true;
        return;
      }
      
      const statusKey = row.dataset.statusKey;
      if (editBtn) editBtn.disabled = false;
      if (approveBtn) approveBtn.disabled = (statusKey === 'approved' || statusKey === 'active');
      if (rejectBtn) rejectBtn.disabled = (statusKey === 'rejected');
      if (deactivateBtn) deactivateBtn.disabled = (statusKey === 'inactive' || statusKey === 'pending' || statusKey === 'rejected');
      if (activateBtn) activateBtn.disabled = (statusKey !== 'inactive');
      if (deleteBtn) deleteBtn.disabled = false;
    });
  }
  
  // Handle action button clicks
  document.addEventListener('click', (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const button = target.closest('.action-btn');
    if (button) {
      if (button.disabled) return;
      if (!selectedRow) return;

    if (button.classList.contains('approve-btn')) {
      if (!confirm('Approve this submission?')) return;
      postAction(selectedRow, 'approve').then(() => {
        selectedRow.classList.remove('selected');
        selectedRow = null;
        updateActionButtons(null);
      });
    } else if (button.classList.contains('reject-btn')) {
      if (!confirm('Reject this submission?')) return;
      postAction(selectedRow, 'reject').then(() => {
        selectedRow.classList.remove('selected');
        selectedRow = null;
        updateActionButtons(null);
      });
    } else if (button.classList.contains('delete-btn')) {
      if (!confirm('Delete this submission permanently?')) return;
      const pk = selectedRow?.dataset.pk;
      if (!pk) return;
      fetch(`/admin/front/submission/${pk}/delete/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrftoken,
        },
      })
        .then(resp => resp.json())
        .then(data => {
          if (data?.ok) {
            selectedRow.remove();
            selectedRow = null;
            updateStats();
            updateActionButtons(null);
            showToast('Submission deleted', 'success');
            try {
              removeUserCard(pk);
              setTimeout(() => showToast('User removed from Users tab', 'info'), 1000);
            } catch (e) { /* ignore */ }
          } else {
            showToast(`Delete failed: ${data?.error || 'unknown'}`, 'error');
          }
        })
        .catch(err => {
          console.error(err);
          showToast('Request failed', 'error');
        });
    } else if (button.classList.contains('edit-btn')) {
      const pk = selectedRow?.dataset.pk;
      if (pk) {
        // Use custom edit page instead of Django admin
        window.location.href = `/admin/front/submission/${pk}/edit/`;
      }
    } else if (button.classList.contains('deactivate-btn')) {
      if (!confirm('Mark this user as inactive?')) return;
      postAction(selectedRow, 'deactivate').then(() => {
        setRowStatus(selectedRow, 'inactive');
        // Sync Users tab: move card from active to inactive
        const pk = selectedRow?.dataset.pk;
        if (pk) {
          const card = document.querySelector(`.active-users .user-card[data-pk="${pk}"]`);
          const container = document.querySelector('.inactive-users');
          if (card && container) {
            card.querySelector('.user-status')?.classList.remove('active','approved');
            card.querySelector('.user-status')?.classList.add('inactive');
            card.querySelector('.user-status').textContent = 'Inactive';
            // swap action button
            const actions = card.querySelector('.user-actions');
            if (actions) actions.innerHTML = '<button class="user-btn user-activate" data-action="activate">Activate</button>';
            container.prepend(card);
          }
        }
        selectedRow.classList.remove('selected');
        selectedRow = null;
        updateActionButtons(null);
        updateStats();
      });
    } else if (button.classList.contains('activate-btn')) {
      if (!confirm('Mark this user as active?')) return;
      postAction(selectedRow, 'activate').then(() => {
        setRowStatus(selectedRow, 'active');
        // Sync Users tab: move card from inactive to active
        const pk = selectedRow?.dataset.pk;
        if (pk) {
          const card = document.querySelector(`.inactive-users .user-card[data-pk="${pk}"]`);
          const container = document.querySelector('.active-users');
          if (card && container) {
            card.querySelector('.user-status')?.classList.remove('inactive');
            card.querySelector('.user-status')?.classList.add('active');
            card.querySelector('.user-status').textContent = 'Active';
            const actions = card.querySelector('.user-actions');
            if (actions) actions.innerHTML = '<button class="user-btn user-deactivate" data-action="deactivate">Deactivate</button>';
            container.prepend(card);
          }
        }
        selectedRow.classList.remove('selected');
        selectedRow = null;
        updateActionButtons(null);
        updateStats();
      });
    }
    return; // handled action buttons
    }

    // Handle Users tab card buttons
    const userBtn = target.closest('.user-btn');
    if (!userBtn) return;
    const action = userBtn.dataset.action;
    if (action !== 'deactivate' && action !== 'activate') return;
    const card = userBtn.closest('.user-card');
    const pk = card?.dataset.pk;
    if (!pk) return;
    if (action === 'deactivate' && !confirm('Mark this user as inactive?')) return;
    if (action === 'activate' && !confirm('Mark this user as active?')) return;

    fetch(`/admin/front/submission/${pk}/action/`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrftoken,
      },
      body: `action=${encodeURIComponent(action)}`,
    })
      .then(resp => resp.json())
      .then(data => {
        if (!data?.ok) {
          showToast('Update failed', 'error');
          return;
        }
        // Update Users card UI
        if (action === 'deactivate') {
          const statusEl = card.querySelector('.user-status');
          if (statusEl) {
            statusEl.classList.remove('active','approved');
            statusEl.classList.add('inactive');
            statusEl.textContent = 'Inactive';
          }
          const actions = card.querySelector('.user-actions');
          if (actions) actions.innerHTML = '<button class="user-btn user-activate" data-action="activate">Activate</button>';
          if (usersInactiveGrid) usersInactiveGrid.prepend(card);
          // Update corresponding row in Submissions tables
          const row = document.querySelector(`.submissions-table tr[data-pk="${pk}"]`);
          if (row) setRowStatus(row, 'inactive');
          updateStats();
          showToast('User marked inactive', 'success');
        } else {
          const statusEl = card.querySelector('.user-status');
          if (statusEl) {
            statusEl.classList.remove('inactive');
            statusEl.classList.add('active');
            statusEl.textContent = 'Active';
          }
          const actions = card.querySelector('.user-actions');
          if (actions) actions.innerHTML = '<button class="user-btn user-deactivate" data-action="deactivate">Deactivate</button>';
          if (usersActiveGrid) usersActiveGrid.prepend(card);
          // Update corresponding row in Submissions tables
          const row = document.querySelector(`.submissions-table tr[data-pk="${pk}"]`);
          if (row) setRowStatus(row, 'active');
          updateStats();
          showToast('User marked active', 'success');
        }
      })
      .catch(err => {
        console.error(err);
        showToast('Request failed', 'error');
      });
  });

  updateStats();
});