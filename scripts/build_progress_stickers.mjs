#!/usr/bin/env node
import sharp from 'sharp';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';

const stages = {
  'on-it': 'ON IT', thinking: 'THINKING', searching: 'SEARCHING',
  coding: 'COOKING', 'still-on-it': 'STILL ON IT',
  'almost-done': 'ALMOST DONE', done: 'DONE', error: 'OOPS', approval: 'YOUR MOVE'
};
const hermesHome = process.env.HERMES_HOME || path.join(os.homedir(), '.hermes');
const output = path.resolve(process.argv[2] || path.join(hermesHome, 'whatsapp', 'progress-stickers'));
await mkdir(output, { recursive: true });

function makeSvg(label, stage) {
  const fontSize = label.length > 9 ? 58 : 76;
  const accent = stage === 'done' ? '#8CF0B0' : stage === 'error' ? '#FF8585' : '#F8D77A';
  const safe = label.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  return '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">' +
    '<defs><linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#252B39"/><stop offset="1" stop-color="#080B12"/></linearGradient>' +
    '<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="' + accent + '"/></linearGradient>' +
    '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>' +
    '<rect x="24" y="24" width="464" height="464" rx="112" fill="url(#glass)" stroke="' + accent + '" stroke-opacity=".85" stroke-width="9"/>' +
    '<rect x="43" y="43" width="426" height="426" rx="96" fill="none" stroke="#FFFFFF" stroke-opacity=".22" stroke-width="3"/>' +
    '<path d="M90 116 Q256 40 422 116" fill="none" stroke="#FFFFFF" stroke-opacity=".16" stroke-width="5"/>' +
    '<circle cx="256" cy="170" r="10" fill="' + accent + '" filter="url(#glow)"/>' +
    '<text x="256" y="292" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="' + fontSize + '" font-weight="900" letter-spacing="2" fill="url(#gold)" stroke="#111722" stroke-width="3" paint-order="stroke" filter="url(#glow)">' + safe + '</text>' +
    '<path d="M142 344 H370" stroke="' + accent + '" stroke-width="5" stroke-linecap="round" opacity=".8"/>' +
    '<text x="256" y="395" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" letter-spacing="6" fill="#FFFFFF" opacity=".72">NABEES AGENT</text></svg>';
}
for (const [stage, label] of Object.entries(stages)) {
  await sharp(Buffer.from(makeSvg(label, stage))).webp({ quality: 92, effort: 6 })
    .toFile(path.join(output, stage + '.webp'));
  console.log('Built ' + stage + '.webp');
}
console.log('Progress stickers ready: ' + output);
