/**
 * LLMO Check — Gratis GEO Audit: Floating Button + Popup Modal
 * Handles open/close modal + form submission → /api/audit
 */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    // Open modal — floating button
    var openBtn = document.getElementById('auditFloatingBtn');
    if (openBtn) {
      openBtn.addEventListener('click', openAuditModal);
    }

    // Open modal — any element with data-open-audit attribute
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('[data-open-audit]');
      if (trigger) {
        e.preventDefault();
        openAuditModal();
      }
    });

    // Close buttons
    document.addEventListener('click', function (e) {
      if (e.target.closest('.audit-modal-close')) {
        closeAuditModal();
      }
      if (e.target.classList.contains('audit-modal-overlay')) {
        closeAuditModal();
      }
    });

    // ESC to close
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeAuditModal();
    });

    // Form submit
    var form = document.getElementById('auditForm');
    if (form) {
      form.addEventListener('submit', handleAuditSubmit);
    }
  });

  // Expose globally for external triggers
  window.openAuditModal = openAuditModal;

  function openAuditModal() {
    var modal = document.getElementById('auditModal');
    var overlay = document.getElementById('auditOverlay');
    if (!modal || !overlay) return;

    overlay.classList.add('active');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Focus first input
    setTimeout(function () {
      var first = modal.querySelector('input[type="text"]');
      if (first) first.focus();
    }, 150);

    // Plausible
    if (window.plausible) {
      window.plausible('Audit Modal Opened');
    }
  }

  function closeAuditModal() {
    var modal = document.getElementById('auditModal');
    var overlay = document.getElementById('auditOverlay');
    if (!modal || !overlay) return;

    overlay.classList.remove('active');
    modal.classList.remove('active');
    document.body.style.overflow = '';

    // Reset form + message
    var form = document.getElementById('auditForm');
    if (form) form.reset();
    var msg = document.getElementById('auditMessage');
    if (msg) { msg.style.display = 'none'; msg.textContent = ''; }
  }

  async function handleAuditSubmit(e) {
    e.preventDefault();

    var form = e.target;
    var btn = document.getElementById('auditSubmitBtn');
    var btnText = btn.querySelector('.audit-btn-text');
    var btnIcon = btn.querySelector('.audit-btn-icon');
    var spinner = btn.querySelector('.audit-spinner');
    var messageEl = document.getElementById('auditMessage');

    var data = {
      brand: form.querySelector('#auditBrand').value.trim(),
      domain: form.querySelector('#auditDomain').value.trim(),
      branche: form.querySelector('#auditBranche').value.trim(),
      email: form.querySelector('#auditEmail').value.trim(),
    };

    var gdprChecked = form.querySelector('#auditGdpr').checked;

    if (!data.brand || !data.email) {
      showMsg(messageEl, 'Bitte fülle mindestens Brand und E-Mail aus.', 'error');
      return;
    }
    if (!gdprChecked) {
      showMsg(messageEl, 'Bitte akzeptiere die Datenschutzerklärung.', 'error');
      return;
    }

    // Loading
    btn.disabled = true;
    btnText.textContent = 'Wird gesendet…';
    if (btnIcon) btnIcon.style.display = 'none';
    spinner.style.display = 'inline-block';
    hideMsg(messageEl);

    try {
      var res = await fetch('https://prompt-monitoring.de/api/v1/audit/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand: data.brand,
          domain: data.domain,
          email: data.email,
          industry: data.branche,
          source: 'llmo-check.de'
        }),
      });
      var result = await res.json();

      if (res.ok) {
        showMsg(messageEl, result.message || 'Vielen Dank! Wir melden uns in Kürze.', 'success');
        form.reset();

        if (window.plausible) {
          window.plausible('Audit CTA Submitted', {
            props: { brand: data.brand, branche: data.branche || '–' },
          });
        }

        // Auto-close after 4s
        setTimeout(closeAuditModal, 4000);
      } else {
        showMsg(messageEl, result.error || 'Etwas ist schiefgelaufen.', 'error');
      }
    } catch (err) {
      console.error('Audit submit error:', err);
      showMsg(messageEl, 'Netzwerkfehler — bitte versuche es erneut.', 'error');
    } finally {
      btn.disabled = false;
      btnText.textContent = 'Sichtbarkeit checken';
      if (btnIcon) btnIcon.style.display = '';
      spinner.style.display = 'none';
    }
  }

  function showMsg(el, text, type) {
    if (!el) return;
    el.textContent = text;
    el.className = 'audit-message ' + type;
    el.style.display = 'block';
    if (type === 'error') setTimeout(function () { hideMsg(el); }, 6000);
  }

  function hideMsg(el) {
    if (!el) return;
    el.style.display = 'none';
    el.textContent = '';
  }
})();
