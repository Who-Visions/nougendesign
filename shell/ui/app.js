// NouGenDesign shell frontend.
//
// Data comes from the Tauri backend (`load_package` command, which reads the
// compiled package through nougendesign-shell-core). Outside Tauri (plain
// static serving), it falls back to the bundled `shell-data.json` snapshot,
// generated from the same package by the core's `shell-data` tool:
//
//   cargo run -p nougendesign-shell-core --bin shell-data -- \
//     ../designs/nougenai-brand > ui/shell-data.json
//
// (package path relative to shell/). The static markup in index.html mirrors
// that snapshot so the page is meaningful before/without JS.

async function fetchSnapshot() {
  if (window.__TAURI__ && window.__TAURI__.core) {
    return { data: await window.__TAURI__.core.invoke('load_package'), mode: 'tauri · live package read' };
  }
  const res = await fetch('shell-data.json');
  if (!res.ok) throw new Error('shell-data.json not available');
  return { data: await res.json(), mode: 'standalone · bundled snapshot' };
}

function render(snapshot) {
  const pkg = snapshot.package;
  document.getElementById('pkg-name').textContent = pkg.name;
  document.getElementById('pkg-dialect').textContent = pkg.dialect;
  document.getElementById('pkg-desc').textContent = pkg.description;
  document.getElementById('pkg-themes').textContent = pkg.themes.join(', ');
  document.getElementById('pkg-tokens').textContent = String(pkg.token_count);
  document.getElementById('pkg-source').textContent = pkg.source_dir;

  const tweakList = document.getElementById('tweak-list');
  if (snapshot.tweaks) {
    tweakList.innerHTML = '';
    for (const dim of snapshot.tweaks.dimensions) {
      const li = document.createElement('li');
      const unit = dim.kind === 'token-step' ? 'steps' : 'options';
      li.innerHTML = '<strong></strong> <span class="dim-meta"></span>';
      li.querySelector('strong').textContent = dim.label;
      li.querySelector('.dim-meta').textContent =
        `${dim.kind} · default ${dim.default} · ${dim.option_count} ${unit}`;
      tweakList.appendChild(li);
    }
  }

  const variantList = document.getElementById('variant-list');
  variantList.innerHTML = '';
  for (const plan of snapshot.variants) {
    const li = document.createElement('li');
    li.innerHTML = '<strong></strong> <span class="dim-meta"></span>';
    li.querySelector('strong').textContent = plan.id;
    li.querySelector('.dim-meta').textContent =
      `${plan.status} · ${plan.mutation_count} mutations`;
    li.title = plan.lock_effect;
    variantList.appendChild(li);
  }

  document.getElementById('verify-gate').textContent = snapshot.verify.gate_of_record;
  document.getElementById('verify-note').textContent = snapshot.verify.note;
  document.getElementById('verify-cmd').textContent = snapshot.verify.command;
}

async function load() {
  try {
    const { data, mode } = await fetchSnapshot();
    render(data);
    document.getElementById('shell-mode').textContent = mode;
  } catch (err) {
    document.getElementById('shell-mode').textContent = 'snapshot markup only (' + err.message + ')';
  }
}

document.getElementById('btn-load').addEventListener('click', load);
window.addEventListener('DOMContentLoaded', load);
