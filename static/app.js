function positionNeedle() {
  const active = document.querySelector('.dial-stop.active');
  const needle = document.querySelector('.dial-needle');
  const scale = document.querySelector('.dial-scale');
  if (!active || !needle || !scale) return;
  const scaleRect = scale.getBoundingClientRect();
  const activeRect = active.getBoundingClientRect();
  const center = activeRect.left + activeRect.width / 2 - scaleRect.left;
  needle.style.left = `${center}px`;
}
window.addEventListener('load', positionNeedle);
window.addEventListener('resize', positionNeedle);

function toast(msg, isError = false) {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = 'toast show' + (isError ? ' error' : '');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('show'), 3200);
}

function setVU(active) {
  const vu = document.getElementById('vu');
  if (!vu) return;
  vu.classList.toggle('active', active);
}

function initFileDrop(dropId, inputId, labelId) {
  const drop = document.getElementById(dropId);
  const input = document.getElementById(inputId);
  const label = document.getElementById(labelId);
  if (!drop || !input) return;
  drop.addEventListener('click', () => input.click());
  drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('drag'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('drag'));
  drop.addEventListener('drop', (e) => {
    e.preventDefault();
    drop.classList.remove('drag');
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      if (label) label.textContent = e.dataTransfer.files[0].name;
    }
  });
  input.addEventListener('change', () => {
    if (input.files.length && label) label.textContent = input.files[0].name;
  });
}

async function postForm(url, formData) {
  setVU(true);
  try {
    const res = await fetch(url, { method: 'POST', body: formData });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
    return data;
  } finally {
    setVU(false);
  }
}

function formatDuration(seconds) {
  if (!seconds && seconds !== 0) return '--:--';
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function formatBytes(bytes) {
  if (!bytes) return '0 KB';
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(0)} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}
