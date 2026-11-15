# Apps Script authentication deployment (test only)

This backend is not production-ready until the deployment and live smoke tests below are completed.

## Isolation rules

- Create a brand-new, empty Google spreadsheet dedicated to Personelise Gym testing.
- Do not use the existing Streamlit spreadsheet, gym billing spreadsheet, or any production data.
- Use synthetic test identities only. Never enter a real user's password or personal data.
- Do not commit Script Properties, tokens, passwords, spreadsheet IDs, or deployment URLs.

## 1. Configure the Apps Script project

1. Create a standalone Google Apps Script project.
2. Copy `Code.gs` into the project.
3. Open **Project Settings → Script Properties** and add:
   - `SPREADSHEET_ID`: ID of the new empty test spreadsheet.
   - `TOKEN_SECRET`: a newly generated, high-entropy secret of at least 32 random bytes.
   - `PASSWORD_PEPPER`: a separate newly generated, high-entropy secret of at least 32 random bytes.
4. Keep the two secrets independent. Store them only in Script Properties and a secure password manager. Never put them in source code, Flutter assets, or GitHub.
5. Save and run no spreadsheet mutation against any existing workbook.

## 2. Deploy a test Web App

1. Select **Deploy → New deployment → Web app**.
2. Execute as the script owner.
3. Set access to the narrowest option that permits the intended test client. The current Flutter client expects an endpoint reachable without an interactive Google sign-in; if that requires broad access, use only the isolated test spreadsheet and synthetic accounts.
4. Deploy and copy the Web App URL into a secure local test note. Do not commit it.
5. Verify the deployment is the test project and points to the new spreadsheet.

## 3. Live smoke tests (two synthetic accounts)

Run from a controlled test client against the test Web App URL:

1. Sign up synthetic account A; confirm a user row and session row are created.
2. Fetch A's profile with its access token; verify only A's identity is returned.
3. Sign up synthetic account B; confirm a distinct user ID and session.
4. Attempt profile access with a modified token; it must be rejected.
5. Log out A; repeat A's profile request; it must be rejected.
6. Confirm B's profile still works after A logs out.
7. Try an incorrect password eight times for a synthetic email; the next attempt must be rate-limited. Do not use a real account for this test.
8. Confirm a successful login clears that synthetic email's rate-limit row.
9. Measure signup/login latency in the actual Apps Script runtime. In particular, verify the production PBKDF2 setting of 210,000 iterations completes reliably within Apps Script execution limits.

## 4. Completion criteria

Phase 3 is complete only when:

- GitHub Actions passes the PBKDF2 and authentication security regression tests.
- The deployed test Web App passes the live two-account isolation and logout tests.
- The 210,000-iteration PBKDF2 runtime has been measured and is acceptable.
- The Flutter client can sign up, log in, restore a session, log out, and retain the documented offline behavior against the test endpoint.

Until then, keep Phase 4 (Sheets fitness-data sync) blocked. No production spreadsheet or existing Streamlit app is part of this deployment.
