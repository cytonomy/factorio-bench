/* Original synthetic evidence explorer. No analytics, credentials, or remote calls. */
'use strict';
const $ = (selector) => document.querySelector(selector);
const number = (value) => new Intl.NumberFormat('en-US').format(value);
let data;
let selectedCase = 0;
let selectedWindow = 0;
let timer;
const titles = {
  'steady-line': ['Steady line', 'Balanced production', 'A factory that keeps its promise.'],
  'fuel-starved': ['Fuel starved', 'An early peak fades', 'A strong start is not sustained output.'],
  'hand-fed': ['Hand fed', 'A misleading total', 'Delivery needs the right provenance.'],
};

function stopPlayback() {
  clearInterval(timer);
  timer = undefined;
  $('#play').replaceChildren();
  const icon = document.createElement('span');
  icon.setAttribute('aria-hidden', 'true');
  icon.textContent = '▶';
  $('#play').append(icon, ' Play');
  $('#play').setAttribute('aria-label', 'Play verification windows');
  $('#factory').classList.remove('playing');
}

function chooseCase(index) {
  stopPlayback();
  selectedCase = index;
  selectedWindow = 0;
  render();
  $('#announcement').textContent = `${data.cases[index].title}. Overall verdict: ${data.cases[index].verdict}.`;
}

function buildControls() {
  for (const [index, example] of data.cases.entries()) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `scenario-button ${example.verdict === 'fail' ? 'failed' : ''}`;
    button.setAttribute('aria-pressed', String(index === 0));
    const num = document.createElement('span');
    num.className = 'scenario-number';
    num.textContent = `0${index + 1}`;
    const details = document.createElement('span');
    for (const [className, text] of [
      ['scenario-title', titles[example.id][0]],
      ['scenario-subtitle', titles[example.id][1]],
      ['scenario-status', `${example.verdict === 'pass' ? '↗' : '↘'} ${example.verdict.toUpperCase()}`],
    ]) {
      const span = document.createElement('span');
      span.className = className;
      span.textContent = text;
      details.append(span);
    }
    button.append(num, details);
    button.addEventListener('click', () => chooseCase(index));
    $('#scenarios').append(button);
  }
  $('#window').disabled = false;
  $('#play').disabled = false;
}

function renderChart(example) {
  const chart = $('#chart');
  const focusedWindow = document.activeElement?.dataset?.window;
  chart.replaceChildren();
  for (const [index, window] of example.windows.entries()) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `window-chart${index === selectedWindow ? ' selected' : ''}`;
    button.dataset.window = String(index);
    button.setAttribute('aria-label', `Window ${index + 1}: ${window.mined} mined, ${window.smelted} smelted, ${window.delivered} delivered. ${window.passed ? 'Pass' : 'Fail'}. Inspect window.`);
    button.setAttribute('aria-pressed', String(index === selectedWindow));
    const bars = document.createElement('span');
    bars.className = 'bars';
    bars.setAttribute('aria-hidden', 'true');
    for (const [kind, count] of [['mine', window.mined], ['smelt', window.smelted], ['deliver', window.delivered]]) {
      // SVG presentation attributes keep generated charts compatible with strict CSP.
      const bar = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      bar.setAttribute('viewBox', '0 0 18 76');
      bar.setAttribute('preserveAspectRatio', 'none');
      bar.setAttribute('width', '18');
      bar.setAttribute('height', '76');
      bar.classList.add('bar-column');
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      const height = Math.max(1, count / 50 * 76);
      rect.setAttribute('x', '0');
      rect.setAttribute('y', String(76 - height));
      rect.setAttribute('width', '18');
      rect.setAttribute('height', String(height));
      rect.setAttribute('rx', '2');
      rect.setAttribute('fill', {mine: '#9bac8c', smelt: '#ca9b68', deliver: '#3d654c'}[kind]);
      bar.append(rect);
      bars.append(bar);
    }
    const caption = document.createElement('span');
    caption.className = 'window-caption';
    caption.textContent = `W0${index + 1}`;
    const counts = document.createElement('span');
    counts.className = `window-counts${window.passed ? '' : ' bad'}`;
    counts.textContent = `${window.mined}/${window.smelted}/${window.delivered}`;
    counts.setAttribute('aria-hidden', 'true');
    button.append(bars, caption, counts);
    button.addEventListener('click', () => {
      stopPlayback();
      selectedWindow = index;
      render();
      announceWindow();
    });
    chart.append(button);
  }
  if (focusedWindow !== undefined) chart.querySelector(`[data-window="${focusedWindow}"]`)?.focus();
}

function announceWindow() {
  const window = data.cases[selectedCase].windows[selectedWindow];
  $('#announcement').textContent = `Window ${selectedWindow + 1} of 5. ${window.passed ? 'Pass' : 'Fail'}. ${window.delivered} qualifying deliveries.`;
}

function render() {
  const example = data.cases[selectedCase];
  const window = example.windows[selectedWindow];
  document.querySelectorAll('.scenario-button').forEach((button, index) => button.setAttribute('aria-pressed', String(index === selectedCase)));
  $('#run-title').textContent = titles[example.id][0];
  $('#verdict').textContent = `${example.verdict === 'pass' ? '✓' : '×'} ${example.verdict.toUpperCase()}`;
  $('#verdict').className = `verdict ${example.verdict}`;
  $('#verdict').setAttribute('aria-label', `Overall run verdict: ${example.verdict}`);
  $('#map-mined').textContent = `${window.mined} ore`;
  $('#map-smelted').textContent = `${window.smelted} plates`;
  $('#map-delivered').textContent = `${window.delivered} verified`;
  $('#window').value = selectedWindow;
  $('#window').setAttribute('aria-valuetext', `Window ${selectedWindow + 1} of 5`);
  $('#window-number').textContent = `0${selectedWindow + 1} / 05`;
  $('#tick-range').textContent = `${number(window.start_tick)}–${number(window.end_tick)}`;
  $('#factory').classList.toggle('starved', window.smelted < data.task.minimum_per_window);
  $('#fault-note').hidden = window.passed;
  $('#fault-note').textContent = window.manual_delivered ? `${window.manual_delivered} manual deposits excluded · hands-off rule violated` : 'Smelting and delivery fall below the target';
  $('#verifier-title').textContent = titles[example.id][2];
  $('#diagnosis').textContent = example.diagnosis;
  $('.verifier-panel').classList.toggle('failed', example.verdict === 'fail');
  $('#window-result').textContent = `${example.windows.filter((item) => item.passed).length} / 5 WINDOWS PASS`;
  renderChart(example);
  const events = example.events.filter((event) => event.tick >= window.start_tick && event.tick < window.end_tick);
  $('#event-count').textContent = `${events.length} events`;
  $('#events').replaceChildren();
  for (const event of events) {
    const row = document.createElement('tr');
    for (const value of [number(event.tick), event.kind, event.source, event.quantity]) {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.append(cell);
    }
    $('#events').append(row);
  }
}

$('#window').addEventListener('input', (event) => {
  stopPlayback();
  selectedWindow = Number(event.target.value);
  render();
  announceWindow();
});
$('#play').addEventListener('click', () => {
  if (timer) return stopPlayback();
  if (selectedWindow === 4) selectedWindow = 0;
  render();
  $('#factory').classList.add('playing');
  $('#play').textContent = 'Ⅱ Pause';
  $('#play').setAttribute('aria-label', 'Pause verification windows');
  timer = setInterval(() => {
    selectedWindow += 1;
    render();
    if (selectedWindow === 4) {
      stopPlayback();
      announceWindow();
    }
  }, 1600);
});
fetch('data/examples.json').then((response) => {
  if (!response.ok) throw new Error('Fixture unavailable');
  return response.json();
}).then((fixture) => {
  if (fixture.schema_version !== 'factorio-bench.demo.v1') throw new Error('Unsupported demo schema');
  data = fixture;
  buildControls();
  render();
}).catch(() => {
  $('#run-title').textContent = 'Example data could not load';
  $('#verdict').textContent = 'UNAVAILABLE';
  $('#verifier-title').textContent = 'Run make demo from the repository.';
  $('#diagnosis').textContent = 'The explorer needs its generated synthetic fixture and the local server. See the repository quickstart.';
  $('#announcement').textContent = 'Example data could not load. Run make demo from the repository.';
});
