/**
 * Nabees WhatsApp AIRich transport.
 * Uses the original NixCode AIRich builder; attribution and license are
 * preserved in ./nixcode.js. No per-message Nabees branding is injected.
 */
import { AIRich } from './nixcode.js';

const QUOTE_NUMBER = '18002428478';
const QUOTE_DISPLAY = 'OpenAI';
const QUOTE_VCARD =
  'BEGIN:VCARD\n' +
  'VERSION:3.0\n' +
  'N:XL;OpenAI,;;;\n' +
  'FN:OpenAI\n' +
  'ORG:OpenAI;\n' +
  'item1.TEL;waid=' + QUOTE_NUMBER + ':+1 (800) 242-8478\n' +
  'item1.X-ABLabel:Phone\n' +
  'END:VCARD';

function addMarkdown(rich, markdown) {
  const source = String(markdown ?? '');
  const codeBlock = /```([a-zA-Z0-9_+#.-]*)[^\S\r\n]*\r?\n([\s\S]*?)\r?\n```/g;
  let cursor = 0;
  let match;
  while ((match = codeBlock.exec(source)) !== null) {
    const before = source.slice(cursor, match.index);
    if (before.trim()) rich.addText(before);
    const language = (match[1] || 'javascript').toLowerCase();
    rich.addCode(language, match[2]);
    cursor = codeBlock.lastIndex;
  }
  const rest = source.slice(cursor);
  if (rest.trim() || cursor === 0) rich.addText(rest || ' ');
}

export async function sendNabeesAIRich(sock, chatId, text) {
  if (!sock || typeof sock.relayMessage !== 'function') {
    throw new TypeError('A connected WhatsApp socket is required for AIRich');
  }
  if (typeof chatId !== 'string' || !chatId) {
    throw new TypeError('A WhatsApp chat JID is required');
  }

  const rich = new AIRich(sock)
    .setTitle('ChatGPT-5')
    .setContextInfo({
      participant: '0@s.whatsapp.net',
      quotedMessage: {
        contactMessage: {
          displayName: QUOTE_DISPLAY,
          vcard: QUOTE_VCARD,
        },
      },
      isForwarded: true,
      forwardingScore: 999,
    });

  addMarkdown(rich, String(text ?? ''));

  // AIRich.send performs relayMessage followed by sendEdit. The caller must
  // hold the bridge send queue for the complete operation.
  return rich.send(chatId, {
    forwarded: true,
    bypassDownload: true,
    notification: false,
  });
}

export default sendNabeesAIRich;
