import { MAP_VIEWBOX, EU_SHAPES, CONTEXT_SHAPES } from './eu-map.js';
import { countBucket } from './logic.js';

const SVG = 'http://www.w3.org/2000/svg';
function node(tag, attrs = {}, parent) {
  const n = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (parent) parent.append(n);
  return n;
}
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;

// "3 in English · 31 in Italian" for the verified ads of one country.
export function describeLanguages(breakdown = [], languageNames = {}) {
  return breakdown.map(({code, count}) => `${count} in ${code === 'unknown' ? 'an unidentified language' : languageNames[code] || code}`).join(' · ');
}

export function describeCountry(name, c = {verified:0, unverified:0}) {
  if (c.verified) return `${plural(c.verified, 'verified HR opportunity', 'verified HR opportunities')}${c.unverified ? ` · ${c.unverified} more to check` : ''}`;
  if (c.unverified) return `Nothing verified yet · ${plural(c.unverified, 'lead', 'leads')} to check`;
  return 'No opportunities collected yet';
}

// Draws the EU-27 map into `svg`. Returns {select(code)} to sync the highlighted country.
export function drawMap({svg, tooltip, wrap, counts, names, onSelect, languages = () => ''}) {
  svg.setAttribute('viewBox', MAP_VIEWBOX);
  svg.replaceChildren();
  const defs = node('defs', {}, svg);
  const hatch = node('pattern', {id:'map-hatch', width:'7', height:'7', patternUnits:'userSpaceOnUse', patternTransform:'rotate(45)'}, defs);
  node('rect', {width:'7', height:'7', class:'hatch-bg'}, hatch);
  node('line', {x1:'0', y1:'0', x2:'0', y2:'7', class:'hatch-line'}, hatch);

  const context = node('g', {class:'map-context', 'aria-hidden':'true'}, svg);
  for (const d of CONTEXT_SHAPES) node('path', {d}, context);

  const layer = node('g', {class:'map-countries'}, svg);
  // Outline overlays drawn above all countries (never moved, never hit-tested) so borders stay visible.
  const selectedOutline = node('path', {class:'map-outline selected-outline', d:''}, svg);
  const hoverOutline = node('path', {class:'map-outline hover-outline', d:''}, svg);
  const badges = node('g', {class:'map-badges', 'aria-hidden':'true'}, svg);
  const outline = code => EU_SHAPES[code].d + (EU_SHAPES[code].small ? `M${EU_SHAPES[code].cx - 8},${EU_SHAPES[code].cy}a8,8 0 1,0 16,0a8,8 0 1,0 -16,0` : '');
  const groups = new Map();
  const order = Object.keys(EU_SHAPES).sort((a, b) => (names[a] || a).localeCompare(names[b] || b));

  function showTip(code, x, y) {
    const c = counts[code] || {verified:0, unverified:0};
    tooltip.replaceChildren();
    const title = document.createElement('strong'); title.textContent = names[code] || code;
    const line = document.createElement('span'); line.textContent = describeCountry(names[code], c);
    const hint = document.createElement('small'); hint.textContent = c.verified || c.unverified ? 'Click to see them' : 'Click to check this country';
    const spoken = languages(code);
    if (spoken) { const lang = document.createElement('span'); lang.className = 'tip-languages'; lang.textContent = spoken; tooltip.append(title, line, lang, hint); }
    else tooltip.append(title, line, hint);
    tooltip.hidden = false;
    const box = wrap.getBoundingClientRect();
    const w = tooltip.offsetWidth, h = tooltip.offsetHeight;
    let left = x - box.left + 16, top = y - box.top - h - 12;
    if (left + w > box.width - 4) left = x - box.left - w - 16;
    if (top < 4) top = y - box.top + 18;
    tooltip.style.left = `${Math.max(4, left)}px`;
    tooltip.style.top = `${top}px`;
  }
  const hideTip = () => { tooltip.hidden = true; hoverOutline.setAttribute('d', ''); };

  for (const code of order) {
    const shape = EU_SHAPES[code];
    const c = counts[code] || {verified:0, unverified:0};
    const bucket = c.verified ? `b${countBucket(c.verified)}` : c.unverified ? 'b-leads' : 'b0';
    const g = node('g', {class:`eu-country ${bucket}`, tabindex:'0', role:'button', 'data-code':code,
      'aria-label':`${names[code] || code}: ${describeCountry(names[code], c)}`}, layer);
    node('path', {d:shape.d}, g);
    if (shape.small) node('circle', {cx:shape.cx, cy:shape.cy, r:'8', class:'small-marker'}, g);
    g.addEventListener('mouseenter', () => hoverOutline.setAttribute('d', outline(code)));
    g.addEventListener('mousemove', e => showTip(code, e.clientX, e.clientY));
    g.addEventListener('mouseleave', hideTip);
    g.addEventListener('focus', () => { hoverOutline.setAttribute('d', outline(code)); const r = g.getBoundingClientRect(); showTip(code, r.left + r.width / 2, r.top + r.height / 2); });
    g.addEventListener('blur', hideTip);
    g.addEventListener('click', () => { hideTip(); onSelect(code); });
    g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); hideTip(); onSelect(code); } });
    groups.set(code, g);
    if (c.verified) {
      const b = node('g', {class:'badge'}, badges);
      node('circle', {cx:shape.cx, cy:shape.cy, r: c.verified > 9 ? '15' : '12'}, b);
      const t = node('text', {x:shape.cx, y:shape.cy, dy:'0.35em', 'text-anchor':'middle'}, b);
      t.textContent = String(c.verified);
    }
  }
  return {
    select(code) {
      for (const [k, g] of groups) {
        const on = k === code;
        g.classList.toggle('is-selected', on);
        g.setAttribute('aria-pressed', String(on));
      }
      selectedOutline.setAttribute('d', code && EU_SHAPES[code] ? outline(code) : '');
    }
  };
}
