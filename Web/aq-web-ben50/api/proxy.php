<?php
const ALLOWED_ORIGIN = 'https://img.proxydough.net/';
const ALLOWED_SCHEME = 'https';
const ALLOWED_HOST   = 'img.proxydough.net';

function deny(int $status, string $message): never
{
    http_response_code($status);
    header('Content-Type: text/plain; charset=utf-8');
    echo $message;
    exit;
}

$url = $_GET['url'] ?? '';
if ($url === '') {
    deny(400, 'Missing "url" parameter.');
}

$parts = parse_url($url);
if ($parts === false || !isset($parts['scheme'], $parts['host'])) {
    deny(400, 'Malformed URL.');
}

if (strtolower($parts['scheme']) !== ALLOWED_SCHEME
    || strtolower($parts['host']) !== ALLOWED_HOST) {
    deny(403, 'Host not allowed.');
}

$context = stream_context_create([
    'http' => [
        'method'          => 'GET',
        'user_agent'      => 'ProxyDough-ImageProxy/1.0',
        'timeout'         => 10,
        'ignore_errors'   => true,
    ],
    'ssl' => [
        'verify_peer'      => true,
        'verify_peer_name' => true,
    ],
]);

$body = @file_get_contents($url, false, $context);

if ($body === false || !isset($http_response_header)) {
    deny(502, 'Failed to fetch the requested asset.');
}

$status = 0;
if (preg_match('#\s(\d{3})\s#', $http_response_header[0], $m)) {
    $status = (int) $m[1];
}

if ($status === 0) {
    deny(502, 'Failed to fetch the requested asset.');
}

header('Content-Type: image/png');
header('Content-Length: ' . strlen($body));
header('Cache-Control: public, max-age=3600');
header('X-Content-Type-Options: nosniff');
echo $body;
