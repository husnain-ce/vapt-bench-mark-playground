const http = require('http');
const mime = require('mime-types');
const fs = require('fs');
const path = require('path');

const DEBUG_TOKEN = process.env.DEBUG_TOKEN || '123456';
const HOST = '0.0.0.0';
const PORT = 1337;
const TEMPLATE_FOLDER = 'templates';
const DISALLOWED_CHARS = [
  "'",
  '"',
  '`',
  ',',
  '.',
  ':',
  'javascript',
  'on',
  'eval',
  'fetch',
  'function',
  'window',
  'top',
  'document',
  'alert',
  'console',
  'location',
  'src',
  '//',
];
const MAX_CODE_LENGTH = 300;

const parseTemplate = (templ) => {
  const templPath = path.join(__dirname, TEMPLATE_FOLDER, templ);
  if (!fs.existsSync(templPath)) throw new Error(`Template ${templ} does not exist.`);

  const content = fs.readFileSync(templPath, 'utf8');
  return content;
};

const serveStatic = (req, filePath) => {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    return new Response('File not found', { status: 404 });
  }
  const contentType = mime.lookup(fullPath) || 'application/octet-stream';
  const fileContent = fs.readFileSync(fullPath);
  return new Response(fileContent, {
    headers: {
      'Content-Type': `${contentType}; charset=utf-8`,
    },
  });
};

Bun.serve({
  hostname: HOST,
  port: PORT,
  fetch: async (req) => {
    const url = new URL(req.url);

    if (url.pathname.startsWith('/public/')) {
      const sanitizedPath = path.normalize(url.pathname);
      return serveStatic(req, sanitizedPath);
    }

    if (url.pathname === '/' || url.pathname === '') {
      if (req.method !== 'GET') {
        return new Response('Method Not Allowed', {
          status: 405,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' },
        });
      }

      const content = parseTemplate('index.html');
      return new Response(content, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    }

    if (url.pathname === '/make') {
      if (req.method !== 'GET') {
        return new Response('Method Not Allowed', {
          status: 405,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' },
        });
      }

      const code = url.searchParams.get('code') || '';

      for (const char of DISALLOWED_CHARS) {
        if (code.toLowerCase().includes(char)) {
          return new Response('Invalid code', {
            status: 400,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' },
          });
        }
      }

      if (code.length > MAX_CODE_LENGTH) {
        return new Response('Code too long', {
          status: 400,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' },
        });
      }

      let content = parseTemplate('make.html');
      content = content.replace('{{code}}', code);

      const res = new Response(content, {
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
      });
      return res;
    }

    // INFO: Still in development process (need debug token)
    if (url.pathname === '/get-github') {
      if (req.headers.get('DEBUG-TOKEN') !== DEBUG_TOKEN) {
        return new Response('This feature is still in development mode, so need debug token', {
          status: 401,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' },
        });
      }

      if (req.method === 'GET') {
        const content = parseTemplate('get-github.html');
        return new Response(content, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
      }

      if (req.method === 'POST') {
        const { url } = await req.json();
        if (!url) {
          return new Response('Invalid request body', {
            status: 400,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' },
          });
        }

        if (
          !url.startsWith('http://raw.githubusercontent.com') &&
          !url.startsWith('https://raw.githubusercontent.com')
        ) {
          return new Response('Invalid URL', {
            status: 400,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' },
          });
        }

        const res = await fetch(url);

        if (!res.ok) {
          return new Response(`Error fetching data: ${res.statusText}`, {
            status: res.status,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' },
          });
        }

        const data = await res.text();

        return new Response(data, {
          headers: { 'Content-Type': 'text/plain; charset=utf-8' },
        });
      }

      return new Response('Method Not Allowed', {
        status: 405,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      });
    }

    return new Response('Not Found', {
      status: 404,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  },
});
