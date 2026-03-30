/* ── State ────────────────────────────────────────────── */
const sessionId = crypto.randomUUID();
let chatHistory    = [];
let pendingSlot    = null;   // { id, date, time, dentistName }
let pendingService = null;   // { id, name }

/* ── DOM refs ─────────────────────────────────────────── */
const messagesEl = () => document.getElementById('messages');
const inputEl    = () => document.getElementById('userInput');

/* ── Bootstrap ────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  loadServices();
  renderWelcome();

  inputEl().addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  // Auto-grow textarea
  inputEl().addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  });
});

/* ── Load services sidebar ────────────────────────────── */
async function loadServices() {
  try {
    const res  = await fetch('/api/services');
    const data = await res.json();
    const el   = document.getElementById('serviceList');
    el.innerHTML = data.map(s => `
      <div class="service-card" onclick="quickAction('Tell me about ${s.name} — price, duration and when I need it')">
        <div class="service-card-name">${s.name}</div>
        <div class="service-card-meta">
          <span class="service-card-price">₹${s.price.toLocaleString()}</span>
          &nbsp;·&nbsp;${s.duration_minutes} min
        </div>
      </div>
    `).join('');
  } catch {
    document.getElementById('serviceList').innerHTML =
      '<div style="font-size:12px;color:#94a3b8;padding:4px">Could not load services</div>';
  }
}

/* ── Welcome message ──────────────────────────────────── */
function renderWelcome() {
  addBotHtml(`
    <div class="message-content">
      👋 Hello! I'm <strong>Denta</strong>, your AI dental assistant at <strong>Bright Smile Dental Clinic</strong>!
      <br><br>
      I can help you:<br>
      &nbsp;📅 Book an appointment<br>
      &nbsp;💡 Recommend the right service<br>
      &nbsp;🦷 Answer dental questions<br>
      &nbsp;🔍 Look up your bookings
      <br><br>
      How can I assist you today? 😊
    </div>
  `);
}

/* ── Send message ─────────────────────────────────────── */
async function sendMessage() {
  const text = inputEl().value.trim();
  if (!text) return;

  inputEl().value = '';
  inputEl().style.height = 'auto';
  addUserMessage(text);
  chatHistory.push({ role: 'user', content: text });

  showTyping();
  document.getElementById('sendBtn').disabled = true;

  try {
    const res  = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
        history: chatHistory.slice(-14),
      }),
    });

    const data = await res.json();
    hideTyping();
    document.getElementById('sendBtn').disabled = false;

    if (data.message) {
      addBotMessage(data.message);
      chatHistory.push({ role: 'assistant', content: data.message });
    }

    // Render slot picker if AI triggered it
    if (data.extra_data?.type === 'availability') {
      renderSlotPicker(data.extra_data);
    }

  } catch (err) {
    hideTyping();
    document.getElementById('sendBtn').disabled = false;
    addBotMessage('⚠️ Connection error. Please make sure the server and Ollama are running.');
  }
}

/* ── Quick action ─────────────────────────────────────── */
function quickAction(text) {
  inputEl().value = text;
  sendMessage();
}

/* ── Render a user bubble ─────────────────────────────── */
function addUserMessage(text) {
  const div = document.createElement('div');
  div.className = 'message user';
  div.innerHTML = `
    <div class="message-bubble">
      <div class="message-content">${escHtml(text)}</div>
    </div>`;
  messagesEl().appendChild(div);
  scrollBottom();
}

/* ── Render a bot bubble (text, supports **bold** & newlines) */
function addBotMessage(text) {
  const formatted = escHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
  addBotHtml(`<div class="message-content">${formatted}</div>`);
}

/* ── Render raw HTML inside a bot bubble ─────────────── */
function addBotHtml(innerHtml) {
  const div = document.createElement('div');
  div.className = 'message assistant';
  div.innerHTML = `
    <div class="message-bubble">
      <div class="bot-icon">🦷</div>
      ${innerHtml}
    </div>`;
  messagesEl().appendChild(div);
  scrollBottom();
}

/* ── Slot picker ──────────────────────────────────────── */
function renderSlotPicker(data) {
  pendingService = { id: data.service_id, name: data.service_name };

  // Group by date
  const byDate = {};
  data.slots.forEach(s => {
    if (!byDate[s.date]) byDate[s.date] = [];
    byDate[s.date].push(s);
  });

  if (Object.keys(byDate).length === 0) {
    addBotMessage("😔 Sorry, no available slots right now. Please call us at +91 98765 43210 to book manually.");
    return;
  }

  const datesHtml = Object.entries(byDate).slice(0, 6).map(([date, slots]) => `
    <div class="date-group">
      <div class="date-label">${fmtDate(date)}</div>
      <div class="time-slots">
        ${slots.slice(0, 6).map(s => `
          <button class="slot-btn"
            onclick="selectSlot(${s.id}, '${date}', '${s.time}', '${escHtml(s.dentist_name)}')">
            ${s.time}
            <small>${s.dentist_name.replace('Dr. ', 'Dr.')}</small>
          </button>`).join('')}
      </div>
    </div>
  `).join('');

  addBotHtml(`
    <div class="slot-picker-card">
      <h3>📅 Available Slots — ${escHtml(data.service_name)}</h3>
      <div class="slots-container">${datesHtml}</div>
    </div>
  `);
}

/* ── User selects a slot ──────────────────────────────── */
function selectSlot(id, date, time, dentistName) {
  pendingSlot = { id, date, time, dentistName };
  renderBookingForm();
}

/* ── Booking form ─────────────────────────────────────── */
function renderBookingForm() {
  const formId = 'bkForm_' + Date.now();
  addBotHtml(`
    <div class="booking-form-card" id="${formId}">
      <h3>✅ ${fmtDate(pendingSlot.date)} at ${pendingSlot.time}</h3>
      <p>With ${pendingSlot.dentistName} &nbsp;·&nbsp; ${pendingService.name}</p>
      <div class="form-group">
        <label>Full Name *</label>
        <input id="bf_name" type="text" placeholder="e.g. Rahul Sharma" />
      </div>
      <div class="form-group">
        <label>Phone Number *</label>
        <input id="bf_phone" type="tel" placeholder="e.g. 9876543210" />
      </div>
      <div class="form-group">
        <label>Email (optional)</label>
        <input id="bf_email" type="email" placeholder="you@example.com" />
      </div>
      <div class="form-group">
        <label>Notes (optional)</label>
        <input id="bf_notes" type="text" placeholder="Any special requests?" />
      </div>
      <div class="form-actions">
        <button class="btn-confirm" onclick="confirmBooking('${formId}')">
          🎉 Confirm Booking
        </button>
        <button class="btn-cancel" onclick="cancelBooking('${formId}')">
          Cancel
        </button>
      </div>
    </div>
  `);
}

/* ── Confirm booking ──────────────────────────────────── */
async function confirmBooking(formId) {
  const name  = document.getElementById('bf_name')?.value.trim();
  const phone = document.getElementById('bf_phone')?.value.trim();
  const email = document.getElementById('bf_email')?.value.trim();
  const notes = document.getElementById('bf_notes')?.value.trim();

  if (!name || !phone) {
    alert('Please enter your name and phone number.');
    return;
  }

  try {
    const res = await fetch('/api/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_name:  name,
        patient_phone: phone,
        patient_email: email || null,
        service_id:    pendingService.id,
        slot_id:       pendingSlot.id,
        notes:         notes || null,
      }),
    });

    if (res.ok) {
      const appt = await res.json();
      document.getElementById(formId)?.closest('.message')?.remove();

      addBotHtml(`
        <div class="success-card">
          <div class="success-title">🎉 Appointment Confirmed!</div>
          <div class="detail-row"><span class="label">Patient</span>  <span class="value">${escHtml(name)}</span></div>
          <div class="detail-row"><span class="label">Service</span>  <span class="value">${escHtml(pendingService.name)}</span></div>
          <div class="detail-row"><span class="label">Doctor</span>   <span class="value">${escHtml(pendingSlot.dentistName)}</span></div>
          <div class="detail-row"><span class="label">Date</span>     <span class="value">${fmtDate(pendingSlot.date)}</span></div>
          <div class="detail-row"><span class="label">Time</span>     <span class="value">${pendingSlot.time}</span></div>
          <div class="detail-row"><span class="label">Booking ID</span><span class="value">#${appt.id}</span></div>
          <br><span style="font-size:13px;color:#166534">Please arrive 10 minutes early. See you soon! 😊</span>
        </div>
      `);

      const confirm = `Appointment confirmed! Booking ID #${appt.id} for ${name} on ${fmtDate(pendingSlot.date)} at ${pendingSlot.time} with ${pendingSlot.dentistName}.`;
      chatHistory.push({ role: 'assistant', content: confirm });

      pendingSlot = null;
      pendingService = null;

    } else {
      const err = await res.json();
      addBotMessage(`❌ Booking failed: ${err.detail} — please choose a different slot.`);
    }

  } catch {
    addBotMessage('❌ Network error while confirming. Please try again.');
  }
}

function cancelBooking(formId) {
  document.getElementById(formId)?.closest('.message')?.remove();
  addBotMessage("No problem! Let me know if you'd like to pick a different slot or need any other help. 😊");
}

/* ── Appointment lookup modal ─────────────────────────── */
function showLookupModal() {
  document.getElementById('lookupModal').style.display = 'flex';
  document.getElementById('lookupPhone').value = '';
  document.getElementById('lookupResults').innerHTML = '';
}
function closeLookupModal() {
  document.getElementById('lookupModal').style.display = 'none';
}
async function lookupAppointments() {
  const phone = document.getElementById('lookupPhone').value.trim();
  if (!phone) { alert('Please enter a phone number.'); return; }

  const res  = await fetch(`/api/appointments/lookup?phone=${encodeURIComponent(phone)}`);
  const data = await res.json();
  const el   = document.getElementById('lookupResults');

  if (!data.found || data.appointments.length === 0) {
    el.innerHTML = '<p style="font-size:13px;color:#64748b">No appointments found for this number.</p>';
    return;
  }

  el.innerHTML = data.appointments.map(a => `
    <div class="appt-row">
      <div class="appt-title">${escHtml(a.service)} — #${a.id}</div>
      <div class="appt-meta">
        ${fmtDate(a.date)} · ${a.time}<br>
        ${escHtml(a.dentist)} &nbsp;·&nbsp;
        <strong style="color:${a.status === 'confirmed' ? '#16a34a' : '#dc2626'}">${a.status}</strong>
      </div>
    </div>
  `).join('');
}

// Close modal clicking outside
document.addEventListener('click', e => {
  const modal = document.getElementById('lookupModal');
  if (e.target === modal) closeLookupModal();
});

/* ── Misc helpers ─────────────────────────────────────── */
function clearChat() {
  if (!confirm('Clear the chat history?')) return;
  messagesEl().innerHTML = '';
  chatHistory = [];
  renderWelcome();
}

function showTyping() {
  document.getElementById('typing').style.display = 'flex';
  scrollBottom();
}
function hideTyping() {
  document.getElementById('typing').style.display = 'none';
}

function scrollBottom() {
  const el = messagesEl();
  el.scrollTop = el.scrollHeight;
}

function fmtDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short', year: 'numeric',
  });
}

function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}