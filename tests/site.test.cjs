const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const docs = path.resolve(__dirname, '../docs');
const payload = JSON.parse(fs.readFileSync(path.join(docs, 'data.json'), 'utf8'));

async function dashboard(ok = true) {
  const elements = new Map();
  const document = {
    querySelector(selector) {
      if (!elements.has(selector)) elements.set(selector, {
        style: {}, children: [], handlers: {}, value: 'All',
        appendChild(child) { this.children.push(child); },
        addEventListener(name, fn) { this.handlers[name] = fn; },
        setAttribute(name, value) { this[name] = value; },
      });
      return elements.get(selector);
    },
    createElement() { return {}; },
  };
  const context = vm.createContext({ document, console: { error() {} },
    fetch: async url => {
      assert.equal(url, 'data.json');
      return { ok, status: ok ? 200 : 404, json: async () => payload };
    },
  });
  await vm.runInContext(fs.readFileSync(path.join(docs, 'app.js'), 'utf8'), context);
  return { context, elements };
}

test('dashboard loads pipeline output and reconciles canonical totals', async () => {
  const { context, elements } = await dashboard();
  const totals = vm.runInContext('total(monthly())', context);
  assert.equal(totals.attempts, 1_000_000);
  assert.equal(totals.successes, payload.overall.successes);
  assert.ok(Math.abs(totals.successful_amount_usd - payload.overall.successful_volume_usd) < 0.01);
  assert.ok(Math.abs(totals.platform_revenue_usd - payload.overall.platform_revenue_usd) < 0.01);
  assert.equal(elements.get('#dataStatus').hidden, true);
  assert.match(elements.get('#successChart').innerHTML, /<svg/);
  assert.doesNotMatch(elements.get('#volumeChart').innerHTML, /NaN|Infinity/);
  assert.match(elements.get('#diagBps').textContent, /-782 bps/);
});

test('all filter combinations render finite metrics and reset restores totals', async () => {
  const { context, elements } = await dashboard();
  vm.runInContext(`
    for (const country of ['All', ...dims.country])
    for (const merchant_segment of ['All', ...dims.merchant_segment])
    for (const device of ['All', ...dims.device])
    for (const payment_method of ['All', ...dims.payment_method]) {
      state.filters = {country, merchant_segment, device, payment_method};
      render();
      if (Object.values(total(monthly())).some(value => !Number.isFinite(value)))
        throw new Error('Non-finite filtered metric');
    }
  `, context);
  const country = elements.get('#countryFilter');
  country.value = 'CA'; country.handlers.change();
  assert.equal(vm.runInContext('state.filters.country', context), 'CA');
  elements.get('#resetFilters').handlers.click();
  assert.equal(vm.runInContext('total(monthly()).attempts', context), 1_000_000);
});

test('missing data produces a visible error', async () => {
  const { elements } = await dashboard(false);
  assert.equal(elements.get('#dataStatus').role, 'alert');
  assert.match(elements.get('#dataStatus').textContent, /could not be loaded/);
});

test('HTML assets, local links and fragment targets exist', () => {
  for (const name of ['index.html', 'decision-memo.html']) {
    const html = fs.readFileSync(path.join(docs, name), 'utf8');
    for (const [, url] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
      if (/^https?:/.test(url)) continue;
      if (url.startsWith('#')) assert.ok(html.includes(`id="${url.slice(1)}"`), url);
      else assert.ok(fs.existsSync(path.join(docs, url)), url);
    }
  }
});
