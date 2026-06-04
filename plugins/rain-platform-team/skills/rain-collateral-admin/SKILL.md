---
name: rain-collateral-admin
description: Look up the collateral contract admin wallet address(es) for a Rain user. Use this skill whenever someone provides a Rain user ID (a UUID like e6a8122e-...) and asks for their wallet address, collateral contract admin address, EVM address, Solana address, or any on-chain address tied to their Rain account. Also trigger when someone says things like "what wallet is on this user", "get the address for user X", "collateral admin for [UUID]", "what's the wallet attached to user [ID]", or "find the wallet for this user ID". Use it proactively any time a Rain user ID is present and wallet/address information is needed.
---

## What this skill does

Retrieves the wallet address(es) attached to a Rain user's collateral contract by querying the Weather Station internal API. Returns the EVM wallet (collateral contract admin), plus Solana/Stellar/Tron addresses if set.

## Requirements

- Claude in Chrome tools must be available (`tabs_context_mcp`, `navigate`, `javascript_tool`)
- Weather Station is only accessible on VPN — if you get a connection error, let the user know they need to be on VPN

## Steps

### Step 1 — Get a browser tab

Use `tabs_context_mcp` (with `createIfEmpty: true`) to get an available tab ID.

### Step 2 — Navigate to Weather Station

Navigate the tab to `https://weatherstation.rain.xyz`. This loads the page and ensures the auth session is active. Wait for the navigation to complete.

### Step 3 — Fetch user data using the session auth

Run this JavaScript in the tab, substituting the actual user ID:

```javascript
(async () => {
  const token = localStorage.getItem('authToken');
  if (!token) return JSON.stringify({ error: 'No authToken found — are you logged in to Weather Station?' });
  const resp = await fetch(`https://weatherstation-api.rain.xyz/api/users/USER_ID_HERE`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await resp.json();
  if (!data.user) return JSON.stringify({ error: data.message || 'User not found', status: resp.status });
  const u = data.user;
  return JSON.stringify({
    evmAddress: u.address,
    solanaAddress: u.solanaAddress,
    stellarAddress: u.stellarAddress,
    tronAddress: u.tronAddress,
    userId: u.id,
    name: `${u.firstName} ${u.lastName}`,
    email: u.email,
  });
})()
```

### Step 4 — Return the result

Parse the JSON returned by the script and present it clearly:

- **EVM wallet address** (collateral contract admin): the `evmAddress` field — this is the primary address, the one set as admin on the user's Rain smart contract
- **Solana address**: `solanaAddress` (if set)
- **Stellar / Tron**: surface these too if non-null

If `evmAddress` is null, note that this user may not have an EVM wallet set.

## Error handling

| Situation | What to do |
|---|---|
| `No authToken found` | Ask the user to open Weather Station in Chrome and log in, then retry |
| 401 Unauthorized | The session may have expired — ask the user to log in to Weather Station again |
| 404 / User not found | Confirm the user ID is correct; double-check it's a production (not sandbox) ID |
| Connection refused / timeout | Likely not on VPN — ask the user to connect to VPN and retry |

## Example output

For user `e6a8122e-69b8-40c6-8d89-f940517b66db`:

> **Collateral contract admin for kairi takeuchi**
> - EVM wallet: `0xF0B19284e43BB74350A6bdD9ff479Fa8c6287753`
> - Solana: `3HWSeVgzPfKACu9eQ795hWxeUzhtJPaWaEkCBo4XwR8f`
