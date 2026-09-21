import http from "node:http";
import { readFile, writeFile, mkdir, stat } from "node:fs/promises";
import { createReadStream } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { randomBytes, scrypt as scryptCallback, timingSafeEqual } from "node:crypto";
import { promisify } from "node:util";

const scrypt = promisify(scryptCallback);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.join(__dirname, "public");
const dataDir = path.join(__dirname, "data");
const dbPath = path.join(dataDir, "db.json");
const PORT = Number(process.env.PORT || 3000);
const SESSION_COOKIE = "stockify_session";
const PRICE_CACHE_TTL = 15 * 60 * 1000;
const priceCache = new Map();

await mkdir(dataDir, { recursive: true });
try { await stat(dbPath); } catch { await writeFile(dbPath, JSON.stringify({ users: [], sessions: [], products: [] }, null, 2)); }

async function loadDb() {
  return JSON.parse(await readFile(dbPath, "utf8"));
}
async function saveDb(db) {
  await writeFile(dbPath, JSON.stringify(db, null, 2));
}
function nextId(items) {
  return items.reduce((max, item) => Math.max(max, Number(item.id) || 0), 0) + 1;
}
function json(res, status, data, headers = {}) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8", ...headers });
  res.end(JSON.stringify(data));
}
function noContent(res, headers = {}) {
  res.writeHead(204, headers);
  res.end();
}
function parseCookies(req) {
  const raw = req.headers.cookie || "";
  return Object.fromEntries(raw.split(";").map(v => v.trim()).filter(Boolean).map(pair => {
    const idx = pair.indexOf("=");
    return [decodeURIComponent(pair.slice(0, idx)), decodeURIComponent(pair.slice(idx + 1))];
  }));
}
async function bodyJson(req) {
  let body = "";
  for await (const chunk of req) {
    body += chunk;
    if (body.length > 1_000_000) throw new Error("Request body too large");
  }
  if (!body) return {};
  try { return JSON.parse(body); } catch { throw new Error("Invalid JSON body"); }
}
async function hashPassword(password) {
  const salt = randomBytes(16).toString("hex");
  const derived = await scrypt(password, salt, 64);
  return `${salt}:${Buffer.from(derived).toString("hex")}`;
}
async function verifyPassword(password, stored) {
  const [salt, hash] = String(stored || "").split(":");
  if (!salt || !hash) return false;
  const derived = Buffer.from(await scrypt(password, salt, 64));
  const expected = Buffer.from(hash, "hex");
  return expected.length === derived.length && timingSafeEqual(expected, derived);
}
function publicUser(user) {
  return {
    id: user.id,
    fullName: user.fullName,
    mobile: user.mobile,
    email: user.email,
    shopName: user.shopName,
    marketLatitude: user.marketLatitude ?? null,
    marketLongitude: user.marketLongitude ?? null,
    marketPincode: user.marketPincode ?? "",
  };
}
function sessionCookie(token, clear = false) {
  const secure = process.env.NODE_ENV === "production" ? "; Secure" : "";
  return `${SESSION_COOKIE}=${clear ? "" : encodeURIComponent(token)}; Path=/; HttpOnly; SameSite=Lax${secure}; Max-Age=${clear ? 0 : 60 * 60 * 24 * 30}`;
}
async function authenticatedUser(req, db) {
  const token = parseCookies(req)[SESSION_COOKIE];
  if (!token) return null;
  const session = db.sessions.find(s => s.token === token && new Date(s.expiresAt).getTime() > Date.now());
  if (!session) return null;
  return db.users.find(u => u.id === session.userId) || null;
}
function cleanText(value) { return typeof value === "string" ? value.trim() : ""; }
function validProductInput(body, partial = false) {
  const result = {};
  const fields = ["productId", "name", "category"];
  for (const key of fields) {
    if (!partial || key in body) {
      const value = cleanText(body[key]);
      if (!value) return { error: `${key} is required.` };
      result[key] = value;
    }
  }
  for (const key of ["quantity", "minimumStock"]) {
    if (!partial || key in body) {
      const value = Number(body[key]);
      if (!Number.isInteger(value) || value < 0) return { error: `${key} must be a non-negative integer.` };
      result[key] = value;
    }
  }
  if (!partial || "price" in body) {
    const price = Number(body.price);
    if (!Number.isFinite(price) || price < 0) return { error: "price must be a non-negative number." };
    result.price = price;
  }
  return { value: result };
}

const demoProducts = [
  ["WM-100", "Wireless Mouse", "Electronics", 34, 799, 8],
  ["KB-220", "Mechanical Keyboard", "Electronics", 12, 2499, 5],
  ["CB-310", "USB-C Cable", "Accessories", 68, 349, 15],
  ["SP-410", "Bluetooth Speaker", "Electronics", 7, 1799, 8],
  ["PB-520", "Power Bank 10000mAh", "Accessories", 18, 1299, 6],
  ["LS-630", "Laptop Stand", "Office", 9, 1199, 5],
  ["LB-740", "LED Bulb 12W", "Home", 42, 199, 12],
  ["NB-850", "Premium Notebook", "Stationery", 26, 149, 10],
  ["OC-960", "Ergonomic Office Chair", "Office", 3, 8499, 4],
  ["WB-107", "Steel Water Bottle", "Home", 0, 599, 6]
];

async function handleApi(req, res, url) {
  const method = req.method || "GET";
  const db = await loadDb();

  if (method === "GET" && url.pathname === "/api/healthz") return json(res, 200, { status: "ok" });

  if (method === "POST" && url.pathname === "/api/auth/register") {
    const body = await bodyJson(req);
    const fullName = cleanText(body.fullName), mobile = cleanText(body.mobile), email = cleanText(body.email).toLowerCase(), shopName = cleanText(body.shopName), password = typeof body.password === "string" ? body.password : "";
    if (!fullName || !mobile || !email || !shopName || !password) return json(res, 400, { error: "All registration fields are required." });
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json(res, 400, { error: "Enter a valid email address." });
    if (password.length < 8) return json(res, 400, { error: "Password must be at least 8 characters." });
    if (db.users.some(u => u.email === email)) return json(res, 409, { error: "An account with that email already exists." });
    const user = { id: nextId(db.users), fullName, mobile, email, shopName, marketLatitude: null, marketLongitude: null, marketPincode: "", passwordHash: await hashPassword(password), createdAt: new Date().toISOString() };
    db.users.push(user);
    const token = randomBytes(32).toString("hex");
    db.sessions.push({ token, userId: user.id, expiresAt: new Date(Date.now() + 30 * 86400000).toISOString() });
    await saveDb(db);
    return json(res, 201, { user: publicUser(user) }, { "Set-Cookie": sessionCookie(token) });
  }

  if (method === "POST" && url.pathname === "/api/auth/login") {
    const body = await bodyJson(req);
    const email = cleanText(body.email).toLowerCase();
    const password = typeof body.password === "string" ? body.password : "";
    const user = db.users.find(u => u.email === email);
    if (!user || !(await verifyPassword(password, user.passwordHash))) return json(res, 401, { error: "Incorrect email or password." });
    const token = randomBytes(32).toString("hex");
    db.sessions = db.sessions.filter(s => s.userId !== user.id || new Date(s.expiresAt).getTime() > Date.now());
    db.sessions.push({ token, userId: user.id, expiresAt: new Date(Date.now() + 30 * 86400000).toISOString() });
    await saveDb(db);
    return json(res, 200, { user: publicUser(user) }, { "Set-Cookie": sessionCookie(token) });
  }

  if (method === "POST" && url.pathname === "/api/auth/logout") {
    const token = parseCookies(req)[SESSION_COOKIE];
    if (token) { db.sessions = db.sessions.filter(s => s.token !== token); await saveDb(db); }
    return json(res, 200, { ok: true }, { "Set-Cookie": sessionCookie("", true) });
  }

  const user = await authenticatedUser(req, db);
  if (url.pathname === "/api/auth/me") return user ? json(res, 200, { user: publicUser(user) }) : json(res, 401, { error: "Not authenticated." });
  if (!user) return json(res, 401, { error: "Not authenticated." });

  if (method === "PATCH" && url.pathname === "/api/user/settings") {
    const body = await bodyJson(req);
    const fullName = cleanText(body.fullName);
    const mobile = cleanText(body.mobile);
    const shopName = cleanText(body.shopName);
    const pincode = cleanText(body.marketPincode);
    const latRaw = body.marketLatitude;
    const lonRaw = body.marketLongitude;

    if (!fullName || !mobile || !shopName) return json(res, 400, { error: "Name, mobile and shop name are required." });
    if (pincode && !/^[0-9]{6}$/.test(pincode)) return json(res, 400, { error: "PIN code must be 6 digits." });

    let marketLatitude = null;
    let marketLongitude = null;
    if (latRaw !== "" && latRaw != null) {
      marketLatitude = Number(latRaw);
      if (!Number.isFinite(marketLatitude) || marketLatitude < -90 || marketLatitude > 90) return json(res, 400, { error: "Latitude must be between -90 and 90." });
    }
    if (lonRaw !== "" && lonRaw != null) {
      marketLongitude = Number(lonRaw);
      if (!Number.isFinite(marketLongitude) || marketLongitude < -180 || marketLongitude > 180) return json(res, 400, { error: "Longitude must be between -180 and 180." });
    }
    if ((marketLatitude == null) !== (marketLongitude == null)) return json(res, 400, { error: "Enter both latitude and longitude, or leave both blank." });

    Object.assign(user, { fullName, mobile, shopName, marketPincode: pincode, marketLatitude, marketLongitude });
    await saveDb(db);
    return json(res, 200, { user: publicUser(user) });
  }

  if (method === "GET" && url.pathname === "/api/products") {
    const search = (url.searchParams.get("search") || "").toLowerCase();
    const category = url.searchParams.get("category") || "";
    let products = db.products.filter(p => p.userId === user.id);
    if (search) products = products.filter(p => p.name.toLowerCase().includes(search) || p.productId.toLowerCase().includes(search));
    if (category) products = products.filter(p => p.category === category);
    products.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
    return json(res, 200, products.map(({ userId, ...p }) => p));
  }

  if (method === "POST" && url.pathname === "/api/products") {
    const body = await bodyJson(req);
    const parsed = validProductInput(body);
    if (parsed.error) return json(res, 400, { error: parsed.error });
    if (db.products.some(p => p.userId === user.id && p.productId.toLowerCase() === parsed.value.productId.toLowerCase())) return json(res, 409, { error: "A product with that Product ID already exists." });
    const now = new Date().toISOString();
    const product = { id: nextId(db.products), userId: user.id, ...parsed.value, createdAt: now, updatedAt: now };
    db.products.push(product); await saveDb(db);
    const { userId, ...result } = product;
    return json(res, 201, result);
  }

  const productMatch = url.pathname.match(/^\/api\/products\/(\d+)$/);
  if (productMatch && method === "PATCH") {
    const id = Number(productMatch[1]);
    const product = db.products.find(p => p.id === id && p.userId === user.id);
    if (!product) return json(res, 404, { error: "Product not found." });
    const body = await bodyJson(req); const parsed = validProductInput(body, true);
    if (parsed.error) return json(res, 400, { error: parsed.error });
    if (parsed.value.productId && db.products.some(p => p.userId === user.id && p.id !== id && p.productId.toLowerCase() === parsed.value.productId.toLowerCase())) return json(res, 409, { error: "A product with that Product ID already exists." });
    Object.assign(product, parsed.value, { updatedAt: new Date().toISOString() });
    await saveDb(db); const { userId, ...result } = product; return json(res, 200, result);
  }
  if (productMatch && method === "DELETE") {
    const id = Number(productMatch[1]);
    const idx = db.products.findIndex(p => p.id === id && p.userId === user.id);
    if (idx < 0) return json(res, 404, { error: "Product not found." });
    db.products.splice(idx, 1); await saveDb(db); return noContent(res);
  }

  const adjustMatch = url.pathname.match(/^\/api\/products\/(\d+)\/adjust-stock$/);
  if (adjustMatch && method === "POST") {
    const id = Number(adjustMatch[1]);
    const product = db.products.find(p => p.id === id && p.userId === user.id);
    if (!product) return json(res, 404, { error: "Product not found." });
    const body = await bodyJson(req); const delta = Number(body.delta);
    if (!Number.isInteger(delta)) return json(res, 400, { error: "delta must be an integer." });
    if (product.quantity + delta < 0) return json(res, 400, { error: "Stock cannot go below zero." });
    product.quantity += delta; product.updatedAt = new Date().toISOString(); await saveDb(db);
    const { userId, ...result } = product; return json(res, 200, result);
  }

  if (method === "GET" && url.pathname === "/api/inventory/summary") {
    const products = db.products.filter(p => p.userId === user.id);
    const categories = new Map();
    for (const p of products) {
      const row = categories.get(p.category) || { category: p.category, quantity: 0, value: 0 };
      row.quantity += p.quantity; row.value += p.quantity * p.price; categories.set(p.category, row);
    }
    return json(res, 200, {
      totalProducts: products.length,
      totalUnits: products.reduce((s, p) => s + p.quantity, 0),
      lowStockProducts: products.filter(p => p.quantity <= p.minimumStock).length,
      inventoryValue: products.reduce((s, p) => s + p.quantity * p.price, 0),
      categoryBreakdown: [...categories.values()].sort((a, b) => b.value - a.value)
    });
  }

  if (method === "POST" && url.pathname === "/api/demo-data") {
    if (db.products.some(p => p.userId === user.id)) return json(res, 409, { error: "Demo data can only be added to an empty inventory." });
    const now = new Date().toISOString();
    for (const row of demoProducts) {
      const [productId, name, category, quantity, price, minimumStock] = row;
      db.products.push({ id: nextId(db.products), userId: user.id, productId, name, category, quantity, price, minimumStock, createdAt: now, updatedAt: now });
    }
    await saveDb(db); return json(res, 201, { ok: true, count: demoProducts.length });
  }

  if (method === "GET" && url.pathname === "/api/market-price") {
    const query = cleanText(url.searchParams.get("query"));
    const platform = cleanText(url.searchParams.get("platform")) || "Flipkart";
    if (!query) return json(res, 400, { error: "Product query is required." });
    const apiKey = process.env.QUICKCOMMERCE_API_KEY || process.env.MARKET_PRICE_API_KEY;
    const lat = user.marketLatitude;
    const lon = user.marketLongitude;
    const pincode = user.marketPincode || "";
    if (!apiKey) return json(res, 503, { error: "Market pricing is not configured by the app owner yet." });
    if (lat == null || lon == null) return json(res, 422, { error: "Set your shop latitude and longitude in Settings before checking market prices." });
    const cacheKey = `${platform}:${query}:${lat}:${lon}:${pincode}`.toLowerCase();
    const cached = priceCache.get(cacheKey);
    if (cached && cached.expiresAt > Date.now()) return json(res, 200, { ...cached.value, cached: true });
    const endpoint = new URL("https://api.quickcommerceapi.com/v1/search");
    endpoint.searchParams.set("q", query); endpoint.searchParams.set("lat", lat); endpoint.searchParams.set("lon", lon); endpoint.searchParams.set("platform", platform);
    if (pincode) endpoint.searchParams.set("pincode", pincode);
    const response = await fetch(endpoint, { headers: { "X-API-Key": apiKey, Accept: "application/json" } });
    if (!response.ok) return json(res, 502, { error: response.status === 402 ? "Market-price API credits are exhausted." : "Unable to retrieve market price." });
    const payload = await response.json();
    const products = (payload?.data?.products || []).filter(p => typeof p.offer_price === "number");
    if (!products.length) return json(res, 404, { error: `No online price found for “${query}”.` });
    const qWords = query.toLowerCase().split(/\s+/).filter(Boolean);
    const score = p => qWords.reduce((s, w) => s + ((p.name || "").toLowerCase().includes(w) ? 1 : 0), 0) + (p.available === false ? -10 : 0);
    products.sort((a, b) => score(b) - score(a));
    const p = products[0];
    const result = { query, productName: p.name || query, brand: p.brand || null, platform, marketPrice: p.offer_price, mrp: typeof p.mrp === "number" ? p.mrp : null, available: p.available !== false, quantity: p.quantity || null, productUrl: p.deeplink || null, fetchedAt: new Date().toISOString() };
    priceCache.set(cacheKey, { value: result, expiresAt: Date.now() + PRICE_CACHE_TTL });
    return json(res, 200, { ...result, cached: false });
  }

  return json(res, 404, { error: "API route not found." });
}

const mime = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon" };
async function serveStatic(req, res, url) {
  let pathname = url.pathname === "/" ? "/index.html" : url.pathname;
  let filePath = path.normalize(path.join(publicDir, pathname));
  if (!filePath.startsWith(publicDir)) return json(res, 403, { error: "Forbidden" });
  try {
    const info = await stat(filePath);
    if (!info.isFile()) throw new Error();
  } catch {
    filePath = path.join(publicDir, "index.html");
  }
  const ext = path.extname(filePath);
  res.writeHead(200, { "Content-Type": mime[ext] || "application/octet-stream", "Cache-Control": ext === ".html" ? "no-cache" : "public, max-age=3600" });
  createReadStream(filePath).pipe(res);
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);
    if (url.pathname.startsWith("/api/")) return await handleApi(req, res, url);
    return await serveStatic(req, res, url);
  } catch (error) {
    console.error(error);
    return json(res, 500, { error: error?.message === "Invalid JSON body" ? error.message : "Internal server error." });
  }
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Stockify running on http://0.0.0.0:${PORT}`);
});
