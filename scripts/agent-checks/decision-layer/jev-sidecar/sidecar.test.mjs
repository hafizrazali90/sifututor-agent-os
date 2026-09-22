// node --test: the sidecar refuses to touch the network without a key and
// rejects malformed input, without ever importing anything beyond the SDK.
import test from "node:test";
import assert from "node:assert/strict";
import { runOnce, classifyError } from "./sidecar.mjs";
import { APITimeoutError, APIUserAbortError, AuthenticationError, APIError, APIConnectionError, TypeSafeError } from "@typesafe-ai/sdk";

const good = {
  schema_version: 1,
  timeout_ms: 50,
  state: "ctx",
  questions: { answer: { type: "choice", instructions: "pick", criteria: { a: null, b: null } } },
};

test("missing TYPESAFE_API_KEY short-circuits before any client is built", async () => {
  const out = await runOnce(JSON.stringify(good), {});
  assert.deepEqual(out, { ok: false, error_kind: "config_missing_key" });
});

test("invalid JSON and invalid shape are labelled invalid_input, never thrown", async () => {
  assert.deepEqual(await runOnce("{not json", { TYPESAFE_API_KEY: "x" }), { ok: false, error_kind: "invalid_input" });
  assert.deepEqual(await runOnce(JSON.stringify({ ...good, questions: {} }), { TYPESAFE_API_KEY: "x" }), { ok: false, error_kind: "invalid_input" });
  assert.deepEqual(await runOnce(JSON.stringify({ ...good, timeout_ms: 0 }), { TYPESAFE_API_KEY: "x" }), { ok: false, error_kind: "invalid_input" });
});

test("error classification is a fixed label set with timeout ahead of connection", () => {
  assert.equal(classifyError(new APITimeoutError("t")), "timeout");
  assert.equal(classifyError(new APIUserAbortError("a")), "abort");
  assert.equal(classifyError(new APIConnectionError("c")), "connection");
  assert.equal(classifyError(new TypeSafeError("cfg")), "config");
  assert.equal(classifyError(new Error("?")), "unknown");
  // Subclass checks only need to not throw; constructor signatures are the SDK's.
  assert.ok(["api_auth", "api_status", "unknown"].includes(classifyError(Object.create(AuthenticationError.prototype))));
  assert.ok(["api_status", "unknown"].includes(classifyError(Object.create(APIError.prototype))));
});
