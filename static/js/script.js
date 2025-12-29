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

    fetch('/order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            const modalOrder = bootstrap.Modal.getInstance(document.getElementById("orderModal"));
            modalOrder.hide();

            const successModal = new bootstrap.Modal(document.getElementById("successModal"));
            successModal.show();

            form.reset();
        } else if (response.status === 401) {
            alert("Sesi berakhir atau Anda belum login. Silakan login kembali.");
            window.location.href = "/login";
        } else {
            alert("Terjadi kesalahan saat menyimpan pesanan.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Gagal terhubung ke server.");
    });
}