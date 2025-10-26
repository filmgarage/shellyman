const state = {
  devices: [],
  filtered: [],
  sortKey: 'name',
  sortDir: 'asc',
  selected: new Set(),
};

const tbody = document.getElementById('devices-tbody');
const filterInput = document.getElementById('filter');
const checkAll = document.getElementById('check-all');
const btnRefresh = document.getElementById('btn-refresh');
const btnEnable = document.getElementById('btn-enable-auth');
const btnDisable = document.getElementById('btn-disable-auth');

function compare(a, b, key) {
  const av = a[key];
  const bv = b[key];
  if (av == null && bv == null) return 0;
  if (av == null) return 1;
  if (bv == null) return -1;
  if (typeof av === 'string') return av.localeCompare(bv);
  if (typeof av === 'boolean') return (av === bv) ? 0 : (av ? -1 : 1);
  return av - bv;
}

function applySort() {
  const { sortKey, sortDir } = state;
  state.filtered.sort((a, b) => {
    const c = compare(a, b, sortKey);
    return sortDir === 'asc' ? c : -c;
  });
}

function applyFilter() {
  const q = (filterInput.value || '').toLowerCase();
  if (!q) { state.filtered = [...state.devices]; return; }
  state.filtered = state.devices.filter(d =>
    (d.name && d.name.toLowerCase().includes(q)) ||
    (d.ip && d.ip.includes(q)) ||
    (d.model && d.model.toLowerCase().includes(q))
  );
}

function badge(text, cls) {
  const s = document.createElement('span');
  s.className = `badge ${cls}`;
  s.textContent = text;
  return s;
}

function render() {
  tbody.innerHTML = '';
  for (const d of state.filtered) {
    const tr = document.createElement('tr');

    // checkbox
    const tdCb = document.createElement('td');
    tdCb.className = 'checkbox-col';
    const cb = document.createElement('md-checkbox');
    cb.checked = state.selected.has(d.id);
    cb.addEventListener('change', () => {
      if (cb.checked) state.selected.add(d.id); else state.selected.delete(d.id);
      updateActionButtons();
      syncHeaderCheckbox();
    });
    tdCb.appendChild(cb);
    tr.appendChild(tdCb);

    // name
    const tdName = document.createElement('td');
    tdName.textContent = d.name || d.id;
    tr.appendChild(tdName);

    // model
    const tdModel = document.createElement('td');
    tdModel.textContent = d.model || '';
    tr.appendChild(tdModel);

    // gen
    const tdGen = document.createElement('td');
    tdGen.textContent = d.gen ?? '';
    tr.appendChild(tdGen);

    // protocol
    const tdProto = document.createElement('td');
    tdProto.textContent = d.protocol || 'Unknown';
    tr.appendChild(tdProto);

    // firmware
    const tdFw = document.createElement('td');
    if (d.firmware_uptodate === true) tdFw.appendChild(badge('Up-to-date','ok'));
    else if (d.firmware_uptodate === false) tdFw.appendChild(badge('Update available','warn'));
    else tdFw.appendChild(badge('Unknown','off'));
    tr.appendChild(tdFw);

    // ip link
    const tdIp = document.createElement('td');
    if (d.ip) {
      const a = document.createElement('a');
      a.href = `http://${d.ip}/`;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.className = 'device-link';
      a.textContent = d.ip;
      tdIp.appendChild(a);
    }
    tr.appendChild(tdIp);

    // auth
    const tdAuth = document.createElement('td');
    if (d.auth_enabled === true) tdAuth.appendChild(badge('On','ok'));
    else if (d.auth_enabled === false) tdAuth.appendChild(badge('Off','off'));
    else tdAuth.appendChild(badge('Unknown','off'));
    tr.appendChild(tdAuth);

    tbody.appendChild(tr);
  }
}

function updateActionButtons() {
  const hasSel = state.selected.size > 0;
  btnEnable.disabled = !hasSel;
  btnDisable.disabled = !hasSel;
}

function syncHeaderCheckbox() {
  const allIds = state.filtered.map(d => d.id);
  const allSelected = allIds.length > 0 && allIds.every(id => state.selected.has(id));
  checkAll.checked = allSelected;
  checkAll.indeterminate = !allSelected && allIds.some(id => state.selected.has(id));
}

async function fetchDevices() {
  const q = filterInput.value ? `?q=${encodeURIComponent(filterInput.value)}` : '';
  const r = await fetch(`/api/devices${q}`);
  const data = await r.json();
  state.devices = data.devices || [];
  state.selected.clear();
  applyFilter();
  applySort();
  render();
  updateActionButtons();
  syncHeaderCheckbox();
}

// Sorting via header click
for (const th of document.querySelectorAll('thead th[data-sort]')) {
  th.style.cursor = 'pointer';
  th.addEventListener('click', () => {
    const key = th.dataset.sort;
    if (state.sortKey === key) {
      state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      state.sortKey = key;
      state.sortDir = 'asc';
    }
    applySort();
    render();
  });
}

// Select all
checkAll.addEventListener('change', () => {
  const ids = state.filtered.map(d => d.id);
  if (checkAll.checked) ids.forEach(id => state.selected.add(id));
  else ids.forEach(id => state.selected.delete(id));
  render();
  updateActionButtons();
});

// Filter typing (debounced)
let t;
filterInput.addEventListener('input', () => {
  clearTimeout(t);
  t = setTimeout(() => {
    state.selected.clear();
    applyFilter();
    applySort();
    render();
    updateActionButtons();
    syncHeaderCheckbox();
  }, 200);
});

btnRefresh.addEventListener('click', fetchDevices);

// Batch auth actions (wired after fetching devices)
async function applyAuth(action) {
  const map = new Map(state.devices.map(d => [d.id, d]));
  const ids = Array.from(state.selected);
  for (const id of ids) {
    const d = map.get(id);
    if (!d) continue;
    try {
      if (d.gen === 1) {
        if (action === 'enable') {
          await fetch('/api/security/gen1/enable', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ip: d.ip})});
        } else {
          await fetch('/api/security/gen1/disable', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ip: d.ip})});
        }
      } else if (d.gen === 2) {
        if (action === 'enable') {
          await fetch('/api/security/gen2/enable', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ip: d.ip})});
        } else {
          await fetch('/api/security/gen2/disable', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ip: d.ip})});
        }
      }
    } catch (e) {
      console.error('auth action failed for', d, e);
    }
  }
  await fetchDevices();
}

btnEnable.addEventListener('click', () => applyAuth('enable'));
btnDisable.addEventListener('click', () => applyAuth('disable'));

fetchDevices();
