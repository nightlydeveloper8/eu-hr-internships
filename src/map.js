import { MAP_VIEWBOX, EU_SHAPES, CONTEXT_SHAPES } from './eu-map.js';
import { countBucket, zoomViewBox } from './logic.js';

const SVG = 'http://www.w3.org/2000/svg';
function node(tag, attrs = {}, parent) {
  const n = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (parent) parent.append(n);
  return n;
}
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;
const reducedMotion = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
const BENELUX = ['NL', 'BE', 'LU'];

// "3 in English · 31 in Italian" for the current ads of one country.
export function describeLanguages(breakdown = [], languageNames = {}) {
  return breakdown.map(({code, count}) => `${count} in ${code === 'unknown' ? 'an unidentified language' : languageNames[code] || code}`).join(' · ');
}

// One-line summary used for accessible names and chips. Absence of listings is never presented as absence of internships.
export function describeCountry(name, c = {verified:0, unverified:0, applicationConfirmed:0}) {
  if (c.verified) return `${plural(c.verified, 'current HR opening', 'current HR openings')} · ${c.applicationConfirmed ?? 0} with a verified direct application${c.unverified ? ` · ${c.unverified} more to check` : ''}`;
  if (c.unverified) return `No current openings confirmed · ${plural(c.unverified, 'lead', 'leads')} to check`;
  return 'No openings observed yet';
}

// Structured rows for the tooltip and the side panel.
export function countryFacts(c = {verified:0, unverified:0, applicationConfirmed:0}) {
  const rows = [];
  if (c.verified) rows.push({kind:'current', value:c.verified, label:c.verified === 1 ? 'current opening' : 'current openings'});
  if (c.applicationConfirmed) rows.push({kind:'direct', value:c.applicationConfirmed, label:c.applicationConfirmed === 1 ? 'direct application verified' : 'direct applications verified'});
  if (c.unverified) rows.push({kind:'lead', value:c.unverified, label:c.unverified === 1 ? 'lead to check' : 'leads to check'});
  return rows;
}

// Draws the EU-27 + CH + GB map into `svg`. Returns {select(code), zoom(step), reset()} for the app to keep in sync.
export function drawMap({svg, tooltip, wrap, benelux, counts, names, onSelect, languages = () => ''}) {
  svg.setAttribute('viewBox', MAP_VIEWBOX);
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  svg.replaceChildren();
  const defs = node('defs', {}, svg);
  const hatch = node('pattern', {id:'map-hatch', width:'6', height:'6', patternUnits:'userSpaceOnUse', patternTransform:'rotate(45)'}, defs);
  node('rect', {width:'6', height:'6', class:'hatch-bg'}, hatch);
  node('line', {x1:'0', y1:'0', x2:'0', y2:'6', class:'hatch-line'}, hatch);
  const shade = node('linearGradient', {id:'map-sheen', x1:'0', y1:'0', x2:'0', y2:'1'}, defs);
  node('stop', {offset:'0', 'stop-color':'#d5e9fa', 'stop-opacity':'0.22'}, shade);
  node('stop', {offset:'1', 'stop-color':'#4ca9ed', 'stop-opacity':'0.06'}, shade);

  const viewport = node('g', {class:'map-viewport'}, svg);
  const context = node('g', {class:'map-context', 'aria-hidden':'true'}, viewport);
  for (const d of CONTEXT_SHAPES) node('path', {d}, context);

  const layer = node('g', {class:'map-countries'}, viewport);
  // Single overlays above every country: the only elements that carry glow filters, so hovering stays cheap.
  const selectedOutline = node('path', {class:'map-outline selected-outline', d:''}, viewport);
  const hoverOutline = node('path', {class:'map-outline hover-outline', d:''}, viewport);
  const badges = node('g', {class:'map-badges', 'aria-hidden':'true'}, viewport);
  const outline = code => EU_SHAPES[code].d + (EU_SHAPES[code].small ? `M${EU_SHAPES[code].cx - 7},${EU_SHAPES[code].cy}a7,7 0 1,0 14,0a7,7 0 1,0 -14,0` : '');
  const groups = new Map();
  const order = Object.keys(EU_SHAPES).sort((a, b) => (names[a] || a).localeCompare(names[b] || b));
  let hovered = '', selected = '', hideTimer;
  const badgeData = [];
  const beneluxButtons = new Map();
  for (const code of BENELUX) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'country-chip';
    const count = document.createElement('b');
    count.textContent = String(counts[code]?.verified || 0);
    button.append(names[code] || code, count);
    if (counts[code]?.applicationConfirmed) {
      const dot = document.createElement('i');
      dot.className = 'key-dot'; dot.setAttribute('aria-hidden', 'true');
      button.append(dot);
    }
    button.setAttribute('aria-label', `${names[code] || code}: ${describeCountry(names[code], counts[code])}`);
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => onSelect(code));
    benelux.append(button);
    beneluxButtons.set(code, button);
  }

  function showTip(code, x, y) {
    clearTimeout(hideTimer);
    const c = counts[code] || {verified:0, unverified:0, applicationConfirmed:0};
    tooltip.replaceChildren();
    const title = document.createElement('strong'); title.textContent = names[code] || code;
    tooltip.append(title);
    const facts = countryFacts(c);
    if (facts.length) {
      const list = document.createElement('ul');
      for (const fact of facts) {
        const li = document.createElement('li'); li.className = `tip-${fact.kind}`;
        const b = document.createElement('b'); b.textContent = String(fact.value);
        li.append(b, ` ${fact.label}`); list.append(li);
      }
      tooltip.append(list);
    } else {
      const none = document.createElement('span'); none.className = 'tip-none'; none.textContent = 'No openings observed yet';
      const caveat = document.createElement('small'); caveat.textContent = 'Our collection is still growing here — this does not mean there are no internships.';
      tooltip.append(none, caveat);
    }
    const spoken = languages(code);
    if (spoken) { const lang = document.createElement('span'); lang.className = 'tip-languages'; lang.textContent = spoken; tooltip.append(lang); }
    const hint = document.createElement('small'); hint.className = 'tip-hint'; hint.textContent = selected === code ? 'Selected' : 'Click to explore';
    tooltip.append(hint);
    tooltip.hidden = false;
    const box = wrap.getBoundingClientRect();
    const w = tooltip.offsetWidth, h = tooltip.offsetHeight;
    let left = x - box.left + 18, top = y - box.top - h - 14;
    if (left + w > box.width - 8) left = x - box.left - w - 18;
    if (top < 8) top = y - box.top + 22;
    tooltip.style.left = `${Math.max(8, Math.min(left, box.width - w - 8))}px`;
    tooltip.style.top = `${Math.max(8, Math.min(top, box.height - h - 8))}px`;
    requestAnimationFrame(() => tooltip.classList.add('is-visible'));
  }
  function hover(code, focus = false) {
    hovered = code;
    hoverOutline.setAttribute('d', code ? outline(code) : '');
    hoverOutline.classList.toggle('is-visible', Boolean(code));
    hoverOutline.classList.toggle('is-focus', Boolean(code) && focus);
    for (const [k, g] of groups) g.classList.toggle('is-hovered', k === code);
  }
  const hideTip = () => {
    tooltip.classList.remove('is-visible');
    hideTimer = setTimeout(() => { tooltip.hidden = true; }, reducedMotion() ? 0 : 160);
    hover('');
  };

  for (const code of order) {
    const shape = EU_SHAPES[code];
    const c = counts[code] || {verified:0, unverified:0, applicationConfirmed:0};
    const bucket = c.verified ? `b${countBucket(c.verified)}` : c.unverified ? 'b-leads' : 'b0';
    const g = node('g', {class:`eu-country ${bucket}`, tabindex:'0', role:'button', 'data-code':code, 'aria-pressed':'false',
      'aria-label':`${names[code] || code}: ${describeCountry(names[code], c)}`}, layer);
    node('path', {d:shape.d}, g);
    if (shape.small) {
      node('circle', {cx:shape.cx, cy:shape.cy, r:'6', class:'small-marker'}, g);
      // Generous invisible hit area so tiny countries remain easy to point at and tap.
      node('circle', {cx:shape.cx, cy:shape.cy, r:'17', class:'hit-area'}, g);
    }
    g.addEventListener('pointerenter', e => { if (e.pointerType === 'mouse' || e.pointerType === 'pen') hover(code); });
    g.addEventListener('pointermove', e => { if (e.pointerType === 'mouse' || e.pointerType === 'pen') showTip(code, e.clientX, e.clientY); });
    g.addEventListener('pointerleave', e => { if (e.pointerType === 'mouse' || e.pointerType === 'pen') hideTip(); });
    g.addEventListener('focus', () => {
      if (!g.matches(':focus-visible')) return;
      hover(code, true);
      const r = g.getBoundingClientRect(); showTip(code, r.left + r.width / 2, r.top + r.height / 2);
    });
    g.addEventListener('blur', hideTip);
    g.addEventListener('click', () => { hideTip(); onSelect(code); });
    g.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); hideTip(); onSelect(code); }
      if (e.key === 'Escape') hideTip();
    });
    groups.set(code, g);
    if (c.verified) badgeData.push({code, cx:Number(shape.cx), cy:Number(shape.cy), label:String(c.verified), direct:c.applicationConfirmed > 0});
  }

  // Badges keep a constant on-screen size: redrawn from user-units-per-pixel after resizes and zooms.
  function drawBadges() {
    const px = svg.clientWidth || svg.getBoundingClientRect().width;
    if (!px) return;
    const unitsPerPixel = box => Math.max(box[2] / px, box[3] / (svg.clientHeight || px));
    const scale = px < 520 ? 0.9 : 1;
    const u = unitsPerPixel(current) * scale;
    const baseUnit = unitsPerPixel(base) * scale;
    const badgeWidth = d => 14 + d.label.length * 7.2;
    const nearby = badgeData.filter(d => beneluxButtons.has(d.code));
    // Base the callout on the unzoomed layout so zooming keeps the same focus targets.
    const separate = nearby.some((a, i) => nearby.slice(i + 1).some(b =>
      Math.abs(a.cx - b.cx) < ((badgeWidth(a) + badgeWidth(b)) / 2 + 4) * baseUnit
      && Math.abs(a.cy - b.cy) < 24 * baseUnit));
    benelux.hidden = !separate;
    badges.replaceChildren();
    for (const d of badgeData) {
      if (separate && beneluxButtons.has(d.code)) continue;
      const width = badgeWidth(d) * u, height = 20 * u;
      const b = node('g', {class:`badge${d.direct ? ' has-direct' : ''}${d.code === selected ? ' is-selected' : ''}`, 'data-code':d.code}, badges);
      node('rect', {x:d.cx - width / 2, y:d.cy - height / 2, width, height, rx:height / 2}, b);
      const t = node('text', {x:d.cx, y:d.cy, dy:'0.36em', 'text-anchor':'middle', 'font-size':(11.5 * u).toFixed(2)}, b);
      t.textContent = d.label;
      if (d.direct) node('circle', {cx:d.cx + width / 2 - u, cy:d.cy - height / 2 + u, r:4.2 * u, class:'direct-dot', 'stroke-width':1.6 * u}, b);
    }
  }

  // Frame the interactive countries tightly, matched to the container's proportions and kept inside the
  // generated geography (display only; context shapes are clipped at the original viewBox).
  const full = MAP_VIEWBOX.split(' ').map(Number);
  let bbox = full;
  try {
    const box = layer.getBBox();
    if (box.width > 0 && box.height > 0) {
      const pad = Math.max(box.width, box.height) * 0.025;
      bbox = [box.x - pad, box.y - pad, box.width + pad * 2, box.height + pad * 2];
    }
  } catch { bbox = full; }
  function fit() {
    const w = svg.clientWidth, h = svg.clientHeight;
    let [x, y, bw, bh] = bbox;
    if (w > 0 && h > 0) {
      const aspect = w / h;
      if (bw / bh < aspect) { const nw = Math.min(bh * aspect, full[2]); x -= (nw - bw) / 2; bw = nw; }
      else { const nh = Math.min(bw / aspect, full[3]); y -= (nh - bh) / 2; bh = nh; }
    }
    x = Math.min(Math.max(x, full[0]), full[0] + full[2] - bw);
    y = Math.min(Math.max(y, full[1]), full[1] + full[3] - bh);
    return [x, y, bw, bh].map(n => Math.round(n * 10) / 10);
  }
  let base = fit(), baseString = base.join(' ');
  let factor = 1, current = [...base], frame;
  svg.setAttribute('viewBox', baseString);
  drawBadges();
  if (typeof ResizeObserver === 'function') new ResizeObserver(() => {
    base = fit(); baseString = base.join(' ');
    if (factor === 1) { cancelAnimationFrame(frame); current = [...base]; svg.setAttribute('viewBox', baseString); }
    drawBadges();
  }).observe(svg);

  // Display-only zoom (viewBox), animated unless the user prefers reduced motion.
  function centre() {
    const shape = EU_SHAPES[selected] || EU_SHAPES[hovered];
    return shape ? [Number(shape.cx), Number(shape.cy)] : [current[0] + current[2] / 2, current[1] + current[3] / 2];
  }
  function apply(target) {
    cancelAnimationFrame(frame);
    if (reducedMotion()) { current = target; svg.setAttribute('viewBox', target.join(' ')); drawBadges(); return; }
    const from = [...current], start = performance.now(), duration = 320;
    const step = now => {
      const t = Math.min(1, (now - start) / duration), e = 1 - Math.pow(1 - t, 3);
      current = from.map((v, i) => v + (target[i] - v) * e);
      svg.setAttribute('viewBox', current.map(n => n.toFixed(1)).join(' '));
      if (t < 1) frame = requestAnimationFrame(step); else { current = target; svg.setAttribute('viewBox', target.join(' ')); drawBadges(); }
    };
    frame = requestAnimationFrame(step);
  }
  function zoomTo(next, [cx, cy] = centre()) {
    factor = Math.min(4, Math.max(1, next));
    wrap.classList.toggle('is-zoomed', factor > 1);
    apply(zoomViewBox(baseString, cx, cy, factor));
    return factor;
  }

  return {
    select(code) {
      selected = code && EU_SHAPES[code] ? code : '';
      for (const [k, g] of groups) {
        const on = k === selected;
        g.classList.toggle('is-selected', on);
        g.setAttribute('aria-pressed', String(on));
      }
      for (const b of badges.children) b.classList.toggle('is-selected', b.dataset.code === selected);
      for (const [k, b] of beneluxButtons) b.setAttribute('aria-pressed', String(k === selected));
      selectedOutline.setAttribute('d', selected ? outline(selected) : '');
      selectedOutline.classList.toggle('is-visible', Boolean(selected));
      if (factor > 1 && selected) zoomTo(factor);
    },
    zoom(step) { return zoomTo(factor * (step > 0 ? 1.6 : 1 / 1.6)); },
    reset() { return zoomTo(1, [base[0] + base[2] / 2, base[1] + base[3] / 2]); },
  };
}
