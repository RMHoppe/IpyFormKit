if (!window.Popper) {
  const script = document.createElement('script');
  script.src = 'https://unpkg.com/@popperjs/core@2';
  script.onload = () => console.log("✅ Popper.js loaded");
  document.head.appendChild(script);
} else {
  console.log("✅ Popper.js already loaded");
}

function waitForPopper(callback) {
  if (window.Popper && typeof Popper.createPopper === 'function') {
    callback();
  } else {
    setTimeout(() => waitForPopper(callback), 50);
  }
}

function measureTextWidth(text, referenceElement) {
  const measuringSpan = document.createElement('span');
  measuringSpan.style.position = 'absolute';
  measuringSpan.style.visibility = 'hidden';
  measuringSpan.style.whiteSpace = 'nowrap';

  // Copy font styles from the reference tooltip
  const computedStyle = window.getComputedStyle(referenceElement);
  measuringSpan.style.font = computedStyle.font;
  measuringSpan.style.fontSize = computedStyle.fontSize;
  measuringSpan.style.fontFamily = computedStyle.fontFamily;
  measuringSpan.style.fontWeight = computedStyle.fontWeight;

  measuringSpan.textContent = text;
  document.body.appendChild(measuringSpan);
  const width = measuringSpan.offsetWidth;
  document.body.removeChild(measuringSpan);
  return width;
}

waitForPopper(() => {
  document.querySelectorAll('.ifk-tooltip').forEach((tooltip) => {
    const tipText = tooltip.querySelector('.ifk-tooltip-text');
    if (!tipText) return;

    let popperInstance = null;

    function show() {
      tipText.style.display = 'block';
      tipText.style.visibility = 'hidden'; // Temporarily hidden to measure

      // Reset previous width before measurement
      tipText.style.width = 'auto';

      // Calculate proper width
      const container = tooltip.closest('.ifk-form') || document.body;
      const containerWidth = container.clientWidth - 14;
      const idealWidth = measureTextWidth(tipText.textContent, tipText);
      const finalWidth = Math.min(idealWidth, containerWidth);
      console.log(finalWidth)

      tipText.style.width = finalWidth + 'px';

      // Create or recreate Popper instance
      if (popperInstance) {
        popperInstance.destroy();
      }

      popperInstance = Popper.createPopper(tooltip, tipText, {
        placement: 'top-end',
        modifiers: [
          {
            name: 'offset',
            options: { offset: [0, 8] },
          },
          {
            name: 'preventOverflow',
            options: {
              boundary: container,
              padding: 4
            },
          },
          {
            name: 'flip',
            options: {
              fallbackPlacements: ['bottom', 'left', 'right'],
            },
          }
        ],
      });

      tipText.style.visibility = 'visible';
    }

    function hide() {
      tipText.style.display = 'none';
      if (popperInstance) {
        popperInstance.destroy();
        popperInstance = null;
      }
    }

    tooltip.addEventListener('mouseenter', show);
    tooltip.addEventListener('mouseleave', hide);
  });
});