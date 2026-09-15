<?php

if (!isset($_POST['picture_name'])) {
    echo "No file.";
    exit;
}

$data = file_get_contents($_POST['picture_name']);
echo base64_encode("$data");