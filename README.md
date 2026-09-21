# Stockify Inventory

A self-contained inventory management web app that can be stored on GitHub and deployed to any Node.js 18+ host.

## Features

- Sign up, sign in, sign out, persistent cookie sessions
- Per-user inventory isolation
- Product create/edit/delete
- Stock adjustment modal with guard against negative stock
- Search and category filters
- Inventory summary metrics and category breakdown
- Low-stock/out-of-stock notifications
- Responsive desktop table + mobile cards
- Subtle animations and reduced-motion support
- INR currency formatting
- Optional live Indian market-price lookup via QuickCommerce API
- Server-side market-price cache (15 minutes)
- Demo inventory loader
- Functional Inventory, Products, Analytics and Settings pages
- Per-user shop location for market-price searches

## Run locally

Requires Node.js 18+.

```bash
npm start
```

Open http://localhost:3000.

## GitHub

Create a repository and upload the contents of this folder. The runtime database file `data/db.json` is intentionally excluded from Git because it can contain user accounts, sessions and inventory data. The app creates it automatically on first start.

## Environment variables

Copy `.env.example` to your host's environment-variable/secrets configuration.

Required only for optional live market pricing:

```text
QUICKCOMMERCE_API_KEY=your_key_here
```

`PORT` is optional locally and defaults to 3000. Many hosting providers set it automatically.

Each Stockify user configures their own **PIN code, latitude and longitude** under **Settings → Shop location**. Those values are stored with that user's account, so different shops can receive location-relevant market prices.

The app does not automatically fetch a market price for every product. Click **Check price** on a product to avoid unnecessary external API usage.

## Storage

This version uses `data/db.json` so it runs without database setup. Passwords are hashed with Node's `scrypt`, and session tokens are stored in an HttpOnly cookie.

For a long-lived production deployment, replace the JSON store with PostgreSQL/Drizzle or another managed database because many hosts use ephemeral filesystems.

## Files

- `server.mjs` — API, authentication, storage, market-price lookup, static server
- `public/index.html` — page shell
- `public/styles.css` — responsive design and animations
- `public/app.js` — frontend application logic
- `data/db.example.json` — empty data-store example
- `.env.example` — environment-variable template
