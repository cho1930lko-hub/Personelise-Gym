// Exercises the real token authentication and rate-limit helpers without Google services.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'Code.gs'), 'utf8');
const secret = 'test-only-token-secret-with-more-than-32-bytes';
const now = Math.floor(Date.now() / 1000);
const users = [['user_id','email','password_salt','password_hash','display_name','created_at','status'],
  ['user-a','a@example.test','','','Account A',new Date().toISOString(),'active']];
const sessions = [['token_hash','user_id','expires_at','revoked_at','created_at']];
const rateRows = [['email_hash','window_start','attempt_count']];

function bytes(value) { return Buffer.from(value); }
const Utilities = {
  getUuid: () => crypto.randomUUID(),
  newBlob(value) {
    const data = Array.isArray(value) ? Buffer.from(value.map(byte => byte & 0xff)) : bytes(value);
    return { getBytes: () => [...data], getDataAsString: () => data.toString('utf8') };
  },
  base64DecodeWebSafe(value) {
    const s = String(value).replace(/-/g, '+').replace(/_/g, '/');
    return [...Buffer.from(s + '='.repeat((4 - s.length % 4) % 4), 'base64')];
  },
  base64EncodeWebSafe(value) { return Buffer.from(value).toString('base64').replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_'); },
  computeHmacSha256Signature(value, key) { return [...crypto.createHmac('sha256', Buffer.from(key)).update(Buffer.from(value)).digest()]; },
  computeDigest(_algorithm, value) { return [...crypto.createHash('sha256').update(String(value)).digest()]; },
  DigestAlgorithm: { SHA_256: 'SHA_256' },
  Charset: { UTF_8: 'UTF_8' },
};
const context = vm.createContext({ Utilities, console, Date, JSON, Math, Number, String, Object, Array, Error });
vm.runInContext(source, context, { filename: 'Code.gs' });

function makeSheet(rows) {
  return {
    getDataRange: () => ({ getValues: () => rows.map(row => row.slice()) }),
    appendRow: row => rows.push(row.slice()),
    getRange(row, col) {
      return {
        setValue(value) { rows[row - 1][col - 1] = value; },
        setValues(values) { values.forEach((r, i) => r.forEach((v, j) => { rows[row - 1 + i][col - 1 + j] = v; })); },
      };
    },
    deleteRow(row) { rows.splice(row - 1, 1); },
  };
}
const sheets = { Users: makeSheet(users), Sessions: makeSheet(sessions), RateLimits: makeSheet(rateRows) };
context.sheet_ = name => sheets[name];
context.getProperty_ = name => name === 'TOKEN_SECRET' ? secret : 'test-pepper';
context.publicError_ = (message, statusCode) => {
  const error = new Error(message); error.publicMessage = message; error.statusCode = statusCode; return error;
};

function tokenFor(payload = {}) {
  const claims = { sub: 'user-a', email: 'a@example.test', iat: now, exp: now + 3600, jti: 'test-jti', ...payload };
  const encoded = context.base64Url_(JSON.stringify(claims));
  return encoded + '.' + context.hmac_(encoded, secret);
}
function tokenForRawJson(json) {
  const encoded = context.base64Url_(json);
  return encoded + '.' + context.hmac_(encoded, secret);
}

function register(token, userId = 'user-a', revoked = '') {
  sessions.push([context.sha256_(token), userId, new Date((now + 3600) * 1000).toISOString(), revoked, new Date().toISOString()]);
}
function rejectsAuth(fn, label) {
  assert.throws(fn, error => error && error.statusCode === 401, label);
}

const valid = tokenFor();
register(valid);
assert.equal(context.authenticate_(valid).userId, 'user-a', 'valid signed active session accepted');

const tampered = valid.slice(0, -1) + (valid.endsWith('A') ? 'B' : 'A');
rejectsAuth(() => context.authenticate_(tampered), 'tampered signature rejected');
rejectsAuth(() => context.authenticate_(tokenFor({ exp: now - 1 })), 'expired token rejected');
rejectsAuth(() => context.authenticate_(tokenFor({ iat: now + 61 })), 'future-issued token rejected');
rejectsAuth(() => context.authenticate_(tokenFor({ exp: now + 13 * 60 * 60 })), 'excessive token lifetime rejected');
rejectsAuth(() => context.authenticate_('not-a-token'), 'malformed token rejected');
rejectsAuth(() => context.authenticate_(tokenForRawJson('null')), 'null claims rejected');
rejectsAuth(() => context.authenticate_(tokenForRawJson('[]')), 'array claims rejected');
rejectsAuth(() => context.authenticate_(tokenFor({ jti: 123 })), 'non-string token id rejected');

const revoked = tokenFor({ jti: 'revoked' });
register(revoked, 'user-a', new Date().toISOString());
rejectsAuth(() => context.authenticate_(revoked), 'revoked session rejected');

const wrongOwner = tokenFor({ jti: 'wrong-owner' });
register(wrongOwner, 'user-b');
rejectsAuth(() => context.authenticate_(wrongOwner), 'session row owned by another user rejected');

const inactive = tokenFor({ jti: 'inactive-user' });
register(inactive);
users[1][6] = 'disabled';
rejectsAuth(() => context.authenticate_(inactive), 'disabled account rejected');
users[1][6] = 'active';

console.log('Apps Script authentication security tests passed: valid, tampered, expired, future, excessive-lifetime, malformed, revoked, cross-user, and disabled-account tokens.');
