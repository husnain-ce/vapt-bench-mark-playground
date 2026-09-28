<?php
// Deliberately vulnerable "employee portal" — classic UNION-based SQL injection
// (mirrors MS3-ub1404's payroll_app.php style login). Backed by sqlite so the
// container stays lightweight; the injection semantics are identical to MySQL.
$dbfile = '/var/lib/ms3app/portal.db';
if (!file_exists($dbfile)) {
    @mkdir('/var/lib/ms3app', 0777, true);
    $db = new PDO('sqlite:' . $dbfile);
    $db->exec("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)");
    $db->exec("INSERT INTO users(username,password,role) VALUES
        ('admin','S3cr3tAdminPass!','admin'),
        ('hr','hunter2','staff'),
        ('leia_organa','help_me_obiwan','staff')");
    @chmod($dbfile, 0666);
}
$db = new PDO('sqlite:' . $dbfile);
$msg = '';
if (isset($_REQUEST['u'])) {
    $u = $_REQUEST['u'];
    $p = isset($_REQUEST['p']) ? $_REQUEST['p'] : '';
    // VULN: unparameterised string concatenation -> SQL injection.
    $sql = "SELECT username, role FROM users WHERE username = '$u' AND password = '$p'";
    try {
        $rows = $db->query($sql);
        $hit = false;
        foreach ($rows as $r) {
            $hit = true;
            $msg .= "Welcome " . $r['username'] . " (role=" . $r['role'] . ")\n";
        }
        if (!$hit) { $msg = "Invalid credentials"; }
    } catch (Exception $e) {
        $msg = "SQL error: " . $e->getMessage();
    }
}
?><!doctype html>
<html><head><title>Employee Portal</title></head>
<body>
<h2>Employee Portal</h2>
<form method="get">
  user: <input name="u"> pass: <input name="p" type="text"> <button>login</button>
</form>
<pre><?php echo htmlspecialchars($msg); ?></pre>
</body></html>
