import json
import threading
import time
import webbrowser
import traceback
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Load PUZZLES
try:
    from utils.puzzles import PUZZLES
except ImportError:
    PUZZLES = {}

# Load solve_nonogram
try:
    from csp_solution import solve_nonogram
except ImportError:
    from csp import solve_nonogram


HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Nonogram CSP 해결기</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    :root {
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #1e293b;
      --text-muted: #64748b;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --grid-line: #cbd5e1;
      --cell-filled: #2563eb;
      --cell-empty: #f1f5f9;
      --cell-size: 35px; /* JS가 퍼즐 배열 크기에 맞춰 동적으로 덮어씌웁니다 */
    }
    
    * { box-sizing: border-box; }
    
    body {
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--text);
      font-family: 'Pretendard', 'Inter', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
      overflow-x: hidden;
    }
    
    .layout-main {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      gap: 30px;
      align-items: flex-start;
      justify-content: center;
      margin-top: 40px;
      margin-bottom: 40px;
      width: 95%;
      max-width: 1600px;
    }
    
    .panel {
      background: var(--card-bg);
      border-radius: 20px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
      border: 1px solid rgba(0, 0, 0, 0.04);
      padding: 30px 40px;
    }
    
    .puzzle-area {
      flex: 1;
      min-width: 720px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    
    .inspector-panel {
      width: 520px;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      gap: 16px;
      animation: slideIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes slideIn {
      from { opacity: 0; transform: translateX(20px); }
      to { opacity: 1; transform: translateX(0); }
    }
    
    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      margin-bottom: 30px;
      width: 100%;
      justify-content: center;
      align-items: center;
    }
    
    select {
      padding: 12px 18px;
      border-radius: 10px;
      border: 1px solid #cbd5e1;
      background: #f8fafc;
      color: var(--text);
      font-size: 15px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
      transition: all 0.2s ease;
    }
    select:hover {
      border-color: #94a3b8;
      background: white;
    }
    
    button {
      padding: 12px 24px;
      border-radius: 10px;
      border: none;
      background: var(--accent);
      color: white;
      font-size: 15px;
      font-weight: 800;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
    }
    
    button:hover {
      background: var(--accent-hover);
      transform: translateY(-2px);
      box-shadow: 0 6px 15px rgba(37, 99, 235, 0.25);
    }
    
    button:disabled {
      background: #cbd5e1;
      color: white;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
    
    
    /* TABS */
    .tabs-container {
      width: 95%; max-width: 1600px;
      margin-top: 20px;
      display: flex;
      border-bottom: 2px solid #e2e8f0;
      gap: 10px;
    }
    .tab-btn {
      padding: 12px 24px;
      background: none; border: none;
      font-size: 1.05rem; font-weight: 800; color: #64748b;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      transition: all 0.2s;
    }
    .tab-btn:hover { color: #2563eb; background: #f8fafc; }
    .tab-btn.active { color: #2563eb; border-bottom: 3px solid #2563eb; background: #eff6ff; border-top-left-radius: 8px; border-top-right-radius: 8px; }
    
    .view-page { display: none; width: 100%; flex-direction: column; align-items: center; }
    .view-page.active { display: flex; }

    /* Trace Slider UI */
    .trace-controls {
      display: flex; gap: 15px; align-items: center; margin-top: 15px; width: 100%; max-width: 900px;
      background: white; padding: 20px 25px; border-radius: 12px; border: 1px solid #e2e8f0;
    }
    .slider-container { flex: 1; display: flex; flex-direction: column; gap: 5px; }
    input[type=range] { width: 100%; cursor: pointer; }
    .slider-labels { display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b; font-weight: 600; }
    .domain-samples-container {
      display: none;
      margin-top: 4px;
      padding: 8px;
      background: #f8fafc;
      border-radius: 6px;
      font-family: monospace;
      font-size: 0.8rem;
      color: #475569;
      letter-spacing: 1.5px;
      line-height: 1.5;
      border: 1px solid #e2e8f0;
      white-space: pre;
    }
    .domain-samples-container.open { display: block; }

    /* Board Layout */
    .layout-board {
      display: grid;
      grid-template-columns: max-content auto;
      grid-template-rows: max-content auto;
      gap: 8px;
      justify-content: center;
    }
    
    .col-hints, .row-hints {
      display: grid;
      gap: 2px;
    }
    
    .col-hint-cell, .row-hint-cell {
      display: flex;
      align-items: center;
      font-size: clamp(10px, 1.5vw, 15px);
      color: #64748b;
      font-weight: 800;
    }
    .col-hints { grid-column: 2; grid-row: 1; }
    .col-hint-cell { flex-direction: column; justify-content: flex-end; line-height: 1.3; }
    .row-hints { grid-column: 1; grid-row: 2; }
    .row-hint-cell { justify-content: flex-end; letter-spacing: 2px; }
    
    .cell-grid {
      grid-column: 2;
      grid-row: 2;
      display: grid;
      gap: 2px;
      background: #e2e8f0;
      padding: 4px;
      border-radius: 6px;
      box-shadow: inset 0 2px 4px rgba(0,0,0,0.03);
      border: 1px solid #cbd5e1;
    }
    
    .cell {
      width: var(--cell-size);
      height: var(--cell-size);
      background: var(--cell-empty);
      border-radius: 3px;
      transition: background 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease;
    }
    
    .cell.filled {
      background: var(--cell-filled);
    }
    
    .cell.highlight {
      background: #fef08a !important; 
      box-shadow: inset 0 0 0 2px #fde047;
    }
    .cell.highlight.filled {
      background: #eab308 !important; 
    }
    
    #stats {
      margin-top: 20px;
      font-size: 1.05rem;
      color: #64748b;
      height: 24px;
      font-weight: 600;
    }
    .error { color: #ef4444 !important; }
    .success { color: #10b981 !important; }
    
    /* Inspector specific */
    .inspector-header {
      font-size: 1.15rem;
      font-weight: 800;
      color: var(--text);
      border-bottom: 2px solid #f1f5f9;
      padding-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .inspector-card {
      border-radius: 12px;
      padding: 16px 20px;
      border: 1px solid #e2e8f0;
      transition: all 0.2s ease;
      background: white;
    }
    
    /* Color emphasize variants */
    .card-var { border-left: 4px solid #8b5cf6; }
    .card-const { border-left: 4px solid #ef4444; }
    .card-dom { border-left: 4px solid #3b82f6; }
    
    .card-title {
      font-size: 0.95rem;
      font-weight: 800;
      letter-spacing: 0.2px;
      margin-bottom: 5px;
    }
    .card-var .card-title { color: #5b21b6; }
    .card-const .card-title { color: #991b1b; }
    .card-dom .card-title { color: #1e40af; }
    
    .card-value {
      font-size: 2.2rem;
      font-weight: 800;
      line-height: 1.1;
    }
    
    .desc-text {
      font-size: 0.8rem;
      color: #64748b;
      margin-top: 6px;
      line-height: 1.4;
      background: #f8fafc;
      padding: 6px 8px;
      border-radius: 6px;
    }
    
    .domain-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 300px;
      overflow-y: auto;
      margin-top: 12px;
      padding-right: 5px;
    }
    .domain-list::-webkit-scrollbar { width: 4px; }
    .domain-list::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 3px; }
    .domain-list::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    
    /* Status items for Domain */
    .domain-item-wrapper {
      display: flex;
      flex-direction: column;
    }
    
    .domain-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.85rem;
      background: white;
      border: 1px solid #e2e8f0;
      padding: 8px 12px;
      border-radius: 6px;
      font-family: monospace;
      color: #334155;
      font-weight: 600;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s ease;
      z-index: 2;
    }
    .domain-item:hover { filter: brightness(0.96); }
    .domain-item.success-item { color: #047857; background: #ecfdf5; border-color: #a7f3d0; }
    .domain-item.error-item { color: #b91c1c; background: #fef2f2; border-color: #fecaca; }
    .domain-item.pending-item { color: #b45309; background: #fef3c7; border-color: #fde68a; }
    
    /* Dropdown UI */
    .domain-dropdown {
      display: none;
      flex-direction: column;
      gap: 4px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-top: none;
      border-bottom-left-radius: 6px;
      border-bottom-right-radius: 6px;
      padding: 12px 14px;
      padding-top: 10px;
      margin-top: -4px;
      margin-bottom: 2px;
      font-size: 0.75rem;
      color: #475569;
      box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
      z-index: 1;
      overflow-x: auto;
      white-space: nowrap;
    }
    .domain-dropdown.open {
      display: flex;
      animation: fadeIn 0.2s ease;
    }
    
    .sample-row {
      display: inline-flex;
      gap: 2px;
      font-family: monospace;
      letter-spacing: 2px;
      color: #0f172a;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-5px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  
  <div class="tabs-container">
    <button class="tab-btn active" onclick="switchTab('page1')">📊 결과 및 인스펙터 (현재 상태)</button>
    <button class="tab-btn" onclick="switchTab('page2')">⏱ 실시간 탐색 디버거 (백트래킹/가지치기)</button>
  </div>

  <div id="page1" class="view-page active">
    <div class="layout-main">

    <!-- Board Area -->
    <div class="panel puzzle-area">
      <div class="controls">
        <select id="testSelect"></select>
        <select id="algoSelect">
          <option value="step1">[Step 1] 도메인 생성 및 초기값 (초기 세팅 확인)</option>
          <option value="step2">[Step 2] 순수 백트래킹 (매우 느림 - 15초 제한)</option>
          <option value="step3">[Step 3] Revise 필터링 + 백트래킹</option>
          <option value="step4" selected>[Step 4] Full AC-3 최적화 알고리즘</option>
        </select>
        <button id="solveBtn" onclick="solve()">퍼즐 풀기</button>
      </div>
      
      <div class="layout-board">
        <div id="colHints" class="col-hints"></div>
        <div id="rowHints" class="row-hints"></div>
        <div id="board" class="cell-grid"></div>
      </div>
      <div id="stats">퍼즐 로드 완료. (준비 중)</div>
    </div>
    
    <!-- CSP Inspector Panel -->
    <div class="panel inspector-panel">
      <div class="inspector-header">
        🔍 CSP 인스펙터 분석
      </div>
      
      <!-- Variables Card -->
      <div class="inspector-card card-var">
        <div class="card-title">🟣 변수 (Variables)</div>
        <div class="card-value" id="insp-vars" style="color: #8b5cf6;">--</div>
        <div id="insp-raw-vars" style="font-size:0.85rem; font-weight:700; color:#6d28d9; margin-top:2px;">가로(R) --개 / 세로(C) --개</div>
        <div class="desc-text">제약을 확인할 수 있는 독립적인 1차원 배열(선형 선분)들입니다.</div>
      </div>
      
      <!-- Constraints Card -->
      <div class="inspector-card card-const">
        <div class="card-title">🔴 제약조건 (Constraints)</div>
        <div class="card-value" id="insp-const" style="color: #ef4444;">--</div>
        <div class="desc-text">모든 가로줄과 세로줄이 교차하는 지점의 <b>픽셀값이 일치</b>해야 한다는 누적 검사 횟수입니다.</div>
      </div>
      
      <!-- Domains Card -->
      <div class="inspector-card card-dom" style="flex: 1;">
        <div class="card-title">🔵 변수별 도메인 상태 (Variable States)</div>
        <div class="card-value" style="font-size: 1.6rem; color: #3b82f6;" id="insp-doms">--</div>
        <div class="desc-text">알고리즘 연산 후 도메인 잔여 현황을 진단합니다. 도메인이 1개가 되어야 올바르게 채워진(Fixed) 상태를 의미합니다.</div>
        <div class="domain-list" id="insp-dom-list">
          <div style="color:#94a3b8; font-size: 0.8rem; padding: 10px;text-align:center;">모드를 실행하여 변수 상태를 확인하세요.</div>
        </div>
      </div>
    </div>
    </div>
  </div>

  <div id="page2" class="view-page">
    <div class="layout-main" style="margin-top: 20px; align-items: flex-start; max-width: 1400px;">
       <div class="panel" style="flex: 2; display: flex; flex-direction: column; align-items: center; max-width: 900px;">
          <h2 style="margin-top: 0;">탐색 추적 보드 (Trace Viewer)</h2>
          <p style="color: #64748b; font-size: 0.9rem; margin-top: 0;">이전 탭에서 퍼즐을 푼 뒤 슬라이더를 움직여 알고리즘 진행 스텝별 배정 상황을 추적하세요.</p>
          
          <div class="layout-board" style="transform: scale(0.85); transform-origin: center top;">
            <div id="traceColHints" class="col-hints"></div>
            <div id="traceRowHints" class="row-hints"></div>
            <div id="traceBoard" class="cell-grid"></div>
          </div>
          
          <div class="trace-controls">
            <button id="playBtn" onclick="togglePlay()" style="padding: 10px 20px; font-size: 14px;">▶ 재생</button>
            <div class="slider-container">
              <input type="range" id="traceSlider" min="0" max="0" value="0" oninput="onSliderChange()">
              <div class="slider-labels">
                <span id="lblStep">Step 0</span>
                <span id="lblTotal">Total 0</span>
              </div>
            </div>
          </div>
          

       </div>

       <div class="panel inspector-panel" style="flex: 1; min-width: 380px; max-height: 900px; display: flex; flex-direction: column;">
         <div class="inspector-header">
           🟢 실시간 변수 상태 전광판
         </div>
         <div style="font-size: 0.85rem; color: #64748b; margin-top: 10px; margin-bottom: 10px; text-align: center;">어떤 변수가 배정되고 도메인이 깎이는지 추적합니다.</div>
         <div id="traceLiveVars" style="display: flex; flex-direction: column; gap: 8px; flex: 1; overflow-y: auto; padding-right: 5px;">
           <div style="color:#94a3b8; text-align:center; padding: 20px;">변수 데이터 대기 중...</div>
         </div>
       </div>
    </div>
  </div>

  <script>
    let puzzlesData = {};
    let currentHints = null;
    
    async function init() {
      const res = await fetch("/api/puzzles");
      puzzlesData = await res.json();
      
      const sel = document.getElementById('testSelect');
      for(let key in puzzlesData) {
        let opt = document.createElement('option');
        opt.value = key;
        opt.textContent = key;
        sel.appendChild(opt);
      }
      
      sel.addEventListener('change', (e) => {
        renderEmptyBoard(e.target.value);
        resetInspector();
        document.getElementById('stats').innerText = "퍼즐 로드 완료. 새로운 퍼즐을 선택했습니다.";
        document.getElementById('stats').className = "";
      });
      
      if(Object.keys(puzzlesData).length > 0) {
        renderEmptyBoard(Object.keys(puzzlesData)[0]);
        resetInspector();
      }
    }
    
    function resetInspector() {
       document.getElementById('insp-vars').innerText = '--';
       document.getElementById('insp-raw-vars').innerText = 'R 배열 --개 / C 배열 --개';
       document.getElementById('insp-const').innerText = '--';
       document.getElementById('insp-doms').innerText = '진단 전';
       document.getElementById('insp-dom-list').innerHTML = `<div style="color:#94a3b8; font-size: 0.8rem; padding: 10px;text-align:center;">모드를 실행하여 변수 상태를 확인하세요.</div>`;
       
       if (currentHints) {
           const M = currentHints.r.length;
           const N = currentHints.c.length;
           document.getElementById('insp-vars').innerText = M + N;
           document.getElementById('insp-raw-vars').innerText = `R0~R${M-1} (${M}개) / C0~C${N-1} (${N}개)`;
           document.getElementById('insp-const').innerText = M * N;
       }
    }
    
    function renderInspector(data) {
       if (data.variables_count) {
           document.getElementById('insp-vars').innerText = data.variables_count;
       }
       if (data.constraints_count) {
           document.getElementById('insp-const').innerText = data.constraints_count;
       }
       
       let totalDomains = 0;
       
       if (data.domain_details) {
           const listEl = document.getElementById('insp-dom-list');
           listEl.innerHTML = "";
           
           for (const [v, detail] of Object.entries(data.domain_details)) {
               const count = detail.count;
               const samples = detail.samples;
               totalDomains += count;
               
               const container = document.createElement('div');
               container.className = "domain-item-wrapper";
               
               const item = document.createElement('div');
               let stateClass = "";
               let stateIcon = "";
               let stateText = "";
               
               if (count === 1) {
                   stateClass = "success-item";
                   stateIcon = "🟢";
                   stateText = "Fixed (1)";
               } else if (count === 0) {
                   stateClass = "error-item";
                   stateIcon = "🔴";
                   stateText = "Conflict! (0)";
               } else {
                   stateClass = "pending-item";
                   stateIcon = "🟡";
                   stateText = `Pending (${count.toLocaleString()})`;
               }
               
               item.className = "domain-item " + stateClass;
               item.innerHTML = `<span>${stateIcon} &nbsp;${v}</span> <span>${stateText}</span>`;
               
               // Create dropdown
               const dropdown = document.createElement('div');
               dropdown.className = "domain-dropdown";
               
               let hintsArr = [];
               const isRow = v.startsWith('R');
               const idx = parseInt(v.substring(1));
               if (isRow && currentHints) hintsArr = currentHints.r[idx];
               if (!isRow && currentHints) hintsArr = currentHints.c[idx];
               
               const hintStr = document.createElement('div');
               hintStr.style.marginBottom = "8px";
               hintStr.style.paddingBottom = "6px";
               hintStr.style.borderBottom = "1px dashed #cbd5e1";
               hintStr.innerHTML = `
                 <div style="font-weight: 800; color: #991b1b; margin-bottom: 3px;">🎯 제약 조건 (Constraint)</div>
                 <div style="color: #475569; font-size: 0.7rem;">- 힌트 블록 연속 수열: <b>[ ${hintsArr.length > 0 ? hintsArr.join(', ') : '0'} ]</b></div>
               `;
               dropdown.appendChild(hintStr);
               const domainTitle = document.createElement('div');
               domainTitle.innerHTML = `
                 <div style="font-weight: 800; color: #1e40af; margin-bottom: 4px;">🌌 도메인 (Domain)</div>
                 <div style="color: #64748b; font-size: 0.75rem; margin-bottom: 2px;">- 힌트 제약을 만족시킬 수 있는 <b>해당 줄 배치의 모든 경우의 수</b>입니다.</div>
                 <div style="color: #64748b; font-size: 0.75rem; margin-bottom: 6px;">- 정답은 반드시 이 아래의 ${count}개 후보 패턴 중 하나여야 합니다.</div>
               `;
               dropdown.appendChild(domainTitle);
               
               if (samples && samples.length > 0) {
                   samples.forEach((s, sIdx) => {
                       const sRowWrapper = document.createElement('div');
                       sRowWrapper.style.display = "flex";
                       sRowWrapper.style.alignItems = "center";
                       sRowWrapper.style.marginBottom = "4px";
                       
                       const numText = document.createElement('div');
                       numText.style.color = "#94a3b8";
                       numText.style.fontSize = "0.75rem";
                       numText.style.width = "20px";
                       numText.style.flexShrink = "0";
                       numText.innerText = `${sIdx + 1}.`;
                       sRowWrapper.appendChild(numText);
                       
                       const sRow = document.createElement('div');
                       sRow.className = "sample-row";
                       s.forEach(val => {
                           const box = document.createElement('div');
                           box.style.width = "13px";
                           box.style.height = "13px";
                           box.style.borderRadius = "2px";
                           box.style.flexShrink = "0";
                           box.style.border = val === 1 ? "1px solid #1d4ed8" : "1px solid #cbd5e1";
                           box.style.backgroundColor = val === 1 ? "#3b82f6" : "#f1f5f9";
                           box.style.marginRight = "2px";
                           sRow.appendChild(box);
                       });
                       sRowWrapper.appendChild(sRow);
                       dropdown.appendChild(sRowWrapper);
                   });
                   if (count > samples.length) {
                       const more = document.createElement('div');
                       more.style.color = "#94a3b8";
                       more.style.marginTop = "4px";
                       more.innerText = `...외 ${count - samples.length}개 경우의 수 존재`;
                       dropdown.appendChild(more);
                   }
               } else {
                   dropdown.innerHTML += "<div style='color:#ef4444;'>유효한 조합이 없습니다.</div>";
               }
               
               container.appendChild(item);
               container.appendChild(dropdown);
               
               // Click Event to highlight board
               item.addEventListener('click', () => {
                   const boardEl = document.getElementById('board');
                   const cells = Array.from(boardEl.children);
                   
                   const isOpen = dropdown.classList.contains('open');
                   
                   document.querySelectorAll('.domain-dropdown.open').forEach(el => el.classList.remove('open'));
                   cells.forEach(c => c.classList.remove('highlight'));
                   document.querySelectorAll('.domain-item').forEach(el => el.style.borderWidth = "1px");
                   
                   if (!isOpen) {
                       dropdown.classList.add('open');
                       item.style.borderWidth = "2px";
                       
                       const M = currentHints.r.length;
                       const N = currentHints.c.length;
                       
                       if (isRow) {
                           for (let c=0; c<N; c++) {
                               cells[idx * N + c].classList.add('highlight');
                           }
                       } else {
                           for (let r=0; r<M; r++) {
                               cells[r * N + idx].classList.add('highlight');
                           }
                       }
                   }
               });
               
               listEl.appendChild(container);
           }
       }
       
       // Update doms title to show sum or status
       const domsEl = document.getElementById('insp-doms');
       if (data.status === "STEP1_DONE") {
           domsEl.innerText = `총합: ${totalDomains.toLocaleString()}`;
       } else if (data.status === "SOLVED") {
           domsEl.innerText = "전체 만족 (완료)";
           domsEl.style.color = "#10b981";
       } else if (data.status === "TIMEOUT") {
           let remaining = Object.values(data.domain_details || {}).filter(d => d.count > 1).length;
           domsEl.innerText = `수렴 실패 (잔여: ${remaining}개)`;
           domsEl.style.color = "#f59e0b";
       } else if (data.status === "NO_SOLUTION") {
           domsEl.innerText = "해답 없음 (모순)";
           domsEl.style.color = "#ef4444";
       }
    }
    
    function renderEmptyBoard(puzzleKey) {
      const data = puzzlesData[puzzleKey];
      currentHints = data;
      
      const M = data.r.length;
      const N = data.c.length;
      
      // Dynamic Cell Sizing Logic (일관된 전체 보드 크기 렌더링)
      const targetBoardPixels = 700; // 퍼즐판 너비 타겟(~700픽셀 사이)
      const maxDim = Math.max(N, M);
      let calculatedCellSize = Math.floor(targetBoardPixels / maxDim);
      calculatedCellSize = Math.max(20, Math.min(85, calculatedCellSize)); // 최대 85px, 최소 20px 허용
      document.documentElement.style.setProperty('--cell-size', `${calculatedCellSize}px`);
      
      const colHintsEl = document.getElementById('colHints');
      const rowHintsEl = document.getElementById('rowHints');
      const boardEl = document.getElementById('board');
      
      // Setup Col Hints (Append Coordinate Axis)
      colHintsEl.innerHTML = "";
      colHintsEl.style.gridTemplateColumns = `repeat(${N}, var(--cell-size))`;
      data.c.forEach((hintArr, idx) => {
        const div = document.createElement('div');
        div.className = "col-hint-cell";
        const val = hintArr.length === 0 ? "0" : hintArr.join('<br>');
        div.innerHTML = val + `<div style="font-size:0.7em; color:#94a3b8; border-top:1px solid #e2e8f0; width:100%; text-align:center; padding-top:2px; margin-top:4px;">C${idx}</div>`;
        colHintsEl.appendChild(div);
      });
      
      // Setup Row Hints (Append Coordinate Axis)
      rowHintsEl.innerHTML = "";
      rowHintsEl.style.gridTemplateRows = `repeat(${M}, var(--cell-size))`;
      data.r.forEach((hintArr, idx) => {
        const div = document.createElement('div');
        div.className = "row-hint-cell";
        const val = hintArr.length === 0 ? "0" : hintArr.join(' ');
        div.innerHTML = val + `<span style="font-size:0.75em; color:#94a3b8; border-left:1px solid #e2e8f0; padding-left:6px; margin-left:6px;">R${idx}</span>`;
        rowHintsEl.appendChild(div);
      });
      
      // Setup Grid
      boardEl.innerHTML = "";
      boardEl.style.gridTemplateColumns = `repeat(${N}, var(--cell-size))`;
      boardEl.style.gridTemplateRows = `repeat(${M}, var(--cell-size))`;
      for(let i=0; i<M*N; i++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        boardEl.appendChild(cell);
      }
    }


    let traceHistory = [];
    let isPlaying = false;
    let playTimer = null;
    let playSpeedMs = 100;
    
    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.view-page').forEach(p => p.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(tabId).classList.add('active');
      if (tabId === 'page2') {
         renderTraceState(document.getElementById('traceSlider').value);
      }
    }
    
    function togglePlay() {
      const btn = document.getElementById('playBtn');
      if (isPlaying) {
         isPlaying = false;
         btn.innerText = "▶ 재생";
         clearInterval(playTimer);
      } else {
         if (traceHistory.length === 0) return;
         isPlaying = true;
         btn.innerText = "⏸ 일시정지";
         
         if (parseInt(document.getElementById('traceSlider').value) >= traceHistory.length - 1) {
             document.getElementById('traceSlider').value = 0;
         }
         
         playTimer = setInterval(() => {
             let slider = document.getElementById('traceSlider');
             let val = parseInt(slider.value);
             if (val < traceHistory.length - 1) {
                 slider.value = val + 1;
                 onSliderChange();
             } else {
                 togglePlay();
             }
         }, playSpeedMs);
      }
    }
    
    function onSliderChange() {
      renderTraceState(parseInt(document.getElementById('traceSlider').value));
    }
    
    function initTraceBoard() {
      // Create empty board for trace identical to main
      const colHintsEl = document.getElementById('traceColHints');
      const rowHintsEl = document.getElementById('traceRowHints');
      const boardEl = document.getElementById('traceBoard');
      
      colHintsEl.innerHTML = document.getElementById('colHints').innerHTML;
      colHintsEl.style.gridTemplateColumns = document.getElementById('colHints').style.gridTemplateColumns;
      
      rowHintsEl.innerHTML = document.getElementById('rowHints').innerHTML;
      rowHintsEl.style.gridTemplateRows = document.getElementById('rowHints').style.gridTemplateRows;
      
      boardEl.innerHTML = document.getElementById('board').innerHTML;
      boardEl.style.gridTemplateColumns = document.getElementById('board').style.gridTemplateColumns;
      boardEl.style.gridTemplateRows = document.getElementById('board').style.gridTemplateRows;

      // Populate Live Vars panel
      const liveVarsEl = document.getElementById('traceLiveVars');
      if (liveVarsEl) {
         liveVarsEl.innerHTML = "";
         
         const createVarUI = (prefix, i) => {
             let wrap = document.createElement('div');
             wrap.style.display = "flex";
             wrap.style.flexDirection = "column";
             wrap.style.cursor = "pointer";
             wrap.title = "클릭하여 도메인 샘플 펼치기";
             
             let div = document.createElement('div');
             div.id = "trace-live-" + prefix + i;
             div.className = "domain-item pending-item";
             div.style.padding = "6px 12px";
             div.innerHTML = `<span>🟡 &nbsp;${prefix}${i}</span> <span>대기중..</span>`;
             
             let samp = document.createElement('div');
             samp.id = "trace-samples-" + prefix + i;
             samp.className = "domain-samples-container";
             
             wrap.onclick = () => {
                 samp.classList.toggle('open');
             };
             
             wrap.appendChild(div);
             wrap.appendChild(samp);
             liveVarsEl.appendChild(wrap);
         };
         
         currentHints.r.forEach((_, i) => createVarUI('R', i));
         currentHints.c.forEach((_, i) => createVarUI('C', i));
      }
    }
    
    function populateLogPanel() {
        const logPanel = document.getElementById('logPanel');
        logPanel.innerHTML = "";
        
        if (!traceHistory || traceHistory.length === 0) {
            logPanel.innerHTML = "<div style='color: #94a3b8; text-align: center; margin-top: 20px;'>트레이스 기록이 없습니다.</div>";
            return;
        }
        
        let prevAssignCount = 0;
        
        traceHistory.forEach((snap, idx) => {
            const row = document.createElement('div');
            row.className = "log-line";
            row.id = "log-" + idx;
            
            let txt = snap.event || "";
            let currentAssignCount = snap.assignment ? Object.keys(snap.assignment).length : 0;
            let icon = "🔹";
            let indent = currentAssignCount * 12;
            let colorSty = "";
            let weightSty = "";
            
            if (txt.includes("Backtracking")) {
                if (currentAssignCount > prevAssignCount) {
                    icon = "✅";
                    txt = `변수 할당 (깊이: ${currentAssignCount})`;
                    colorSty = "color: #34d399;";
                    weightSty = "font-weight: 800;";
                } else if (currentAssignCount < prevAssignCount) {
                    icon = "⏪";
                    txt = `백트래킹 (변수 회수)`;
                    colorSty = "color: #fb7185;";
                } else {
                    icon = "🔄";
                    txt = `다른 값 시도 (깊이: ${currentAssignCount})`;
                    colorSty = "color: #94a3b8;";
                }
            } else if (txt.includes("Revise")) {
                icon = "✂️";
                colorSty = "color: #c084fc;";
                indent = indent + 10;
            }
            
            prevAssignCount = currentAssignCount;
            
            row.innerHTML = `
              <div class="step-num">[${idx}]</div>
              <div class="log-txt" style="margin-left: ${indent}px; ${colorSty} ${weightSty}">
                ${icon} ${txt}
              </div>
            `;
            logPanel.appendChild(row);
        });
    }
    
    function renderTraceState(stepIdx) {
       document.getElementById('lblStep').innerText = "Step " + stepIdx;
       if (!traceHistory || traceHistory.length === 0) return;
       
       const snap = traceHistory[stepIdx];
       const boardEl = document.getElementById('traceBoard');
       const M = currentHints.r.length;
       const N = currentHints.c.length;
       
       // Reset
       Array.from(boardEl.children).forEach(c => {
         c.classList.remove('filled');
         c.classList.remove('highlight');
         c.style.background = 'var(--cell-empty)';
       });
       
       // Render Assignment to board
       if (snap.assignment) {
           for (let r=0; r<M; r++) {
               let rVar = "R" + r;
               if (snap.assignment[rVar]) {
                   let rowArr = snap.assignment[rVar];
                   for (let c=0; c<N; c++) {
                       if (rowArr[c] === 1) {
                           boardEl.children[r * N + c].classList.add("filled");
                       }
                   }
               }
           }
       }
       
       // Update Live Vars Tracker & Samples by searching backward for the latest domain snapshot
       let domSnap = null;
       for (let i = stepIdx; i >= 0; i--) {
           if (traceHistory[i].domains) {
               domSnap = traceHistory[i].domains;
               break;
           }
       }
       
       if (domSnap) {
           ['R', 'C'].forEach(prefix => {
               const max = prefix === 'R' ? M : N;
               for(let i=0; i<max; i++) {
                   const key = prefix + i;
                   const el = document.getElementById('trace-live-' + key);
                   const sampEl = document.getElementById('trace-samples-' + key);
                   if(!el) continue;
                   
                   if(snap.assignment && snap.assignment[key]) {
                      const arr = snap.assignment[key];
                      const txt = arr.map(x => x ? '■' : '□').join('');
                      el.className = "domain-item success-item";
                      el.style.borderColor = "#34d399";
                      el.style.backgroundColor = "rgba(52, 211, 153, 0.1)";
                      el.innerHTML = `<span>✅ &nbsp;${key}</span> <span style="font-family:monospace;letter-spacing:1px;font-size:0.8rem;color:#0f172a;">[${txt}]</span>`;
                      if (sampEl) sampEl.innerHTML = "<div style='color:#64748b;text-align:center;'>할당 완료됨</div>";
                   } else {
                      const domInfo = domSnap[key];
                      if(!domInfo) continue;
                      
                      const count = domInfo.count;
                      const samples = domInfo.samples || [];
                      
                      if(count === 0) {
                          el.className = "domain-item error-item";
                          el.style.backgroundColor = "rgba(239, 68, 68, 0.1)";
                          el.innerHTML = `<span>🔴 &nbsp;${key}</span> <span>충돌! (0개)</span>`;
                      } else {
                          el.className = "domain-item pending-item";
                          el.style.borderColor = "#c084fc";
                          el.style.backgroundColor = "white";
                          el.innerHTML = `<span>🟡 &nbsp;${key}</span> <span>도메인 ${count}개 남음</span>`;
                      }
                      
                      if (sampEl) {
                          let sampHtml = "";
                          samples.forEach(s => {
                              const rowTxt = s.map(x => x ? '■' : '□').join(' ');
                              sampHtml += `<div>[${rowTxt}]</div>`;
                          });
                          if(count > samples.length) {
                              sampHtml += `<div style="color:#94a3b8; font-style:italic; margin-top:4px;">...외 ${count - samples.length}개 조합 숨김</div>`;
                          }
                          sampEl.innerHTML = sampHtml;
                      }
                   }
               }
           });
           
           // Render Probability Heatmap on the Board using the domain samples
           for (let r=0; r<M; r++) {
               let rKey = "R" + r;
               for (let c=0; c<N; c++) {
                   let cKey = "C" + c;
                   
                   // Skip if assigned
                   let assigned = false;
                   if (snap.assignment && (snap.assignment[rKey] !== undefined || snap.assignment[cKey] !== undefined)) {
                       assigned = true;
                   }
                   if (assigned) continue;
                   
                   let domR = domSnap[rKey];
                   let domC = domSnap[cKey];
                   
                   let sum = 0; let total = 0;
                   if (domR && domR.samples) {
                       sum += domR.samples.filter(s => s[c] === 1).length;
                       total += domR.samples.length;
                   }
                   if (domC && domC.samples) {
                       sum += domC.samples.filter(s => s[r] === 1).length;
                       total += domC.samples.length;
                   }
                   
                   if (total > 0) {
                       const p = sum / total;
                       if (p > 0) {
                           // Apply a blue color with opacity proportional to the probability
                           boardEl.children[r * N + c].style.background = `rgba(59, 130, 246, ${p * 0.6})`;
                       }
                   }
               }
           }
       }
    }

    async function solve() {
      const testName = document.getElementById('testSelect').value;
      const algoName = document.getElementById('algoSelect').value;
      const stats = document.getElementById('stats');
      const boardEl = document.getElementById('board');
      const btn = document.getElementById('solveBtn');
      
      stats.innerText = "서버 연산 중입니다...";
      stats.className = "";
      btn.disabled = true;
      
      // Clear board
      Array.from(boardEl.children).forEach(c => {
        c.classList.remove('filled');
        c.style.opacity = "";
      });
      
      try {
        const res = await fetch("/api/solve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ test: testName, algo: algoName })
        });
        const data = await res.json();
        
        if(data.error) {
          stats.innerText = "서버 에러: " + data.error;
          stats.className = "error";
          btn.disabled = false;
          return;
        }
        
        // Render inspector if domain tracking is present
        
        if(data.trace_history) {
            traceHistory = data.trace_history;
            document.getElementById('traceSlider').max = traceHistory.length - 1;
            document.getElementById('traceSlider').value = 0;
            document.getElementById('lblTotal').innerText = "Total " + (traceHistory.length - 1);
            initTraceBoard();
            renderTraceState(0);
        } else {
            traceHistory = [];
        }

        if(data.domain_details) {
            renderInspector(data);
        }
        
        // Handle Step-specific returns
        if(data.status === "STEP1_DONE") {
          stats.innerText = `[Step 1] 도메인 생성 완료 (전체 도메인 조합 후보 수: ${data.domains.toLocaleString()}개)`;
          stats.className = "success";
          btn.disabled = false;
          return;
        }
        
        if(data.status === "TIMEOUT") {
          stats.innerText = `[${algoName}] 타임아웃: ${data.msg} (소요시간: ${data.time.toFixed(8)}초)`;
          stats.className = "error";
          btn.disabled = false;
          return;
        }
        
        if(data.status === "NO_SOLUTION") {
          stats.innerText = `해답을 찾지 못했습니다! (소요시간: ${data.time.toFixed(8)}초)`;
          stats.className = "error";
          btn.disabled = false;
          return;
        }
        
        stats.innerText = `[${algoName}] 퍼즐 해결 성공! (소요시간: ${data.time.toFixed(8)}초) 보드 렌더링 중...`;
        stats.className = "success";
        
        const grid = data.board;
        const M = grid.length;
        const N = grid[0].length;
        
        for(let r=0; r<M; r++) {
          for(let c=0; c<N; c++) {
            if (grid[r][c] === 1) {
              const cellIdx = r * N + c;
              setTimeout(() => {
                const cellEl = boardEl.children[cellIdx];
                cellEl.classList.add("filled");
                cellEl.style.opacity = "1";
              }, (r * N + c) * 4);
            }
          }
        }
      } catch (err) {
        stats.innerText = "통신 에러: " + err;
        stats.className = "error";
      }
      
      btn.disabled = false;
    }
    
    init();
  </script>
</body>
</html>
"""

class UIRequestHandler(BaseHTTPRequestHandler):
    def _json_response(self, payload, status=HTTPStatus.OK):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _html_response(self, payload, status=HTTPStatus.OK):
        encoded = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path == "/":
            self._html_response(HTML)
            return
        elif self.path == "/api/puzzles":
            self._json_response(PUZZLES)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length else b"{}"
        data = json.loads(raw.decode("utf-8")) if raw else {}


        if self.path == "/api/solve":
            test_name = data.get("test", "Puzzle_01_7x7_Tree")
            algo_name = data.get("algo", "step4")
            
            do_trace = algo_name in ["step2", "step3", "step4"]
            
            import sys
            trace_history = []
            last_domains_str = ""
            
            def tracer(frame, event, arg):
                nonlocal last_domains_str
                # Only trace returns from the specific modules
                if event == "return":
                    co_name = frame.f_code.co_name
                    filename = frame.f_code.co_filename
                    if "step2_backtrack" in filename or "step3_revise" in filename or "step4_ac3" in filename:
                        locs = frame.f_locals
                        
                        assignment = {}
                        if "assignment" in locs and type(locs["assignment"]) is dict:
                            assignment = locs["assignment"].copy()
                            
                        # If inside backtracking, assignment is passed.
                        # IF inside ac3, csp.domains is mutating
                        csp = locs.get("csp")
                        dom_struct = None
                        dom_str = last_domains_str
                        
                        if csp and hasattr(csp, "domains"):
                            cur_dom_str = str({k: len(v) for k, v in csp.domains.items()})
                            if cur_dom_str != last_domains_str:
                                dom_str = cur_dom_str
                                dom_struct = {k: {"count": len(v), "samples": v[:10]} for k, v in csp.domains.items()}
                        
                        desc = f"{co_name} returned."
                        if "revise" in co_name:
                            desc = f"Revise {locs.get('r_var', '')} - {locs.get('c_var', '')}"
                        elif "backtracking_search" in co_name:
                            desc = f"Backtracking (배정된 변수 수: {len(assignment)})"
                            
                        snap = {"event": desc, "assignment": assignment}
                        if dom_struct is not None:
                            snap["domains"] = dom_struct
                        
                        if len(trace_history) == 0 or trace_history[-1]["event"] != desc or trace_history[-1]["assignment"] != assignment or last_domains_str != dom_str:
                            trace_history.append(snap)
                            last_domains_str = dom_str
                            
                return tracer

            if test_name not in PUZZLES:
                self._json_response({"error": "Unknown test"}, HTTPStatus.BAD_REQUEST)
                return
                
            hints = PUZZLES[test_name]
            
            start = time.perf_counter()
            if do_trace:
                sys.settrace(tracer)
            try:
                ans = solve_nonogram(hints["r"], hints["c"], algo=algo_name)
            except Exception as e:
                if do_trace: sys.settrace(None)
                self._json_response({"error": traceback.format_exc()})
                return
            if do_trace: sys.settrace(None)
            elapsed = time.perf_counter() - start
            
            if not ans or isinstance(ans, dict) is False:
                self._json_response({"status": "ERROR", "error": "Invalid return type"})
                return
                
            ans["time"] = elapsed
            if do_trace:
                ans["trace_history"] = trace_history

            # Format the output grid if solved
            if ans.get("status") == "SOLVED" and "assignment" in ans:
                M = len(hints["r"])
                grid = []
                for i in range(M):
                    grid.append(ans["assignment"].get(f"R{i}", []))
                ans["board"] = grid
                
            self._json_response(ans)
            return
            
        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format, *args):
        pass # 터미널 로그 숨김

def run_server():
    server = ThreadingHTTPServer(("127.0.0.1", 8080), UIRequestHandler)
    url = "http://127.0.0.1:8080"
    print(f"Nonogram CSP Solver UI running at {url}")
    print("Press Ctrl+C to stop the server.")

    # 자동 브라우저 오픈
    opener = threading.Timer(0.5, lambda: webbrowser.open(url))
    opener.daemon = True
    opener.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    run_server()
