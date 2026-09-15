<?php
$name = 'Bob';
$flag = 'ASIS{test-flag} - Admin (bot) has the real flag';
if(isset($_GET['wrong-user'])){
	echo 'username seems to be incorrect...';
	die();
}
if(isset($_GET['name'])){
	$name = $_GET['name'];
}
if(isset($_COOKIE['flag'])){
	$flag = $_COOKIE['flag'];
	if(isset($_GET['n'])){
		$flag = substr($flag,0,intval($_GET['n']));
	}
}
?>
<!DOCTYPE html>
<html>
<head>
	<title>Dangling</title>
	<meta http-equiv="Content-Security-Policy" content="child-src 'none'; script-src 'sha256-shg8OlN4zY3doFkqbsOiT8wlfB7Qrrw/44M507cGP3M='; style-src 'sha256-XSx24vDv8OWR3fxnxv9Bc/yD/h8eec55vh7PNn63yNs=';">
</head>
<body>
	<div>
		Hey <?= $name ?>, just press the button to get your flag
	</div>
	<button id="btn">
		Gimme flag
	</button>
	<flag id="flag"><?= $flag ?></flag>
	<style>
		body {
			font-family: 'arial';
			background-color: #DAD4B5;
			text-align: center;
			font-weight: bold;
			color: #800000;
			font-size: 20px;
		}

		div {
			margin-bottom: 15px;
			margin-top: 40px;
		}

		button {
			margin-bottom: 10px;
			background-color: #982B1C;
			border: 0px;
			font-size: 16px;
			padding: 10px 20px;
			font-family: 'arial';
			border-radius: 1px;
			color: #F2E8C6;
			cursor: pointer;
		}

		#flag {
			display: none;
		}

		#profilepic {
			border-radius: 5px;
			margin-top: 30px;
		}
	</style>
	<script>
		document.querySelector('#btn').onclick = _=>alert(document.querySelector('#flag').innerText)
	</script>
</body>
</html>