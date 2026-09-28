<?php
// Deliberately vulnerable "network diagnostics" tool — OS command injection.
// Representative of MS3-ub1404's web apps (e.g. cmd-passing PHP endpoints).
$host = isset($_REQUEST['host']) ? $_REQUEST['host'] : '';
?><!doctype html>
<html><head><title>Network Diagnostics</title></head>
<body>
<h2>Ping a host</h2>
<form method="get">
  <input name="host" value="<?php echo htmlspecialchars($host); ?>" placeholder="10.0.0.1">
  <button>ping</button>
</form>
<pre>
<?php
if ($host !== '') {
    // VULN: raw concatenation into a shell — no sanitisation.
    system("ping -c 1 " . $host);
}
?>
</pre>
</body></html>
