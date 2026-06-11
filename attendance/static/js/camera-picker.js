/**
 * CameraPicker — smart camera selector
 * - 1 camera  → auto-start, no UI shown
 * - 2+ cameras → show compact dropdown with only video inputs
 * - devicechange → auto-refresh list, notify user of new devices
 *
 * Usage:
 *   const picker = new CameraPicker({
 *     root: '#camera-picker-root',   // where to inject the UI
 *     facingMode: 'user',            // fallback if no deviceId
 *     idealWidth: 640, idealHeight: 480,
 *     onStream: (stream) => { video.srcObject = stream; },
 *     onError: (msg) => { console.error(msg); },
 *   });
 *   picker.init();         // enumerate + auto-start or show picker
 *   picker.stop();         // stop active stream
 */
class CameraPicker {
  constructor(opts = {}) {
    this.root        = typeof opts.root === 'string' ? document.querySelector(opts.root) : opts.root;
    this.facingMode  = opts.facingMode  || 'user';
    this.idealWidth  = opts.idealWidth  || 640;
    this.idealHeight = opts.idealHeight || 480;
    this.onStream    = opts.onStream    || (() => {});
    this.onError     = opts.onError     || ((m) => console.error('[CameraPicker]', m));
    this._stream     = null;
    this._selectedId = null;
    this._devices    = [];
    this._el         = null;
  }

  // ── Public API ──────────────────────────────────────────────────────────────

  async init() {
    // Request permission first so labels are populated
    try {
      const tmp = await navigator.mediaDevices.getUserMedia({ video: true });
      tmp.getTracks().forEach(t => t.stop());
    } catch (_) {}

    await this._refresh(true);
    navigator.mediaDevices.addEventListener('devicechange', () => this._onDeviceChange());
  }

  stop() {
    if (this._stream) {
      this._stream.getTracks().forEach(t => t.stop());
      this._stream = null;
    }
  }

  async switchTo(deviceId) {
    this.stop();
    this._selectedId = deviceId;
    await this._start(deviceId);
  }

  get stream()     { return this._stream; }
  get deviceCount(){ return this._devices.length; }

  // ── Private ─────────────────────────────────────────────────────────────────

  async _refresh(autoStart) {
    const all = await navigator.mediaDevices.enumerateDevices();
    this._devices = all.filter(d => d.kind === 'videoinput');
    this._render();
    if (autoStart) {
      const id = this._selectedId || (this._devices[0] && this._devices[0].deviceId);
      if (id) await this._start(id);
    }
  }

  async _start(deviceId) {
    try {
      const constraints = deviceId
        ? { video: { deviceId: { exact: deviceId }, width: { ideal: this.idealWidth }, height: { ideal: this.idealHeight } } }
        : { video: { facingMode: this.facingMode,   width: { ideal: this.idealWidth }, height: { ideal: this.idealHeight } } };
      this._stream = await navigator.mediaDevices.getUserMedia(constraints);
      this._selectedId = this._stream.getVideoTracks()[0]?.getSettings()?.deviceId || deviceId;
      this._updateSelectValue();
      this.onStream(this._stream);
    } catch (e) {
      this.onError('تعذّر فتح الكاميرا: ' + (e.message || e));
    }
  }

  _render() {
    if (!this.root) return;
    if (this._devices.length <= 1) {
      // hide picker — single camera
      if (this._el) this._el.style.display = 'none';
      return;
    }
    if (!this._el) {
      this._el = document.createElement('div');
      this._el.className = 'camera-picker-wrap';
      this._el.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;background:rgba(15,23,42,.7);
          backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.12);border-radius:10px;
          padding:6px 12px;font-size:13px;color:#e2e8f0;">
          <span style="font-size:16px;">📷</span>
          <select id="_cp_select" style="background:transparent;border:0;color:#e2e8f0;
            font-size:13px;cursor:pointer;outline:none;flex:1;min-width:0;"></select>
        </div>`;
      this.root.appendChild(this._el);
      this._el.querySelector('#_cp_select').addEventListener('change', (e) => {
        this.switchTo(e.target.value);
      });
    }
    // Fill options
    const sel = this._el.querySelector('#_cp_select');
    const prev = sel.value;
    sel.innerHTML = this._devices.map((d, i) =>
      `<option value="${d.deviceId}">${d.label || 'كاميرا ' + (i + 1)}</option>`
    ).join('');
    if (prev && this._devices.find(d => d.deviceId === prev)) sel.value = prev;
    this._el.style.display = '';
  }

  _updateSelectValue() {
    if (!this._el) return;
    const sel = this._el.querySelector('#_cp_select');
    if (sel && this._selectedId) sel.value = this._selectedId;
  }

  async _onDeviceChange() {
    const prevCount = this._devices.length;
    const all = await navigator.mediaDevices.enumerateDevices();
    const next = all.filter(d => d.kind === 'videoinput');
    const added = next.filter(d => !this._devices.find(p => p.deviceId === d.deviceId));
    this._devices = next;
    this._render();

    if (added.length > 0) {
      // new camera hot-plugged — notify and auto-switch if user was on built-in
      this._showHotplugBanner(added[0]);
    }
  }

  _showHotplugBanner(device) {
    const banner = document.createElement('div');
    const label = device.label || 'كاميرا خارجية';
    banner.style.cssText = `position:fixed;top:16px;left:50%;transform:translateX(-50%);
      z-index:9999;background:#0f172a;border:1px solid #38bdf8;color:#e2e8f0;
      padding:10px 18px;border-radius:12px;font-size:13px;font-weight:600;
      box-shadow:0 4px 20px rgba(0,0,0,.4);display:flex;align-items:center;gap:10px;`;
    banner.innerHTML = `<span style="font-size:18px;">📷</span>
      <span>تم اكتشاف ${label} — <button id="_cp_switch" style="color:#38bdf8;background:none;border:0;cursor:pointer;font-weight:700;">تبديل إليها</button></span>
      <button id="_cp_dismiss" style="color:#94a3b8;background:none;border:0;cursor:pointer;font-size:16px;">✕</button>`;
    document.body.appendChild(banner);
    banner.querySelector('#_cp_switch').onclick  = () => { this.switchTo(device.deviceId); banner.remove(); };
    banner.querySelector('#_cp_dismiss').onclick = () => banner.remove();
    setTimeout(() => banner.remove(), 8000);
  }
}

window.CameraPicker = CameraPicker;
