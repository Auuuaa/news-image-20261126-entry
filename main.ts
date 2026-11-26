// THE WORLD TODAY — news-image-20261126 entry point.
//
// render.py drew the front page into entry.png ahead of time. This
// program only confirms the PNG is whole and inside the bounty limits
// (1024x1024, at most 1 MiB, every chunk checksum valid), then
// copies it to the directory the harness asks for.
//
// The PNG is found next to this script, never next to the working
// directory: the grader may run node from anywhere, so looking the
// file up by a bare relative path would fail with ENOENT outside
// the repository.

import { crc32 } from "node:zlib";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const SIDE_PX = 1024;
const BYTE_CAP = 1024 * 1024;

const here = dirname(fileURLToPath(import.meta.url));
const pngPath = join(here, "entry.png");

function die(reason: string): never {
  console.error(`entry.png failed validation: ${reason}`);
  process.exit(1);
}

function checkImage(bytes: Buffer): void {
  if (bytes.length > BYTE_CAP) {
    die(`file is ${bytes.length} bytes, over the 1 MiB cap`);
  }
  if (bytes.length < PNG_MAGIC.length || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    die("missing PNG signature");
  }
  let cursor = 8;
  let headerSeen = false;
  let endSeen = false;
  while (cursor + 12 <= bytes.length) {
    const size = bytes.readUInt32BE(cursor);
    const type = bytes.toString("ascii", cursor + 4, cursor + 8);
    const payloadEnd = cursor + 8 + size;
    if (payloadEnd + 4 > bytes.length) {
      die(`chunk ${type} overruns the file`);
    }
    const expected = bytes.readUInt32BE(payloadEnd);
    const actual = crc32(bytes.subarray(cursor + 4, payloadEnd));
    if (expected !== actual) {
      die(`chunk ${type} has a bad CRC`);
    }
    if (type === "IHDR") {
      headerSeen = true;
      const w = bytes.readUInt32BE(cursor + 8);
      const h = bytes.readUInt32BE(cursor + 12);
      const depth = bytes[cursor + 16];
      const colourType = bytes[cursor + 17];
      if (w !== SIDE_PX || h !== SIDE_PX) {
        die(`image is ${w}x${h}, expected ${SIDE_PX}x${SIDE_PX}`);
      }
      if (depth !== 8 || (colourType !== 2 && colourType !== 6)) {
        die(`unexpected colour setup: depth ${depth}, type ${colourType}`);
      }
    }
    cursor = payloadEnd + 4;
    if (type === "IEND") {
      endSeen = true;
      break;
    }
  }
  if (!headerSeen) {
    die("no IHDR chunk");
  }
  if (!endSeen) {
    die("no IEND chunk — file is truncated");
  }
}

function main(): void {
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "./output";
  const bytes = readFileSync(pngPath);
  checkImage(bytes);
  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, "entry.png");
  copyFileSync(pngPath, target);
  const written = statSync(target).size;
  if (written !== bytes.length) {
    die(`copied ${written} bytes, expected ${bytes.length}`);
  }
  const again = readFileSync(target);
  if (!again.equals(bytes)) {
    die("copied file differs from entry.png");
  }
  console.log(`entry.png OK: ${SIDE_PX}x${SIDE_PX}, ${bytes.length} bytes -> ${target}`);
}

main();
