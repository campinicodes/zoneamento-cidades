// Front-end genérico: escolhe/detecta cidade, desenha polígonos ou envia arquivo → /api/consulta(-arquivo).
const mapa = L.map('mapa').setView([-15.8, -47.9], 4);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19, attribution: '© OpenStreetMap | Zoneamento: bases oficiais municipais (ver referências)'}).addTo(mapa);
const sel = document.getElementById('cidade'), linkRef = document.getElementById('link-ref');
let CIDADES = {}, ultimo = null, camadaZonas = null;

// ---- cidades
async function carregarCidades() {
  const r = await (await fetch('/api/cidades')).json();
  r.cidades.forEach(c => {
    CIDADES[c.slug] = c;
    sel.insertAdjacentHTML('beforeend', `<option value="${c.slug}">${c.municipio}/${c.uf}${c.exemplo_ficticio ? ' (FICTÍCIO)' : ''}</option>`);
  });
  atualizarLink();
  tabelaStatus(r.cidades);
}
function tabelaStatus(cs) {
  const e = s => s == null ? '–' : s;
  const err = x => !x ? '–' : (x.min === x.max ? `${x.min} m` : `${x.min}–${x.max} m`);
  const lin = cs.map(c => { const s = c.status || {};
    const pct = s.pct_area_base_oficial;
    const q = pct == null ? '' : pct >= 99 ? 'ok' : pct > 0 ? 'mix' : 'aprox';
    return `<tr><td><a href="#" data-slug="${c.slug}" class="ir">${c.municipio}/${c.uf}</a></td><td class="n">${e(s.n_zonas)}</td>
      <td class="n q-${q}">${pct == null ? '–' : pct + '%'}</td><td class="n">${err(s.erro_estimado_m)}</td>
      <td>${e(s.data_levantamento)}</td><td class="n">${e(s.n_lacunas)}</td>
      <td><a href="/referencias/${c.slug}" target="_blank" title="referências e lacunas">ref.</a></td></tr>`; }).join('');
  document.getElementById('tabela-status').innerHTML = `<table class="status"><thead><tr><th>Cidade</th><th>Zonas</th>
    <th title="% da área das zonas base com geometria de vetor oficial">Geom. oficial</th><th>Erro est.</th><th>Levantamento</th><th>Lacunas</th><th></th></tr></thead><tbody>${lin}</tbody></table>`;
  document.querySelectorAll('#tabela-status a.ir').forEach(a => a.addEventListener('click', ev => {
    ev.preventDefault(); sel.value = a.dataset.slug; centrar(a.dataset.slug); atualizarLink(); }));
}
function atualizarLink(slug) {
  slug = slug || sel.value;
  linkRef.style.display = slug ? '' : 'none';
  linkRef.href = slug ? `/referencias/${slug}` : '#';
}
function centrar(slug) {
  const c = CIDADES[slug]; if (!c) return;
  mapa.setView([c.centro_mapa.lat, c.centro_mapa.lon], c.centro_mapa.zoom || 12);
}
sel.addEventListener('change', () => { centrar(sel.value); atualizarLink(); if (document.getElementById('ver-zonas').checked) alternarZonas(true); });

// ---- camada de zonas da cidade selecionada (cores por tipo/código, genérico)
const cor = s => { let h = 0; for (const ch of s) h = (h * 31 + ch.charCodeAt(0)) % 360; return `hsl(${h},65%,55%)`; };
async function alternarZonas(ligar) {
  if (camadaZonas) { mapa.removeLayer(camadaZonas); camadaZonas = null; }
  const slug = sel.value || (ultimo && ultimo.resultados.find(x => x.cidade) || {cidade: {}}).cidade.slug;
  if (!ligar || !slug) return;
  const fc = await (await fetch(`/api/zonas/${slug}`)).json();
  camadaZonas = L.geoJSON(fc, {
    style: f => f.geometry.type.includes('Line') ? {color: '#00bcd4', weight: 4}
      : {color: '#555', weight: .5, fillColor: cor(f.properties.codigo), fillOpacity: f.properties.tipo === 'base' ? .35 : .55},
    onEachFeature: (f, l) => l.bindTooltip(`${f.properties.codigo} (${f.properties.tipo}) ${f.properties.rotulo || ''}`)
  }).addTo(mapa);
  camadaZonas.bringToBack();
}
document.getElementById('ver-zonas').addEventListener('change', e => alternarZonas(e.target.checked));

// ---- desenho (vários polígonos)
const desenhados = new L.FeatureGroup().addTo(mapa);
mapa.addControl(new L.Control.Draw({position: 'topleft',
  draw: {polygon: {allowIntersection: false, showArea: true}, rectangle: true, polyline: false, circle: false, marker: false, circlemarker: false},
  edit: {featureGroup: desenhados}}));
const consultarDesenhados = () => consultar(desenhados.toGeoJSON());
mapa.on(L.Draw.Event.CREATED, e => { desenhados.addLayer(e.layer); consultarDesenhados(); });
mapa.on(L.Draw.Event.EDITED, consultarDesenhados);
mapa.on(L.Draw.Event.DELETED, () => desenhados.getLayers().length ? consultarDesenhados() : painel('<p class="nota">Nenhuma consulta.</p>'));
document.getElementById('limpar').addEventListener('click', () => { desenhados.clearLayers(); ultimo = null; baixar.disabled = true; painel('<p class="nota">Nenhuma consulta ainda.</p>'); });

function desenhar(resultados) {
  desenhados.clearLayers();
  resultados.forEach((r, i) => L.geoJSON(r.geometria, {style: {color: '#e60000', weight: 3}})
    .bindTooltip(`${i + 1}. ${r.nome}`, {permanent: resultados.length > 1}).eachLayer(x => desenhados.addLayer(x)));
  if (desenhados.getLayers().length) mapa.fitBounds(desenhados.getBounds(), {maxZoom: 16});
}

// ---- API
async function consultar(geojson) {
  painel('<p class="nota">Consultando…</p>');
  const r = await fetch('/api/consulta', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                         body: JSON.stringify({geojson, cidade: sel.value || null})});
  mostrar(await r.json());
}
window.consultarGeoJSON = async geojson => { const r = await consultar(geojson); };
document.getElementById('form-arq').addEventListener('submit', async ev => {
  ev.preventDefault();
  const f = document.getElementById('arquivo').files[0]; if (!f) return;
  const fd = new FormData(); fd.append('arquivo', f); if (sel.value) fd.append('cidade', sel.value);
  painel('<p class="nota">Lendo arquivo…</p>');
  const res = await (await fetch('/api/consulta-arquivo', {method: 'POST', body: fd})).json();
  if (res.resultados) desenhar(res.resultados);
  mostrar(res);
});
const baixar = document.getElementById('baixar');
baixar.addEventListener('click', () => {
  if (!ultimo) return;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(ultimo, null, 2)], {type: 'application/json'}));
  a.download = `zoneamento_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.json`; a.click();
});

// ---- renderização genérica
const painel = h => document.getElementById('resultado').innerHTML = h;
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const fmt = v => v === null || v === undefined ? '<span class="nota">null (sem fonte – ver lacunas)</span>'
  : typeof v === 'object' ? Object.entries(v).map(([k, x]) => `${esc(k.replace(/_/g, ' '))}: ${fmt(x)}`).join('<br>') : esc(v);
// parâmetro normalizado (schema 1.1): a "forma" diz como ler valor/faixa/condicionais/formula
const num = (v, u) => u === 'fracao' ? `${esc(v)} <span class="nota">(${+(v * 100).toFixed(2)}%)</span>` : esc(v);
const FORMA_TXT = {livre: 'livre', herda_da_base: 'igual ao da zona base', nao_aplicavel: 'não se aplica'};
function fmtCaso(c, u) {
  switch (c.forma) {
    case 'unico': return num(c.valor, u) + (u && u !== 'fracao' ? ' <span class="nota">' + esc(u) + '</span>' : '');
    case 'lista': return (c.valor || []).map(esc).join(', ') || '—';
    case 'faixa': return `${c.faixa.min ?? '…'} a ${c.faixa.max ?? '…'}` + (u ? ' <span class="nota">' + esc(u) + '</span>' : '');
    case 'formula': return `<code>${esc(c.formula)}</code>` + (c.faixa && c.faixa.min !== null ? ` (mín. ${esc(c.faixa.min)})` : '') + (c.faixa && c.faixa.max !== null ? ` (máx. ${esc(c.faixa.max)})` : '');
    case 'texto': return `<i>${esc(c.texto_original)}</i>`;
    case 'sem_dado': return fmt(null);
    default: return esc(FORMA_TXT[c.forma] || c.forma);
  }
}
function fmtParam(p) {
  if (!p.forma) return fmt(p.valor) + (p.unidade ? ' <span class="nota">' + esc(p.unidade) + '</span>' : '');   // legado 1.0
  let h = p.forma === 'condicional' ? '' : fmtCaso(p, p.unidade);
  if (p.condicionais) h += (h ? '<br>' : '') + p.condicionais.map(c => `${esc(c.condicao)}: ${fmtCaso(c, p.unidade)}${c.observacao ? ' <span class="nota">' + esc(c.observacao) + '</span>' : ''}`).join('<br>');
  return h;
}
const cit = p => p && p.fonte_id ? `<div class="cit">${esc(p.fonte_id)} – ${esc(p.fonte_lei || '')}${p.artigo_anexo ? ', ' + esc(p.artigo_anexo) : ''}
   ${p.fonte_url ? `<a href="${p.fonte_url}" target="_blank" rel="noopener">[lei]</a>` : ''}${p.origem ? `<br><i>${esc(p.origem)}</i>` : ''}</div>` : '';
const ROT = {ca_minimo: 'CA mínimo', ca_basico: 'CA básico', ca_maximo: 'CA máximo', taxa_ocupacao: 'Taxa de ocupação',
  gabarito_altura_max_m: 'Gabarito (m)', gabarito_pavimentos: 'Pavimentos', taxa_permeabilidade: 'Permeabilidade',
  lote_minimo_m2: 'Lote mínimo (m²)', testada_minima_m: 'Testada mínima (m)', usos_permitidos: 'Usos', vagas: 'Vagas', densidade: 'Densidade'};
function linhasParam(obj, prefixo = '') {
  let h = '';
  const ordem = k => { const i = Object.keys(ROT).indexOf(k); return i < 0 ? 99 : i; };
  for (const [k, p] of Object.entries(obj || {}).sort((a, b) => ordem(a[0]) - ordem(b[0]))) {
    const rot = prefixo + (ROT[k] || k.replace(/_/g, ' '));
    if (p && typeof p === 'object' && 'valor' in p)
      h += `<tr><td>${esc(rot)}</td><td>${fmtParam(p)}${cit(p)}
             ${p.observacao ? `<div class="nota">${esc(p.observacao)}</div>` : ''}</td></tr>`;
    else if (p && typeof p === 'object') h += linhasParam(p, rot + ' › ');
    else if (p === null) h += `<tr><td>${esc(rot)}</td><td>${fmt(null)}</td></tr>`;
  }
  return h;
}
const tabSob = lst => lst && lst.length ? `<table>${lst.map(x => `<tr><td>${esc(x.codigo)}${x.detalhes ? '<div class="nota">' + x.detalhes.slice(0, 4).map(d => `${esc(d.rotulo)} ${d.pct_terreno}%`).join(' · ') + '</div>' : ''}</td>
   <td>${x.area_m2.toLocaleString('pt-BR')} m²</td><td>${x.pct_terreno}%</td></tr>`).join('')}</table>` : '<div class="nota">nenhuma</div>';

function blocoResultado(r, i, n) {
  if (r.erro) return `<details class="poligono" open><summary>${i + 1}. ${esc(r.nome)} – erro</summary><div><div class="alerta">${esc(r.erro)}</div></div></details>`;
  const R = r.resultado, F = r.parametros || {}, compl = Object.entries(r.camadas_complementares || {}).filter(([, c]) => c.sobreposicoes.length);
  return `<details class="poligono" ${i === 0 ? 'open' : ''}><summary>${n > 1 ? (i + 1) + '. ' + esc(r.nome) + ' – ' : ''}${esc(r.cidade.municipio)}/${esc(r.cidade.uf)} · ${esc(R.zona_aplicavel || '—')}${R.zona_dos_indices !== R.zona_aplicavel ? ' → ' + esc(R.zona_dos_indices) : ''}</summary><div>
    <div class="nota">Cidade: ${esc(r.cidade.municipio)}/${esc(r.cidade.uf)} (${esc(r.cidade.deteccao)}) · <a href="${r.referencias}" target="_blank">referências e lacunas</a></div>
    <h3>Terreno</h3>Área: <b>${r.terreno.area_m2.toLocaleString('pt-BR')} m²</b> (${r.terreno.area_ha} ha) · <span class="nota">${esc(r.terreno.crs_area)}</span>
    <h3>Zona aplicável</h3>
    <div class="zona">${esc(R.zona_aplicavel || '—')}${R.zona_dos_indices !== R.zona_aplicavel ? ` → índices ${esc(R.zona_dos_indices)}` : ''}</div>
    <div>${esc(R.nome_zona_aplicavel || '')}</div><div class="nota">${esc(R.criterio)}</div>
    <div class="nota">Base predominante: ${esc(R.zona_base_predominante || '—')}${R.zona_base_efetiva !== R.zona_base_predominante ? ' (índices de ' + esc(R.zona_base_efetiva) + ')' : ''}
      ${R.macrozona_predominante ? ' · Macrozona: ' + esc(R.macrozona_predominante) : ''}${R.permeabilidade_codigo ? ' · Permeabilidade: ' + esc(R.permeabilidade_codigo) : ''}</div>
    <h3>Parâmetros (${esc(F.codigo || '—')}) – com citação</h3><table>${linhasParam(F.parametros)}</table>
    ${r.parametros_zona_base ? `<details><summary>Sem testada para o eixo: parâmetros da base ${esc(r.parametros_zona_base.codigo)}</summary><table>${linhasParam(r.parametros_zona_base.parametros)}</table></details>` : ''}
    ${r.macrozona ? `<h4>Macrozona ${esc(r.macrozona.codigo_predominante)}</h4><table>${linhasParam(r.macrozona.parametros)}</table>` : ''}
    <h3>Sobreposições (% do terreno)</h3>
    <h4>Zonas base</h4>${tabSob(r.sobreposicoes.zonas_base)}
    <h4>Zonas sobrepostas</h4>${tabSob(r.sobreposicoes.sobrepostas)}
    <h4>Eixos (distância)</h4>${r.sobreposicoes.eixos.length ? `<table>${r.sobreposicoes.eixos.slice(0, 6).map(e => `<tr><td>${esc(e.codigo)}</td><td>${e.distancia_m.toLocaleString('pt-BR')} m</td><td>${e.toca ? 'toca' : e.dentro_da_distancia ? '≤ ' + e.distancia_max_m + ' m' : ''}</td></tr>`).join('')}</table>` : '<div class="nota">nenhum próximo</div>'}
    ${compl.map(([n, c]) => `<h4>${esc(n)} <span class="nota">(${esc(c.papel)})</span></h4>${tabSob(c.sobreposicoes)}`).join('')}
    <h3>Alertas</h3>${r.alertas.map(a => `<div class="alerta ${a.tipo}">⚠ <b>${esc(a.tipo)}</b>: ${esc(a.texto)}${a.fundamento ? `<div class="cit">${esc(a.fundamento)}</div>` : ''}</div>`).join('')}
  </div></details>`;
}
function mostrar(res) {
  if (res.erro) { painel(`<div class="alerta">${esc(res.erro)}</div>`); return; }
  ultimo = res; baixar.disabled = false; document.getElementById('status-cidades').open = false;
  const n = res.resultados.length;
  painel(`<div class="nota">${n} polígono(s) analisado(s). ${esc(res.aviso)}</div>` + res.resultados.map((r, i) => blocoResultado(r, i, n)).join(''));
  const c = res.resultados.find(x => x.cidade);
  if (c) atualizarLink(c.cidade.slug);
}

// ---- atalhos de URL p/ teste/compartilhamento: ?cidade=slug&poligono=<GeoJSON>&zonas=1
carregarCidades().then(() => {
  const qs = new URLSearchParams(location.search);
  if (qs.get('cidade')) { sel.value = qs.get('cidade'); centrar(sel.value); atualizarLink(); }
  if (qs.get('poligono')) {
    try { const gj = JSON.parse(qs.get('poligono'));
          consultar(gj).then(() => { if (ultimo && ultimo.resultados) desenhar(ultimo.resultados);
                                     if (qs.get('zonas') === '1') { document.getElementById('ver-zonas').checked = true; alternarZonas(true); } }); }
    catch (e) { painel('<div class="alerta">Parâmetro "poligono" inválido.</div>'); }
  } else if (qs.get('zonas') === '1') { document.getElementById('ver-zonas').checked = true; alternarZonas(true); }
});
