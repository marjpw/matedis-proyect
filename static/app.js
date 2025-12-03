// ====================================
// DOM Elements
// ====================================
const fileInput = document.getElementById('fileInput');
const dropzone = document.getElementById('dropzone');
const analyzeBtn = document.getElementById('analyzeBtn');
const compressBtn = document.getElementById('compressBtn');
const decompressBtn = document.getElementById('decompressBtn');
const demoBtn = document.getElementById('demoBtn');
const statsPre = document.getElementById('stats');
const canvas = document.getElementById('treeCanvas');
const ctx = canvas.getContext('2d');
const freqCanvas = document.getElementById('freqCanvas');
const freqCtx = freqCanvas.getContext('2d');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressLabel = document.getElementById('progressLabel');
const compareDiv = document.getElementById('compare');
const notificationsContainer = document.getElementById('notifications');
const huffmanCodesTableDiv = document.getElementById('huffmanCodesTable');

// ====================================
// State
// ====================================
let file = null;
let currentTree = null;
let currentFrequencies = null;
let currentCodes = null;

// ====================================
// Utility Functions
// ====================================

function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };
  
  notification.innerHTML = `
    <span class="notification-icon">${icons[type] || icons.info}</span>
    <span class="notification-message">${message}</span>
  `;
  
  notificationsContainer.appendChild(notification);
  
  setTimeout(() => {
    notification.style.animation = 'slideOut 250ms cubic-bezier(0.4, 0, 0.2, 1)';
    setTimeout(() => notification.remove(), 250);
  }, 4000);
}

function showProgress(label = 'Procesando...') {
  progressContainer.classList.add('active');
  progressLabel.textContent = label;
  progressFill.style.width = '0%';
  
  // Simular progreso
  let progress = 0;
  const interval = setInterval(() => {
    progress += Math.random() * 15;
    if (progress > 90) progress = 90;
    progressFill.style.width = `${progress}%`;
  }, 100);
  
  return () => {
    clearInterval(interval);
    progressFill.style.width = '100%';
    setTimeout(() => {
      progressContainer.classList.remove('active');
      progressFill.style.width = '0%';
    }, 300);
  };
}

function hideProgress() {
  progressContainer.classList.remove('active');
  progressFill.style.width = '0%';
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function validateFile(f, maxSize = 750 * 1024 * 1024) {
  if (!f) {
    showNotification('Por favor selecciona un archivo', 'error');
    return false;
  }
  
  if (f.size > maxSize) {
    showNotification(`El archivo es demasiado grande. Máximo ${formatBytes(maxSize)}`, 'error');
    return false;
  }
  
  if (f.size === 0) {
    showNotification('El archivo está vacío', 'error');
    return false;
  }
  
  return true;
}

// ====================================
// Manejo de archivos
// ====================================

fileInput.addEventListener('change', e => {
  file = e.target.files[0];
  if (file) {
    statsPre.innerText = `📄 Archivo: ${file.name}\n💾 Tamaño: ${formatBytes(file.size)}`;
    showNotification(`Archivo cargado: ${file.name}`, 'success');
  }
});

dropzone.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('dragover', e => {
  e.preventDefault();
  dropzone.classList.add('drag-over');
});

dropzone.addEventListener('dragleave', e => {
  e.preventDefault();
  dropzone.classList.remove('drag-over');
});

dropzone.addEventListener('drop', e => {
  e.preventDefault();
  dropzone.classList.remove('drag-over');
  file = e.dataTransfer.files[0];
  if (file) {
    statsPre.innerText = `📄 Archivo: ${file.name}\n💾 Tamaño: ${formatBytes(file.size)}`;
    showNotification(`Archivo cargado: ${file.name}`, 'success');
  }
});

// ====================================
// API
// ====================================

analyzeBtn.addEventListener('click', async () => {
  if (!validateFile(file)) return;
  
  const fd = new FormData();
  fd.append('file', file);
  
  const stopProgress = showProgress('Analizando archivo...');
  statsPre.innerText = '⏳ Analizando...';
  
  try {
    const res = await fetch('/api/analyze', { method: 'POST', body: fd });
    const j = await res.json();
    
    stopProgress();
    
    if (j.error) {
      showNotification(`Error: ${j.error}`, 'error');
      statsPre.innerText = `❌ Error: ${j.error}`;
      return;
    }
    
    const compressionRatio = ((1 - (j.entropy / 8)) * 100).toFixed(2);
    let efficiencyText = '';
    if (j.efficiency >= 98) {
      efficiencyText = '⭐⭐⭐⭐⭐ Excelente';
    } else if (j.efficiency >= 95) {
      efficiencyText = '⭐⭐⭐⭐ Muy buena';
    } else if (j.efficiency >= 90) {
      efficiencyText = '⭐⭐⭐ Buena';
    } else {
      efficiencyText = '⭐⭐ Aceptable';
    }

    statsPre.innerText = `📊 ANÁLISIS COMPLETADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Archivo: ${file.name}
💾 Tamaño: ${formatBytes(j.original_size)}
🔤 Símbolos únicos: ${Object.keys(j.frequencies).length}
📈 Entropía (H): ${j.entropy.toFixed(4)} bits/símbolo
📏 Longitud promedio (L): ${j.avg_code_length.toFixed(4)} bits/símbolo
⚡ Eficiencia: ${j.efficiency.toFixed(2)}%
📉 Compresión teórica: ~${compressionRatio}%`;
    
    currentTree = j.tree;
    currentFrequencies = j.frequencies;
    currentCodes = j.codes;
    
    console.log('=== About to render Huffman codes table ===');
    console.log('j.codes:', j.codes);
    console.log('j.frequencies:', j.frequencies);
    console.log('Number of codes:', Object.keys(j.codes || {}).length);
    console.log('Number of frequencies:', Object.keys(j.frequencies || {}).length);
    
    drawTree(j.tree);
    drawFrequencyChart(j.frequencies);
    renderHuffmanCodesTable(j.codes, j.frequencies);
    showNotification('Análisis completado exitosamente', 'success');
  } catch (error) {
    stopProgress();
    showNotification(`Error de red: ${error.message}`, 'error');
    statsPre.innerText = `❌ Error de red: ${error.message}`;
  }
});

compressBtn.addEventListener('click', async () => {
  if (!validateFile(file)) return;
  
  const fd = new FormData();
  fd.append('file', file);
  
  const stopProgress = showProgress('Comprimiendo archivo...');
  statsPre.innerText = '⚡ Comprimiendo...';
  
  try {
    const r = await fetch('/api/compress', { method: 'POST', body: fd });
    
    stopProgress();
    
    if (!r.ok) {
      const j = await r.json();
      showNotification(`Error: ${j.error || 'Error desconocido'}`, 'error');
      statsPre.innerText = `❌ Error: ${j.error || 'Error desconocido'}`;
      return;
    }
    
    const blob = await r.blob();
    
    const header = r.headers.get('X-Comp-Stats');
    if (header) {
      try {
        const s = JSON.parse(header);
        const ratio = ((1 - (s.compressed_size / s.original_size)) * 100).toFixed(2);
        const gzipRatio = ((1 - (s.gzip_size / s.original_size)) * 100).toFixed(2);
        
        compareDiv.innerHTML = `
          <div style="line-height: 2;">
            <strong>📊 COMPARACIÓN DE COMPRESIÓN</strong><br>
            Original: <strong>${formatBytes(s.original_size)}</strong> | 
            Huffman: <strong>${formatBytes(s.compressed_size)}</strong> (${ratio > 0 ? '-' : '+'}${Math.abs(ratio)}%) | 
            gzip: <strong>${formatBytes(s.gzip_size)}</strong> (${gzipRatio > 0 ? '-' : '+'}${Math.abs(gzipRatio)}%)<br>
            ⏱️ Tiempo: <strong>${s.duration_s.toFixed(3)} s</strong>
          </div>
        `;
        
        statsPre.innerText = `✅ COMPRESIÓN COMPLETADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Original: ${formatBytes(s.original_size)}
📦 Comprimido: ${formatBytes(s.compressed_size)}
📊 Ratio: ${ratio > 0 ? '-' : '+'}${Math.abs(ratio)}%
⏱️ Tiempo: ${s.duration_s.toFixed(3)} s`;
      } catch (e) {
        console.error('Error parsing stats:', e);
      }
    }
    
    // Descargar archivo
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name + '.huff';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    
    showNotification('Archivo comprimido y descargado exitosamente', 'success');
  } catch (error) {
    stopProgress();
    showNotification(`Error de red: ${error.message}`, 'error');
    statsPre.innerText = `❌ Error de red: ${error.message}`;
  }
});

decompressBtn.addEventListener('click', async () => {
  if (!validateFile(file)) return;
  
  if (!file.name.endsWith('.huff')) {
    showNotification('Por favor selecciona un archivo .huff', 'warning');
  }
  
  const fd = new FormData();
  fd.append('file', file);
  
  const stopProgress = showProgress('Descomprimiendo archivo...');
  statsPre.innerText = '🔓 Descomprimiendo...';
  
  try {
    const r = await fetch('/api/decompress', { method: 'POST', body: fd });
    
    stopProgress();
    
    if (!r.ok) {
      const j = await r.json();
      showNotification(`Error: ${j.error || 'Error desconocido'}`, 'error');
      statsPre.innerText = `❌ Error: ${j.error || 'Error desconocido'}`;
      return;
    }
    
    const blob = await r.blob();
    
    // Descargar archivo
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name.replace('.huff', '_decompressed');
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    
    statsPre.innerText = `✅ DESCOMPRESIÓN COMPLETADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Archivo original recuperado
💾 Tamaño: ${formatBytes(blob.size)}`;
    
    showNotification('Archivo descomprimido exitosamente', 'success');
  } catch (error) {
    stopProgress();
    showNotification(`Error de red: ${error.message}`, 'error');
    statsPre.innerText = `❌ Error de red: ${error.message}`;
  }
});

demoBtn.addEventListener('click', async () => {
  const sample = new TextEncoder().encode('ABRACADABRA! 🎩✨');
  const blob = new Blob([sample], { type: 'application/octet-stream' });
  file = new File([blob], 'demo.txt');
  
  statsPre.innerText = `📄 Archivo: demo.txt\n💾 Tamaño: ${formatBytes(sample.length)}\n📝 Contenido: ABRACADABRA! 🎩✨`;
  showNotification('Archivo de demostración cargado', 'info');
});

// ====================================
// Observar arbol
// ====================================

function drawTree(tree) {
  // Set canvas size
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  if (!tree) {
    ctx.fillStyle = '#6b7280';
    ctx.font = '16px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('El árbol de Huffman aparecerá aquí', canvas.width / 2, canvas.height / 2);
    return;
  }
  
  // Calculate tree depth for better spacing
  function getDepth(node) {
    if (!node) return 0;
    return 1 + Math.max(getDepth(node.left), getDepth(node.right));
  }
  
  const maxDepth = getDepth(tree);
  const verticalSpacing = Math.min(80, (canvas.height - 60) / maxDepth);
  
  function traverse(node, depth, xMin, xMax, parentX = null, parentY = null) {
    if (!node) return;
    
    const x = (xMin + xMax) / 2;
    const y = 30 + depth * verticalSpacing;
    
    if (parentX !== null && parentY !== null) {
      ctx.strokeStyle = '#374151';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(parentX, parentY + 20);
      ctx.lineTo(x, y - 20);
      ctx.stroke();
    }
    
    const isLeaf = node.symbol !== null;
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, 22);
    
    if (isLeaf) {
      gradient.addColorStop(0, '#8b5cf6');
      gradient.addColorStop(1, '#6d28d9');
    } else {
      gradient.addColorStop(0, '#3b82f6');
      gradient.addColorStop(1, '#1e40af');
    }
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, 20, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.strokeStyle = isLeaf ? '#a78bfa' : '#60a5fa';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px Inter, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    let label = '';
    if (node.symbol !== null) {
      const char = node.symbol >= 32 && node.symbol <= 126 
        ? String.fromCharCode(node.symbol) 
        : `0x${node.symbol.toString(16).toUpperCase()}`;
      label = `${char}`;
    } else {
      label = `${node.freq}`;
    }
    
    ctx.fillText(label, x, y);
    
    if (node.symbol !== null) {
      ctx.font = '10px Inter';
      ctx.fillStyle = '#9ca3af';
      ctx.fillText(`(${node.freq})`, x, y + 32);
    }
    
    if (node.left) {
      traverse(node.left, depth + 1, xMin, x, x, y);
    }
    if (node.right) {
      traverse(node.right, depth + 1, x, xMax, x, y);
    }
  }
  
  traverse(tree, 0, 40, canvas.width - 40);
}

// ====================================
// Frequency Chart Visualization
// ====================================

function drawFrequencyChart(frequencies) {
  if (!frequencies || Object.keys(frequencies).length === 0) {
    freqCanvas.width = freqCanvas.offsetWidth;
    freqCanvas.height = freqCanvas.offsetHeight;
    freqCtx.clearRect(0, 0, freqCanvas.width, freqCanvas.height);
    freqCtx.fillStyle = '#6b7280';
    freqCtx.font = '16px Inter, sans-serif';
    freqCtx.textAlign = 'center';
    freqCtx.fillText('El gráfico de frecuencias aparecerá aquí', freqCanvas.width / 2, freqCanvas.height / 2);
    return;
  }

  freqCanvas.width = freqCanvas.offsetWidth;
  freqCanvas.height = freqCanvas.offsetHeight;
  
  freqCtx.clearRect(0, 0, freqCanvas.width, freqCanvas.height);
  
  const sortedFreqs = Object.entries(frequencies)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 50);
  
  if (sortedFreqs.length === 0) return;
  
  const maxFreq = sortedFreqs[0][1];
  const padding = { top: 40, right: 40, bottom: 80, left: 60 };
  const chartWidth = freqCanvas.width - padding.left - padding.right;
  const chartHeight = freqCanvas.height - padding.top - padding.bottom;
  const barWidth = chartWidth / sortedFreqs.length;
  
  // Dibujar titulo
  freqCtx.fillStyle = '#e5e7eb';
  freqCtx.font = 'bold 18px Inter';
  freqCtx.textAlign = 'center';
  freqCtx.fillText('Distribución de Frecuencias (Top 50)', freqCanvas.width / 2, 25);
  
  // Dibujar ejes
  freqCtx.strokeStyle = '#374151';
  freqCtx.lineWidth = 2;
  freqCtx.beginPath();
  freqCtx.moveTo(padding.left, padding.top);
  freqCtx.lineTo(padding.left, freqCanvas.height - padding.bottom);
  freqCtx.lineTo(freqCanvas.width - padding.right, freqCanvas.height - padding.bottom);
  freqCtx.stroke();
  
  // Dibujar barras
  sortedFreqs.forEach(([byte, freq], index) => {
    const barHeight = (freq / maxFreq) * chartHeight;
    const x = padding.left + index * barWidth;
    const y = freqCanvas.height - padding.bottom - barHeight;
    
    // Crear gradiente para la barra
    const gradient = freqCtx.createLinearGradient(x, y, x, freqCanvas.height - padding.bottom);
    const hue = (index / sortedFreqs.length) * 280 + 200; // Efecto arcoíris
    gradient.addColorStop(0, `hsl(${hue}, 70%, 60%)`);
    gradient.addColorStop(1, `hsl(${hue}, 70%, 40%)`);
    
    // Dibujar barra
    freqCtx.fillStyle = gradient;
    freqCtx.fillRect(x + 2, y, barWidth - 4, barHeight);
    
    // Dibujar borde de la barra
    freqCtx.strokeStyle = `hsl(${hue}, 70%, 70%)`;
    freqCtx.lineWidth = 1;
    freqCtx.strokeRect(x + 2, y, barWidth - 4, barHeight);
    
    // Etiqueta (caracter o hex)
    const char = parseInt(byte) >= 32 && parseInt(byte) <= 126 
      ? String.fromCharCode(parseInt(byte))
      : `${parseInt(byte).toString(16)}`;
    
    freqCtx.save();
    freqCtx.translate(x + barWidth / 2, freqCanvas.height - padding.bottom + 10);
    freqCtx.rotate(-Math.PI / 4);
    freqCtx.fillStyle = '#9ca3af';
    freqCtx.font = '11px Courier New, monospace';
    freqCtx.textAlign = 'right';
    freqCtx.fillText(char, 0, 0);
    freqCtx.restore();
    
    // Mostrar valor de frecuencia al pasar el mouse (siempre mostrar para los primeros 10)
    if (index < 10) {
      freqCtx.fillStyle = '#e5e7eb';
      freqCtx.font = 'bold 11px Inter';
      freqCtx.textAlign = 'center';
      freqCtx.fillText(freq, x + barWidth / 2, y - 5);
    }
  });
  
  // Etiquetas del eje Y
  freqCtx.fillStyle = '#9ca3af';
  freqCtx.font = '12px Inter';
  freqCtx.textAlign = 'right';
  for (let i = 0; i <= 5; i++) {
    const value = Math.round((maxFreq / 5) * i);
    const y = freqCanvas.height - padding.bottom - (chartHeight / 5) * i;
    freqCtx.fillText(value, padding.left - 10, y + 4);
    
    // Linea de la cuadricula
    freqCtx.strokeStyle = '#374151';
    freqCtx.lineWidth = 1;
    freqCtx.setLineDash([2, 4]);
    freqCtx.beginPath();
    freqCtx.moveTo(padding.left, y);
    freqCtx.lineTo(freqCanvas.width - padding.right, y);
    freqCtx.stroke();
    freqCtx.setLineDash([]);
  }
  
  // Etiqueta del eje Y
  freqCtx.save();
  freqCtx.translate(20, freqCanvas.height / 2);
  freqCtx.rotate(-Math.PI / 2);
  freqCtx.fillStyle = '#9ca3af';
  freqCtx.font = '14px Inter';
  freqCtx.textAlign = 'center';
  freqCtx.fillText('Frecuencia', 0, 0);
  freqCtx.restore();
  
  // Etiqueta del eje X
  freqCtx.fillStyle = '#9ca3af';
  freqCtx.font = '14px Inter';
  freqCtx.textAlign = 'center';
  freqCtx.fillText('Caracteres (ordenados por frecuencia)', freqCanvas.width / 2, freqCanvas.height - 10);
}


// ====================================
// Tabla de Códigos de Huffman
// ====================================

function renderHuffmanCodesTable(codes, frequencies) {
  try {
    console.log('=== renderHuffmanCodesTable START ===');
    console.log('Codes object:', codes);
    console.log('Frequencies object:', frequencies);
    
    if (!huffmanCodesTableDiv) {
      console.error('FATAL: Element not found!');
      return;
    }
    
    if (!codes || !frequencies) {
      console.warn('Missing data');
      huffmanCodesTableDiv.innerHTML = '<div style="padding:2rem;text-align:center;color:#999;">No hay datos</div>';
      return;
    }
    
    // Construir array de datos
    const items = [];
    for (let key in codes) {
      const byteVal = parseInt(key);
      const freq = frequencies[key] || frequencies[byteVal] || 0;
      items.push({
        byte: byteVal,
        code: codes[key],
        freq: freq,
        len: codes[key].length
      });
    }
    
    console.log(`Total items: ${items.length}`);
    
    // Ordenar
    items.sort((a,b) => b.freq - a.freq);
    const top = items.slice(0, 50);
    
    // Construir HTML
    let html = '<table><thead><tr><th>Char</th><th>Freq</th><th>Code</th><th>Len</th></tr></thead><tbody>';
    
    for (let i = 0; i < top.length; i++) {
      const it = top[i];
      let ch = (it.byte >= 32 && it.byte <= 126) ? String.fromCharCode(it.byte) : ('0x'+it.byte.toString(16).toUpperCase());
      if (ch === '<') ch = '&lt;';
      if (ch === '>') ch = '&gt;';
      if (ch === '&') ch = '&amp;';
      html += `<tr><td class="char-col">${ch}</td><td class="freq-col">${it.freq}</td><td class="code-col">${it.code}</td><td class="length-col">${it.len}</td></tr>`;
    }
    
    html += '</tbody></table>';
    
    console.log(`HTML length: ${html.length}`);
    huffmanCodesTableDiv.innerHTML = html;
    console.log('===  DONE ===');
  } catch (e) {
    console.error('ERROR:', e);
    if (huffmanCodesTableDiv) huffmanCodesTableDiv.innerHTML = '<div style="padding:2rem;color:red;">Error: ' + e.message + '</div>';
  }
}


// ====================================
// Inicialización
// ====================================

// Verificar si huffmanCodesTableDiv se encuentra
console.log('Inicializando app.js');
console.log('Elemento huffmanCodesTableDiv:', huffmanCodesTableDiv);

if (!huffmanCodesTableDiv) {
  console.error('ERROR: huffmanCodesTable div not found in DOM!');
} else {
  console.log('SUCCESS: huffmanCodesTable div found');
}

// Agregar animación CSS para slideOut
const style = document.createElement('style');
style.textContent = `
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(400px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Configuración inicial del lienzo
drawTree(null);
drawFrequencyChart(null);

// Redimensionar el lienzo al cambiar el tamaño de la ventana
window.addEventListener('resize', () => {
  if (currentTree) {
    drawTree(currentTree);
  } else {
    drawTree(null);
  }
  
  if (currentFrequencies) {
    drawFrequencyChart(currentFrequencies);
  } else {
    drawFrequencyChart(null);
  }
});

