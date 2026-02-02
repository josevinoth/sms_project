// dashboard_extras.js
// Initializes flatpickr on #from-date and #to-date and handles Export button using html2pdf.
(function(){
  // safe init for flatpickr
  try{
    if(typeof flatpickr !== 'undefined'){
      const opts = { dateFormat: 'Y-m-d', allowInput: true, altInput: false };
      if(document.getElementById('from-date')) flatpickr('#from-date', opts);
      if(document.getElementById('to-date')) flatpickr('#to-date', opts);
    }
  }catch(e){ console.warn('flatpickr init failed', e); }

  // Export to PDF using html2pdf
  try{
    const exportBtn = document.getElementById('export-pdf');
    if(exportBtn){
      exportBtn.addEventListener('click', function(){
        const el = document.querySelector('.dashboard-root') || document.body;
        if(typeof html2pdf === 'undefined'){
          alert('Export library not loaded.');
          return;
        }
        const opt = {
          margin:       8,
          filename:     'warehouse-dashboard.pdf',
          image:        { type: 'jpeg', quality: 0.98 },
          html2canvas:  { scale: 1.4, useCORS: true },
          jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };
        // small visual feedback
        exportBtn.disabled = true;
        exportBtn.innerText = 'Exporting...';
        setTimeout(()=>{
          html2pdf().from(el).set(opt).save().then(()=>{
            exportBtn.disabled = false;
            exportBtn.innerText = 'Export';
          }).catch(err=>{
            console.error(err);
            exportBtn.disabled = false;
            exportBtn.innerText = 'Export';
            alert('Export failed: see console');
          });
        }, 120);
      });
    }
  }catch(e){ console.warn('Export init failed', e); }

  // small utility: apply Chart.js default tweaks if Chart exists
  try{
    if(window.Chart){
      // reduce global animation and prefer responsive but not fixed aspect
      if(Chart.defaults && Chart.defaults.font){
        Chart.defaults.font.family = "Inter, Arial, sans-serif";
      }
      if(Chart.defaults && Chart.defaults.plugins && Chart.defaults.plugins.legend){
        Chart.defaults.plugins.legend.labels.boxWidth = 10;
      }
      // register datalabels plugin if available
      try{ if(window.Chart && window.Chart.register && typeof ChartDataLabels !== 'undefined'){ Chart.register(ChartDataLabels); } }catch(e){ console.warn('ChartDataLabels register failed', e); }
    }
  }catch(e){ console.warn('Chart defaults tweak failed', e); }
})();

// New: reveal dashboard and animate charts + counters when visible
(function(){
  try{
    const root = document.querySelector('.dashboard-root');
    if(!root) return;

    // count-up animation for numeric KPI elements
    function parseNumber(text){
      if(!text) return 0;
      // remove non-numeric except dot
      const cleaned = String(text).replace(/[^0-9\.\-]/g, '') || '0';
      return parseFloat(cleaned);
    }
    function formatNumber(val, origText){
      // preserve formatting (if orig contains comma), but keep simple thousands separator
      if(isNaN(val)) return origText;
      if(Math.abs(val) >= 1000) return Math.round(val).toLocaleString();
      return (Math.round(val*100)/100).toString();
    }
    function animateCount(el, duration=900){
      const start = 0;
      const end = parseNumber(el.textContent);
      if(isNaN(end)) return;
      const startTime = performance.now();
      function frame(now){
        const t = Math.min(1, (now - startTime)/duration);
        const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic
        const cur = start + (end - start) * eased;
        el.textContent = formatNumber(cur, el.textContent);
        if(t < 1) requestAnimationFrame(frame);
        else el.textContent = formatNumber(end, el.textContent);
      }
      requestAnimationFrame(frame);
    }

    // animate existing Chart.js charts by updating options and calling update()
    function animateCharts(){
      if(!window.Chart) return;
      const configs = [
        { id: 'spacePie', opts: { animation: { duration: 1100, easing: 'easeOutBack' } } },
        { id: 'areaVolumeDonut', opts: { animation: { duration: 1100, easing: 'easeOutBack' } } },
        { id: 'nestedDonut', opts: { animation: { duration: 1100, easing: 'easeOutBack' } } },
        { id: 'customerRevenueBar', opts: { animation: { duration: 1200, easing: 'easeOutQuart' } } }
      ];
      configs.forEach(c => {
        try{
          let chart = null;
          try{ chart = Chart.getChart(c.id); }catch(e){}
          if(!chart){ const el = document.getElementById(c.id); if(el){ try{ chart = Chart.getChart(el) }catch(e){} } }
          if(chart){
            chart.options = chart.options || {};
            chart.options.animation = c.opts.animation;
            if(chart.config && chart.config.options) chart.config.options.animation = c.opts.animation;
            // reset chart (if supported) so the animation plays from scratch
            try{ if(typeof chart.reset === 'function') chart.reset(); }catch(e){}
            chart.update();
          }
        }catch(e){ console.warn('chart animate error', c.id, e); }
      });
    }

    // Use IntersectionObserver to reveal only once
    const observer = new IntersectionObserver((entries, obs)=>{
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          root.classList.add('revealed');
          // animate metric counts
          const elems = root.querySelectorAll('.metric-value');
          elems.forEach(el=> animateCount(el, 900));
          // Recreate charts (preferred) so animations play cleanly. If createDashboardCharts isn't available yet, poll briefly.
          const runCreateCharts = ()=>{
            try{
              if(typeof window.createDashboardCharts === 'function'){
                window.createDashboardCharts();
              } else if(typeof window.createDashboardCharts === 'undefined'){
                // poll for up to 1 second
                let attempts = 0;
                const t = setInterval(()=>{
                  attempts++;
                  if(typeof window.createDashboardCharts === 'function'){ window.createDashboardCharts(); clearInterval(t); }
                  if(attempts>10) clearInterval(t);
                }, 100);
              }
            }catch(e){ console.warn('failed to create charts on reveal', e); }
          };
          setTimeout(runCreateCharts, 250);

          obs.unobserve(root);
        }
      });
    }, { threshold: 0.12 });

    // start observing
    observer.observe(root);

    // Helper to poll and call createDashboardCharts when it becomes available
    function tryCreateCharts(maxAttempts = 15, interval = 200){
      let attempts = 0;
      const t = setInterval(()=>{
        attempts++;
        if(typeof window.createDashboardCharts === 'function'){
          try{ window.createDashboardCharts(); console.log('createDashboardCharts: invoked by tryCreateCharts'); }catch(e){ console.warn('createDashboardCharts threw', e); }
          clearInterval(t);
        }
        if(attempts >= maxAttempts) clearInterval(t);
      }, interval);
      return t;
    }

    // If the dashboard is already visible on load (no scroll), create charts immediately or poll for the function
    try{
      if(root.getBoundingClientRect().top < window.innerHeight){
        tryCreateCharts(10,150);
      }
    }catch(e){ /* ignore */ }

    // Also try on window load in case template-defined function appears after this script
    window.addEventListener('load', ()=>{ tryCreateCharts(12,150); });

    // fallback: try after short delays to cover race conditions
    setTimeout(()=> tryCreateCharts(8,200), 300);
    setTimeout(()=> tryCreateCharts(6,300), 900);

  }catch(err){ console.warn('dashboard reveal init failed', err); }
})();
