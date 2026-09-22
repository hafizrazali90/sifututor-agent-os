#!/usr/bin/env node
// Thin sidecar around the official @typesafe-ai/sdk (TypeSafeClient.systemOne).
//
// Protocol (schema_version 1), one JSON document in on stdin, one JSON line out:
//   in : { schema_version: 1, timeout_ms, state, questions, base_url?, model? }
//   ok : { schema_version: 1, ok: true,  result: { model, answers, usage } }
//   err: { schema_version: 1, ok: false, error_kind }
//
// Rules this file enforces on purpose:
//   * No policy. Question building and answer validation live in the Python
//     caller (provider_jev.py); this file only moves bytes through the SDK.
//   * SDK retries are disabled (retry.maxRetries = 0). The Python caller owns
//     retry and its single-in-flight guard, so a timeout can never leave a
//     second request running.
//   * A hard AbortController deadline aborts the in-flight request at
//     timeout_ms even if the SDK's own timeout does not fire first.
//   * error_kind is a fixed label. Messages, response bodies and stack traces
//     are never written to stdout, so the Python metadata-only log stays clean.
//   * TYPESAFE_API_KEY is read only by the SDK (its documented fallback); this
//     file never prints, copies or forwards it.

import {
  TypeSafeClient,
  TypeSafeError,
  APIError,
  APIConnectionError,
  APITimeoutError,
  APIUserAbortError,
  AuthenticationError,
  RateLimitError,
} from "@typesafe-ai/sdk";

const SCHEMA_VERSION = 1;

function emit(body) {
  process.stdout.write(JSON.stringify({ schema_version: SCHEMA_VERSION, ...body }) + "\n");
}

function fail(errorKind) {
  emit({ ok: false, error_kind: errorKind });
}

function readStdin() {
  return new Promise((resolve) => {
    const chunks = [];
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (c) => chunks.push(c));
    process.stdin.on("end", () => resolve(chunks.join("")));
  });
}

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validateInput(input) {
  if (!isPlainObject(input) || input.schema_version !== SCHEMA_VERSION) return false;
  if (!Number.isInteger(input.timeout_ms) || input.timeout_ms <= 0) return false;
  if (!isPlainObject(input.questions) || Object.keys(input.questions).length === 0) return false;
  if (input.base_url !== undefined && typeof input.base_url !== "string") return false;
  if (input.model !== undefined && typeof input.model !== "string") return false;
  return true;
}

export function classifyError(error) {
  // Order matters: APITimeoutError extends APIConnectionError.
  if (error instanceof APIUserAbortError) return "abort";
  if (error instanceof APITimeoutError) return "timeout";
  if (error instanceof AuthenticationError) return "api_auth";
  if (error instanceof RateLimitError) return "api_rate_limit";
  if (error instanceof APIError) return "api_status";
  if (error instanceof APIConnectionError) return "connection";
  if (error instanceof TypeSafeError) return "config";
  return "unknown";
}

export async function runOnce(rawInput, env = process.env) {
  let input;
  try {
    input = JSON.parse(rawInput);
  } catch {
    return { ok: false, error_kind: "invalid_input" };
  }
  if (!validateInput(input)) return { ok: false, error_kind: "invalid_input" };
  if (!env.TYPESAFE_API_KEY) return { ok: false, error_kind: "config_missing_key" };

  const controller = new AbortController();
  const deadline = setTimeout(() => controller.abort(), input.timeout_ms);
  try {
    const client = new TypeSafeClient({
      ...(input.base_url ? { baseURL: input.base_url } : {}),
      timeout: input.timeout_ms,
      retry: { maxRetries: 0 },
      logLevel: "off",
    });
    const request = { state: input.state ?? null, questions: input.questions };
    if (input.model) request.model = input.model;
    const result = await client.systemOne(request, { signal: controller.signal, timeout: input.timeout_ms });
    return { ok: true, result: { model: result.model, answers: result.answers, usage: result.usage } };
  } catch (error) {
    return { ok: false, error_kind: classifyError(error) };
  } finally {
    clearTimeout(deadline);
  }
}

const invokedDirectly = process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href;
if (invokedDirectly) {
  const raw = await readStdin();
  const outcome = await runOnce(raw);
  emit(outcome);
}
