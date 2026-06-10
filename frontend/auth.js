const API = 'http://127.0.0.1:8000/api';

// ─── Login ───────────────────────────────────────────────
async function handleLogin() {
    const username   = document.getElementById('username').value.trim();
    const password   = document.getElementById('password').value.trim();
    const errorMsg   = document.getElementById('error-msg');
    const errorText  = document.getElementById('error-text');
    const successMsg = document.getElementById('success-msg');
    const btn        = document.getElementById('login-btn');
    const label      = document.getElementById('btn-label');
    const spinner    = document.getElementById('spinner');

    errorMsg.style.display   = 'none';
    successMsg.style.display = 'none';

    if (!username || !password) {
        errorText.textContent  = 'Please fill in all fields.';
        errorMsg.style.display = 'flex';
        return;
    }

    btn.disabled          = true;
    label.style.display   = 'none';
    spinner.style.display = 'block';

    try {
        const res  = await fetch(`${API}/auth/login/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ username, password })
        });
        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('access_token',  data.access);
            localStorage.setItem('refresh_token', data.refresh);
            successMsg.style.display = 'flex';
            setTimeout(() => window.location.href = '/dashboard.html', 1000);
        } else {
            errorText.textContent  = 'Invalid username or password.';
            errorMsg.style.display = 'flex';
        }
    } catch {
        errorText.textContent  = 'Cannot reach server. Is Django running?';
        errorMsg.style.display = 'flex';
    } finally {
        btn.disabled          = false;
        label.style.display   = 'block';
        spinner.style.display = 'none';
    }
}

// ─── Register ────────────────────────────────────────────
async function handleRegister() {
    const username   = document.getElementById('username').value.trim();
    const email      = document.getElementById('email').value.trim();
    const password   = document.getElementById('password').value.trim();
    const errorMsg   = document.getElementById('error-msg');
    const errorText  = document.getElementById('error-text');
    const successMsg = document.getElementById('success-msg');
    const btn        = document.getElementById('reg-btn');
    const label      = document.getElementById('btn-label');
    const spinner    = document.getElementById('spinner');

    errorMsg.style.display   = 'none';
    successMsg.style.display = 'none';

    if (!username || !password) {
        errorText.textContent  = 'Username and password are required.';
        errorMsg.style.display = 'flex';
        return;
    }
    if (password.length < 6) {
        errorText.textContent  = 'Password must be at least 6 characters.';
        errorMsg.style.display = 'flex';
        return;
    }

    btn.disabled          = true;
    label.style.display   = 'none';
    spinner.style.display = 'block';

    try {
        const res  = await fetch(`${API}/auth/register/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ username, email, password })
        });
        const data = await res.json();

        if (res.ok) {
            successMsg.style.display = 'flex';
            setTimeout(() => window.location.href = '/login.html', 1500);
        } else {
            const first = Object.values(data)[0];
            errorText.textContent  = Array.isArray(first) ? first[0] : first;
            errorMsg.style.display = 'flex';
        }
    } catch {
        errorText.textContent  = 'Cannot reach server. Is Django running?';
        errorMsg.style.display = 'flex';
    } finally {
        btn.disabled          = false;
        label.style.display   = 'block';
        spinner.style.display = 'none';
    }
}

// ─── Password strength (register page only) ──────────────
function checkStrength(val) {
    const wrap  = document.getElementById('strength');
    const fill  = document.getElementById('s-fill');
    const label = document.getElementById('s-label');
    if (!wrap) return;
    if (!val) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';

    let score = 0;
    if (val.length >= 6)            score++;
    if (val.length >= 10)           score++;
    if (/[A-Z]/.test(val))          score++;
    if (/[0-9]/.test(val))          score++;
    if (/[^A-Za-z0-9]/.test(val))   score++;

    const levels = [
        { pct: '20%', color: '#f87171', text: 'Very weak'   },
        { pct: '40%', color: '#fb923c', text: 'Weak'        },
        { pct: '60%', color: '#facc15', text: 'Fair'        },
        { pct: '80%', color: '#34d399', text: 'Strong'      },
        { pct: '100%',color: '#10b981', text: 'Very strong' },
    ];
    const l = levels[Math.min(score - 1, 4)] || levels[0];
    fill.style.width      = l.pct;
    fill.style.background = l.color;
    label.textContent     = l.text;
    label.style.color     = l.color;
}

// ─── Toggle password visibility ──────────────────────────
function togglePw() {
    const inp = document.getElementById('password');
    inp.type  = inp.type === 'password' ? 'text' : 'password';
}

// ─── Shared helpers ──────────────────────────────────────
function getToken()  { return localStorage.getItem('access_token'); }
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login.html';
}
function requireAuth() {
    if (!getToken()) window.location.href = '/login.html';
}

// Enter key support
document.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    if (document.getElementById('login-btn'))  handleLogin();
    if (document.getElementById('reg-btn'))    handleRegister();
});
