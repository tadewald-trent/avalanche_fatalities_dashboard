const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, LevelFormat, convertInchesToTwip
} = require('docx');

const SRC = '../research_questions.md';
const OUT = '../research_questions.docx';

const raw = fs.readFileSync(SRC, 'utf-8');
const lines = raw.split('\n');

// ---- inline span parser: bold (**..**) and inline code (`..`) ----
function parseInline(text) {
  const runs = [];
  let i = 0;
  let buf = '';
  const flushPlain = () => {
    if (buf) {
      runs.push(new TextRun({ text: buf, font: 'Calibri' }));
      buf = '';
    }
  };
  while (i < text.length) {
    if (text.startsWith('**', i)) {
      const end = text.indexOf('**', i + 2);
      if (end !== -1) {
        flushPlain();
        runs.push(new TextRun({ text: text.slice(i + 2, end), bold: true, font: 'Calibri' }));
        i = end + 2;
        continue;
      }
    }
    if (text[i] === '`') {
      const end = text.indexOf('`', i + 1);
      if (end !== -1) {
        flushPlain();
        runs.push(new TextRun({
          text: text.slice(i + 1, end),
          font: 'Consolas',
          size: 20,
          shading: { fill: 'F0F0F0' },
        }));
        i = end + 1;
        continue;
      }
    }
    buf += text[i];
    i++;
  }
  flushPlain();
  return runs;
}

// ---- split source into blank-line-separated blocks, preserving raw lines per block ----
const blocks = [];
let cur = [];
for (const line of lines) {
  if (line.trim() === '') {
    if (cur.length) { blocks.push(cur); cur = []; }
  } else {
    cur.push(line);
  }
}
if (cur.length) blocks.push(cur);

const children = [];
// Each numbered-list block gets its own numbering reference so lists restart
// at 1 instead of continuing a shared counter across unrelated lists.
let listCounter = 0;
const numberingDefs = [];
function newListReference() {
  listCounter += 1;
  const reference = `list-${listCounter}`;
  numberingDefs.push({
    reference,
    levels: [
      {
        level: 0,
        format: LevelFormat.DECIMAL,
        text: '%1.',
        alignment: AlignmentType.START,
        style: { paragraph: { indent: { left: convertInchesToTwip(0.35), hanging: convertInchesToTwip(0.25) } } },
      },
    ],
  });
  return reference;
}

for (const block of blocks) {
  const first = block[0];

  // horizontal rule -> drop entirely (heading spacing-before substitutes)
  if (first.trim() === '---') continue;

  // top-level title line: "# Title — Subtitle"
  if (first.startsWith('# ')) {
    const text = first.slice(2).trim();
    const parts = text.split(' — ');
    children.push(new Paragraph({
      heading: HeadingLevel.TITLE,
      spacing: { after: 40 },
      children: [new TextRun({ text: parts[0] })],
    }));
    if (parts.length > 1) {
      children.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { after: 240 },
        children: [new TextRun({ text: parts.slice(1).join(' — ') })],
      }));
    }
    continue;
  }

  // section heading: "## ..."
  if (first.startsWith('## ')) {
    const text = first.slice(3).trim();
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 240, after: 160 },
      children: [new TextRun({ text })],
    }));
    continue;
  }

  // numbered list block: lines starting "N. " begin new items; indented continuation lines join prior item
  if (/^\d+\.\s/.test(first)) {
    const items = [];
    for (const line of block) {
      if (/^\d+\.\s/.test(line)) {
        items.push(line.replace(/^\d+\.\s/, ''));
      } else {
        items[items.length - 1] += ' ' + line.trim();
      }
    }
    const reference = newListReference();
    for (const item of items) {
      children.push(new Paragraph({
        numbering: { reference, level: 0 },
        spacing: { after: 160 },
        children: parseInline(item),
      }));
    }
    continue;
  }

  // plain paragraph: join wrapped lines with a single space
  const text = block.map(l => l.trim()).join(' ');
  children.push(new Paragraph({
    spacing: { after: 160 },
    children: parseInline(text),
  }));
}

const doc = new Document({
  numbering: { config: numberingDefs },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log('Wrote', OUT, buf.length, 'bytes');
});
