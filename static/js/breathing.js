const techniques = {
  box:  { inhale: 4, hold1: 4, exhale: 4, hold2: 4, name: 'Box Breathing' },
  '478': { inhale: 4, hold1: 7, exhale: 8, hold2: 0, name: '4-7-8 Breathing' },
  calm: { inhale: 5, hold1: 0, exhale: 5, hold2: 0, name: 'Calm Breathing' }
};

let current = 'box';
let running = false;
let timer = null;
let cycles = 0;
let totalSeconds = 0;
let sessionTimer = null;

function setTechnique(key) {
  if (running) stopBreathing();
  current = key;
  document.querySelectorAll('[id^=btn-]').forEach(b => b.classList.remove('active-technique'));
  document.getElementById('btn-' + key).classList.add('active-technique');
  document.getElementById('breathText').textContent = 'Ready';
  document.getElementById('breathCount').textContent = '';
}

function startBreathing() {
  running = true;
  cycles = 0;
  totalSeconds = 0;
  document.getElementById('startBtn').classList.add('d-none');
  document.getElementById('stopBtn').classList.remove('d-none');
  sessionTimer = setInterval(() => {
    totalSeconds++;
    document.getElementById('sessionTime').textContent = totalSeconds + 's';
  }, 1000);
  runCycle();
}

function stopBreathing() {
  running = false;
  clearTimeout(timer);
  clearInterval(sessionTimer);
  document.getElementById('startBtn').classList.remove('d-none');
  document.getElementById('stopBtn').classList.add('d-none');
  document.getElementById('breathText').textContent = 'Ready';
  document.getElementById('breathCount').textContent = '';
  document.getElementById('phaseDisplay').textContent = '—';
  setCircleScale(1);
}

async function runCycle() {
  if (!running) return;
  const t = techniques[current];

  await phase('Inhale', t.inhale, 1.3);
  if (!running) return;

  if (t.hold1 > 0) {
    await phase('Hold', t.hold1, 1.3);
    if (!running) return;
  }

  await phase('Exhale', t.exhale, 1.0);
  if (!running) return;

  if (t.hold2 > 0) {
    await phase('Hold', t.hold2, 1.0);
    if (!running) return;
  }

  cycles++;
  document.getElementById('cycleCount').textContent = cycles;
  runCycle();
}

function phase(label, seconds, scale) {
  return new Promise(resolve => {
    if (!running) { resolve(); return; }
    document.getElementById('breathText').textContent = label;
    document.getElementById('phaseDisplay').textContent = label;
    setCircleScale(scale);
    let remaining = seconds;
    document.getElementById('breathCount').textContent = remaining;

    const tick = () => {
      if (!running) { resolve(); return; }
      remaining--;
      if (remaining <= 0) {
        document.getElementById('breathCount').textContent = '';
        resolve();
      } else {
        document.getElementById('breathCount').textContent = remaining;
        timer = setTimeout(tick, 1000);
      }
    };
    timer = setTimeout(tick, 1000);
  });
}

function setCircleScale(scale) {
  document.getElementById('breathingCircle').style.transform = `scale(${scale})`;
}
