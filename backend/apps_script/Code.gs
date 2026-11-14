/**
 * Personelise Gym account API — Google Apps Script Web App.
 *
 * Deploy as a Web App (execute as owner; access: anyone) only after setting
 * Script Properties and using a NEW, dedicated test spreadsheet. Do not point
 * this at the existing Streamlit/production spreadsheet.
 *
 * Required Script Properties:
 *   SPREADSHEET_ID     ID of a dedicated app data spreadsheet
 *   TOKEN_SECRET       32+ random bytes, base64url or hex text
 *   PASSWORD_PEPPER    independent random secret, 32+ random bytes
 *
 * All requests use POST JSON. Authenticated requests send access_token in the
 * JSON body because Apps Script Web App events do not reliably expose headers.
 * No user_id is accepted for authorization; it is derived from the signed token.
 */

const CFG = Object.freeze({
  USERS: 'Users',
  SESSIONS: 'Sessions',
  RATE_LIMITS: 'RateLimits',
  TOKEN_TTL_SECONDS: 12 * 60 * 60,
  PASSWORD_ITERATIONS: 210000,
  RATE_WINDOW_SECONDS: 15 * 60,
  MAX_LOGIN_ATTEMPTS: 8,
  MAX_BODY_CHARS: 12000,
});

function doPost(e) {
  try {
    const bodyText = e && e.postData && e.postData.contents;
    if (!bodyText || bodyText.length > CFG.MAX_BODY_CHARS) {
      return json_({ error: 'Invalid request body.' }, 400);
    }
    const body = JSON.parse(bodyText);
    if (!body || typeof body !== 'object' || Array.isArray(body)) {
      return json_({ error: 'Invalid request.' }, 400);
    }
    ensureConfigured_();
    ensureSchema_();

    const action = String(body.action || '');
    if (action === 'signup') return signup_(body);
    if (action === 'login') return login_(body);
    if (action === 'profile') {
      const identity = authenticate_(body.access_token);
      return json_({
        user_id: identity.userId,
        email: identity.email,
        display_name: identity.displayName,
      });
    }
    if (action === 'logout') {
      const identity = authenticate_(body.access_token);
      revokeToken_(identity.tokenHash);
      return json_({ ok: true });
    }
    return json_({ error: 'Unsupported action.' }, 400);
  } catch (err) {
    console.error('API failure: ' + String(err && err.stack || err));
    const message = err && err.publicMessage
      ? err.publicMessage
      : 'The request could not be completed.';
    const status = err && err.statusCode ? err.statusCode : 500;
    const code = status === 401 ? 'AUTH_INVALID' : 'REQUEST_FAILED';
    return json_({ error: message, code: code }, status);
  }
}

function signup_(body) {
  const email = normalizeEmail_(body.email);
  const password = validatePassword_(body.password);
  const rawDisplayName = String(body.display_name || '').trim();
  if (rawDisplayName.length < 2 || rawDisplayName.length > 80 ||
      /[\\u0000-\\u001F\\u007F]/.test(rawDisplayName)) {
    throw publicError_('Enter a name between 2 and 80 characters.', 400);
  }
  // Prevent user-controlled names from being interpreted as spreadsheet formulas.
  const displayName = /^[=+@-]/.test(rawDisplayName) ? "'" + rawDisplayName : rawDisplayName;

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const users = sheet_(CFG.USERS);
    const rows = users.getDataRange().getValues();
    for (let i = 1; i < rows.length; i++) {
      if (String(rows[i][1]).toLowerCase() === email) {
        throw publicError_('An account with this email already exists.', 409);
      }
    }
    const userId = Utilities.getUuid();
    const salt = randomToken_(24);
    const hash = passwordHash_(password, salt);
    const now = new Date().toISOString();
    users.appendRow([userId, email, salt, hash, displayName, now, 'active']);
    return json_(issueSession_(userId, email, displayName));
  } finally {
    lock.releaseLock();
  }
}

function login_(body) {
  const email = normalizeEmail_(body.email);
  const password = String(body.password || '');
  if (!password || password.length > 256) {
    throw publicError_('Email or password is incorrect.', 401);
  }
  // Reserve an attempt atomically before password verification. This prevents
  // concurrent requests from bypassing the per-email attempt ceiling.
  beginLoginAttempt_(email);

  const users = sheet_(CFG.USERS);
  const rows = users.getDataRange().getValues();
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (String(row[1]).toLowerCase() !== email) continue;
    if (String(row[6]) !== 'active') break;
    const candidate = passwordHash_(password, String(row[2]));
    if (!constantTimeEqual_(candidate, String(row[3]))) break;
    clearRateLimit_(email);
    return json_(issueSession_(String(row[0]), email, String(row[4])));
  }
  throw publicError_('Email or password is incorrect.', 401);
}

function issueSession_(userId, email, displayName) {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    sub: userId,
    email: email,
    iat: now,
    exp: now + CFG.TOKEN_TTL_SECONDS,
    jti: Utilities.getUuid(),
  };
  const encoded = base64Url_(JSON.stringify(payload));
  const signature = hmac_(encoded, getProperty_('TOKEN_SECRET'));
  const token = encoded + '.' + signature;
  const tokenHash = sha256_(token);
  sheet_(CFG.SESSIONS).appendRow([
    tokenHash, userId, new Date(payload.exp * 1000).toISOString(), '', new Date().toISOString()
  ]);
  return {
    access_token: token,
    user_id: userId,
    email: email,
    display_name: displayName,
    expires_at: new Date(payload.exp * 1000).toISOString(),
  };
}

function authenticate_(tokenValue) {
  const token = String(tokenValue || '');
  if (token.length < 30 || token.length > 4096) {
    throw publicError_('Session is invalid or expired. Please sign in again.', 401);
  }
  const parts = token.split('.');
  if (parts.length !== 2) {
    throw publicError_('Session is invalid or expired. Please sign in again.', 401);
  }
  const expected = hmac_(parts[0], getProperty_('TOKEN_SECRET'));
  if (!constantTimeEqual_(expected, parts[1])) {
    throw publicError_('Session is invalid or expired. Please sign in again.', 401);
  }
  let payload;
  try {
    payload = JSON.parse(Utilities.newBlob(Utilities.base64DecodeWebSafe(parts[0])).getDataAsString());
  } catch (_) {
    throw publicError_('Session is invalid or expired. Please sign in again.', 401);
  }
  const now = Math.floor(Date.now() / 1000);
  if (typeof payload.sub !== 'string' || !payload.sub ||
      !Number.isSafeInteger(payload.iat) || !Number.isSafeInteger(payload.exp) ||
      !payload.jti || payload.exp <= now || payload.iat > now + 60 ||
      payload.exp <= payload.iat ||
      payload.exp - payload.iat > CFG.TOKEN_TTL_SECONDS) {
    throw publicError_('Session is invalid or expired. Please sign in again.', 401);
  }

  const tokenHash = sha256_(token);
  const sessions = sheet_(CFG.SESSIONS).getDataRange().getValues();
  let active = false;
  for (let i = 1; i < sessions.length; i++) {
    if (constantTimeEqual_(String(sessions[i][0]), tokenHash) &&
        String(sessions[i][1]) === String(payload.sub) &&
        !sessions[i][3] &&
        new Date(sessions[i][2]).getTime() > Date.now()) {
      active = true;
      break;
    }
  }
  if (!active) throw publicError_('Session has been revoked. Please sign in again.', 401);

  const users = sheet_(CFG.USERS).getDataRange().getValues();
  for (let i = 1; i < users.length; i++) {
    if (String(users[i][0]) === String(payload.sub) &&
        String(users[i][6]) === 'active') {
      return {
        userId: String(users[i][0]),
        email: String(users[i][1]),
        displayName: String(users[i][4]),
        tokenHash: tokenHash,
      };
    }
  }
  throw publicError_('Account is unavailable.', 401);
}

function revokeToken_(tokenHash) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const sessions = sheet_(CFG.SESSIONS);
    const rows = sessions.getDataRange().getValues();
    for (let i = 1; i < rows.length; i++) {
      if (constantTimeEqual_(String(rows[i][0]), tokenHash)) {
        sessions.getRange(i + 1, 4).setValue(new Date().toISOString());
        return;
      }
    }
  } finally {
    lock.releaseLock();
  }
}

function normalizeEmail_(value) {
  const email = String(value || '').trim().toLowerCase();
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw publicError_('Enter a valid email address.', 400);
  }
  return email;
}

function validatePassword_(value) {
  const password = String(value || '');
  if (password.length < 12 || password.length > 256) {
    throw publicError_('Use a password between 12 and 256 characters.', 400);
  }
  return password;
}

// PBKDF2-HMAC-SHA256; pepper is stored only in Apps Script Script Properties.
function passwordHash_(password, salt) {
  const pepper = getProperty_('PASSWORD_PEPPER');
  // Use the documented Byte[]/Byte[] overload: both the HMAC input and key
  // are UTF-8/raw byte arrays. This is required for the PBKDF2 block loop.
  const passwordKey = Utilities.newBlob(password + pepper).getBytes();
  const saltBytes = Utilities.base64DecodeWebSafe(salt);
  const block = saltBytes.concat([0, 0, 0, 1]);
  let u = Utilities.computeHmacSha256Signature(block, passwordKey);
  let result = u.slice();
  for (let i = 1; i < CFG.PASSWORD_ITERATIONS; i++) {
    u = Utilities.computeHmacSha256Signature(u, passwordKey);
    for (let j = 0; j < result.length; j++) result[j] = result[j] ^ u[j];
  }
  return base64UrlBytes_(result);
}

function beginLoginAttempt_(email) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const tab = sheet_(CFG.RATE_LIMITS);
    const rows = tab.getDataRange().getValues();
    const key = sha256_(email);
    const now = new Date();
    for (let i = 1; i < rows.length; i++) {
      if (String(rows[i][0]) !== key) continue;
      const started = new Date(rows[i][1]).getTime();
      const count = Number(rows[i][2]) || 0;
      if (Number.isFinite(started) &&
          now.getTime() - started < CFG.RATE_WINDOW_SECONDS * 1000) {
        if (count >= CFG.MAX_LOGIN_ATTEMPTS) {
          throw publicError_('Too many attempts. Try again in 15 minutes.', 429);
        }
        tab.getRange(i + 1, 3).setValue(count + 1);
      } else {
        tab.getRange(i + 1, 2, 1, 2).setValues([[now.toISOString(), 1]]);
      }
      return;
    }
    tab.appendRow([key, now.toISOString(), 1]);
  } finally {
    lock.releaseLock();
  }
}
function clearRateLimit_(email) {
  const tab = sheet_(CFG.RATE_LIMITS);
  const rows = tab.getDataRange().getValues();
  const key = sha256_(email);
  for (let i = 1; i < rows.length; i++) {
    if (String(rows[i][0]) === key) {
      tab.deleteRow(i + 1);
      return;
    }
  }
}
function findRateRow_(email) {
  const rows = sheet_(CFG.RATE_LIMITS).getDataRange().getValues();
  const key = sha256_(email);
  for (let i = 1; i < rows.length; i++) {
    if (String(rows[i][0]) === key) {
      return { start: rows[i][1], count: Number(rows[i][2]) };
    }
  }
  return null;
}

function ensureConfigured_() {
  getProperty_('SPREADSHEET_ID');
  getProperty_('TOKEN_SECRET');
  getProperty_('PASSWORD_PEPPER');
}
function getProperty_(name) {
  const value = PropertiesService.getScriptProperties().getProperty(name);
  if (!value || value.length < 24) {
    throw new Error('Missing or weak Script Property: ' + name);
  }
  return value;
}
function ensureSchema_() {
  const ss = SpreadsheetApp.openById(getProperty_('SPREADSHEET_ID'));
  const definitions = {};
  definitions[CFG.USERS] = ['user_id','email','password_salt','password_hash','display_name','created_at','status'];
  definitions[CFG.SESSIONS] = ['token_hash','user_id','expires_at','revoked_at','created_at'];
  definitions[CFG.RATE_LIMITS] = ['email_hash','window_start','attempt_count'];
  Object.keys(definitions).forEach(function(name) {
    let tab = ss.getSheetByName(name);
    if (!tab) tab = ss.insertSheet(name);
    if (tab.getLastRow() === 0) {
      tab.getRange(1, 1, 1, definitions[name].length).setValues([definitions[name]]);
      tab.setFrozenRows(1);
      return;
    }
    const expected = definitions[name];
    const actual = tab.getRange(1, 1, 1, expected.length).getValues()[0];
    if (expected.some(function(header, index) { return String(actual[index]) !== header; })) {
      throw new Error('Unexpected header schema in sheet: ' + name);
    }
  });
}
function sheet_(name) {
  return SpreadsheetApp.openById(getProperty_('SPREADSHEET_ID')).getSheetByName(name);
}
function hmac_(value, secret) {
  const bytes = Utilities.computeHmacSha256Signature(value, secret);
  return base64UrlBytes_(bytes);
}
function sha256_(value) {
  return base64UrlBytes_(Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256, value, Utilities.Charset.UTF_8
  ));
}
function randomToken_(bytes) {
  const seed = Utilities.getUuid() + ':' + Utilities.getUuid() + ':' + Date.now();
  const digest = Utilities.computeHmacSha256Signature(seed, getProperty_('TOKEN_SECRET'));
  return base64UrlBytes_(digest).substring(0, bytes);
}
function base64Url_(text) {
  return base64UrlBytes_(Utilities.newBlob(text).getBytes());
}
function base64UrlBytes_(bytes) {
  return Utilities.base64EncodeWebSafe(bytes).replace(/=+$/g, '');
}
function constantTimeEqual_(a, b) {
  a = String(a); b = String(b);
  let diff = a.length ^ b.length;
  const length = Math.max(a.length, b.length);
  for (let i = 0; i < length; i++) {
    diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  }
  return diff === 0;
}
function publicError_(message, statusCode) {
  const error = new Error(message);
  error.publicMessage = message;
  error.statusCode = statusCode;
  return error;
}
function json_(data, statusCode) {
  // ContentService does not support arbitrary HTTP status codes; clients must
  // inspect the JSON error envelope as well as the transport status.
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
