// ====================================
// Huffman Codes Table
// ====================================

function renderHuffmanCodesTable(codes, frequencies) {
  try {
    console.log('=== renderHuffmanCodesTable START ===');
    console.log('codes:', codes);
    console.log('frequencies:', frequencies);
    console.log('huffmanCodesTableDiv:', huffmanCodesTableDiv);
    
    // Validate element exists
    if (!huffmanCodesTableDiv) {
      console.error('ERROR: huffmanCodesTableDiv is null or undefined!');
      return;
    }
    
    // Validate inputs
    if (!codes) {
      console.warn('No codes provided');
      huffmanCodesTableDiv.innerHTML = '<p style="padding: 2rem; text-align: center; color: #9ca3af;">No hay códigos para mostrar</p>';
      return;
    }
    
    if (!frequencies) {
      console.warn('No frequencies provided');
      huffmanCodesTableDiv.innerHTML = '<p style="padding: 2rem; text-align: center; color: #9ca3af;">No hay frecuencias para mostrar</p>';
      return;
    }
    
    const codesKeys = Object.keys(codes);
    console.log('Number of codes:', codesKeys.length);
    
    if (codesKeys.length === 0) {
      huffmanCodesTableDiv.innerHTML = '<p style="padding: 2rem; text-align: center; color: #9ca3af;">La tabla está vacía</p>';
      return;
    }
    
    // Convert codes to array with frequencies
    const codesArray = [];
    for (const [byteStr, code] of Object.entries(codes)) {
      const byte = parseInt(byteStr);
      const freq = frequencies[byteStr] || frequencies[byte] || 0;
      codesArray.push({
        byte: byte,
        code: code,
        frequency: freq,
        length: code.length
      });
    }
    
    console.log('codesArray length:', codesArray.length);
    console.log('First 3 items:', codesArray.slice(0, 3));
    
    // Sort by frequency (descending)
    codesArray.sort((a, b) => b.frequency - a.frequency);
    
    // Take top 50
    const topCodes = codesArray.slice(0, 50);
    console.log('topCodes length:', topCodes.length);
    
    // Build table
    let html = '<table>';
    html += '<thead><tr>';
    html += '<th>Carácter</th>';
    html += '<th>Frecuencia</th>';
    html += '<th>Código Binario</th>';
    html += '<th>Longitud</th>';
    html += '</tr></thead>';
    html += '<tbody>';
    
    for (const item of topCodes) {
      let charDisplay;
      if (item.byte >= 32 && item.byte <= 126) {
        charDisplay = String.fromCharCode(item.byte);
        if (charDisplay === '<') charDisplay = '&lt;';
        else if (charDisplay === '>') charDisplay = '&gt;';
        else if (charDisplay === '&') charDisplay = '&amp;';
      } else {
        charDisplay = '0x' + item.byte.toString(16).toUpperCase().padStart(2, '0');
      }
      
      html += '<tr>';
      html += `<td class="char-col">${charDisplay}</td>`;
      html += `<td class="freq-col">${item.frequency}</td>`;
      html += `<td class="code-col">${item.code}</td>`;
      html += `<td class="length-col">${item.length}</td>`;
      html += '</tr>';
    }
    
    html += '</tbody></table>';
    
    console.log('Setting innerHTML, HTML length:', html.length);
    huffmanCodesTableDiv.innerHTML = html;
    console.log('=== renderHuffmanCodesTable END SUCCESS ===');
    
  } catch (error) {
    console.error('ERROR in renderHuffmanCodesTable:', error);
    console.error('Error stack:', error.stack);
    if (huffmanCodesTableDiv) {
      huffmanCodesTableDiv.innerHTML = `<p style="padding: 2rem; text-align: center; color: #ef4444;">Error: ${error.message}</p>`;
    }
  }
}
