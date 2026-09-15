document.getElementById('convertForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/api/convert', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').classList.remove('hidden');

        document.getElementById('convertedTime').textContent = `${data.from_zone} → ${data.to_zone}`;

        createClock('clockFromZone', parseFloat(data.from_hour_angle), parseFloat(data.from_minute_angle));
        createClock('clockToZone', parseFloat(data.to_hour_angle), parseFloat(data.to_minute_angle));
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while converting the time.');
    });
});

function createClock(containerId, hourAngle, minuteAngle) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';  // Clear any existing clock

    // Clock
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 100 100");
    svg.setAttribute("class", "absolute w-full h-full");
    container.appendChild(svg);

    // Circle
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", "50");
    circle.setAttribute("cy", "50");
    circle.setAttribute("r", "45");
    circle.setAttribute("fill", "none");
    circle.setAttribute("stroke", "#333");
    circle.setAttribute("stroke-width", "1");
    svg.appendChild(circle);

    // Hour hand
    const hourHand = document.createElementNS("http://www.w3.org/2000/svg", "line");
    hourHand.setAttribute("x1", "50");
    hourHand.setAttribute("y1", "50");
    hourHand.setAttribute("x2", "50");
    hourHand.setAttribute("y2", "10");
    hourHand.setAttribute("stroke", "black");
    hourHand.setAttribute("stroke-width", "4");
    hourHand.setAttribute("transform", `rotate(${hourAngle}, 50, 50)`);
    svg.appendChild(hourHand);

    // Minute hand
    const minuteHand = document.createElementNS("http://www.w3.org/2000/svg", "line");
    minuteHand.setAttribute("x1", "50");
    minuteHand.setAttribute("y1", "50");
    minuteHand.setAttribute("x2", "50");
    minuteHand.setAttribute("y2", "5");
    minuteHand.setAttribute("stroke", "red");
    minuteHand.setAttribute("stroke-width", "2");
    minuteHand.setAttribute("transform", `rotate(${minuteAngle}, 50, 50)`);
    svg.appendChild(minuteHand);
}

function updateTimezoneClocks() {
    const timezones = document.querySelectorAll('[id^="time_"]');
    
    timezones.forEach(timezoneElement => {
        const timezone = timezoneElement.id.replace("time_", "");
        
        const currentTime = new Date().toLocaleTimeString('en-US', {
            timeZone: timezone,
            hour12: true
        });
        timezoneElement.textContent = currentTime;

        setInterval(function() {
            const updatedTime = new Date().toLocaleTimeString('en-US', {
                timeZone: timezone,
                hour12: true
            });
            timezoneElement.textContent = updatedTime;
        }, 1000);
    });
}

window.onload = updateTimezoneClocks;
