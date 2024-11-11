function validateForm() {
    var email = document.getElementById('email').value;
    var emailError = document.getElementById('emailError');
    var username = document.getElementById('username').value;
    var usernameError = document.getElementById('usernameError');
    var contact_number = document.getElementById('contact_number').value;
    var contact_numberError = document.getElementById('contact_number')

    // Email validation regex
    var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z]+\.[a-zA-Z]{2,}$/;
    
    // Username validation regex: Must start with a letter
    var usernamePattern = /^[a-zA-Z][a-zA-Z0-9_]*$/;

    var valid = true;

    // Username validation: Must start with a letter
    if (!usernamePattern.test(username)) {
        //usernameError.textContent = "Username must start with a letter and can only contain letters, numbers, and underscores.";
        alert("Invalid username. It must start with a letter.");
        valid = false;
    } else {
        usernameError.textContent = ""; // Clear the error message if valid
    }

    // Email validation
    if (!emailPattern.test(email)) {
        //emailError.textContent = "Invalid email format. Please enter a valid email (e.g., example@gmail.com). No numbers allowed after '@'.";
        alert("Invalid email. Please follow the correct format (e.g., example@gmail.com).");
        valid = false;
    } else {
        emailError.textContent = ""; // Clear the error message if valid
    }

    

    if(contact_number.length !== 10 || isNaN(contact)){
        alert("Contact Number must be of 10 digits.")
        valid=false;
    } else {
        contactError.textContent = "";
    }

    return valid; // Return false if either validation fails
}



var diwaliDate = new Date("November 02, 2024 00:00:00").getTime();

var countdownTimer = setInterval(function() {

    var now = new Date().getTime();

    var distance = diwaliDate - now;
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    document.getElementById("countdown").innerHTML = days + "d " + hours + "h " +
    minutes + "m " + seconds + "s ";

    if (distance < 0) {
        clearInterval(countdownTimer);
        document.getElementById("countdown").innerHTML = "EXPIRED";
    }
}, 1000);

function verifyCoupon() {
    const couponCode = document.getElementById('coupon_code').value;
    const currentAmount = parseFloat(document.getElementById('current_amount').value);

    if (!couponCode) {
        document.getElementById('coupon-status').innerHTML = "Please enter a coupon code.";
        return;
    }

    fetch('/verifyCoupon', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ coupon: couponCode }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            const discountPercentage = 15;  // Assuming a fixed 15% discount for valid coupons
            const discountAmount = (discountPercentage / 100) * currentAmount;
            const totalAmount = currentAmount - discountAmount;

            document.getElementById('coupon-status').innerHTML = "<span style='color:green;'>Coupon applied! 15% off.</span>";
            document.getElementById('discount').value = discountPercentage + "%";
            document.getElementById('total_amount').value = totalAmount.toFixed(2);
            document.getElementById('hidden_total_amount').value = totalAmount.toFixed(2);  // Update hidden field
        } else {
            document.getElementById('coupon-status').innerHTML = "<span style='color:red;'>Invalid coupon code.</span>";
            document.getElementById('discount').value = "0%";
            document.getElementById('total_amount').value = currentAmount.toFixed(2);
            document.getElementById('hidden_total_amount').value = currentAmount.toFixed(2);  // Reset total amount in hidden field
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('coupon-status').innerHTML = "<span style='color:red;'>Error verifying coupon.</span>";
    });
}