document.addEventListener("DOMContentLoaded", function() {
    const currency = document.querySelectorAll('.currency-pn');
    currency.forEach(element => {
        if (parseFloat(element.innerHTML.slice(1)) < 0) {
            element.classList.remove('text-success')
            element.classList.add('text-danger')
        }
    });
  });