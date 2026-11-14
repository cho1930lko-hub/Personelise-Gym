// Runs the actual Apps Script PBKDF2 helper in a Node VM with Utilities mocks.
// No network, spreadsheet, secrets, or production account data are used.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync(
  require('node:path').join(__dirname, '..', 'Code.gs'),
  'utf8',
);
const Utilities = {
  newBlob(value) {
    const bytes = Buffer.from(String(value), 'utf8');
    return { getBytes: () => Array.from(bytes) };
  },
  base64DecodeWebSafe(value) {
    const normalized = String(value).replace(/-/g, '+').replace(/_/g, '/');
    return Array.from(Buffer.from(normalized, 'base64'));
  },
  computeHmacSha256Signature(value, key) {
    return Array.from(crypto.createHmac('sha256', Buffer.from(key)).update(Buffer.from(value)).digest());
  },
  base64EncodeWebSafe(value) {
    return Buffer.from(value).toString('base64').replace(/=/g, '').replace(/\\+/g, '-').replace(/\\//g, '_');
  },
};
const context = vm.createContext({ Utilities });
vm.runInContext(source, context, { filename: 'Code.gs' });

function expected(password, salt, iterations, pepper) {
  return crypto.pbkdf2Sync(password + pepper, salt, iterations, 32, 'sha256')
    .toString('base64url');
}

// RFC 7914 / PBKDF2-HMAC-SHA256 one-iteration known-answer vector.
assert.equal(
  context.passwordHashWithIterations_('password', 'c2FsdA', 1, ''),
  'EAv2z_z4syxD5yJSVsT4N6hlSMkszDVICAWYfLcL4Xs'.replace(/^/, ''),
  'PBKDF2 one-iteration known-answer vector',
);

// Cross-check several rounds and the pepper input against Node's independent
// OpenSSL-backed PBKDF2 implementation.
for (const iterations of [2, 3, 100]) {
  const salt = 'dGVzdC1zYWx0';
  const actual = context.passwordHashWithIterations_('gym-pass', salt, iterations, 'server-pepper');
  const reference = expected('gym-pass', Buffer.from(salt, 'base64url'), iterations, 'server-pepper');
  assert.equal(actual, reference, `PBKDF2 mismatch at ${iterations} iterations`);
}

assert.throws(
  () => context.passwordHashWithIterations_('p', 'c2FsdA', 0, ''),
  /Invalid PBKDF2 iteration count/,
);
console.log('Apps Script PBKDF2 implementation matches independent Node/OpenSSL vectors.');
