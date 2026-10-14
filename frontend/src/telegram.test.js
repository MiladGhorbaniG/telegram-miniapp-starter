import { describe, expect, it } from "vitest";
import { authHeaders, formatPrice, readInitData } from "./telegram.js";

describe("mini app helpers", () => {
  it("reads init data only when Telegram provides it", () => {
    expect(readInitData(undefined)).toBe("");
    expect(readInitData({ WebApp: { initData: "user=1&hash=abc" } })).toBe(
      "user=1&hash=abc",
    );
  });

  it("sends init data ahead of the demo user", () => {
    expect(authHeaders("signed")).toEqual({ Authorization: "TMA signed" });
    expect(authHeaders("")).toEqual({ "X-Dev-User": "1001" });
  });

  it("formats the reading room price", () => {
    expect(formatPrice(900)).toBe("$9.00");
  });
});
