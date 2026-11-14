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
let uuidCounter = 0;
const Utilities = {
  getUuid() {
    const suffix = String(uuidCounter++).padStart(12, '0');
    return '123e4567-e89b-42d3-a456-' + suffix;
  },
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
    return Buffer.from(value).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
  },
};
const context = vm.createContext({ Utilities });
vm.runInContext(source, context, { filename: 'Code.gs' });

function expected(password, salt, iterations, pepper) {
  return crypto.pbkdf2Sync(password + pepper, salt, iterations, 32, 'sha256')
    .toString('base64url');
}

// Published PBKDF2-HMAC-SHA256 one-iteration known-answer vector.
assert.equal(
  context.passwordHashWithIterations_('password', 'c2FsdA', 1, ''),
  'Eg-2z_z4syxD5yJSVsT4N6hlSMkszDVICAWYfLcL4Xs',
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

const salt = context.randomToken_(24);
assert.equal(Buffer.from(salt, 'base64url').length, 24, 'salt must contain 24 random bytes');
assert.notEqual(salt, context.randomToken_(24), 'successive salts must differ');
assert.throws(() => context.randomToken_(8), /between 16 and 32 bytes/);

// Verify the exact HMAC primitive used by signed session tokens against Node.
const tokenPayload = 'eyJzdWIiOiJ1c2VyLTEiLCJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDAwNDMyMDAsImp0aSI6InRlc3QifQ';
const tokenSecret = 'test-only-token-secret-32-bytes-minimum';
const expectedSignature = crypto.createHmac('sha256', tokenSecret)
  .update(tokenPayload, 'utf8').digest('base64url');
assert.equal(context.hmac_(tokenPayload, tokenSecret), expectedSignature,
  'session token HMAC must match independent Node/OpenSSL output');
assert.equal(context.constantTimeEqual_(expectedSignature, expectedSignature), true);
assert.equal(context.constantTimeEqual_(expectedSignature, expectedSignature + 'x'), false);
assert.equal(context.constantTimeEqual_('short', 'longer'), false);
assert.equal(context.constantTimeEqual_('', ''), true);

console.log('Apps Script PBKDF2, UUID salt, and session HMAC primitives passed independent Node/OpenSSL checks.');
