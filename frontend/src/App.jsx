import { useEffect, useState } from "react";
import { authHeaders, formatPrice, readInitData } from "./telegram.js";

const API = import.meta.env.VITE_API_URL || "http://localhost:8020";

export function App() {
  const [profile, setProfile] = useState(null);
  const [plans, setPlans] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [question, setQuestion] = useState("What is the late fee?");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const initData = readInitData(window.Telegram);
  const headers = {
    ...authHeaders(initData),
    "Content-Type": "application/json",
  };

  async function refresh() {
    const me = await fetch(`${API}/api/me`, { headers });
    if (!me.ok) throw new Error("The desk did not recognize this member.");
    setProfile(await me.json());
    const planResponse = await fetch(`${API}/api/plans`);
    setPlans(await planResponse.json());
    const current = await fetch(`${API}/api/subscriptions/current`, {
      headers,
    });
    const body = await current.json();
    setSubscription(body.subscription);
  }

  useEffect(() => {
    refresh().catch((err) => setError(err.message));
  }, []);

  async function subscribe(planId) {
    setBusy(true);
    setError("");
    try {
      const checkout = await fetch(`${API}/api/subscriptions/checkout`, {
        method: "POST",
        headers,
        body: JSON.stringify({ plan_id: planId }),
      });
      const started = await checkout.json();
      if (!checkout.ok) throw new Error(started.detail || "Checkout failed.");
      const confirmed = await fetch(`${API}/api/subscriptions/confirm`, {
        method: "POST",
        headers,
        body: JSON.stringify({ checkout_id: started.checkout_id }),
      });
      const done = await confirmed.json();
      if (!confirmed.ok) throw new Error("The mock provider did not confirm.");
      setSubscription(done);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function ask(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await fetch(`${API}/api/faq`, {
        method: "POST",
        headers,
        body: JSON.stringify({ question }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error("The desk notes did not answer.");
      setAnswer(body.answer);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>BookNook desk</h1>
      <p className="lede">
        {initData
          ? "Opened inside Telegram."
          : "Demo mode. The API is accepting the local dev member header."}
      </p>
      {profile ? (
        <p>
          {profile.first_name || "Member"} · id {profile.telegram_id}
        </p>
      ) : null}
      <section>
        {plans.map((plan) => (
          <article key={plan.id} className="card">
            <h2>{plan.title}</h2>
            <p>{plan.blurb}</p>
            <p>
              {formatPrice(plan.amount_cents)} / {plan.interval}
            </p>
            <button
              type="button"
              disabled={busy}
              onClick={() => subscribe(plan.id)}
            >
              {busy ? "Working…" : "Pay with the mock desk"}
            </button>
          </article>
        ))}
      </section>
      {subscription ? (
        <p>
          Plan {subscription.plan_id} is {subscription.status}.
          {subscription.receipt_ready
            ? ` ${subscription.receipt_note}`
            : " Receipt is still printing."}
        </p>
      ) : null}
      <form onSubmit={ask}>
        <label htmlFor="question">Ask the desk</label>
        <input
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button type="submit" disabled={busy}>
          Ask
        </button>
      </form>
      {answer ? <p>{answer}</p> : null}
      {error ? <p className="error">{error}</p> : null}
    </main>
  );
}
