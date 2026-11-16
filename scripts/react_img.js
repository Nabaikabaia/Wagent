import { prepareWAMessageMedia } from '@whiskeysockets/baileys';
import { readFileSync } from 'node:fs';
import path from 'node:path';

export class ReactImg {
  constructor(conn) {
    if (!conn || typeof conn.relayMessage !== 'function' || typeof conn.waUploadToServer !== 'function') {
      throw new TypeError('Compatible Baileys connection required');
    }
    this.conn = conn;
  }
  build({ parentMessageKey, associationType = 11, stickerMessage }) {
    if (!parentMessageKey || typeof parentMessageKey.id !== 'string' ||
        typeof parentMessageKey.remoteJid !== 'string') throw new TypeError('A complete parentMessageKey is required');
    if (!stickerMessage || typeof stickerMessage !== 'object') throw new TypeError('Prepared stickerMessage is required');
    return { messageContextInfo: { messageAssociation: { associationType, parentMessageKey } }, stickerMessage };
  }
  async send(chatId, { parentMessageKey, associationType = 11, filePath }) {
    if (!filePath || path.extname(filePath).toLowerCase() !== '.webp') throw new TypeError('A local .webp sticker file is required');
    const media = await prepareWAMessageMedia(
      { sticker: readFileSync(filePath) },
      { upload: this.conn.waUploadToServer, mediaTypeOverride: 'sticker' }
    );
    return this.conn.relayMessage(chatId, this.build({
      parentMessageKey, associationType, stickerMessage: media.stickerMessage
    }), {});
  }
  static create(conn) { return new ReactImg(conn); }
}
export default ReactImg;
