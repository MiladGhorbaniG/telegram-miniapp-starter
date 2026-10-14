export function readInitData(telegram) {
  const data = telegram && telegram.WebApp && telegram.WebApp.initData;
  return typeof data === "string" ? data : "";
}

export function authHeaders(initData, demoUserId = "1001") {
  if (initData) {
    return { Authorization: `TMA ${initData}` };
  }
  return { "X-Dev-User": String(demoUserId) };
}

export function formatPrice(cents) {
  return `$${(cents / 100).toFixed(2)}`;
}
