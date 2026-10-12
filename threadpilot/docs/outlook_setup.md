# Send the morning email from Outlook in one click

**What the general manager sees.** Dashboard → **Generate email**. The draft opens already written from the 07:00 briefing,
with yesterday's recipients already filled in. They read it, edit if they want, and press **Send with Outlook**. The email
leaves from their own Outlook mailbox and lands in their Sent Items like any other email. ThreadPilot records who it went to
and when, so reopening the draft says "Sent 07:45 from gm@… to …" and the button becomes **Send again** (which asks first).

The first send asks them to sign in to Microsoft once and allow "Send mail as you". After that, sending is one click.

## How it works, and why it is safe

| Question | Answer |
|---|---|
| Who sends the email? | Microsoft, from the manager's own mailbox (Microsoft Graph `POST /me/sendMail`). Not the ThreadPilot server. |
| What can ThreadPilot do in the mailbox? | Only send, as the signed-in person (permission `Mail.Send`). It cannot read, move or delete mail. |
| Where is the Microsoft sign-in kept? | In that browser only (`frontend/outlook.js`, Microsoft's MSAL library, sign-in with PKCE). The server never receives a Microsoft password or token, and there is no client secret anywhere. **Use another account** in the dialog forgets it. |
| Can it send by itself? | No. Only the manager's click sends, after the full text is on screen. The chat cannot send it. |
| What goes out? | Exactly the subject and text in the dialog, as plain text (no HTML, so nothing in the briefing can change how the email looks or add links). |
| What does the server store? | The draft (as before), the To/Cc lists, and for each send: time, sender address, draft version, count (`briefing_email_deliveries`, migration `0006`). |
| What if something fails? | The dialog says so and says whether anything was sent. A send is recorded only after Outlook accepts it (HTTP 202). If Outlook returns a server error, the dialog says to check Sent Items before sending again, because Microsoft may have sent it anyway. |

Without the setup below, the button reads **Open in Outlook** instead: it opens Outlook (or the phone's mail app) with the
recipients, subject and text filled in, and the manager presses Send there. That needs no setup at all.

## Set it up (about 10 minutes, once, by one person)

### 1. Register the app with Microsoft

You need a Microsoft Entra directory to register an app in. Use one of these:

* **Your NUS account.** Many university directories do not let students register apps. If step 2 says you do not have
  permission, use the next option.
* **A free Azure account** (portal.azure.com, sign up with your personal Microsoft account). Signing up creates a
  "Default Directory" you own. Microsoft may ask for a phone number and a card to verify you; registering an app is free.

Then:

1. Go to **https://entra.microsoft.com** → **Applications** → **App registrations** → **New registration**.
   (In portal.azure.com: search for "App registrations".)
2. **Name:** `ThreadPilot`.
3. **Supported account types:** *Accounts in any organizational directory and personal Microsoft accounts*. This lets
   a Hotmail/Outlook.com account and a work or school account both sign in.
4. **Redirect URI:** platform **Single-page application (SPA)**, and the address of `auth-redirect.html` on the site the
   manager uses. Add every address where the app is opened (Authentication → Add URI):

   | Where the app is opened | Redirect URI to add |
   |---|---|
   | The team's CloudBase site | `https://dss5105-track1-i7gxvcy5k7ef5ac9b-1500904749.ap-singapore.app.tcloudbase.com/auth-redirect.html` |
   | GitHub Pages (if used) | `https://jingweiluo557.github.io/<path to the frontend>/auth-redirect.html` |
   | Your laptop (Docker or `scripts.serve`) | `http://localhost:8000/auth-redirect.html` (open the app at `localhost`, not `127.0.0.1`) |

   It must match exactly, including `https`, the path and no trailing slash, or Microsoft shows `redirect_uri_mismatch`.
   Do **not** choose the "Web" platform; it would require a secret.
5. **Register.** On the app's **Overview** page, copy the **Application (client) ID** (a GUID).
6. **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions** → tick **Mail.Send** →
   **Add permissions**. (`User.Read` is already there; leave it.) Do not add application permissions.
7. Do **not** create a client secret or certificate. This app does not use one.

### 2. Put the client ID in the app

In `frontend/config.js`:

```js
outlook: {clientId: 'paste-the-application-client-id-here', tenant: 'common'}
```

The client ID is public (it is in every page Microsoft sign-in shows), so it is committed like the API address. `tenant`
stays `common` for any account type; use `consumers` for personal accounts only, or your directory ID for work accounts
only.

Optional default recipients for the very first draft (after that, each draft reuses the last list that was sent or saved):
`BRIEFING_EMAIL_TO=gm@company.com,planner@company.com` in `.env`.

### 3. Deploy and try it

Redeploy (CloudBase and/or Pages, as for any frontend change; on CloudBase the database migration `0006` runs with the
others). Then open the Dashboard → **Generate email** → put your own address in To → **Send with Outlook** → sign in →
**Accept** on Microsoft's "Permissions requested" screen. The email arrives in your inbox and in your Sent Items.

## If something goes wrong

| What you see | Why, and the fix |
|---|---|
| `AADSTS50011` / `redirect_uri_mismatch` | The address in the browser is not one of the redirect URIs. Add it exactly as in step 4. |
| "The browser blocked the Microsoft sign-in window" | Allow pop-ups for the site, then press Send again. |
| "Need admin approval" on Microsoft's screen | A work or school directory that does not let users approve apps. Ask its IT admin to grant consent, or use a personal Outlook.com account. |
| "This app is unverified" on Microsoft's screen | Normal for a student project; Microsoft shows it for apps without a verified publisher. Personal accounts can still accept. |
| "Your Microsoft sign-in has expired" | Press Send again. Browsers limit how long a web page may keep a Microsoft sign-in (about a day), so the first send of a day may flash Microsoft's window; if you are still signed in to Microsoft it closes by itself. |
| The button says **Open in Outlook** | `clientId` in `frontend/config.js` is empty or not a GUID. |

## Tested

* `tests/test_outlook_send.py`, in a real browser, with Microsoft replaced at its two edges (sign-in library and Graph):
  sign-in starts from the click before anything else (otherwise browsers block the window); exactly the reviewed text goes
  to To and Cc; a send is recorded only after Outlook accepts it; the second send needs no sign-in; blocked, closed and
  lost sign-in windows, refused permission and Outlook errors each say what happened; the dialog fits a 320 px phone with
  Send on screen.
* `backend/tests/test_dashboard.py`: recipients are validated and carried to the next day's draft, sends are recorded and
  counted, the migration upgrades an existing database.
* Checked by hand against Microsoft's real sign-in library (MSAL 5.22.0, `frontend/vendor/`, MIT licence): the sign-in
  address asks for `Mail.Send openid profile offline_access` with PKCE (`S256`) and the right redirect URI. A real send
  needs the app registration above and has not been run from this repository.
