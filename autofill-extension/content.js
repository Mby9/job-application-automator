console.log("Smart Job Auto-Filler content script loaded.");

function getLabelFor(element) {
  let labelText = "";

  // 1. Explicit label via ID
  if (element.id) {
    const label = document.querySelector(`label[for="${element.id}"]`);
    if (label) labelText = label.innerText.trim();
  }

  // 2. aria-label (often highly accurate for screen readers)
  if (!labelText && element.getAttribute('aria-label')) {
    labelText = element.getAttribute('aria-label').trim();
  }

  // 2.5 aria-labelledby
  if (!labelText && element.getAttribute('aria-labelledby')) {
    const labelId = element.getAttribute('aria-labelledby');
    const labelEl = document.getElementById(labelId);
    if (labelEl) labelText = labelEl.innerText.trim();
  }

  // 3. Wrapping label tag
  if (!labelText) {
    const parentLabel = element.closest('label');
    if (parentLabel) {
      let clone = parentLabel.cloneNode(true);
      let inputs = clone.querySelectorAll('input, select, textarea');
      inputs.forEach(i => i.remove());
      labelText = clone.innerText.trim();
    }
  }

  // 4. Preceding sibling
  if (!labelText) {
    const prev = element.previousElementSibling;
    if (prev && ['LABEL', 'SPAN', 'DIV'].includes(prev.tagName)) {
      labelText = prev.innerText.trim();
    }
  }

  // 5. 'name' attribute
  if (!labelText && element.name && element.name.length > 1) {
    labelText = element.name.replace(/[-_]/g, ' ').trim();
  }

  // 6. 'placeholder' attribute as absolute last resort
  if (!labelText && element.placeholder) {
    let p = element.placeholder.trim();
    const lowerP = p.toLowerCase();
    // Filter out instructory placeholders
    if (!lowerP.startsWith("e.g.") && 
        !lowerP.startsWith("start typing") && 
        p.split(' ').length <= 4) {
      labelText = p;
    }
  }

  if (!labelText) return "Unknown Field";

  // Clean up formatting (remove colons, asterisks, newlines)
  labelText = labelText.replace(/[:*\n\r]/g, '').trim();
  
  // If still too long, it's likely a paragraph, not a label
  if (labelText.length > 50) return "Unknown Field";

  // Capitalize first letter for consistency
  return labelText.charAt(0).toUpperCase() + labelText.slice(1);
}

// Learning Mode: Save field on change
document.addEventListener('change', (e) => {
  const target = e.target;
  if (target.tagName === 'INPUT' || target.tagName === 'SELECT' || target.tagName === 'TEXTAREA') {
    if (target.type === 'file') return; // Skip file inputs for learning
    
    const label = getLabelFor(target);
    const value = target.value;
    
    if (label && label !== "Unknown Field" && value && value.length > 1) {
      console.log(`Learning: ${label} = ${value}`);
      chrome.runtime.sendMessage({
        type: "SAVE_FIELD",
        data: { label_text: label, field_value: value }
      });
    }
  }
});

// Fill Mode: Request semantic matching on load
async function autoFillForm() {
    const inputs = document.querySelectorAll('input, select, textarea');
    const labelsOnPage = Array.from(inputs).map(input => getLabelFor(input)).filter(l => l);

    if (labelsOnPage.length === 0) return;

    chrome.runtime.sendMessage({ 
        type: "MATCH_FIELDS", 
        data: { labels: labelsOnPage } 
    }, (response) => {
        if (response && response.success) {
            const mappings = response.data; // Key: current label, Value: field value
            
            inputs.forEach(input => {
                if (input.type === 'file') return; // Skip file inputs for autofill
                
                const label = getLabelFor(input);
                if (label && label !== "Unknown Field" && mappings[label] && !input.value) {
                    console.log(`Auto-filling (semantic match): ${label} with ${mappings[label]}`);
                    input.value = mappings[label];
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        }
    });
}

// Wait a bit for dynamic forms
setTimeout(autoFillForm, 2000);
