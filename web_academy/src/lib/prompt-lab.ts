import { createServerFn } from "@tanstack/react-start";

const SYSTEM = `You are Imagine Prompt Master for Grok Imagine Cinematic Studio.
Rewrite the user's notes into ONE paste-ready cinematic still prompt.
Order: subject → environment → lighting → lens → mood.
End with a short Negatives line.
No preamble, no markdown fences, no title — only the prompt body.
Keep under 120 words. Adult fictional characters only.`;

export type EnhanceResult =
  | { ok: true; text: string }
  | { ok: false; error: string };

export const enhanceCinematicPrompt = createServerFn({ method: "POST" })
  .inputValidator((input: { notes: string }) => {
    const notes = (input?.notes ?? "").trim();
    if (!notes) throw new Error("Notes are required");
    if (notes.length > 800) throw new Error("Notes too long (max 800 chars)");
    return { notes };
  })
  .handler(async ({ data }): Promise<EnhanceResult> => {
    const apiKey = process.env.XAI_API_KEY;
    if (!apiKey) {
      return { ok: false, error: "AI is not available in this environment" };
    }

    try {
      const res = await fetch("https://api.x.ai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "grok-4.5",
          max_tokens: 280,
          temperature: 0.7,
          messages: [
            { role: "system", content: SYSTEM },
            {
              role: "user",
              content: `Craft a Grok Imagine still prompt from:\n${data.notes}`,
            },
          ],
        }),
        signal: AbortSignal.timeout(20_000),
      });

      if (!res.ok) {
        return { ok: false, error: `xAI API error ${res.status}` };
      }

      const body = (await res.json()) as {
        choices?: { message?: { content?: string } }[];
      };
      const text = body.choices?.[0]?.message?.content?.trim() ?? "";
      if (!text) return { ok: false, error: "Empty response from model" };
      return { ok: true, text };
    } catch (e) {
      if (e instanceof Error && e.name === "TimeoutError") {
        return { ok: false, error: "Request timed out — try Assemble instead" };
      }
      return { ok: false, error: "Network error calling xAI" };
    }
  });
