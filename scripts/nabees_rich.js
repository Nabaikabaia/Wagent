/**
 * Nabees WhatsApp response presentation.
 * Native WhatsApp formatting plus the OpenAI contact-card quote from the
 * original Nabees GPT-5 plugin. No third-party AIRich source is redistributed.
 */
const QUOTE_NUMBER = "18002428478";
const QUOTE_DISPLAY = "OpenAI";
const QUOTE_VCARD =
  "BEGIN:VCARD\\n" +
  "VERSION:3.0\\n" +
  "N:XL;OpenAI,;;;\\n" +
  "FN:OpenAI\\n" +
  "ORG:OpenAI;\\n" +
  "item1.TEL;waid=" + QUOTE_NUMBER + ":+1 (800) 242-8478\\n" +
  "item1.X-ABLabel:Phone\\n" +
  "END:VCARD";

function renderMarkdownTables(text) {
  return String(text).replace(
    /(?:^\\s*\\|[^\\n]*\\|\\s*\\n?){2,}/gm,
    (block) => {
      const rows = block.split("\\n")
        .map((line) => line.trim())
        .filter((line) => line.startsWith("|") && line.endsWith("|"))
        .map((line) => line.slice(1, -1).split("|").map((cell) => cell.trim()));
      if (rows.length < 2) return block;
      const headers = rows[0];
      const dataRows = rows.slice(1).filter((row) =>
        !row.every((cell) => /^:?-{3,}:?$/.test(cell))
      );
      if (!dataRows.length) return block;
      return dataRows.map((row) =>
        row.map((cell, index) => headers[index] ? "*" + headers[index] + ":* " + cell : cell).join("\\n")
      ).join("\\n\\n");
    }
  );
}

export function buildNabeesRichPayload(payload, isFirstChunk = false) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return payload;
  const result = { ...payload };
  if (typeof result.text === "string") {
    result.text = renderMarkdownTables(result.text);
    if (isFirstChunk) result.text = "*Nabees*\\n\\n" + result.text;
  } else if (result.extendedTextMessage && typeof result.extendedTextMessage.text === "string") {
    result.extendedTextMessage = { ...result.extendedTextMessage };
    result.extendedTextMessage.text = renderMarkdownTables(result.extendedTextMessage.text);
    if (isFirstChunk) result.extendedTextMessage.text = "*Nabees*\\n\\n" + result.extendedTextMessage.text;
  }
  if (isFirstChunk) {
    const contextInfo = result.contextInfo || result.extendedTextMessage?.contextInfo || {};
    const contactContext = {
      participant: "0@s.whatsapp.net",
      quotedMessage: { contactMessage: { displayName: QUOTE_DISPLAY, vcard: QUOTE_VCARD } },
      isForwarded: true,
      forwardingScore: 999
    };
    if (result.extendedTextMessage) {
      result.extendedTextMessage.contextInfo = { ...contextInfo, ...contactContext };
    } else {
      result.contextInfo = { ...contextInfo, ...contactContext };
    }
  }
  return result;
}
export default buildNabeesRichPayload;
