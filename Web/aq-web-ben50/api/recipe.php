<?php
if(!in_array($_SERVER["REMOTE_ADDR"], ["127.0.0.1", "::1"])) {
	http_response_code(403);
	die("Access not allowed.");
} else {
	die("ASIS{fake_flag}");
}
