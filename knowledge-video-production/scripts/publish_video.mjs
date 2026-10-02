#!/usr/bin/env node
// Node >= 22. Credentials are loaded from a local file or the process environment.
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import path from 'node:path';

const help = `Publish a final knowledge video to Alibaba OSS and verify anonymous access.
Usage: node publish_video.mjs --video FILE --topic SLUG --prefix PROJECT/knowledge-videos
       --output TOPIC/video/publication.json [--poster FILE] [--title TEXT]
       [--env-file LOCAL_ENV] [--sdk-root DIRECTORY] [--ffprobe BINARY] [--dry-run]
Required environment for publishing: OSS_REGION, OSS_BUCKET, OSS_ACCESS_KEY_ID,
OSS_ACCESS_KEY_SECRET. Install ali-oss locally or supply an existing --sdk-root.
The prefix is explicit; an inherited OSS_PREFIX is never used. No objects are deleted.`;

async function hashFile(file) {
  const hash = createHash('sha256');
  for await (const chunk of createReadStream(file)) hash.update(chunk);
  return hash.digest('hex');
}

function parseArgs(argv) {
  const result = {};
  const values = new Set(['video', 'topic', 'prefix', 'output', 'poster', 'title', 'env-file', 'sdk-root', 'ffprobe']);
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i].replace(/^--/, '');
    if (['help', 'dry-run'].includes(key)) result[key] = true;
    else if (argv[i].startsWith('--') && values.has(key) && argv[i + 1] && !argv[i + 1].startsWith('--')) result[key] = argv[++i];
    else throw new Error('Invalid or missing command-line argument; use --help.');
  }
  return result;
}

async function verifyPublic(url, expected, ranges) {
  const head = await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(60_000) });
  if (head.status !== 200 || Number(head.headers.get('content-length')) !== expected.bytes
      || head.headers.get('content-type')?.split(';')[0] !== expected.contentType) {
    throw new Error(`Anonymous HEAD verification failed (${head.status}).`);
  }
  const verified = { headStatus: head.status, contentLength: expected.bytes, contentType: expected.contentType };
  if (ranges) {
    const range = await fetch(url, { headers: { Range: 'bytes=0-1023' }, signal: AbortSignal.timeout(60_000) });
    const bytes = new Uint8Array(await range.arrayBuffer());
    const contentRange = range.headers.get('content-range');
    if (range.status !== 206 || bytes.length !== 1024 || contentRange !== `bytes 0-1023/${expected.bytes}`) {
      throw new Error(`Anonymous Range verification failed (${range.status}).`);
    }
    Object.assign(verified, { rangeStatus: 206, rangeBytes: bytes.length, contentRange });
  }
  const full = await fetch(url, { signal: AbortSignal.timeout(180_000) });
  if (full.status !== 200 || !full.body) throw new Error(`Anonymous download failed (${full.status}).`);
  const hash = createHash('sha256');
  let count = 0;
  for await (const chunk of full.body) { hash.update(chunk); count += chunk.length; }
  if (count !== expected.bytes || hash.digest('hex') !== expected.sha256) throw new Error('Downloaded object differs from the local final file.');
  return { ...verified, fullDownloadSha256Matches: true, verifiedAt: new Date().toISOString() };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) { console.log(help); return; }
  for (const key of ['video', 'topic', 'prefix', 'output']) if (!args[key]) throw new Error(`Missing --${key}; use --help.`);
  if (!/^[a-z0-9][a-z0-9-]*$/.test(args.topic) || !/^[a-z0-9][a-z0-9_/-]*$/.test(args.prefix)
      || args.prefix.includes('..') || args.prefix.endsWith('/')) throw new Error('Use a safe topic slug and an explicit project prefix.');
  const video = path.resolve(args.video);
  if (path.extname(video).toLowerCase() !== '.mp4') throw new Error('The final delivery must be an MP4 file.');
  const probe = spawnSync(args.ffprobe || 'ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-show_chapters', '-of', 'json', video], { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
  if (probe.status !== 0) throw new Error('ffprobe failed; supply the correct --ffprobe executable and an existing final MP4.');
  const media = JSON.parse(probe.stdout);
  const v = media.streams.find(s => s.codec_type === 'video');
  const a = media.streams.find(s => s.codec_type === 'audio');
  if (v?.codec_name !== 'h264' || a?.codec_name !== 'aac') throw new Error('Expected a browser-compatible H.264 / AAC final file.');
  const [numerator, denominator] = v.avg_frame_rate.split('/').map(Number);
  const plan = [];
  for (const [kind, file, contentType] of [['video', video, 'video/mp4'], ...(args.poster ? [['poster', path.resolve(args.poster), 'image/jpeg']] : [])]) {
    if (kind === 'poster' && !/\.jpe?g$/i.test(file)) throw new Error('The optional poster must be a JPEG.');
    const bytes = (await stat(file)).size;
    const sha256 = await hashFile(file);
    const filename = path.basename(file);
    if (!/^[a-zA-Z0-9._-]+$/.test(filename)) throw new Error('Use a URL-safe media filename.');
    plan.push({ kind, file, key: `${args.prefix}/${args.topic}/${sha256.slice(0, 16)}/${filename}`, bytes, sha256, contentType });
  }
  if (args['dry-run']) {
    console.log(JSON.stringify({ dryRun: true, planned: plan.map(({ file, ...asset }) => asset), media: { width: v.width, height: v.height, durationSeconds: Number(media.format.duration), fps: numerator / denominator } }, null, 2));
    return;
  }
  if (args['env-file']) process.loadEnvFile(path.resolve(args['env-file']));
  const env = process.env;
  if (['OSS_REGION', 'OSS_BUCKET', 'OSS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_SECRET'].some(k => !env[k])) throw new Error('OSS configuration is incomplete; credentials remain in a local ignored file.');
  if (!/^oss-[a-z0-9-]+$/.test(env.OSS_REGION) || !/^[a-z0-9][a-z0-9-]+$/.test(env.OSS_BUCKET)) throw new Error('Unexpected OSS region or bucket format.');
  const require = createRequire(args['sdk-root'] ? path.join(path.resolve(args['sdk-root']), 'package.json') : import.meta.url);
  const OSS = require('ali-oss');
  const client = new OSS({ region: env.OSS_REGION, bucket: env.OSS_BUCKET, accessKeyId: env.OSS_ACCESS_KEY_ID, accessKeySecret: env.OSS_ACCESS_KEY_SECRET, secure: true, authorizationV4: true, timeout: 180_000 });
  const assets = {};
  for (const item of plan) {
    let existing;
    try { existing = await client.head(item.key); }
    catch (error) { if (error.status !== 404 && error.code !== 'NoSuchKey') throw error; }
    if (existing) {
      const headers = existing.res?.headers || {};
      if (Number(headers['content-length']) !== item.bytes || headers['x-oss-meta-sha256'] !== item.sha256) throw new Error('A conflicting object already exists; no object has been overwritten.');
    } else {
      const headers = { 'Content-Type': item.contentType, 'Cache-Control': 'public, max-age=31536000, immutable', 'x-oss-object-acl': 'public-read', 'x-oss-meta-sha256': item.sha256 };
      if (item.bytes > 1024 * 1024) await client.multipartUpload(item.key, item.file, { partSize: 1024 * 1024, parallel: 2, mime: item.contentType, headers });
      else await client.put(item.key, item.file, { mime: item.contentType, headers });
    }
    const url = `https://${env.OSS_BUCKET}.${env.OSS_REGION}.aliyuncs.com/${item.key}`;
    const verification = await verifyPublic(url, item, item.kind === 'video');
    assets[item.kind] = { url, key: item.key, bytes: item.bytes, sha256: item.sha256, contentType: item.contentType, verification };
    console.log(`Published and verified ${item.kind}: ${url}`);
  }
  const manifest = {
    schemaVersion: 1, title: args.title || args.topic, topic: args.topic,
    publishedAt: new Date().toISOString(),
    durationSeconds: Number(media.format.duration), width: v.width, height: v.height,
    fps: numerator / denominator, videoCodec: v.codec_name, audioCodec: a.codec_name,
    frameCount: Number(v.nb_frames) || null,
    chapters: media.chapters.map(c => ({ title: c.tags?.title || '', start: Number(c.start_time), end: Number(c.end_time) })),
    assets,
  };
  const output = path.resolve(args.output);
  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(output, JSON.stringify(manifest, null, 2) + '\n');
  console.log('Public publication manifest saved. Browser playback validation is a separate required step.');
}

main().catch(error => {
  // SDK errors can carry signed requests. Never dump error objects or request URLs.
  const known = error.constructor === Error && !error.code ? error.message : `Object-storage request failed (code ${String(error.code || 'unknown').replace(/[^a-zA-Z0-9_-]/g, '')}, status ${Number(error.status) || 'unknown'}).`;
  console.error(known);
  process.exitCode = 1;
});
