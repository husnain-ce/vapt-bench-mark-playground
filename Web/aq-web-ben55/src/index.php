<?php

$images = [
    "./images/acid.png",
    "./images/happy.png",
    "./images/jerry.png",
    "./images/christmas.png",
    "./images/open_eyes.png",
    "./images/tickle.png"
];

$selected = null;

if ($_SERVER["REQUEST_METHOD"] === "GET") {
    $selected = $images[array_rand($images)];
}

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $headers = getallheaders();
    if (!empty($headers["Image"])) {
        $raw = $headers["Image"];

        $blockedProtocols = [
            "http://", "https://", "ftp://", "ftps://",
            "file://", "data://", "expect://", "php://",
            "passwd"
        ];

        foreach ($blockedProtocols as $proto) {
            if (strpos($raw, $proto) !== false) {
                $raw = "";
                break;
            }
        }    

        if (str_contains($raw, "../") || str_contains($raw, "..\\")) {
            $raw = "";
        }

        if ($raw === "" || trim($raw) === "") {
            $selected = $images[array_rand($images)];
        } else {
            $selected = $raw;
        }

    } else {
        $selected = $images[array_rand($images)];
    }
}


$ch = curl_init("http://localhost:80/getpic.php");
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(["picture_name" => $selected]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$encodedImage = curl_exec($ch);
curl_close($ch);

$extension = strtolower(pathinfo($selected, PATHINFO_EXTENSION));
$mime = ($extension === "png") ? "image/png" :
        (($extension === "jpeg" || $extension === "jpg") ? "image/jpeg" : "application/octet-stream");

if ($_SERVER["REQUEST_METHOD"] === "GET") {
?>
<!DOCTYPE html>
<html>
<head>
<style>

body {
    background: linear-gradient(135deg, #1A1A2E, #6B1E7C);
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-size: cover;
    font-family: "Trebuchet MS", Arial, sans-serif;
    text-align: center;
    padding-top: 40px;
    color: #F2F7F5;
    margin: 0;
    min-height: 100vh;
}

.container {
    background: #3AABA3;
    padding: 40px;
    display: inline-block;
    border-radius: 25px;
    box-shadow: 0 0 35px rgba(0, 255, 156, 0.7),
                0 0 55px rgba(182, 255, 0, 0.45);
    border: 4px solid #00FF9C;
    max-width: 650px;
    margin: 0 auto;
}

button {
    padding: 16px 32px;
    font-size: 20px;
    background:#6B1E7C; 
    color:white; 
    border:none; 
    border-radius:10px; 
    cursor:pointer;
    transition: all 0.3s ease;
    margin-top: 15px;
}

button:hover {
    background: #8A2C9E;
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(182, 255, 0, 0.7);
}

img {
    max-width: 550px;
    width: 100%;
    border-radius: 15px;
    margin-bottom: 20px;
    border: 5px solid #B6FF00;
    box-shadow: 0 0 20px rgba(255,255,255,0.4);
}

h2 {
    color: #00FF9C;
    text-shadow: 0 0 12px #00FF9C;
    font-size: 2.2rem;
    margin-bottom: 25px;
}
</style>
</head>
<body>

<div class="container">
    <h2>Rick & Morty Gallery</h2>

    <img id="pic" src="data:<?php echo $mime; ?>;base64,<?php echo $encodedImage; ?>" alt="Photo Frame">
    <hr>
    <button onclick="nextImage()">Next</button>
</div>

<script>
function nextImage() {

    const images = [
        "./images/acid.png",
        "./images/happy.png",
        "./images/jerry.png",
        "./images/christmas.png",
        "./images/open_eyes.png",
        "./images/tickle.png"
    ];

    const randomImage = images[Math.floor(Math.random() * images.length)];

    fetch("index.php", { 
        method: "POST",
        headers: { 
            "Image": randomImage 
        }
    })
    .then(response => response.text())
    .then(base64 => {
        let mime = "image/png"; 
        document.getElementById("pic").src =
            "data:" + mime + ";base64," + base64;
    });
}
</script>

</body>
</html>

<?php
} else {
    echo $encodedImage;
}
?>
