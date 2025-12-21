// Navbar auto close on link click (mobile)
document.addEventListener('DOMContentLoaded', function () {
    var navCollapse = document.getElementById('navMenu');

    if (navCollapse) {
        var bsCollapse = new bootstrap.Collapse(navCollapse, {
            toggle: false
        });

        var navLinks = navCollapse.querySelectorAll('.nav-link');

        navLinks.forEach(function (link) {
            link.addEventListener('click', function () {
                if (navCollapse.classList.contains('show')) {
                    bsCollapse.hide();
                }
            });
        });
    }
});

// selected service data
let selectedService = "";
let selectedPrice = 0;

// open order modal
function openOrder(service, price) {
    selectedService = service;
    selectedPrice = price;

    document.getElementById("layanan").value = service;
    document.getElementById("harga").value =
        "Rp " + price.toLocaleString("id-ID");

    const modal = new bootstrap.Modal(
        document.getElementById("orderModal")
    );
    modal.show();
}

// submit order form
function submitOrder() {
    const form = document.getElementById("orderForm");

    // form validation
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const data = {
        nama: document.getElementById("nama").value,
        telepon: document.getElementById("telepon").value,
        alamat: document.getElementById("alamat").value,
        tanggal: document.getElementById("tanggal").value,
        bank: document.getElementById("bank").value,
        layanan: selectedService,
        harga: selectedPrice
    };

    // simulate send data
    console.log("ORDER DATA:", data);

    // close order modal
    const modalOrder = bootstrap.Modal.getInstance(
        document.getElementById("orderModal")
    );
    modalOrder.hide();

    // show success modal
    const successModal = new bootstrap.Modal(
        document.getElementById("successModal")
    );
    successModal.show();

    // reset form
    form.reset();
}
